# Gesta

> Tus hábitos convertidos en un RPG

| Campo | Valor |
|---|---|
| Archivo | `src/apps/15-gesta.html` (15 KB) |
| id (manifest / `data-app`) | `gesta` / `gesta` |
| `<title>` | Gesta |
| Categorías | productividad juegos |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Press Start 2P, VT323 |
| Splash | fondo `#0f380f` → `#306230`, texto `#9bbc0f`, acento `#8bac0f` |

## Concepto
Tus hábitos diarios convertidos en un RPG pixel art con paleta Game Boy: cumplir hábitos ataca a jefes.

## Cómo está hecha
Sprites a partir de mapas de caracteres, monstruos procedurales simétricos por semilla, reinicio diario con penalización de vida por hábitos no hechos.

## Mecánicas y recompensas
- Hábitos con dificultad (XP, oro, daño)
- 5 jefes (la procrastinación y compañía)
- Niveles del héroe
- Tienda: espada, casco, capa, escudo, mascota, corona
- Racha diaria

**Controles:** Marcar/desmarcar hábitos, añadir nuevos, comprar equipo.

## Paleta (`:root`)
`--g0` #0f380f · `--g1` #306230 · `--g2` #8bac0f · `--g3` #9bbc0f · `--shell` #c4c0b8 · `--shell2` #a8a49c

## Persistencia
Claves `OS.save/load` (localStorage `nexo.gesta.<clave>`): `state`

## Integración con NEXO
- 4 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 4 logros:
  - `gesta_l5` **Veterano** — Tu héroe de Gesta llegó a nivel 5
  - `gesta_boss1` **Matadragones** — Derrotaste a tu primer jefe en Gesta
  - `gesta_day` **Día perfecto** — Completaste todos tus hábitos del día
  - `gesta_shop` **Armadura completa** — Compraste todo en la tienda de Gesta

## Ideas para escalar
- [ ] Hábitos semanales
- [ ] Recordatorios
- [ ] Clases (mago, guerrero)
- [ ] Modo grupo/party

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
