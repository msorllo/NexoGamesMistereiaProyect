# Plano

> Dibuja rampas y guía la física

| Campo | Valor |
|---|---|
| Archivo | `src/apps/16-plano.html` (13 KB) |
| id (manifest / `data-app`) | `plano` / `plano` |
| `<title>` | Plano |
| Categorías | juegos mente |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Architects Daughter, Share Tech Mono |
| Splash | fondo `#0b3d91` → `#0a3278`, texto `#e8f0ff`, acento `#ffe27a` |

## Concepto
Puzle de física sobre un plano técnico azul: dibujas rampas con tinta limitada para llevar bolas al recipiente.

## Cómo está hecha
Física de círculos contra segmentos con sub-pasos, zonas donde no se puede dibujar, cajetín de plano real.

## Mecánicas y recompensas
- 8 láminas
- Tinta limitada; estrellas según tinta usada
- Vigas existentes y zonas prohibidas

**Controles:** Arrastrar para dibujar, Soltar bolas, Deshacer, Borrar.

## Paleta (`:root`)
`--bp` #0b3d91 · `--bp2` #0a3278 · `--line` #e8f0ff · `--red` #ff6b5a · `--yel` #ffe27a

## Persistencia
Claves `OS.save/load` (localStorage `nexo.plano.<clave>`): `best`, `unl`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `plano_3` **Ingeniería eficiente** — 3 estrellas en una lámina de Plano
  - `plano_all` **Colegiado** — Aprobaste las 8 láminas de Plano

## Ideas para escalar
- [ ] Muelles y ventiladores
- [ ] Editor de niveles
- [ ] Materiales (goma, hielo)
- [ ] Repetición de la solución

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
