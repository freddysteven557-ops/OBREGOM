"""Detección de los mejores momentos combinando volumen del audio y cambios de escena.

En gameplay, los momentos "clipeables" (tiroteos, persecuciones, choques, gritos del
streamer) suelen coincidir con picos de volumen y con muchos cambios bruscos de imagen.
"""

from dataclasses import dataclass

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

AUDIO_WEIGHT = 0.65
SCENE_WEIGHT = 0.35
PEAK_BONUS = 0.3  # premia ventanas con un pico fuerte aunque el resto sea tranquilo
MIN_SCORE_RATIO = 0.3  # descarta clips con menos del 30% del puntaje del mejor


@dataclass
class Highlight:
    start: float
    end: float
    score: float

    @property
    def length(self):
        return self.end - self.start


def _normalize(values, low_pct, high_pct):
    lo, hi = np.percentile(values, [low_pct, high_pct])
    if hi - lo < 1e-6:
        return np.zeros_like(values, dtype=float)
    return np.clip((values - lo) / (hi - lo), 0.0, 1.0)


def score_per_second(loudness_db, scene_times):
    """Puntaje 0..1 de "intensidad" para cada segundo."""
    seconds = len(loudness_db)
    loud = _normalize(np.asarray(loudness_db, dtype=float), 10, 99)

    cuts = np.zeros(seconds)
    for t in scene_times:
        cuts[min(int(t), seconds - 1)] += 1
    scenes = np.clip(cuts / 3.0, 0.0, 1.0)  # 3+ cambios por segundo = máximo

    return AUDIO_WEIGHT * loud + SCENE_WEIGHT * scenes


def pick_highlights(scores, duration, clip_length, count, min_gap=5):
    """Elige hasta `count` ventanas de `clip_length` segundos sin solaparse, mejores primero."""
    clip_length = int(round(clip_length))
    if duration <= clip_length or len(scores) <= clip_length:
        return [Highlight(0.0, float(duration), float(np.mean(scores)) if len(scores) else 0.0)]

    windows = sliding_window_view(np.asarray(scores, dtype=float), clip_length)
    window_scores = windows.mean(axis=1) + PEAK_BONUS * windows.max(axis=1)
    last_start = duration - clip_length

    available = np.ones(len(window_scores), dtype=bool)
    available[np.arange(len(window_scores)) > last_start] = False

    picked = []
    while len(picked) < count and available.any():
        masked = np.where(available, window_scores, -np.inf)
        start = int(np.argmax(masked))
        if picked and window_scores[start] < MIN_SCORE_RATIO * picked[0].score:
            break  # lo que queda es relleno aburrido
        picked.append(Highlight(float(start), float(start + clip_length), float(window_scores[start])))
        lo = max(0, start - clip_length - min_gap + 1)
        hi = min(len(available), start + clip_length + min_gap)
        available[lo:hi] = False

    return picked
