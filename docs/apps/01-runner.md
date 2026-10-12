# Neón Runner

> Carreras infinitas en una autopista de 1986

| Campo | Valor |
|---|---|
| Archivo | `src/apps/01-runner.html` (18 KB) |
| id (manifest / `data-app`) | `runner` / `runner` |
| `<title>` | Neón Runner |
| Categorías | juegos 3d |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Audiowide, Chakra Petch |
| Splash | fondo `#1a0033` → `#3b0a5e`, texto `#ffe9f6`, acento `#ff2e88` |

## Concepto
Carreras arcade pseudo-3D estilo outrun de 1986: autopista infinita con curvas y colinas, sol de rayas, palmeras y tráfico neón.

## Cómo está hecha
Canvas 2D con proyección de segmentos (técnica clásica de "pseudo 3D road"). 2400 segmentos en bucle, sprites dibujados por código (coches, palmeras, monedas).

## Mecánicas y recompensas
- Esquivar coches (3 escudos)
- Monedas: +50 puntos y recargan nitro
- Nitro con ESPACIO (doble toque en móvil): 34% del depósito, x1,45 de velocidad
- Cada 3.000 m un sector nuevo más rápido y con otro tono de color
- 5 misiones por carrera (monedas, sector 3, 1.500 m sin chocar, nitro x3, 320 km/h)

**Controles:** ← → / A D para girar, ESPACIO nitro. Móvil: mitades izquierda/derecha de la pantalla.

## Paleta (`:root`)
`--ink` #1a0033 · `--pink` #ff2e88 · `--sun` #ffb800 · `--cyan` #00f0ff · `--fog` #3b0a5e · `--txt` #ffe9f6

## Persistencia
Claves `OS.save/load` (localStorage `nexo.runner.<clave>`): `best`, `runs`

## Integración con NEXO
- 4 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `runner_s5` **Piloto de sector 5** — Llegaste al sector 5 en Neón Runner
  - `runner_c100` **Lluvia de oro** — 100 monedas en una carrera
  - `runner_first` **Primera vuelta** — Arrancaste en Neón Runner

## Ideas para escalar
- [ ] Selector de coches desbloqueables con monedas
- [ ] Túneles y noche/lluvia por sector
- [ ] Fantasma de tu mejor carrera
- [ ] Banda sonora synthwave generada con WebAudio
- [ ] Ranking online

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
