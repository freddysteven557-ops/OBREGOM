"""Subtítulos automáticos (opcional, con faster-whisper) y textos para publicar en redes."""

DEFAULT_HASHTAGS = ["#GTA6", "#GTAVI", "#GrandTheftAuto", "#Gaming", "#Gameplay", "#Rockstar"]

PLATFORM_LIMITS = {"tiktok": 2200, "instagram": 2200, "youtube_shorts": 100, "youtube": 100}

_model = None


def whisper_available():
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        return False
    return True


def transcribe(wav_path, language=None, model_size="small"):
    """Devuelve una lista de (inicio, fin, texto) usando faster-whisper."""
    global _model
    from faster_whisper import WhisperModel

    if _model is None:
        _model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _ = _model.transcribe(str(wav_path), language=language, vad_filter=True)
    return [(s.start, s.end, s.text.strip()) for s in segments if s.text.strip()]


def _timestamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(segments, dest):
    lines = []
    for i, (start, end, text) in enumerate(segments, 1):
        lines += [str(i), f"{_timestamp(start)} --> {_timestamp(end)}", text, ""]
    with open(dest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return dest


def social_post(index, title, hashtags, transcript=""):
    """Título y descripción sugeridos para cada red social."""
    tags = " ".join(hashtags)
    name = f"{title} #{index}" if title else f"Clip #{index}"
    hook = transcript[:120].rstrip() + ("…" if len(transcript) > 120 else "") if transcript else ""
    body = f"{hook}\n\n{tags}" if hook else tags
    return {
        "tiktok": f"{name} 🔥 {body}"[: PLATFORM_LIMITS["tiktok"]],
        "instagram": f"{name} 🔥\n\n{body}"[: PLATFORM_LIMITS["instagram"]],
        "youtube_shorts": {
            "title": f"{name} #Shorts"[: PLATFORM_LIMITS["youtube_shorts"]],
            "description": body,
        },
        "youtube": {"title": name[: PLATFORM_LIMITS["youtube"]], "description": body},
    }
