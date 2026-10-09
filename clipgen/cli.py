"""Línea de comandos: python -m clipgen VIDEO [VIDEO...] -o clips/"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from . import captions
from .export import render_clip
from .highlights import pick_highlights, score_per_second
from .media import FFmpegError, extract_audio_wav, loudness_per_second, probe, require_ffmpeg, scene_changes

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".webm", ".avi", ".flv", ".ts"}


def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="clipgen",
        description="Detecta los mejores momentos de tus videos de GTA 6 y los exporta como clips para redes.",
    )
    p.add_argument("inputs", nargs="+", type=Path, help="Videos o carpetas con videos")
    p.add_argument("-o", "--output", type=Path, default=Path("clips"), help="Carpeta de salida (por defecto: clips/)")
    p.add_argument("-n", "--clips", type=int, default=5, help="Clips por video (por defecto: 5)")
    p.add_argument("-d", "--duration", type=float, default=30, help="Duración de cada clip en segundos (por defecto: 30)")
    p.add_argument("-f", "--format", choices=["ambos", "vertical", "horizontal"], default="ambos",
                   help="vertical = 9:16 (TikTok/Reels/Shorts), horizontal = 16:9 (YouTube)")
    p.add_argument("--vertical-mode", choices=["blur", "crop"], default="blur",
                   help="blur = video completo con fondo desenfocado, crop = recorte al centro")
    p.add_argument("--subs", action="store_true", help="Subtítulos automáticos (requiere: pip install faster-whisper)")
    p.add_argument("--language", default=None, help="Idioma de los subtítulos, p. ej. es o en (por defecto: autodetectar)")
    p.add_argument("--title", default="GTA 6", help="Título base para las publicaciones")
    p.add_argument("--hashtags", default=" ".join(captions.DEFAULT_HASHTAGS), help="Hashtags separados por espacios")
    p.add_argument("--scene-threshold", type=float, default=0.3, help="Sensibilidad a cambios de escena (0-1)")
    p.add_argument("--no-scenes", action="store_true", help="Usar solo el audio (más rápido en videos muy largos)")
    p.add_argument("--dry-run", action="store_true", help="Solo mostrar los momentos detectados, sin exportar")
    return p.parse_args(argv)


def collect_videos(inputs):
    videos = []
    for path in inputs:
        if path.is_dir():
            videos += sorted(f for f in path.iterdir() if f.suffix.lower() in VIDEO_EXTENSIONS)
        elif path.is_file():
            videos.append(path)
        else:
            print(f"⚠ No existe: {path}", file=sys.stderr)
    return videos


def append_manifest(path, entries):
    """Agrega al manifest existente para no perder clips de ejecuciones anteriores."""
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    path.write_text(json.dumps(existing + entries, ensure_ascii=False, indent=2), encoding="utf-8")


def fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def process_video(video, args, formats, use_subs, hashtags):
    print(f"\n▶ {video.name}")
    duration, has_audio = probe(video)
    print(f"  Duración {fmt_time(duration)}{'' if has_audio else ' (sin audio)'} — analizando…")

    loudness = loudness_per_second(video, duration, has_audio)
    scenes = [] if args.no_scenes else scene_changes(video, args.scene_threshold)
    highlights = pick_highlights(score_per_second(loudness, scenes), duration, args.duration, args.clips)

    results = []
    for i, hl in enumerate(highlights, 1):
        name = f"{video.stem}_clip{i:02}"
        print(f"  [{i}] {fmt_time(hl.start)} – {fmt_time(hl.end)}  puntaje {hl.score:.2f}")
        if args.dry_run:
            continue

        segments, srt = [], None
        with tempfile.TemporaryDirectory() as tmp:
            if use_subs and has_audio:
                wav = Path(tmp) / "audio.wav"
                extract_audio_wav(video, hl.start, hl.length, wav)
                segments = captions.transcribe(wav, args.language)
                if segments:
                    # Nombre fijo para el filtro de ffmpeg; la copia con el nombre del clip va a la salida.
                    srt = captions.write_srt(segments, Path(tmp) / "subs.srt")
                    shutil.copy(srt, args.output / f"{name}.srt")

            files = {}
            for fmt in formats:
                dest = args.output / f"{name}_{fmt}.mp4"
                render_clip(video, hl.start, hl.length, dest, fmt, args.vertical_mode, srt, has_audio)
                files[fmt] = dest.name
                print(f"      ✓ {dest.name}")

        transcript = " ".join(text for _, _, text in segments)
        results.append({
            "name": name,
            "source": str(video),
            "start": hl.start,
            "end": hl.end,
            "score": round(hl.score, 3),
            "files": files,
            "subtitles": f"{name}.srt" if srt else None,
            "transcript": transcript,
            "post": captions.social_post(i, args.title, hashtags, transcript),
        })
    return results


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        require_ffmpeg()
    except FFmpegError as e:
        print(e, file=sys.stderr)
        return 1

    videos = collect_videos(args.inputs)
    if not videos:
        print("No se encontraron videos.", file=sys.stderr)
        return 1

    formats = ["vertical", "horizontal"] if args.format == "ambos" else [args.format]
    hashtags = args.hashtags.split()
    use_subs = args.subs and not args.dry_run
    if use_subs and not captions.whisper_available():
        print("⚠ Subtítulos desactivados: instala faster-whisper (pip install faster-whisper).", file=sys.stderr)
        use_subs = False

    if not args.dry_run:
        args.output.mkdir(parents=True, exist_ok=True)

    manifest = []
    for video in videos:
        try:
            manifest += process_video(video, args, formats, use_subs, hashtags)
        except FFmpegError as e:
            print(f"  ✗ Error con {video.name}: {e}", file=sys.stderr)

    if not args.dry_run:
        manifest_path = args.output / "manifest.json"
        append_manifest(manifest_path, manifest)
        print(f"\nListo: {len(manifest)} clips en {args.output}/ (textos para publicar en {manifest_path.name})")
    return 0
