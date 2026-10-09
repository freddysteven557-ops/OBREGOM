# OBREGOM — Generador de clips de GTA 6

Genera clips cortos estilo GTA 6 listos para **TikTok, Instagram Reels, YouTube Shorts y YouTube**,
de dos formas:

- **Con IA (Higgsfield):** escribes qué quieres ver y se genera el video → `python -m clipgen.ia`
- **Desde tus grabaciones:** recorta automáticamente los mejores momentos de tus partidas → `python -m clipgen`

## Clips con IA (Higgsfield)

1. Crea una cuenta y una API key en [Higgsfield Cloud](https://cloud.higgsfield.ai) y carga saldo
   (la API se paga aparte de la suscripción web).
2. Instala y configura:

   ```bash
   pip install -r requirements.txt higgsfield-client
   export HF_KEY="tu-api-key:tu-api-secret"
   ```

3. Genera:

   ```bash
   # Un clip a partir de un prompt
   python -m clipgen.ia "persecución policial en un auto deportivo por la playa al atardecer"

   # Varios clips desde un archivo (uno por línea)
   python -m clipgen.ia -p prompts/ejemplos.txt -d 8

   # Animar una imagen tuya (primer fotograma)
   python -m clipgen.ia "the car drifts and speeds away" --image portada.jpg

   # Ver qué se enviaría sin gastar créditos
   python -m clipgen.ia -p prompts/ejemplos.txt --dry-run
   ```

| Opción | Qué hace | Por defecto |
|---|---|---|
| `-p, --prompts-file` | Archivo con un prompt por línea | — |
| `-d, --duration` | Segundos por clip (Kling 3.0: 3–15) | `5` |
| `-f, --format` | `ambos`, `vertical` o `horizontal` | `ambos` |
| `--image` | Imagen (archivo o URL) como primer fotograma | — |
| `--model` | Modelo de Higgsfield, p. ej. `kling-video/v3.0/pro` o un ID completo `…/text-to-video` | `kling-video/v3.0/std` |
| `--style` | Estilo que se añade a cada prompt (`""` para ninguno) | estética de ciudad tipo Miami/neón |
| `--dry-run` | Mostrar las solicitudes sin llamar a la API | apagado |

Con `ambos` se hace **una sola generación** en 16:9 y la versión vertical se arma con fondo
desenfocado, así pagas un video y no dos. Si solo publicas en TikTok/Reels usa `-f vertical`
para generar directamente en 9:16 a pantalla completa.

Cada video generado cuesta créditos: prueba primero con `--dry-run` y con clips cortos.
Los clips se guardan como `ia_<fecha>_<n>_vertical.mp4` / `_horizontal.mp4` y se agregan a
`clips/manifest.json` junto con el prompt y el texto para publicar.

## Clips desde tus grabaciones

Convierte tus partidas, streams o grabaciones largas en clips cortos:

1. **Detecta los mejores momentos** de forma automática: busca picos de volumen (disparos,
   explosiones, gritos) y cambios bruscos de imagen (persecuciones, choques, cortes).
2. **Exporta cada clip** en vertical 9:16 (1080×1920) y/o horizontal 16:9 (1920×1080).
3. **Subtítulos automáticos** opcionales (con Whisper), quemados en el video.
4. **Genera los textos para publicar** (título, descripción y hashtags por red) en `manifest.json`.

### Instalación

Necesitas Python 3.9+ y [ffmpeg](https://ffmpeg.org/download.html) (también para el modo IA).

```bash
pip install -r requirements.txt
pip install faster-whisper   # opcional, solo si quieres subtítulos
```

### Uso

```bash
# 5 clips de 30 s por video, en vertical y horizontal
python -m clipgen mi_partida.mp4

# Una carpeta entera, 8 clips de 20 s, solo vertical y con subtítulos en español
python -m clipgen grabaciones/ -n 8 -d 20 -f vertical --subs --language es

# Ver qué momentos elegiría, sin exportar nada
python -m clipgen mi_partida.mp4 --dry-run
```

Los clips quedan en `clips/`:

```
clips/
├── mi_partida_clip01_vertical.mp4     ← el mejor momento
├── mi_partida_clip01_horizontal.mp4
├── mi_partida_clip01.srt              ← si usaste --subs
├── ...
└── manifest.json                      ← tiempos, puntaje y textos para cada red
```

### Opciones del modo grabaciones

| Opción | Qué hace | Por defecto |
|---|---|---|
| `-o, --output` | Carpeta de salida | `clips` |
| `-n, --clips` | Máximo de clips por video | `5` |
| `-d, --duration` | Duración de cada clip (s) | `30` |
| `-f, --format` | `ambos`, `vertical` o `horizontal` | `ambos` |
| `--vertical-mode` | `blur` (video completo + fondo desenfocado) o `crop` (recorte al centro) | `blur` |
| `--subs` / `--language` | Subtítulos automáticos e idioma (`es`, `en`…) | apagado / autodetectar |
| `--title` / `--hashtags` | Título base y hashtags de las publicaciones | `GTA 6` / `#GTA6 #GTAVI …` |
| `--scene-threshold` | Sensibilidad a cambios de escena (0–1) | `0.3` |
| `--no-scenes` | Analizar solo el audio (más rápido en videos de horas) | apagado |
| `--dry-run` | Mostrar los momentos sin exportar | apagado |

Si un video es aburrido, la herramienta genera menos clips de los pedidos en lugar de rellenar
con momentos flojos.

## Publicar en redes

Cada clip en `manifest.json` trae un bloque `post` con el texto para `tiktok`, `instagram`,
`youtube_shorts` y `youtube`. Súbelos a mano o prográmalos con una herramienta como Metricool
(necesita que el video esté en una URL pública, por ejemplo Google Drive o Dropbox).

## Sobre derechos de autor

GTA 6 es propiedad de Rockstar Games / Take-Two. Rockstar suele permitir subir **tu propio
gameplay**, pero resubir trailers oficiales o videos de otros creadores puede generar
reclamos o bajas de la cuenta. Usa grabaciones propias o material que tengas permiso para usar,
y agrega valor (comentario, edición, reacciones).

Para los clips con IA: márcalos como contenido generado con IA (TikTok, Instagram y YouTube lo
exigen) y no los presentes como material oficial ni filtraciones de Rockstar. Evita usar logos
oficiales o personajes reales en los prompts.

## Tests

```bash
python -m unittest -v
```
