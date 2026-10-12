# Faro

> Gira espejos y guía la luz hasta cada barco

| Campo | Valor |
|---|---|
| Archivo | `src/apps/21-faro.html` (17 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `faro` / `faro` |
| `<title>` | Faro |
| Categorías | 3d juegos mente |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader |
| Fuentes | DM Serif Display, Nunito Sans |
| Splash | fondo `#0b1a33` → `#1d3a66`, texto `#e8f4ff`, acento `#ffd35a` |

## Concepto
Puzle de luz 3D nocturno: giras espejos para que el haz del faro ilumine todos los barcos.

## Cómo está hecha
Three.js r147 + modelos Blender (faro, espejo, barco, roca, casilla, boya). Niveles generados por semilla con garantía de solución (camino constructivo + verificación por trazado). Mar con vértices animados.

## Assets 3D (Blender)
- Script: `blender/scripts/b_faro.py` (usa `blib.py`) → exporta `blender/glb/faro.glb`, guarda `blender/blend/faro.blend` y renderiza `blender/renders/faro.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- 8 noches (5x5 a 8x8, hasta 7 espejos, 3 barcos)
- Objetivo de giros = espejos mal orientados al inicio
- Estrellas por giros
- El haz atraviesa barcos y lo bloquean rocas

**Controles:** Clic/toque en espejos; arrastrar para orbitar la cámara.

## Paleta (`:root`)
`--night` #0b1a33 · `--deep` #06101f · `--gold` #ffd35a · `--foam` #e8f4ff · `--red` #d7263d · `--mut` #8ea3c4

## Persistencia
Claves `OS.save/load` (localStorage `nexo.faro.<clave>`): `stars`, `unl`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `faro_1` **Primera luz** — Guiaste tu primer barco a puerto
  - `faro_3s` **Farero experto** — 5 noches con 3 estrellas
  - `faro_all` **Guardián de la costa** — Completaste las 8 noches de Faro

## Ideas para escalar
- [ ] Prismas que dividen el haz
- [ ] Espejos fijos y móviles
- [ ] Niebla que cambia
- [ ] Editor de niveles

## Registro de cambios
- 2026-09-23 · v1 creada (modelos 3D en Blender 5.0, render Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
