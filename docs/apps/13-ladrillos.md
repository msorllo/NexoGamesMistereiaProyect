# Ladrillos

> Rompe muros Memphis con power-ups

| Campo | Valor |
|---|---|
| Archivo | `src/apps/13-ladrillos.html` (15 KB) |
| id (manifest / `data-app`) | `ladrillos` / `ladrillos` |
| `<title>` | Ladrillos Memphis |
| Categorías | juegos |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Chango, Nunito |
| Splash | fondo `#ffe3ec` → `#fff5f8`, texto `#1b1b3a`, acento `#ff4f9a` |

## Concepto
Breakout de colores estilo Memphis con power-ups y 6 muros.

## Cómo está hecha
Canvas 2D, colisiones AABB por sub-pasos, ladrillos de 2 golpes, acero indestructible, bombas.

## Mecánicas y recompensas
- Power-ups: pala ancha, multibola, láser, lento, vida
- Combo sin tocar la pala
- 6 niveles desbloqueables

**Controles:** Ratón/dedo mueve la pala; clic/ESPACIO lanza o dispara.

## Paleta (`:root`)
`--bg` #ffe3ec · `--pink` #ff4f9a · `--teal` #3ad0c9 · `--yel` #ffd23f · `--vio` #6c4cff · `--ink` #1b1b3a · `--white` #fffdf7

## Persistencia
Claves `OS.save/load` (localStorage `nexo.ladrillos.<clave>`): `done`, `unl`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `lad_c12` **Carambola** — Combo de 12 ladrillos en Ladrillos
  - `lad_all` **Demolición total** — Derribaste los 6 muros de Ladrillos

## Ideas para escalar
- [ ] Editor de niveles
- [ ] Jefe final
- [ ] Modo infinito
- [ ] Tabla de récords

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
