# La Cripta

> Laberinto 3D a la luz de una antorcha

| Campo | Valor |
|---|---|
| Archivo | `src/apps/03-cripta.html` (16 KB) |
| id (manifest / `data-app`) | `cripta` / `cripta` |
| `<title>` | La Cripta |
| Categorías | juegos 3d |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Crimson Pro, Pirata One |
| Splash | fondo `#140f0c` → `#3a1d0c`, texto `#eadbc0`, acento `#ff8a2a` |

## Concepto
Laberinto 3D en primera persona (estilo Wolfenstein) a la luz de una antorcha: recoge llaves doradas y escapa por la puerta sellada.

## Cómo está hecha
Raycaster DDA sobre ImageData a baja resolución (pixel art escalado), texturas procedurales 64x64 (piedra con musgo, puerta, suelo), sprites de llaves con z-buffer, laberinto generado por backtracking + bucles extra.

## Mecánicas y recompensas
- 7 niveles que crecen de tamaño
- 1-5 llaves por nivel colocadas en callejones sin salida
- Estrellas por tiempo (par = 20 + nivel·18 s)
- Almas = puntuación acumulada
- Minimapa (tecla M)

**Controles:** WASD / flechas, arrastrar ratón para girar, M minimapa. Móvil: cruceta táctil.

## Paleta (`:root`)
`--stone` #1a1512 · `--torch` #ff8a2a · `--ember` #c2410c · `--bone` #eadbc0 · `--moss` #6b7a4a · `--blood` #8b1e1e

## Persistencia
Claves `OS.save/load` (localStorage `nexo.cripta.<clave>`): `best`, `souls`, `unlocked`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `cripta_3` **Sombra veloz** — 3 estrellas en un nivel de La Cripta
  - `cripta_7` **Señor de la Cripta** — Escapaste del séptimo sótano

## Ideas para escalar
- [ ] Enemigos (fantasmas) con IA simple
- [ ] Trampas y palancas
- [ ] Antorcha que se consume (tiempo)
- [ ] Tiendas entre niveles

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
