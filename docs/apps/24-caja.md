# Caja de Música

> Clava púas en el tambor y recrea melodías

| Campo | Valor |
|---|---|
| Archivo | `src/apps/24-caja.html` (16 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `caja` / `caja` |
| `<title>` | Caja de Música |
| Categorías | 3d creatividad |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader |
| Fuentes | Italiana, Libre Franklin |
| Splash | fondo `#210a15` → `#5a1f3a`, texto `#f6e6dc`, acento `#d4a94e` |

## Concepto
Caja de música 3D: clavas púas en el tambor para recrear melodías; la bailarina gira y la tapa-espejo la refleja.

## Cómo está hecha
Three.js + modelos Blender (caja, tapa con bisagra, tambor, púa, peine, manivela, bailarina) + RoomEnvironment para metales. Síntesis de caja de música con armónicos y reverb por convolución. Partitura 16x15 sincronizada con el tambor.

## Assets 3D (Blender)
- Script: `blender/scripts/b_caja.py` (usa `blib.py`) → exporta `blender/glb/caja.glb`, guarda `blender/blend/caja.blend` y renderiza `blender/renders/caja.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- 4 canciones objetivo (Estrellita, Martinillo, Oda a la alegría, Cumpleaños feliz) + composición libre
- Validación por orden de notas (sin acordes)
- Cada canción desbloquea un acabado (cerezo, ébano, marfil, lacado)

**Controles:** Clic en la partitura o en el cilindro 3D, Dar cuerda, tempo.

## Paleta (`:root`)
`--wine` #3a1426 · `--wine2` #210a15 · `--gold` #d4a94e · `--cream` #f6e6dc · `--rose` #ffc2d6 · `--mut` #c9a9b6

## Persistencia
Claves `OS.save/load` (localStorage `nexo.caja.<clave>`): `s`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 4 logros:
  - `caja_first` **Primera melodía** — Recreaste tu primera canción
  - `caja_all` **Maestro relojero** — Recreaste las 4 melodías
  - `caja_12` **Compositor** — Tocaste una melodía de 12 notas o más
  - `caja_100` **Cien notas** — La caja ha sonado 100 notas

## Ideas para escalar
- [ ] Tambor de 32 pasos
- [ ] Compartir melodía por código
- [ ] Más canciones populares españolas
- [ ] Grabar a WAV

## Registro de cambios
- 2026-09-23 · v1 creada (modelos 3D en Blender 5.0, render Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
