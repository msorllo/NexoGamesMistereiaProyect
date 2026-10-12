# La Coctelera

> Mezcla, agita y descubre recetas

| Campo | Valor |
|---|---|
| Archivo | `src/apps/17-coctelera.html` (15 KB) |
| id (manifest / `data-app`) | `coctelera` / `coctelera` |
| `<title>` | La Coctelera |
| Categorías | creatividad |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Josefin Sans, Limelight |
| Splash | fondo `#120d0a` → `#3a2616`, texto `#f3e6cf`, acento `#4ef2e0` |

## Concepto
Bar clandestino: sirves medidas en un vaso, agitas y descubres 12 recetas (3 sin alcohol) mientras atiendes pedidos.

## Cómo está hecha
Vaso SVG con capas de líquido, mezcla de color ponderada, burbujas animadas, detección de receta por conjunto de ingredientes.

## Mecánicas y recompensas
- 17 ingredientes
- Pedidos de clientes con pista
- Propinas y racha
- Recetario secreto

**Controles:** Clic en botellas, Hielo, Agitar, Vaciar, Servir.

## Paleta (`:root`)
`--wood` #120d0a · `--wood2` #1e1510 · `--amber` #e0a458 · `--brass` #c9a45c · `--cream` #f3e6cf · `--neon` #4ef2e0 · `--rose` #ff6f91 · `--mut` #9c8a73

## Persistencia
Claves `OS.save/load` (localStorage `nexo.coctelera.<clave>`): `found`, `served`, `tips`

## Integración con NEXO
- 3 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `coc_all` **Maestro coctelero** — Descubriste las 12 recetas
  - `coc_str` **Barra imparable** — 5 pedidos seguidos perfectos
  - `coc_na` **Sin alcohol, con arte** — Descubriste los 3 cócteles sin alcohol

## Ideas para escalar
- [ ] Proporciones exactas
- [ ] Guarniciones
- [ ] Versión para hostelería real (carta del bar del cliente)
- [ ] Modo contrarreloj

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
