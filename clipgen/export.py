"""Renderizado de clips en vertical (9:16) y horizontal (16:9)."""

from pathlib import Path

from .media import run

FORMATS = {
    "vertical": (1080, 1920),    # TikTok, Reels, YouTube Shorts
    "horizontal": (1920, 1080),  # YouTube, X, Facebook
}

SUBTITLE_STYLE = (
    "FontName=Arial,FontSize=14,Bold=1,PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=60"
)


def video_filter(fmt, vertical_mode="blur", subtitles=None):
    """Grafo de filtros de ffmpeg; la salida se etiqueta como [v]."""
    w, h = FORMATS[fmt]
    if fmt == "vertical" and vertical_mode == "blur":
        # El video completo al centro y una copia ampliada y desenfocada de fondo.
        graph = (
            f"[0:v]split=2[bg][fg];"
            f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bgb];"
            f"[fg]scale={w}:-2[fgs];"
            f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2"
        )
    elif fmt == "vertical":
        # Recorte al centro: llena la pantalla pero pierde los lados.
        graph = f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    else:
        graph = (
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
        )
    graph += ",setsar=1"
    if subtitles:
        # Se ejecuta ffmpeg desde la carpeta del .srt para no escapar rutas dentro del filtro.
        graph += f",subtitles={Path(subtitles).name}:force_style='{SUBTITLE_STYLE}'"
    return graph + "[v]"


def render_clip(source, start, length, dest, fmt, vertical_mode="blur",
                subtitles=None, has_audio=True):
    source = Path(source).resolve()
    dest = Path(dest).resolve()
    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{length:.3f}",
        "-filter_complex", video_filter(fmt, vertical_mode, subtitles),
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", "30",
    ]
    if has_audio:
        fade_out = max(0.0, length - 0.5)
        cmd += ["-map", "0:a:0", "-c:a", "aac", "-b:a", "160k",
                "-af", f"afade=t=in:d=0.3,afade=t=out:st={fade_out:.3f}:d=0.5"]
    cmd += ["-movflags", "+faststart", str(dest)]
    run(cmd, cwd=Path(subtitles).resolve().parent if subtitles else None)
    return dest
