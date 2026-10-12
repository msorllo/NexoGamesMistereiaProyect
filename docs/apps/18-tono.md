# Tono

> Recompón degradados de color

| Campo | Valor |
|---|---|
| Archivo | `src/apps/18-tono.html` (10 KB) |
| id (manifest / `data-app`) | `tono` / `tono` |
| `<title>` | Tono |
| Categorías | mente juegos |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Lexend |
| Splash | fondo `#f7f7f2` → `#ffffff`, texto `#222226`, acento `#4776e6` |

## Concepto
Puzle de degradados: reordena fichas de color hasta recomponer la transición entre 4 esquinas.

## Cómo está hecha
Interpolación bilineal de 4 colores, fichas fijas como referencia, intercambio por clic o arrastre con animación elástica.

## Mecánicas y recompensas
- 12 niveles de 4x5 a 10x12
- Estrellas por movimientos vs objetivo
- Ver solución 2 s (+3 movimientos)

**Controles:** Clic en dos fichas o arrastrar.

## Paleta (`:root`)
`--bg` #f7f7f2 · `--ink` #222226 · `--mut` #8d8d93 · `--line` #e4e4dd

## Persistencia
Claves `OS.save/load` (localStorage `nexo.tono.<clave>`): `done`, `unl`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `tono_3` **Ojo de pintor** — 3 estrellas en Tono
  - `tono_all` **Maestro del color** — Completaste el último nivel de Tono

## Ideas para escalar
- [ ] Modo daltónico
- [ ] Niveles diarios
- [ ] Degradados de marcas/fotos

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
