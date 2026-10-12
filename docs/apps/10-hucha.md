# Hucha

> Metas de ahorro con monedas que caen

| Campo | Valor |
|---|---|
| Archivo | `src/apps/10-hucha.html` (14 KB) |
| id (manifest / `data-app`) | `hucha` / `hucha` |
| `<title>` | Hucha |
| Categorías | productividad |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Rubik Mono One, Work Sans |
| Splash | fondo `#ffe14d` → `#f5f5f0`, texto `#111111`, acento `#111111` |

## Concepto
Metas de ahorro en estilo neo-brutalista con un bote donde caen monedas con física.

## Cómo está hecha
Física de círculos (verlet simple) en canvas; nº de monedas proporcional al progreso; confeti en hitos.

## Mecánicas y recompensas
- Varias metas con color propio
- Hitos 25/50/75/100% con confeti
- Pronóstico de fecha según ritmo
- 6 insignias
- Metas de ejemplo que se reinician con el primer ingreso real

**Controles:** +5/+20/+50/+100, cantidad libre, Sacar.

## Paleta (`:root`)
`--bg` #f5f5f0 · `--ink` #111 · `--yel` #ffe14d · `--mint` #7cf0b3 · `--pink` #ff8fb1 · `--blue` #8fb8ff · `--white` #fff

## Persistencia
Claves `OS.save/load` (localStorage `nexo.hucha.<clave>`): `badges`, `cur`, `goals`

## Integración con NEXO
- 3 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 0 logros:

## Ideas para escalar
- [ ] Ingresos recurrentes
- [ ] Reto de las 52 semanas
- [ ] Metas compartidas en pareja
- [ ] Divisas

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
