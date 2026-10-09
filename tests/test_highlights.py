import unittest

import numpy as np

from clipgen.captions import _timestamp, social_post
from clipgen.highlights import pick_highlights, score_per_second


class HighlightTests(unittest.TestCase):
    def test_loud_section_is_picked_first(self):
        loudness = np.full(120, -40.0)
        loudness[70:80] = -5.0
        hl = pick_highlights(score_per_second(loudness, []), 120, 15, 3)
        self.assertLessEqual(hl[0].start, 70)
        self.assertGreaterEqual(hl[0].end, 80)

    def test_scene_cuts_add_score(self):
        loudness = np.full(60, -30.0)
        cuts = [40 + i * 0.3 for i in range(20)]
        hl = pick_highlights(score_per_second(loudness, cuts), 60, 10, 1)
        self.assertTrue(hl[0].start <= 40 < hl[0].end)

    def test_clips_do_not_overlap(self):
        rng = np.random.default_rng(0)
        loudness = rng.uniform(-40, -5, 600)
        hl = pick_highlights(score_per_second(loudness, []), 600, 30, 8)
        spans = sorted((h.start, h.end) for h in hl)
        for (_, end), (start, _) in zip(spans, spans[1:]):
            self.assertLessEqual(end, start)
        for h in hl:
            self.assertLessEqual(h.end, 600)

    def test_boring_filler_is_dropped(self):
        loudness = np.full(300, -40.0)
        loudness[100:110] = -3.0
        hl = pick_highlights(score_per_second(loudness, []), 300, 20, 5)
        self.assertEqual(len(hl), 1)

    def test_short_video_returns_whole_video(self):
        hl = pick_highlights(np.zeros(8), 7.5, 30, 3)
        self.assertEqual((hl[0].start, hl[0].end), (0.0, 7.5))


class CaptionTests(unittest.TestCase):
    def test_srt_timestamp(self):
        self.assertEqual(_timestamp(3725.5), "01:02:05,500")

    def test_social_post_limits(self):
        post = social_post(1, "GTA 6 " * 40, ["#GTA6"], "hola " * 100)
        self.assertLessEqual(len(post["youtube_shorts"]["title"]), 100)
        self.assertIn("#GTA6", post["tiktok"])


if __name__ == "__main__":
    unittest.main()
