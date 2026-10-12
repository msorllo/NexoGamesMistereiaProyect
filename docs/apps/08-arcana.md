# Arcana

> Memoria con los 22 arcanos mayores

| Campo | Valor |
|---|---|
| Archivo | `src/apps/08-arcana.html` (14 KB) |
| id (manifest / `data-app`) | `arcana` / `arcana` |
| `<title>` | Arcana |
| Categorías | juegos mente |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Cinzel Decorative, EB Garamond |
| Splash | fondo `#0f1638` → `#24306b`, texto `#efe3c8`, acento `#d9b46a` |

## Concepto
Juego de memoria con los 22 arcanos mayores del tarot; cada pareja encontrada entra en tu grimorio con su lectura.

## Cómo está hecha
Cartas con flip 3D en CSS, símbolos SVG propios por arcano, grid que se adapta al alto de la pantalla.

## Mecánicas y recompensas
- 5 tiradas (6 a 15 parejas)
- Estrellas por movimientos
- Grimorio coleccionable de 22 cartas

**Controles:** Clic en cartas.

## Paleta (`:root`)
`--night` #0f1638 · `--deep` #080c24 · `--gold` #d9b46a · `--gold2` #f2d99a · `--crim` #8e2c3a · `--parch` #efe3c8 · `--ink` #2a1f14 · `--haze` #8d93b8

## Persistencia
Claves `OS.save/load` (localStorage `nexo.arcana.<clave>`): `best`, `grim`, `unl`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `arc_3` **Clarividente** — 3 estrellas en Arcana
  - `arc_all` **Grimorio completo** — Descubriste los 22 arcanos mayores

## Ideas para escalar
- [ ] Modo contrarreloj
- [ ] Arcanos menores como expansión
- [ ] Tirada diaria con mensaje
- [ ] Animación de barajado

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
