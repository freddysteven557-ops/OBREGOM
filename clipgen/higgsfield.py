"""Generación de video con IA usando la API de Higgsfield (https://cloud.higgsfield.ai).

Credenciales por variables de entorno: HF_KEY="clave:secreto", o HF_API_KEY + HF_API_SECRET.
"""

import os
import shutil
import urllib.request
from pathlib import Path

DEFAULT_MODEL = "kling-video/v3.0/std"  # se completa con /text-to-video o /image-to-video

ASPECT_RATIOS = {"vertical": "9:16", "horizontal": "16:9", "cuadrado": "1:1"}

FAILED_STATUSES = ("Failed", "NSFW", "Cancelled")


class HiggsfieldError(RuntimeError):
    pass


def has_credentials():
    return bool(os.environ.get("HF_KEY") or (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET")))


def _client():
    try:
        import higgsfield_client
    except ImportError:
        raise HiggsfieldError("Falta el SDK de Higgsfield: pip install higgsfield-client") from None
    return higgsfield_client


def endpoint(model, with_image):
    """Acepta un ID completo (…/text-to-video) o una base como 'kling-video/v3.0/std'."""
    if model.endswith("-to-video"):
        return model
    return f"{model.rstrip('/')}/{'image' if with_image else 'text'}-to-video"


def build_arguments(prompt, duration, aspect_ratio, image_url=None):
    args = {"prompt": prompt, "duration": int(duration)}
    if image_url:
        args["image_url"] = image_url  # primer fotograma; la proporción sale de la imagen
    else:
        args["aspect_ratio"] = aspect_ratio
    return args


def upload_image(path_or_url):
    if str(path_or_url).startswith(("http://", "https://")):
        return str(path_or_url)
    return _client().upload_file(str(path_or_url))


def find_video_url(result):
    """La respuesta trae result['video']['url']; si cambia el formato, busca cualquier URL de video."""
    video = result.get("video") if isinstance(result, dict) else None
    if isinstance(video, dict) and video.get("url"):
        return video["url"]
    stack = [result]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str) and item.startswith("http") and ".mp4" in item:
            return item
    raise HiggsfieldError(f"La respuesta de Higgsfield no trae un video: {result}")


def generate(model_id, arguments, on_status=None):
    """Envía la generación, espera a que termine y devuelve (request_id, url_del_video)."""
    hf = _client()
    controller = hf.submit(model_id, arguments=arguments)
    request_id = getattr(controller, "request_id", None)
    for status in controller.poll_request_status():
        name = type(status).__name__
        if on_status:
            on_status(name)
        if name in FAILED_STATUSES:
            raise HiggsfieldError(f"Higgsfield devolvió '{name}' (solicitud {request_id})")
    return request_id, find_video_url(controller.get())


def download(url, dest):
    dest = Path(dest)
    with urllib.request.urlopen(url, timeout=300) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)
    return dest
