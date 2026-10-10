# Vitrina ObreGom + DrQuesos

Rebranding de la vitrina refrigerada (antes "Distribuidora de Carnes JYR") con los logos reales de ObreGom y DrQuesos.

| Archivo | Qué es |
|---|---|
| `salida/vitrina-obregom-drquesos.jpg` | Foto final (4000×3000): color corregido + vinilo nuevo + etiquetas en los quesos |
| `salida/antes-despues.jpg` | Comparación lado a lado |
| `salida/vinilo-frontal.png` | Arte plano del vinilo del frente (7360×800) |
| `marca/` | Imágenes de marca originales y logos recortados con fondo transparente |
| `original/vitrina-original.jpg` | Foto original |

## Qué se hizo

- **Limpieza de color:** se quitó el tinte morado/magenta del LED (la carne conserva su rojo) y lo amarillento del piso; el queso vuelve a blanco crema; contraste y nitidez leves.
- **Vinilo frontal** en formato ObreGom (negro, rojo y blanco), sobre las calcomanías de JYR y la de la vitrina vecina:
  - Logo **ObreGom** en su marco rojo.
  - Centro: *Procesadora · Almacenadora · Distribuidora* y *Cerdo · Res · Pollo · Embutidos · Mariscos*.
  - Logo **DrQuesos** quemado sobre textura de queso, con borde rojo.
- **Etiquetas DrQuesos** sobre los bloques de queso al vacío.

## Regenerar

```bash
cd vitrina
python3 vinilo.py     # arte plano
python3 componer.py   # foto final + antes/después
```

Requiere Python 3 con Pillow y NumPy. Fuentes en `fonts/` (Google Fonts, OFL) e Inter del sistema.
