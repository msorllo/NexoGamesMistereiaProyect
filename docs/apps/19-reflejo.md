# Reflejo

> Entrena puntería y tiempo de reacción

| Campo | Valor |
|---|---|
| Archivo | `src/apps/19-reflejo.html` (14 KB) |
| id (manifest / `data-app`) | `reflejo` / `reflejo` |
| `<title>` | Reflejo |
| Categorías | juegos |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Barlow, Barlow Condensed |
| Splash | fondo `#ffffff` → `#f2f2f2`, texto `#0a0a0a`, acento `#ff3b30` |

## Concepto
Entrenador de reflejos con diseño suizo: precisión, reacción y rastreo, con rangos de Bronce a Leyenda.

## Cómo está hecha
DOM + requestAnimationFrame, medición con performance.now(), rating combinado de los tres modos.

## Mecánicas y recompensas
- Precisión: 30 dianas que encogen
- Reacción: 5 intentos, media en ms
- Rastreo: 15 s siguiendo la diana
- Rangos por rating

**Controles:** Ratón/dedo. Escape vuelve al menú.

## Paleta (`:root`)
`--w` #ffffff · `--ink` #0a0a0a · `--red` #ff3b30 · `--g` #e9e9e9 · `--g2` #9a9a9a · `--grn` #00b86b

## Persistencia
Claves `OS.save/load` (localStorage `nexo.reflejo.<clave>`): `best`

## Integración con NEXO
- 4 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `ref_perfect` **Pulso de cirujano** — Precisión sin un solo fallo
  - `ref_220` **Relámpago** — Media de reacción por debajo de 220 ms
  - `ref_leyenda` **Leyenda** — Alcanzaste el rango Leyenda en Reflejo

## Ideas para escalar
- [ ] Modo daltónico y sonido
- [ ] Historial y gráfica de progreso
- [ ] Retos diarios

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
