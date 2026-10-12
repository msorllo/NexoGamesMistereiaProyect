# Tiza

> Escribe rápido antes de que la palabra caiga

| Campo | Valor |
|---|---|
| Archivo | `src/apps/07-tiza.html` (13 KB) |
| id (manifest / `data-app`) | `tiza` / `tiza` |
| `<title>` | Tiza |
| Categorías | juegos mente |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Cabin Sketch, Patrick Hand |
| Splash | fondo `#2b4a3e` → `#23402f`, texto `#f2f0e6`, acento `#f4e285` |

## Concepto
Juego de mecanografía en una pizarra verde: las palabras caen y hay que escribirlas antes de que toquen la línea.

## Cómo está hecha
DOM absoluto para las palabras, canvas para el polvo de tiza, normalización sin tildes para escribir sin acentos, input oculto para teclado móvil.

## Mecánicas y recompensas
- 4 bancos de palabras por dificultad
- Nivel cada 10 palabras, 3 vidas, combo x1-x5
- Palabras especiales: amarilla limpia todo, azul congela, rosa x3
- Misiones: nivel 5, combo 15, 40 PPM, 3 rosas

**Controles:** Teclado. Backspace borra, Escape limpia.

## Paleta (`:root`)
`--board` #2b4a3e · `--board2` #23402f · `--wood` #8a5a36 · `--chalk` #f2f0e6 · `--yel` #f4e285 · `--pink` #f5a3b8 · `--blue` #a7d3f0

## Persistencia
Claves `OS.save/load` (localStorage `nexo.tiza.<clave>`): `best`, `bestLvl`, `ms`

## Integración con NEXO
- 3 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 1 logros:
  - `tiza_60` **Dedos de rayo** — 60 PPM en Tiza

## Ideas para escalar
- [ ] Modo frases/refranes
- [ ] Idiomas (inglés, valenciano)
- [ ] Modo profesor con listas propias
- [ ] Duelo a pantalla partida

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
