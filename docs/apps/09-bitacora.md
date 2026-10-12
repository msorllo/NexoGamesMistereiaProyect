# Bitácora

> Diario de ánimo con tu año en píxeles

| Campo | Valor |
|---|---|
| Archivo | `src/apps/09-bitacora.html` (14 KB) |
| id (manifest / `data-app`) | `bitacora` / `bitacora` |
| `<title>` | Bitácora de Ánimo |
| Categorías | bienestar |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Instrument Serif, Manrope |
| Splash | fondo `#eef2f7` → `#ffffff`, texto `#1d2433`, acento `#3b5bdb` |

## Concepto
Diario de ánimo de 30 segundos al día con "año en píxeles", curva de 30 días y patrones detectados.

## Cómo está hecha
Blobs SVG animados con CSS path morph, gráfica SVG, correlación simple de etiquetas con el ánimo. Arranca con datos de EJEMPLO marcados que se borran al registrar el primer día.

## Mecánicas y recompensas
- 5 ánimos, energía 1-10, 10 etiquetas, nota
- Racha y medallas 3/7/30 días
- Insights: etiqueta que más sube/baja el ánimo, mejor día de la semana

**Controles:** Elegir ánimo → Guardar el día.

## Paleta (`:root`)
`--bg` #eef2f7 · `--card` #ffffff · `--ink` #1d2433 · `--mut` #6b7488 · `--line` #dde3ec · `--m5` #ffb347 · `--m4` #7fd1ae · `--m3` #9ab4e8 · `--m2` #b39ddb · `--m1` #6f7fa3 · `--acc` #3b5bdb

## Persistencia
Claves `OS.save/load` (localStorage `nexo.bitacora.<clave>`): `log`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `bit_3` **Tres en raya** — 3 días seguidos registrando tu ánimo
  - `bit_7` **Semana consciente** — 7 días seguidos
  - `bit_tags` **Día completo** — Registraste un día con 4 etiquetas o más

## Ideas para escalar
- [ ] Recordatorio diario (notificación)
- [ ] Exportar CSV
- [ ] Gráfico por etiqueta
- [ ] Frases de reflexión según patrón

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
