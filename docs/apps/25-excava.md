# Yacimiento

> Excava capa a capa y llena tu museo de fósiles

| Campo | Valor |
|---|---|
| Archivo | `src/apps/25-excava.html` (22 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `excava` / `excava` |
| `<title>` | Yacimiento |
| Categorías | 3d juegos mente |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader |
| Fuentes | Alfa Slab One, IBM Plex Sans Condensed |
| Splash | fondo `#d99a5b` → `#f0c48a`, texto `#3b2416`, acento `#2a7f7a` |

## Concepto
Excavación arqueológica por vóxeles: retiras tierra capa a capa y extraes fósiles y reliquias para tu museo.

## Cómo está hecha
Three.js InstancedMesh (9x9x6 vóxeles) + modelos Blender (cráneo, amonites, trilobites, ámbar, ánfora, moneda, geoda, pico, pincel). Miniaturas del museo renderizadas en tiempo real a dataURL.

## Assets 3D (Blender)
- Script: `blender/scripts/b_excava.py` (usa `blib.py`) → exporta `blender/glb/excava.glb`, guarda `blender/blend/excava.blend` y renderiza `blender/renders/excava.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- 45 de energía por expedición
- Pico (1 golpe; capas profundas 2) — si golpea una pieza, sale dañada (50%)
- Pincel: extrae intacto si la pieza está expuesta o sondea caliente/templado/frío
- Radar: 3 usos, marca columna
- Destellos cuando una pieza queda expuesta
- 3 yacimientos desbloqueables y museo de 7 piezas

**Controles:** Elegir herramienta y clic en bloques; arrastrar para orbitar.

## Paleta (`:root`)
`--ochre` #d99a5b · `--soil` #3b2416 · `--parch` #f4e7cf · `--teal` #2a7f7a · `--rust` #b4532a · `--mut` #8a6a52

## Persistencia
Claves `OS.save/load` (localStorage `nexo.excava.<clave>`): `s`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `exc_clean` **Manos de cirujano** — Extrajiste un fósil intacto con el pincel
  - `exc_rex` **Cazador de dinosaurios** — Encontraste un cráneo de terópodo intacto
  - `exc_all` **Conservador del museo** — Las 7 piezas intactas en tu museo

## Ideas para escalar
- [ ] Piezas multi-bloque (esqueleto completo)
- [ ] Restauración como minijuego
- [ ] Más yacimientos (Atapuerca, íbero)
- [ ] Excavar por capas con cortes transversales

## Registro de cambios
- 2026-09-23 · v1 creada (modelos 3D en Blender 5.0, render Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
