# Planetario 3D

> Orbita el sistema solar y completa tu bitácora

| Campo | Valor |
|---|---|
| Archivo | `src/apps/02-planetario.html` (17 KB) |
| id (manifest / `data-app`) | `planetario` / `planetario` |
| `<title>` | Planetario 3D |
| Categorías | 3d mente |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Cormorant Garamond, IBM Plex Mono |
| Splash | fondo `#04060c` → `#101a33`, texto `#e9f1ff`, acento `#f4d8a0` |

## Concepto
Sistema solar 3D navegable como cuaderno de exploración: visitas los 8 planetas, lees datos reales y respondes preguntas.

## Cómo está hecha
Canvas 2D con proyección 3D propia (cámara orbital yaw/pitch, esferas con degradado y terminador, anillos, 900 estrellas). Sin librerías.

## Mecánicas y recompensas
- Visitar planetas (+15 XP la primera vez)
- Pregunta del observatorio por planeta (+20 XP)
- Tour guiado automático
- Control de velocidad del tiempo

**Controles:** Arrastrar para orbitar, rueda para zoom, clic en planeta.

## Paleta (`:root`)
`--void` #04060c · `--ice` #e9f1ff · `--frost` #9cc9ff · `--dim` #5d6b85 · `--gold` #f4d8a0

## Persistencia
Claves `OS.save/load` (localStorage `nexo.planetario.<clave>`): `answered`, `visited`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `plan_sabio` **Astrónomo sabio** — Acertaste las 8 preguntas del observatorio
  - `plan_all` **Gran viajero** — Visitaste los 8 planetas
  - `plan_rings` **Señor de los anillos** — Observaste Saturno de cerca

## Ideas para escalar
- [ ] Pasar a Three.js con texturas reales (NASA dominio público)
- [ ] Lunas principales (Ío, Europa, Titán)
- [ ] Escala real conmutable
- [ ] Misiones de sondas históricas (Voyager, Cassini)

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
