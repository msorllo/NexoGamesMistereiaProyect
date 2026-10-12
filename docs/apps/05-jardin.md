# Jardín Focus

> Pomodoros que hacen crecer plantas

| Campo | Valor |
|---|---|
| Archivo | `src/apps/05-jardin.html` (14 KB) |
| id (manifest / `data-app`) | `jardin` / `jardin` |
| `<title>` | Jardín Focus |
| Categorías | bienestar productividad |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Karla, Young Serif |
| Splash | fondo `#dfe7d5` → `#f6f8f1`, texto `#2f4a3a`, acento `#c9774f` |

## Concepto
Pomodoro que hace crecer una planta mientras te concentras; si abandonas, se marchita. Las plantas completadas viven en tu invernadero.

## Cómo está hecha
Árboles recursivos procedurales en canvas (parámetros por especie: ángulo, profundidad, colores), semilla aleatoria por sesión, girasol con dibujo propio.

## Mecánicas y recompensas
- Sesiones de 15/25/50 min
- Semillas como moneda: comprar 6 especies
- Racha diaria de sesiones
- Modo demostración (1 min = 1 s)

**Controles:** Elegir duración, escribir tarea, Plantar y empezar / Rendirse.

## Paleta (`:root`)
`--sage` #dfe7d5 · `--leaf` #2f4a3a · `--moss` #6d8a62 · `--blush` #f2a7b5 · `--clay` #c9774f · `--paper` #f6f8f1 · `--mut` #7d8f7c

## Persistencia
Claves `OS.save/load` (localStorage `nexo.jardin.<clave>`): `cur`, `day`, `owned`, `seeds`, `shelf`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 4 logros:
  - `jardin_first` **Primera semilla** — Plantaste tu primera sesión
  - `jardin_4` **Jardinero constante** — 4 sesiones en un día
  - `jardin_10` **Invernadero lleno** — 10 plantas cultivadas
  - `jardin_all` **Botánica completa** — Todas las especies desbloqueadas

## Ideas para escalar
- [ ] Descansos cortos/largos automáticos
- [ ] Estadísticas semanales
- [ ] Sonidos ambiente (lluvia, bosque)
- [ ] Jardín compartido por equipo

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
