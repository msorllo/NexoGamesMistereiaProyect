# Eco

> Repite el canto de las medusas

| Campo | Valor |
|---|---|
| Archivo | `src/apps/14-eco.html` (12 KB) |
| id (manifest / `data-app`) | `eco` / `eco` |
| `<title>` | Eco Abisal |
| Categorías | juegos mente |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Comfortaa, Quicksand |
| Splash | fondo `#021a24` → `#0a4a5c`, texto `#d9fbf4`, acento `#19e3c0` |

## Concepto
Simon dice con 4 medusas bioluminiscentes; cada acierto te hunde 10 m en el océano.

## Cómo está hecha
Canvas con medusas animadas por código, zonas de profundidad que oscurecen el fondo, peces linterna que aparecen con la profundidad, notas con armónicos.

## Mecánicas y recompensas
- Modos: Clásico, Espejo (al revés, 80 m), Corriente rápida (120 m)
- Zonas: iluminada → fosa hadal
- Récord por modo

**Controles:** Clic en medusas o teclas 1-4.

## Paleta (`:root`)
`--deep` #021a24 · `--teal` #19e3c0 · `--vio` #9b6bff · `--pink` #ff5fa2 · `--amb` #ffc15e · `--foam` #d9fbf4 · `--mist` #6fa3a8

## Persistencia
Claves `OS.save/load` (localStorage `nexo.eco.<clave>`): `best`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `eco_100` **Medianoche** — Llegaste a 100 m en Eco
  - `eco_200` **Explorador abisal** — Llegaste a 200 m en Eco

## Ideas para escalar
- [ ] Modo zen sin fallo
- [ ] Más criaturas coleccionables
- [ ] Secuencias musicales reconocibles

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
