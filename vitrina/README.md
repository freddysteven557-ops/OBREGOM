# Vitrina Obregón + Doctor Queso

Rebranding de la vitrina refrigerada (antes "Distribuidora de Carnes JYR").

| Archivo | Qué es |
|---|---|
| `salida/vitrina-obregon-doctor-queso.jpg` | Foto final (4000×3000): color corregido + vinilo nuevo + etiquetas en los quesos |
| `salida/antes-despues.jpg` | Comparación lado a lado |
| `salida/vinilo-frontal.png` | Arte plano del vinilo del frente (7360×800) |
| `original/vitrina-original.jpg` | Foto original |

## Qué se hizo

- **Limpieza de color:** se quitó el tinte morado/magenta del LED (la carne conserva su rojo) y lo amarillento del piso; el queso vuelve a blanco crema; contraste y nitidez leves.
- **Vinilo frontal:** reemplaza las tres calcomanías de JYR (y la de la vitrina vecina) con una banda negra con filetes vino/oro:
  - **Obregón · Carnes Selectas** (escudo vino con toro y estrellas)
  - Lema central: *Frescura y calidad* · Res · Cerdo · Pollo · Chorizos · Quesos
  - **Doctor Queso · Quesos empacados al vacío** (insignia amarilla/azul con cuña de queso y cruz)
- **Etiquetas Doctor Queso** sobre los bloques de queso al vacío.

## Regenerar

```bash
cd vitrina
python3 vinilo.py     # arte plano
python3 componer.py   # foto final + antes/después
```

Requiere Python 3 con Pillow y NumPy. Fuentes incluidas en `fonts/` (Google Fonts, licencia OFL).
Para usar logos oficiales, reemplaza `insignia_obregon` / `insignia_doctor_queso` en `vinilo.py`.
