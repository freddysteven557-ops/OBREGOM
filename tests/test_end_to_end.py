import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("ffmpeg"), "requiere ffmpeg")
class EndToEndTest(unittest.TestCase):
    def test_generates_vertical_and_horizontal_clips(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            video = tmp / "partida.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-y",
                "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=40",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=40,volume='if(between(t,25,30),1.0,0.02)':eval=frame",
                "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", str(video),
            ], check=True)

            out = tmp / "clips"
            subprocess.run([sys.executable, "-m", "clipgen", str(video), "-o", str(out), "-n", "2", "-d", "8"],
                           check=True, cwd=ROOT)

            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            best = manifest[0]
            self.assertTrue(best["start"] <= 25 < best["end"])
            for fmt, size in {"vertical": "1080,1920", "horizontal": "1920,1080"}.items():
                path = out / best["files"][fmt]
                dims = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                     "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip()
                self.assertEqual(dims, size)


if __name__ == "__main__":
    unittest.main()
