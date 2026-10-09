"""Clips generados con IA (Higgsfield): python -m clipgen.ia "prompt" [-o clips/]"""

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

from . import captions, higgsfield
from .cli import append_manifest
from .export import render_clip
from .media import FFmpegError, probe, require_ffmpeg

# Se añade a cada prompt para mantener una estética coherente entre clips.
DEFAULT_STYLE = (
    "cinematic open-world video game footage, sunny neon Miami-inspired city, "
    "palm trees, ocean drive, dynamic camera, high detail"
)


def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="clipgen.ia",
        description="Genera clips estilo GTA 6 con la IA de Higgsfield y los deja listos para redes.",
    )
    p.add_argument("prompts", nargs="*", help="Descripción de cada clip (uno por argumento)")
    p.add_argument("-p", "--prompts-file", type=Path, help="Archivo .txt con un prompt por línea")
    p.add_argument("-o", "--output", type=Path, default=Path("clips"), help="Carpeta de salida (por defecto: clips/)")
    p.add_argument("-d", "--duration", type=int, default=5, help="Segundos por clip (Kling 3.0: 3-15; por defecto: 5)")
    p.add_argument("-f", "--format", choices=["ambos", "vertical", "horizontal"], default="ambos",
                   help="ambos = una sola generación 16:9 y la versión 9:16 se arma con fondo desenfocado")
    p.add_argument("--image", help="Imagen (archivo o URL) como primer fotograma: usa image-to-video")
    p.add_argument("--model", default=higgsfield.DEFAULT_MODEL,
                   help=f"Modelo de Higgsfield (por defecto: {higgsfield.DEFAULT_MODEL})")
    p.add_argument("--style", default=DEFAULT_STYLE, help="Texto de estilo que se añade a cada prompt ('' para ninguno)")
    p.add_argument("--title", default="GTA 6", help="Título base para las publicaciones")
    p.add_argument("--hashtags", default=" ".join(captions.DEFAULT_HASHTAGS + ["#IA", "#AIvideo"]),
                   help="Hashtags separados por espacios")
    p.add_argument("--dry-run", action="store_true", help="Mostrar lo que se enviaría sin gastar créditos")
    return p.parse_args(argv)


def load_prompts(args):
    prompts = list(args.prompts)
    if args.prompts_file:
        lines = args.prompts_file.read_text(encoding="utf-8").splitlines()
        prompts += [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    return prompts


def full_prompt(prompt, style):
    return f"{prompt}. {style}" if style else prompt


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    prompts = load_prompts(args)
    if not prompts:
        print("Escribe al menos un prompt, p. ej.: python -m clipgen.ia \"persecución policial en la playa\"",
              file=sys.stderr)
        return 1

    native = "horizontal" if args.format == "ambos" else args.format
    formats = ["vertical", "horizontal"] if args.format == "ambos" else [args.format]
    model_id = higgsfield.endpoint(args.model, with_image=bool(args.image))

    if args.dry_run:
        for i, prompt in enumerate(prompts, 1):
            arguments = higgsfield.build_arguments(full_prompt(prompt, args.style), args.duration,
                                                   higgsfield.ASPECT_RATIOS[native], args.image)
            print(f"[{i}] POST {model_id}\n    {json.dumps(arguments, ensure_ascii=False)}")
        return 0

    try:
        require_ffmpeg()
        if not higgsfield.has_credentials():
            raise higgsfield.HiggsfieldError(
                "Faltan credenciales: export HF_KEY=\"tu-api-key:tu-api-secret\" (https://cloud.higgsfield.ai)")
        image_url = higgsfield.upload_image(args.image) if args.image else None
    except (FFmpegError, higgsfield.HiggsfieldError) as e:
        print(e, file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    hashtags = args.hashtags.split()
    batch = time.strftime("%Y%m%d-%H%M%S")
    entries = []

    for i, prompt in enumerate(prompts, 1):
        name = f"ia_{batch}_{i:02}"
        print(f"\n▶ [{i}/{len(prompts)}] {prompt}")
        arguments = higgsfield.build_arguments(full_prompt(prompt, args.style), args.duration,
                                               higgsfield.ASPECT_RATIOS[native], image_url)
        try:
            request_id, url = higgsfield.generate(
                model_id, arguments, on_status=lambda s: print(f"  … {s}", flush=True))
            with tempfile.TemporaryDirectory() as tmp:
                raw = higgsfield.download(url, Path(tmp) / "raw.mp4")
                duration, has_audio = probe(raw)
                files = {}
                for fmt in formats:
                    dest = args.output / f"{name}_{fmt}.mp4"
                    render_clip(raw, 0, duration, dest, fmt, has_audio=has_audio)
                    files[fmt] = dest.name
                    print(f"  ✓ {dest.name}")
        except (FFmpegError, higgsfield.HiggsfieldError, OSError) as e:
            print(f"  ✗ {e}", file=sys.stderr)
            continue

        entries.append({
            "name": name,
            "source": "higgsfield",
            "model": model_id,
            "request_id": request_id,
            "prompt": arguments["prompt"],
            "video_url": url,
            "files": files,
            "post": captions.social_post(i, args.title, hashtags, prompt),
        })

    if entries:
        append_manifest(args.output / "manifest.json", entries)
    print(f"\nListo: {len(entries)}/{len(prompts)} clips en {args.output}/")
    return 0 if entries else 1


if __name__ == "__main__":
    raise SystemExit(main())
