# Minigolf Cósmico

> Seis hoyos flotando entre asteroides

| Campo | Valor |
|---|---|
| Archivo | `src/apps/22-golf.html` (18 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `golf` / `golf` |
| `<title>` | Minigolf Cósmico |
| Categorías | 3d juegos |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader |
| Fuentes | Exo 2, Russo One |
| Splash | fondo `#12062b` → `#3a1a72`, texto `#f1ecff`, acento `#39f3ff` |

## Concepto
Minigolf en plataformas flotantes entre asteroides con setas de neón, portales y brazos giratorios.

## Cómo está hecha
Three.js + modelos Blender (bola, bandera, hoyo, asteroides, bumper, portal, planeta, ovni, tee). Hoyos definidos en ASCII; física 2D sobre la rejilla con colisión por celdas, bumpers circulares y brazo giratorio.

## Assets 3D (Blender)
- Script: `blender/scripts/b_golf.py` (usa `blib.py`) → exporta `blender/glb/golf.glb`, guarda `blender/blend/golf.blend` y renderiza `blender/renders/golf.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- 6 hoyos con par (17)
- Tiro tipo tirachinas con fuerza
- Tarjeta de puntuación y récord
- Reintentar hoyo suma golpe

**Controles:** Arrastrar y soltar; ⟲ ⟳ rotan la cámara.

## Paleta (`:root`)
`--void` #12062b · `--cyan` #39f3ff · `--pink` #ff4fd8 · `--lilac` #c6b8ff · `--txt` #f1ecff

## Persistencia
Claves `OS.save/load` (localStorage `nexo.golf.<clave>`): `best`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 4 logros:
  - `golf_ace` **Hoyo en uno** — Metiste la bola de un solo golpe
  - `golf_birdie` **Pájaro cósmico** — Terminaste un hoyo bajo par
  - `golf_done` **Astronauta del green** — Terminaste los 6 hoyos
  - `golf_par` **Par galáctico** — Recorrido completo al par o mejor

## Ideas para escalar
- [ ] Más hoyos (JSON)
- [ ] Rampas y alturas
- [ ] Multijugador por turnos local
- [ ] Pieles de bola

## Registro de cambios
- 2026-09-23 · v1 creada (modelos 3D en Blender 5.0, render Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
