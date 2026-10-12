# Cerebro Bauhaus

> Trivial de 48 preguntas con rangos

| Campo | Valor |
|---|---|
| Archivo | `src/apps/12-bauhaus.html` (19 KB) |
| id (manifest / `data-app`) | `bauhaus` / `bauhaus` |
| `<title>` | Cerebro Bauhaus |
| Categorías | mente juegos |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Big Shoulders Display, Outfit |
| Splash | fondo `#151515` → `#2a2a2a`, texto `#efece4`, acento `#f4c20d` |

## Concepto
Trivial de cultura general con composición Bauhaus (formas primarias animadas) y rangos.

## Cómo está hecha
48 preguntas en 4 categorías, temporizador de 15 s, multiplicador por racha, composiciones geométricas en DOM.

## Mecánicas y recompensas
- Rondas de 10
- Puntos por rapidez x racha
- Comodines: 50/50, +10 s, saltar
- Rangos: Aprendiz → Genio Bauhaus
- 4 misiones

**Controles:** Clic o teclas 1-4.

## Paleta (`:root`)
`--paper` #efece4 · `--red` #e63022 · `--yel` #f4c20d · `--blue` #1f4fa8 · `--blk` #151515 · `--gry` #d8d3c6

## Persistencia
Claves `OS.save/load` (localStorage `nexo.bauhaus.<clave>`): `ms`, `played`, `total`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 1 logros:
  - `bau_genio` **Genio Bauhaus** — Alcanzaste el rango máximo

## Ideas para escalar
- [ ] Ampliar a 300 preguntas en JSON aparte
- [ ] Modo duelo
- [ ] Preguntas con imagen
- [ ] Categoría local (Baix Maestrat)

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
