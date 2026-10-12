# Mochi

> Tu mascota virtual más blandita

| Campo | Valor |
|---|---|
| Archivo | `src/apps/20-mochi.html` (20 KB) |
| id (manifest / `data-app`) | `mochi` / `mochi` |
| `<title>` | Mochi |
| Categorías | bienestar juegos |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Baloo 2, Mochiy Pop One |
| Splash | fondo `#ffd9c7` → `#fff8f0`, texto `#5b3a3a`, acento `#ff9eb5` |

## Concepto
Mascota virtual kawaii con necesidades, minijuego de atrapar estrellas, tienda de sombreros y fondos, y evolución.

## Cómo está hecha
Mascota en SVG con expresiones según ánimo, degradación de stats con el tiempo (también estando fuera, limitada), minijuego en canvas.

## Mecánicas y recompensas
- Hambre, alegría, energía, limpieza
- Comer (3 comidas), jugar, dormir, bañar
- Cariño → niveles (evoluciona en 3 y 6)
- Tienda: 5 sombreros, 4 fondos
- Nombre editable (doble clic)

**Controles:** Botones de cuidado, clic para acariciar.

## Paleta (`:root`)
`--peach` #ffd9c7 · `--pink` #ff9eb5 · `--mint` #b8f2e6 · `--cream` #fff8f0 · `--cocoa` #5b3a3a · `--sun` #ffd166 · `--lav` #cdb4f6

## Persistencia
Claves `OS.save/load` (localStorage `nexo.mochi.<clave>`): `pet`

## Integración con NEXO
- 5 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 5 logros:
  - `mochi_shop` **Mochi fashionista** — Compraste todo en la tienda de Mochi
  - `mochi_evo` **Primera evolución**
  - `mochi_evo2` **Mochi radiante**
  - `mochi_pet` **Achuchón** — Acariciaste a tu Mochi 20 veces
  - `mochi_30` **Lluvia de estrellas** — 30 puntos en el minijuego de Mochi

## Ideas para escalar
- [ ] Más minijuegos
- [ ] Accesorios animados
- [ ] Visitas de otros mochis
- [ ] Notificación cuando tiene hambre

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
