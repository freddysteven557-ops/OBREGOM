"""Lectura de video con ffmpeg/ffprobe: duración, audio y cambios de escena."""

import json
import re
import shutil
import subprocess

import numpy as np

AUDIO_RATE = 8000  # Hz; suficiente para medir volumen y rápido de procesar


class FFmpegError(RuntimeError):
    pass


def require_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise FFmpegError(f"No se encontró '{tool}'. Instálalo: https://ffmpeg.org/download.html")


def run(cmd, capture_stdout=False, cwd=None):
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE if capture_stdout else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        tail = proc.stderr.decode(errors="replace").strip().splitlines()[-5:]
        raise FFmpegError(f"Falló: {' '.join(cmd[:3])} ...\n" + "\n".join(tail))
    return proc


def probe(path):
    """Devuelve (duración en segundos, tiene_audio)."""
    proc = run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_stdout=True,
    )
    info = json.loads(proc.stdout)
    duration = float(info["format"].get("duration", 0.0))
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    return duration, has_audio


def loudness_per_second(path, duration, has_audio):
    """Volumen RMS (dBFS) de cada segundo del video."""
    seconds = max(1, int(np.ceil(duration)))
    if not has_audio:
        return np.full(seconds, -90.0)

    proc = run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1",
         "-ar", str(AUDIO_RATE), "-f", "s16le", "-"],
        capture_stdout=True,
    )
    samples = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    padded = np.zeros(seconds * AUDIO_RATE, dtype=np.float32)
    n = min(len(samples), len(padded))
    padded[:n] = samples[:n]
    rms = np.sqrt(np.mean(padded.reshape(seconds, AUDIO_RATE) ** 2, axis=1))
    return 20 * np.log10(np.maximum(rms, 3e-5))  # piso de -90 dB para el silencio


_PTS_RE = re.compile(r"pts_time:([0-9.]+)")


def scene_changes(path, threshold=0.3):
    """Marcas de tiempo (s) donde la imagen cambia bruscamente: cortes, explosiones, choques."""
    proc = run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-an",
         "-vf", f"fps=10,scale=320:-2,select='gt(scene,{threshold})',showinfo",
         "-f", "null", "-"],
    )
    return [float(m.group(1)) for m in _PTS_RE.finditer(proc.stderr.decode(errors="replace"))]


def extract_audio_wav(path, start, length, dest):
    """Extrae un tramo de audio a WAV 16 kHz mono (formato que espera Whisper)."""
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", str(path),
         "-t", f"{length:.3f}", "-vn", "-ac", "1", "-ar", "16000", str(dest)])
