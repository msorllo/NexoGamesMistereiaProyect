# Flujo

> Arte generativo con campos de ruido

| Campo | Valor |
|---|---|
| Archivo | `src/apps/11-flujo.html` (12 KB) |
| id (manifest / `data-app`) | `flujo` / `flujo` |
| `<title>` | Flujo Estudio |
| Categorías | creatividad |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Figtree, Syne |
| Splash | fondo `#f4f3ef` → `#ffffff`, texto `#121212`, acento `#e8452c` |

## Concepto
Estudio de arte generativo: partículas que siguen un campo de ruido Perlin y dejan trazos; la obra se cuelga en una galería.

## Cómo está hecha
Perlin 2D propio, 200-4000 partículas, simetría espejo/caleidoscopio, remolinos al hacer clic, miniaturas JPEG en localStorage.

## Mecánicas y recompensas
- 6 paletas, 5 parámetros
- Obra del día (paleta + simetría) +50 XP
- Galería de 12 obras

**Controles:** Clic en lienzo = remolino (Shift invierte). Panel lateral.

## Paleta (`:root`)
`--wall` #f4f3ef · `--ink` #121212 · `--mut` #8b8a85 · `--line` #dedcd5 · `--acc` #e8452c

## Persistencia
Claves `OS.save/load` (localStorage `nexo.flujo.<clave>`): `daily`, `gal`, `num`, `usedPal`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `flujo_first` **Primer lienzo** — Dejaste que Flujo pintara 400 fotogramas
  - `flujo_pal` **Cromática total** — Probaste todas las paletas de Flujo
  - `flujo_5` **Exposición individual** — 5 obras en tu galería

## Ideas para escalar
- [ ] Exportar a alta resolución
- [ ] Animación en bucle (GIF/WebM)
- [ ] Imprimir póster (servicio externo)
- [ ] Más campos (curl noise, atractores)

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
