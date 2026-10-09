import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

from clipgen import higgsfield, ia


class Queued:
    pass


class Completed:
    pass


class Failed:
    pass


class FakeController:
    def __init__(self, video_url, final_status):
        self.request_id = "req-123"
        self.video_url = video_url
        self.final_status = final_status

    def poll_request_status(self):
        yield Queued()
        yield self.final_status()

    def get(self):
        return {"status": "completed", "video": {"url": self.video_url}}


class FakeSDK:
    def __init__(self, video_url, final_status=Completed):
        self.video_url = video_url
        self.final_status = final_status
        self.calls = []

    def submit(self, model_id, arguments):
        self.calls.append((model_id, arguments))
        return FakeController(self.video_url, self.final_status)


class HiggsfieldUnitTests(unittest.TestCase):
    def test_endpoint(self):
        self.assertEqual(higgsfield.endpoint("kling-video/v3.0/std", False), "kling-video/v3.0/std/text-to-video")
        self.assertEqual(higgsfield.endpoint("kling-video/v3.0/std", True), "kling-video/v3.0/std/image-to-video")
        self.assertEqual(higgsfield.endpoint("x/y/image-to-video", False), "x/y/image-to-video")

    def test_arguments(self):
        self.assertEqual(higgsfield.build_arguments("hola", 5, "9:16"),
                         {"prompt": "hola", "duration": 5, "aspect_ratio": "9:16"})
        self.assertNotIn("aspect_ratio", higgsfield.build_arguments("hola", 5, "9:16", "https://img"))

    def test_find_video_url_fallback(self):
        self.assertEqual(higgsfield.find_video_url({"jobs": [{"raw": {"url": "https://cdn/x.mp4"}}]}),
                         "https://cdn/x.mp4")
        with self.assertRaises(higgsfield.HiggsfieldError):
            higgsfield.find_video_url({"images": []})

    def test_failed_generation_raises(self):
        sdk = FakeSDK("https://cdn/x.mp4", final_status=Failed)
        with mock.patch.object(higgsfield, "_client", return_value=sdk):
            with self.assertRaises(higgsfield.HiggsfieldError):
                higgsfield.generate("m/text-to-video", {"prompt": "x"})

    def test_dry_run_does_not_call_api(self):
        with mock.patch.object(higgsfield, "_client", side_effect=AssertionError("no debe llamar a la API")):
            out = StringIO()
            with redirect_stdout(out):
                self.assertEqual(ia.main(["persecución en la playa", "--dry-run", "-f", "vertical"]), 0)
        self.assertIn('"aspect_ratio": "9:16"', out.getvalue())
        self.assertIn("kling-video/v3.0/std/text-to-video", out.getvalue())


@unittest.skipUnless(shutil.which("ffmpeg"), "requiere ffmpeg")
class IaEndToEndTest(unittest.TestCase):
    def test_generates_downloads_and_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fake_video = tmp / "generado.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=24:duration=3",
                "-f", "lavfi", "-i", "sine=duration=3", "-c:v", "libx264", "-preset", "ultrafast",
                "-c:a", "aac", "-shortest", str(fake_video)], check=True)

            sdk = FakeSDK(fake_video.as_uri())
            out = tmp / "clips"
            with mock.patch.object(higgsfield, "_client", return_value=sdk), \
                    mock.patch.dict(os.environ, {"HF_KEY": "k:s"}), redirect_stdout(StringIO()):
                code = ia.main(["persecución policial", "-o", str(out), "-d", "3"])

            self.assertEqual(code, 0)
            model_id, arguments = sdk.calls[0]
            self.assertEqual(model_id, "kling-video/v3.0/std/text-to-video")
            self.assertEqual(arguments["aspect_ratio"], "16:9")  # "ambos" genera una sola vez en 16:9
            entry = json.loads((out / "manifest.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(entry["request_id"], "req-123")
            self.assertEqual(set(entry["files"]), {"vertical", "horizontal"})
            for name in entry["files"].values():
                self.assertTrue((out / name).stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
