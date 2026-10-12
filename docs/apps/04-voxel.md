# Voxel Isla

> Construye tu isla flotante bloque a bloque

| Campo | Valor |
|---|---|
| Archivo | `src/apps/04-voxel.html` (14 KB) |
| id (manifest / `data-app`) | `voxel` / `voxel` |
| `<title>` | Voxel Isla |
| Categorías | 3d creatividad |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Fredoka |
| Splash | fondo `#9fd8ff` → `#e6f6ff`, texto `#2d3a5c`, acento `#ff7a59` |

## Concepto
Constructor isométrico de una isla flotante con bloques; las misiones desbloquean materiales nuevos.

## Cómo está hecha
Canvas 2D isométrico con 4 rotaciones de vista, orden de pintado por profundidad, picking por polígono de cara visible, mundo en diccionario "x,y,z".

## Mecánicas y recompensas
- 11 tipos de bloque (5 iniciales, 6 desbloqueables)
- 5 misiones: 10 bloques, altura 10, 3 árboles, lago, 120 bloques
- Modo borrar, rotar vista, día/noche
- El mundo se guarda

**Controles:** Clic coloca en la cara señalada, clic derecho o modo ⌫ borra, R rota, E borrar.

## Paleta (`:root`)
`--sky1` #9fd8ff · `--sky2` #e6f6ff · `--ink` #2d3a5c · `--coral` #ff7a59 · `--card` #ffffff · `--soft` #eef4fb

## Persistencia
Claves `OS.save/load` (localStorage `nexo.voxel.<clave>`): `baseWater`, `placed`, `qdone`, `world`

## Integración con NEXO
- 1 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `voxel_all` **Arquitecta de islas** — Completaste todas las misiones de Voxel Isla
  - `voxel_night` **Noche estrellada** — Viste tu isla de noche

## Ideas para escalar
- [ ] Exportar la isla a GLB para Blender
- [ ] Criaturas que pasean
- [ ] Plantillas y compartir por código
- [ ] Ciclo de agua/cascadas

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
