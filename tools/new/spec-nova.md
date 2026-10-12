# 31 · NOVA SURGE — shoot'em up 3D por niveles con jefes (id `nova`, archivo `31-nova.html`, glb `nova`)

Tagline (≤48): **"Doce niveles, ocho jefes y cero piedad"**
Categorías: `3d juegos`. Fila Premium del lanzador (`new=2`).
Es la app nº 31 de NEXO y la más "arcade" de todas: mucha acción, mucha dopamina, muchas interacciones y sonido propio.
Lee `CLAUDE.md` (contrato de app) y `tools/new/BRIEF.md` (listón Premium). Este spec manda si hay conflicto.

---
## 1. Identidad visual (no negociable)
- **Estilo "ácido militar"**: HUD de caza táctico de los 90 con color ácido. Líneas finas de 1 px, esquinas en escuadra (corner brackets), franjas de peligro diagonales, paneles inclinados (`skewX(-8deg)`), botones con esquinas achaflanadas (`clip-path`), números grandes monoespaciados, ligera trama de scanlines. Nada centrado en tarjetas redondeadas iguales, nada de emojis, nada de degradado morado→azul.
- **Fuentes** (Google Fonts, siempre con fallback):
  - Display: `'Tektur',Impact,sans-serif` (pesos 600/800/900; mayúsculas, a veces `skewX(-8deg)`).
  - Texto/HUD: `'Martian Mono',ui-monospace,monospace` (300/400/600/800; números y microcopy).
  - URL: `https://fonts.googleapis.com/css2?family=Tektur:wght@400;600;800;900&family=Martian+Mono:wght@300;400;600;800&display=swap`
- **Paleta** (tokens en `:root`):
  - `--bg:#070906` vacío verdinegro · `--bg2:#141c0e` · `--fg:#eef2e4` hueso · `--mut:#8a927c`
  - `--acc:#c8ff1f` **ácido** (jugador, UI principal, disparos propios)
  - `--hot:#ff2e4d` alerta/enemigo (balas enemigas: núcleo blanco + halo `--hot`)
  - `--amb:#ffb000` ámbar (chatarra, avisos, franjas de peligro)
  - `--ice:#8fd6ff` (solo sector I) · rarezas: común `#b7bfae`, rara `#3fa9ff`, épica `#c45bff`, legendaria `#ffb000` (con destello)
  - Manifest: `bg:#070906`, `bg2:#141c0e`, `fg:#eef2e4`, `acc:#c8ff1f`, `font:"'Tektur',Impact,sans-serif"`.
- **Legibilidad ante todo**: fondos oscuros y algo desaturados, balas enemigas SIEMPRE las más brillantes de la pantalla (núcleo blanco, halo rosa-rojo, bloom). Las balas propias son ácido, más finas y alargadas.
- Microcopy en español de España, tono de radio militar con gracia ("Control: contactos a las doce", "Firma térmica enorme. No es un asteroide.", "Chatarra es chatarra, piloto. Recógela.").

## 2. Concepto y bucle
Shoot'em up vertical en 3D con cámara inclinada (estilo Sky Force / Ikaruga): la nave va abajo, los enemigos entran por arriba, el mundo 3D se desplaza por debajo con parallax. **Campaña de 12 niveles en 4 sectores**, cada nivel con una mecánica nueva y un set-piece propio, **4 jefes intermedios (jefes)** y **4 jefes de sector (jefes finales)**, el último es NOVA, el jefe final absoluto, con 3 fases.
Entre niveles eliges **1 de 3 modificaciones** (cartas con rareza) que cambian tu nave durante la partida (roguelite ligero). Chatarra = moneda permanente para el Hangar (mejoras fijas y pinturas).
Bucle corto: oleada 10–20 s → recompensa (combo, chatarra, potencia) → nivel 90–130 s → resultados con nota S/A/B/C → carta de mejora → siguiente.

## 3. Controles
- **Disparo automático siempre** (móvil friendly).
- Ratón: la nave persigue el puntero (velocidad máx.). Teclado: WASD/flechas; **Mayús = modo preciso** (lento, muestra el hitbox). Espacio = SOBRECARGA (si está llena). X / clic derecho = BOMBA. Esc/P = pausa.
- Táctil: arrastre **relativo** en cualquier parte (la nave se mueve con el delta del dedo ×1.25, no salta bajo el dedo). Botones grandes (≥ 48 px): BOMBA (izq. abajo) y SOBRECARGA (der. abajo), pausa arriba.
- Accesibilidad: `aria-label`, foco visible, `prefers-reduced-motion` → menos sacudida/partículas, opción "Sacudida" on/off.

## 4. Sistemas de juego (valores base; el balance fino se ajusta al probar)
- **Campo lógico** en el plano XZ de three (y=0): x ∈ [-8, 8], z ∈ [-12, 12] (z negativo = arriba de la pantalla). Jugador limitado a x ∈ [-7.6, 7.6], z ∈ [-10, 11]. Los enemigos nacen en z ≈ -14 (o por los lados, x ≈ ±11) y se eliminan al salir (|x|>12 o z>14). La cámara encuadra el campo entero en cualquier aspecto (retrato móvil y apaisado); en escritorio sobran laterales para HUD y para ver el mundo.
- **Jugador**: velocidad 13 u/s (preciso 6). Hitbox r = 0.16 (punto brillante visible en modo preciso), radio de ROCE r = 0.85. Blindaje base 4 (segmentos). Al recibir daño: −1 blindaje, 2 s de invulnerabilidad (parpadeo), onda que borra balas en r=3, pierde 1 nivel de potencia que sale despedido como cápsula P recuperable.
- **Disparo**: 9 ráfagas/s, daño 1 por bala, velocidad 34. Potencia P1–P5 (cápsulas P): P1 2 cañones; P2 3; P3 +2 en abanico; P4 +20 % cadencia; P5 +2 abanico y +25 % daño. Las modificaciones se suman encima.
- **Roce (graze)**: cada bala enemiga que pasa por el radio de roce sin tocar el hitbox cuenta 1 roce una vez: +10 pts, +1.5 % sobrecarga, chispa y "tic" agudo. Contador de roces en el HUD.
- **Combo**: cada baja en < 2.2 s desde la anterior encadena. Multiplicador: 0–9 ×1 · 10 ×2 · 25 ×3 · 50 ×4 · 100 ×5 · 200 ×8. Rozar alarga el temporizador. Al subir de multiplicador: banner grande + sonido (a partir de ×4, efecto sonoro especial más potente).
- **Sobrecarga (Overdrive)**: medidor 0–100 (baja +2, roce +1.5, daño a jefe +0.05/pto). Llena → botón late. Activa: 6 s, el MUNDO va a 0.55× (la nave no), cadencia ×2.5, daño ×1.5, balas más gordas, bloom sube, viñeta ácida, la música dobla el tempo del hi-hat.
- **Bombas**: 2 por nivel (+Hangar/mods). Borra todas las balas enemigas (se convierten en chatarra), 40 de daño a todo (a jefes 3 % de su vida máx.), 1.5 s de invulnerabilidad, onda expansiva enorme, flash, sub-grave.
- **Chatarra**: la sueltan las bajas (1–3 piezas), las balas canceladas (1) y los jefes (lluvias de 60–200). Se atrae con imán (r 2.5 base). Sonido de recogida en escala ascendente por racha. Es permanente (se conserva aunque pierdas).
- **Recogibles**: `P` potencia, `B` bomba, `R` reparación (+1 blindaje). Los `portador` son piñatas: sueltan lluvia de todo.
- **Muerte y reintentos**: blindaje 0 → si quedan REINTENTOS (base 2 por partida, +Hangar): reapareces en el sitio con blindaje lleno, 3 s de invulnerabilidad, combo perdido. Sin reintentos → GAME OVER: fin de la partida, pantalla de "casi" ("Al jefe le quedaba un 8 %", "Te faltaban 14 s para el final del nivel"), la chatarra se queda.
- **Nota del nivel**: puntos = 50·(bajas/aparecidos) + 30·max(0, 1 − golpes/4) + 20·min(1, combo máx./comboObjetivo). S ≥ 90, A ≥ 75, B ≥ 55, C resto. **Estrellas**: ★ superar, ★★ superar sin gastar reintento, ★★★ nota S.
- **Dificultad por nivel** (i = 0..11): vida enemiga ×(1 + 0.15·i), velocidad de balas ×(1 + 0.05·i), cadencia enemiga ×(1 + 0.07·i). **Pesadilla** (se desbloquea al vencer a NOVA): vida ×1.4, balas ×1.2 y cada enemigo suelta 3 "balas de venganza" al morir; puntuación ×2.

## 5. Estructura de campaña
- 4 sectores × 3 niveles. Una PARTIDA empieza en el primer nivel de un sector desbloqueado (checkpoint) y sigue hasta el final si no pierdes. Si empiezas en el sector k (>1), eliges k cartas de golpe ("Kit de despegue") para no ir desnudo.
- Tras cada nivel superado: resultados → **elige 1 de 3 modificaciones** (tras un jefe de sector, mínimo una épica garantizada). Opción "Chatarra" (+50) si no te gusta ninguna, y "Rebarajar" (cuesta 30 chatarra).
- La partida en curso se guarda al empezar cada nivel (si cierras, "Continuar" te devuelve al inicio de ese nivel con tus mods).
- **Contrato del día**: cada día (semilla por fecha) un nivel ya desbloqueado + un modificador ("Balas trazadoras dobles", "Sin bombas", "Todo elite", "Velocidad ×1.3") y 3 mods fijas. Primera victoria del día: +150 chatarra y XP. Aparece en la portada.

## 6. Los 12 niveles (cada uno distinto; mecánica nueva + set-piece)
Temas de entorno (`theme`): `hielo`, `azufre`, `astillero`, `corona` (+ `hangar` para menús). Cada nivel dura 90–130 s hasta su jefe.

**SECTOR I · CINTURÓN GLACIAL** (`hielo`: espacio azul marino profundo, campo de asteroides de hielo en capas, planeta cian lejano con anillos, polvo de nieve; música 128 BPM La menor)
1. **Despegue** — tutorial por radio (moverse, disparo automático, recoger, bomba, SOBRECARGA forzada al final con el medidor precargado). `dardo` en V, línea y columna seno; un `portador` piñata a mitad; cierre con 3 `caza`. Sin jefe.
2. **Deriva** — `asteroide` g/m/p que se parten, `torreta` ancladas a asteroides grandes, `dardo` en seno. Set-piece "Lluvia de hielo" (`lluvia_hielo`: 8 s de piedras pequeñas rápidas). **Jefe: ROMPEHIELOS**.
3. **La Trituradora** — aproximación corta entre restos y **JEFE FINAL DE SECTOR: LA TRITURADORA**.

**SECTOR II · NEBULOSA DE AZUFRE** (`azufre`: niebla ocre y ámbar en capas, cristales flotantes con vetas encendidas, relámpagos que iluminan la escena; 136 BPM Re menor, ácido más sucio)
4. **Campo minado** — rejillas de `mina` (las explosiones de mina dañan a otras minas → reacciones en cadena), `puerta_laser` que se encienden a ritmo, estreno del `kamikaze`. Set-piece "El pasillo": 4 puertas láser seguidas a ritmo.
5. **Enjambre** — bandadas de `avispa` (12–20, comportamiento de bandada), `kamikaze`, `rayo` (círculo de aviso → descarga). **Jefe: LA REINA**.
6. **La Hidra** — niebla espesa que se abre de golpe: **JEFE FINAL DE SECTOR: LA HIDRA**.

**SECTOR III · ASTILLERO ORBITAL** (`astillero`: megaestructura metálica pasando por debajo con paneles, tuberías, antenas, balizas rojas giratorias, chispas y vapor; 140 BPM Mi frigio, industrial)
7. **El cañón** — `pasillo` (muros laterales que estrechan el campo), `aplastador` que entra desde los lados con aviso, `torreta` en los muros, `dardo`. Set-piece "La compactadora": aplastadores alternos a ritmo.
8. **Espejos** — `escudero` (escudo frontal que REFLEJA tus balas: hay que flanquear o romper el escudo), `saltador` (teletransporte + anillo), `portador`. **Jefe: EL PRISMA**.
9. **El Acorazado** — el casco del acorazado va entrando por debajo: **JEFE FINAL DE SECTOR: EL ACORAZADO**.

**SECTOR IV · CORONA DE NOVA** (`corona`: superficie estelar por shader (granulación carmesí-naranja, manchas, protuberancias), brasas que suben, calima; 150 BPM Fa# menor)
10. **Tormenta solar** — `llamarada` (columnas avisadas que barren), `pulso_emp` (anillo avisado; si te pilla, 2 s sin armas), estreno de `centinela` (elite), `saltador`.
11. **El guante** — oleadas relámpago con élites de todos los tipos, cada una con 10 s de reloj ("¡OLEADA LIMPIA +500!" si la limpias a tiempo). **Jefe: LOS GEMELOS**.
12. **NOVA** — sin enemigos normales: aproximación dramática (la estrella se enciende, radio nerviosa) y **JEFE FINAL ABSOLUTO: NOVA** (3 fases). Final: cámara lenta, blanco total, supernova, créditos, desbloqueo de Pesadilla.

## 7. Enemigos y peligros (IDs exactos para `spawn()`)
Todos miran hacia abajo de la pantalla (modelo con el morro a +Y de Blender = −Z de three → rotar π). Vida = base × dificultad. `elite:true` → ×2.5 vida, detalles dorados, más balas, ×3 puntos.

| ID | Modelo(s) | Vida | Comportamiento |
|---|---|---|---|
| `dardo` | `Dardo` | 3 | Rápido, sigue `path`; dispara 1 bala apuntada de vez en cuando. |
| `caza` | `Caza` | 14 | Entra, se para (`stay`), dispara abanicos de 3–5, se va. |
| `torreta` | `Torreta_Base` + `Torreta_Cabeza` | 18 | Anclada al suelo/asteroide/muro (se desplaza con el mundo o con `anchor`); la cabeza apunta; ráfagas de 3. |
| `asteroide` (`size:'g'|'m'|'p'`) | `Asteroide_G/M/P` | 30/10/3 | Deriva y gira; se parte en 2–3 del tamaño menor; choca contra la nave (daño). |
| `lluvia_hielo` | (usa `Asteroide_P`) | — | Peligro: durante `dur` s genera piedras pequeñas rápidas. |
| `mina` | `Mina` | 6 | Flota lenta; al morir o si te acercas (r 2.5) parpadea 0.6 s y estalla en anillo de 12–16 balas; su explosión daña a minas cercanas (cadena). |
| `avispa` | `Avispa` | 2 | En bandada (12–20) hacia el jugador con separación/alineación. |
| `kamikaze` | `Kamikaze` | 5 | Se fija en ti (línea roja de aviso 0.7 s) y embiste en línea recta. |
| `escudero` | `Escudero` + `Escudo` | 20 | Escudo frontal que refleja tus balas (vuelven como balas enemigas); tras 25 impactos el escudo se rompe; disparo de orbes lentos grandes. |
| `saltador` | `Saltador` | 10 | Se teletransporta (implosión de partículas) y dispara anillo. |
| `portador` | `Portador` | 40 | Lento y gordo; al morir: lluvia de chatarra + P + a veces B/R. |
| `centinela` | `Centinela` | 60 | Élite blindado: espirales dobles y ráfagas apuntadas. |
| `aplastador` | `Aplastador` | ∞ | Peligro: bloque que entra desde un lado (aviso de franjas 1 s) hasta `depth` y vuelve. |
| `puerta_laser` | 2× `Pilon` | 25 c/u | Dos pilones con haz entre ellos que se enciende/apaga a ritmo (`on`,`off`); destruir un pilón apaga la puerta. |
| `pasillo` | (muros por código o `Casco_Panel`) | ∞ | Muros laterales durante `dur` s con anchura variable (`w0`→`w1`); tocarlos daña. |
| `rayo` | (efecto) | — | Círculo de aviso 1 s en (x,z) → descarga vertical que daña. |
| `llamarada` | (efecto) | — | Columna avisada que barre horizontal o vertical. |
| `pulso_emp` | (efecto) | — | Anillo que se expande desde un punto; si te toca: 2 s sin armas (no quita vida). |

Parámetros comunes de `spawn(type, opts)`: `x, z, path, speed, stay, fire, elite, delay, anchor, dir, size, dur, ...`. Trayectorias (`path`): `recto`, `seno`, `curva_i`, `curva_d`, `parada`, `lateral_i`, `lateral_d`, `orbita`, `persigue`. Formaciones del nivel (`form`): `linea`, `v`, `columna`, `arco`, `pinza`, `lluvia`, `rejilla`.

## 8. Jefes (IDs para `boss:`)
Todos: entrada con **ALERTA** (franjas de peligro a pantalla completa, sirena), tarjeta con nombre y subtítulo, barra de vida segmentada por fases, parpadeo blanco al recibir daño, cada cambio de fase = explosión + cámara lenta 0.6 s + patrón nuevo, muerte = cadena de explosiones 2–3 s a cámara lenta + flash + lluvia de chatarra. Puntos débiles con material emisivo `Punto_Debil` (daño ×2).

**Jefes (intermedios)**
- `rompehielos` · **ROMPEHIELOS** "Rompehielos minero sin tripulación" — `Rompehielos` + `Taladro` (gira). Barre de lado a lado soltando abanicos de esquirlas; carga hacia abajo con aviso (franja) y vuelve; tras la carga expone el punto débil trasero 2 s. Vida 700.
- `reina` · **LA REINA** "Nodriza del enjambre" — `Reina`. Suelta bandadas de `avispa`, 6 avispas en órbita que la protegen (bloquean balas), aguijones curvos. Fase 2: se enfurece, órbita más rápida, ráfagas en espiral. Vida 900.
- `prisma` · **EL PRISMA** "Cristal de defensa del astillero" — `Prisma_Nucleo` + 6× `Prisma_Petalo`. Cerrado = invulnerable y devuelve tus balas como esquirlas; se abre en ciclos exponiendo el núcleo; haces láser que rotan. Vida 1100.
- `gemelos` · **LOS GEMELOS** "Interceptores gemelos" — 2× `Gemelo`. Se mueven en espejo con un haz entre ellos; al morir uno, el otro se enfurece (doble cadencia). Vida 2×700.

**Jefes finales de sector**
- `trituradora` · **LA TRITURADORA** "Estación minera renegada" (sector I) — `Trituradora` (cuerpo) + 4× `Brazo_Sierra` + 4× `Sierra` (giran). F1: los brazos rotan y barren, cada brazo se destruye (300). F2 (sin brazos o < 50 %): núcleo expuesto, espiral de esquirlas + lanza asteroides. F3 (< 20 %): gira rápido, anillos de balas. Vida núcleo 1600.
- `hidra` · **LA HIDRA** "Serpiente de la nebulosa" (sector II) — `Hidra_Cabeza` + 10× `Hidra_Segmento` + `Hidra_Cola`. Ondula por el campo; cada segmento tiene torreta y se puede volar (se acorta); la cabeza es el punto débil. F2: se parte en DOS serpientes. F3: niebla + embestidas avisadas. Vida total 2600.
- `acorazado` · **EL ACORAZADO** "Buque insignia de la flota" (sector III) — `Acorazado` (casco enorme que ocupa la parte alta) + 4× `Acorazado_Torreta` + `Acorazado_Canon` + `Acorazado_Puente`. F1: torretas (destructibles). F2: el cañón principal carga (aviso) y barre un láser gigante. F3: puente expuesto y hangares que sueltan `dardo`. Vida 3600.
- `nova` · **NOVA** "El corazón de la estrella" (FINAL) — `Nova_Nucleo` + 8× `Nova_Placa` (orbitan y bloquean) + 2× `Nova_Anillo`. F1 "Corona": placas en órbita + espirales. F2 "Eclipse": escena se oscurece, cruz láser giratoria + invoca `centinela`. F3 "Supernova": flor de balas desesperada, la arena se encoge, cuenta atrás de 20 s; si aguantas y la rematas → final. Vida 5200.

## 9. Modificaciones (catálogo; niveles 1–3 salvo legendarias)
Rarezas y probabilidades base: común 55 %, rara 28 %, épica 13 %, legendaria 4 % (Hangar "Suerte" las mejora). Coger una que ya tienes = sube de nivel (máx. 3). Cada carta: icono SVG propio, nombre, nivel, texto corto con el efecto exacto.
- ARMA: `doble` Cañón doble (+1/+2/+3 cañones) · `abanico` Abanico (+2 balas en abanico por nivel) · `perforante` Perforante (atraviesa 1/2/3) · `rebote` Rebote (rebota en bordes 1/2/3) · `misiles` Misiles buscadores (1 cada 1.2/0.9/0.6 s) · `laser` Lanza láser (rayo perforante cada 4/3/2 s) · `cadencia` Cadencia (+15/30/45 %) · `calibre` Calibre (+20/40/60 % daño) · `critico` Crítico (10/18/25 % de ×3 con "¡CRÍTICO!") · `metralla` Metralla (las bajas sueltan 4/6/8 esquirlas propias) · `cadena` Arco voltaico (12/20/28 % de rayo a 2–4 enemigos) · `orbes` Orbes (1/2/3 orbes que giran, dañan y bloquean balas).
- DEFENSA: `blindaje` Blindaje (+1/+2/+3) · `escudo` Escudo regenerativo (absorbe 1 golpe, recarga 20/15/10 s) · `roce` Piloto temerario (radio de roce +30/60/90 % y el roce da más sobrecarga) · `fase` Onda de fase (al recibir daño, onda que borra balas r 5/7/9 y +1 s invulnerable) · `anulador` Anulador (cada baja borra balas cercanas r 1.5/2.5/3.5 → chatarra).
- UTILIDAD: `iman` Imán (+60/120/200 % radio) · `sobrecarga` Reactor (sobrecarga +2/+3/+4 s y se llena +25/50/75 % más rápido) · `bombas` Arsenal (+1/+2/+3 bombas por nivel) · `drones` Escolta (1/2/3 drones que disparan contigo) · `codicia` Codicia (+25/50/75 % chatarra pero enemigos +10/15/20 % vida).
- LEGENDARIAS (nivel único): `supernova` Supernova (activar sobrecarga provoca una detonación de pantalla completa) · `tiempo_bala` Tiempo bala (cuando una bala te va a dar, el tiempo se frena 0.6 s; 1 vez cada 8 s) · `enjambre` Enjambre (cada baja lanza un minimisil) · `fenix` Fénix (una vez por partida, al morir resucitas con blindaje lleno y explosión enorme).
- **Hangar** (permanente, con chatarra; 5 niveles cada línea, coste creciente): Blindaje inicial, Potencia inicial, Bombas iniciales, Imán, Reintentos, Suerte (rarezas).
- **Pinturas** (cosmético: color del casco `Casco`, del motor y de la estela): Ácido (inicial), Hueso, Óxido, Fantasma, Sangre (vencer a la Trituradora), Oro (vencer a NOVA), Pesadilla (superar Pesadilla). Algunas se compran, otras por hitos o estrellas totales.
- **Códice**: colección de las 26 modificaciones (silueta hasta que la descubres, nivel máximo alcanzado) + bestiario de jefes derrotados.

## 10. UI y pantallas
- **Portada**: escena 3D del hangar (nave girando sobre `Plataforma`, luces, polvo), logo NOVA SURGE con barrido/glitch, botones JUGAR / CONTINUAR, SECTORES, HANGAR, CÓDICE, contrato del día, sonido/música. Chatarra y estrellas visibles.
- **Mapa de sectores**: 4 sectores × 3 niveles con estrellas, candados, iconos de jefe; elegir checkpoint.
- **Intro de nivel**: tarjeta "NIVEL 04 · CAMPO MINADO" + frase de radio, 1.5 s.
- **HUD**: puntuación (FX.count), multiplicador de combo grande que late, blindaje en segmentos, bombas, medidor de sobrecarga, potencia P1–P5, roces, barra de progreso del nivel (hasta el jefe), barra de jefe segmentada, subtítulos de radio. Escritorio: paneles laterales. Móvil: arriba puntuación/combo, abajo botones.
- **Popups**: números de daño/puntos, "¡CRÍTICO!", "+ROCE", "×4 COMBO", "¡OLEADA LIMPIA!", proyectados en 3D→pantalla (pool DOM).
- **Resultados**: sello de nota S/A/B/C que cae con golpe, estrellas una a una, contadores, récord.
- **Cartas de modificación**: 3 cartas entran volando, giran, destello según rareza (legendaria: haz dorado + coro), hover/foco inclina la carta. Rebarajar y "Chatarra +50".
- **Pausa**, **Game Over** con el "casi", **Victoria** (créditos en scroll tras NOVA), **Hangar**, **Códice**, **Ajustes** (música, efectos, sacudida).

## 11. Audio (100 % sintetizado, SIN voz: nada de locutor ni speechSynthesis; solo música y efectos)
- **Música procedural "acid"**: secuenciador con look-ahead: bajo TB-303 (sierra/cuadrada + filtro paso bajo resonante con envolvente y acentos/slides), batería 909 sintetizada (bombo, caja, hats, palmas), arpegio. Una pista por sector (tempo/tonalidad de §6), variante JEFE (más capas, más distorsión), menú tranquilo, victoria. Intensidad por capas (0–2). Sobrecarga = hats al doble.
- **Efectos**: disparo (blip suave, limitado para no saturar), impacto, explosiones por tamaño (ruido filtrado + caída de tono + sub), chatarra (escala ascendente por racha), roce (tic agudo), potencia, bomba (sub-grave + barrido), sobrecarga (subida + drop), sirena de ALERTA, cambio de fase, muerte de jefe, UI (hover/clic/carta/sello/contador), daño propio, EMP, rayo.
- **Sin voz** (decisión de Marco): los momentos clave (alerta de jefe, sobrecarga, combos altos, sector despejado, jefe abatido) se marcan con efectos sonoros especiales y textos en pantalla, nunca con voz sintetizada. `SND.say` existe solo como no-op por compatibilidad.
- Todo respeta `FX.muted` y los ajustes guardados. Sin audio hasta el primer gesto.

## 12. Assets de Blender (nombres EXACTOS; morro a +Y de Blender; la cámara ve desde ARRIBA inclinada ~35°, así que el detalle importante va en la cara superior +Z y en la silueta vista desde arriba)
Materiales con nombre fijo: usa `blender/scripts/nova_mats.py` → `M('Nombre')` (tabla única, no definas otros parámetros para esos nombres). Low-poly estilizado de ciencia ficción "hard-surface": biseles, paneles, tomas de aire, antenas, luces emisivas. Un objeto unido por asset con el nombre exacto; origen en el pivote que indica la tabla (por defecto el centro, a la altura z=0).
Grupos (cada uno en su script, ver §13):
- **A · jugador, recogibles, entorno, enemigos pequeños** (≤ 330 KB): `Nave` (1.5 largo, 1.3 envergadura; `Casco`, `Casco_Acento`, `Cabina`, `Motor`), `Dron` (0.5), `Chatarra` (0.35, tuerca/engranaje), `Potencia` (cápsula 0.6 con una "P" en relieve), `Bomba_Item` (0.6), `Reparacion` (0.6, cruz), `Plataforma` (hangar hexagonal 6 de ancho con luces `Motor`), `Casco_Panel` (placa de megaestructura 8×8 que tesela en Y, greebles), `Tuberia` (8 largo), `Antena` (3 alto), `Roca_Azufre` (1.5, vetas `Azufre`), `Baliza` (1, luz `Enemigo_Luz`), `Dardo` (1.1), `Caza` (1.8), `Torreta_Base` (1.3) + `Torreta_Cabeza` (origen en el eje de giro, cañones hacia +Y), `Mina` (1.0, pinchos), `Avispa` (0.6), `Kamikaze` (1.0), `Asteroide_G` (3.2), `Asteroide_M` (1.8), `Asteroide_P` (0.9) (hielo: `Hielo` + `Roca`).
- **B · enemigos grandes y jefes intermedios** (≤ 330 KB): `Escudero` (1.6) + `Escudo` (placa curva delante, material `Escudo_Energia`, origen en el centro del escudero), `Saltador` (1.2), `Portador` (2.6, cajas `Chatarra`), `Centinela` (2.0, `Oro_Elite`), `Aplastador` (4×2×1.5, franjas `Peligro_Amarillo`/`Peligro_Negro`), `Pilon` (0.8×0.8×1.6 alto, emisor), `Rompehielos` (4.5) + `Taladro` (origen en el eje, gira sobre Y de Blender), `Reina` (5 de ancho, abdomen `Punto_Debil`), `Prisma_Nucleo` (2.5, octaedro facetado) + `Prisma_Petalo` (1 pétalo, origen en la bisagra; el código pone 6), `Gemelo` (3).
- **C · jefes finales** (≤ 380 KB): `Trituradora` (cuerpo, 7 de ancho, ojo `Punto_Debil`), `Brazo_Sierra` (4 largo, origen en el extremo que va al cubo), `Sierra` (disco d 2.2 con dientes, origen en el centro, gira sobre Z de Blender), `Hidra_Cabeza` (3), `Hidra_Segmento` (d 1.8 con torreta encima), `Hidra_Cola`, `Acorazado` (14 × 9, cubierta detallada), `Acorazado_Torreta` (1.6, origen en el pivote), `Acorazado_Canon` (5 largo, origen en el pivote), `Acorazado_Puente` (3×2×2, ventanas `Punto_Debil`), `Nova_Nucleo` (esfera d 4, costuras `Nova_Costura`, plasma `Nova_Plasma`), `Nova_Placa` (placa curva 2.4×1.6), `Nova_Anillo` (toro d 7 segmentado).
- Presupuesto total del GLB ≤ 1 MB (`export_apply=True`). Enemigos 300–1500 triángulos, jugador ~2.5k, jefes finales hasta ~8k.
- **Icono** (render Cycles 256 px en `b_nova.py`): la `Nave` en primer plano inclinada con el motor ácido encendido disparando hacia arriba, silueta de un jefe detrás, fondo `#0b0f08`. Tiene que leerse a 64 px.

## 13. Arquitectura del código (desarrollo en partes, un único HTML al final)
Fuente durante el desarrollo: `tools/new/nova/`. `python tools/new/nova/assemble.py` genera `src/apps/31-nova.html` (o `--out ruta`, `--skip 30-,40-` para excluir partes). Estructura:
```
tools/new/nova/head.html        <!doctype>…<head> con fuentes, <title>, <style>/*__CSS__*/</style></head><body>
tools/new/nova/body.html        canvas #c, #load y contenedores DOM (#hud, #ui, #fx)
tools/new/nova/css/NN-*.css     se concatenan en orden dentro de <style>
tools/new/nova/js/00-fx.js      kit FX copiado TAL CUAL de tools/templates/premium3d.html (entre los marcadores)
tools/new/nova/js/10-core.js    motor (núcleo)            → agente CORE
tools/new/nova/js/20-enemies.js enemigos, trayectorias, peligros, patrones extra → agente ENEMIGOS
tools/new/nova/js/30-bosses.js  8 jefes                    → agente JEFES
tools/new/nova/js/40-levels.js  12 niveles + 5 entornos    → agente NIVELES
tools/new/nova/js/50-meta.js    mods, hangar, pinturas, códice, guardado, logros, XP → agente META
tools/new/nova/js/60-ui.js      pantallas, HUD, popups     → agente UI
tools/new/nova/js/65-audio.js   música y efectos          → agente AUDIO
tools/new/nova/js/90-boot.js    arranque                   → agente CORE
tools/new/nova/API.md           documentación del núcleo   → agente CORE (la leen todos)
```
- Cada `js/*.js` va en su propio `<script>` (un fallo no tumba a los demás). **Cada módulo que no sea el núcleo va entero dentro de `(()=>{ 'use strict'; … })();`** y solo publica cosas asignando en los espacios de nombres del núcleo. Nunca escribas la cadena `</script>` dentro del JS.
- Espacios de nombres globales (los crea `10-core.js`; nadie más crea globales): `G` (estado), `REG` (`enemies`, `bosses`, `levels`, `mods`, `themes`, `skins`), `BUS` (eventos `on/off/emit`), `PAT` (patrones de balas), `EB`/`PB` (balas enemigas/propias), `BEAM` (láseres y avisos), `SPAWN` (spawn y formaciones), `JUICE` (explosiones, popups, flash, hit-stop, cámara lenta), `CAM`, `SHIP`, `ENV`, `UI`, `SND`, `MUS`, `META`, `SAVE`, `N` (API de pruebas en `window.N`). Los módulos UI/SND/MUS/ENV/META traen stubs en el núcleo y el módulo correspondiente los sustituye con `Object.assign`.
- **Eventos del BUS** (nombres y datos fijos; audio, UI y meta se enganchan aquí):
  `shot{kind}`, `hit{e,dmg,crit}`, `kill{e,type,x,z,score,elite,boss}`, `hurt{hp}`, `shield{}`, `graze{count}`, `pickup{kind,value,chain}`, `power{level}`, `bomb{}`, `od_ready{}`, `od_start{}`, `od_end{}`, `combo{chain,mult}`, `enemy_fire{type,x,z}` (limitado), `explode{x,z,size}`, `hazard_warn{kind}`, `emp{}`, `lightning{}`, `boss_warn{id,name,title}`, `boss_start{id}`, `boss_phase{id,phase}`, `boss_die{id}`, `level_start{level}`, `level_clear{level,grade,stars,stats}`, `sector_clear{sector}`, `player_die{retries}`, `revive{}`, `gameover{stats}`, `victory{}`, `radio{text}`, `screen{name}`, `mod_pick{id,lv,rarity}`, `ui{kind}` (`hover`,`click`,`back`,`buy`,`error`,`card_in`,`card_flip`,`card_pick`,`stamp`,`count`,`star`).
- **Firma de audio** (el módulo de audio las implementa; los demás pueden llamarlas directamente): `SND.play(name, opts)` con nombres `shot, hit, crit, explode_s, explode_m, explode_l, pickup, graze, power, bomb, od, alarm, phase, boss_die, hurt, shield, emp, thunder, laser_warn, laser, ui_hover, ui_click, ui_back, ui_buy, ui_error, card, card_legend, stamp, star, level_up`; `SND.say(texto)`; `MUS.play(pista)` (`menu`,`s1`,`s2`,`s3`,`s4`,`boss`,`final`,`victory`), `MUS.intensity(0..2)`, `MUS.stop(fade)`, `MUS.duck(seg)`; `SND.settings({music,sfx})`.
- **Niveles como datos** (DSL que interpreta el núcleo): `{id, sector, name, theme, music, scroll, gradeCombo, intro:'frase de radio', events:[{t, spawn:'dardo', form:'v', n:5, x:0, path:'recto', …}, {t, hazard:'puerta_laser', …}, {t, wait:'clear'}, {t, boss:'rompehielos'}, {t, radio:'…'}, {t, banner:'…'}, {t, env:'rayo_flash'}, {t, od:90}, {t, music:'boss'}, {t, scroll:1.5}, {t, fn:(G)=>{}}]}`. El reloj del nivel se detiene mientras hay `wait` o jefe vivo. El nivel termina cuando no quedan eventos ni enemigos (sin contar peligros).
- **Rendimiento**: InstancedMesh para balas (propias ~400, enemigas ~900), pools para enemigos (clones reutilizados por tipo), partículas del kit, anillos de onda en pool, 1 luz de destello reutilizada. Nada de crear geometrías/materiales por frame. Simulación a paso fijo (1/60) separada del render, con escala de tiempo (cámara lenta, hit-stop). Colisiones en 2D (XZ). Destello de impacto cambiando temporalmente a un material blanco compartido (no clonar materiales por enemigo). Calidad adaptativa del kit.
- **API de pruebas `window.N`**: `state()`, `play(level,{mods})`, `ff(seg)` (simula sin renderizar), `god(bool)`, `auto(bool)` (piloto automático sencillo), `killAll()`, `boss(id)`, `bossHp(frac)`, `mod(id,lv)`, `give(kind)`, `hurt()`, `die()`, `clear()`, `screen(nombre)`, `warnings()` (modelos o tipos que faltan). Los módulos pueden añadir funciones a `N`.

## 14. Logros (literales, `OS.achieve('nova_…','…','…')`) y XP
`nova_despegue` "Despegue" (supera el nivel 1) · `nova_trituradora` "Chatarra de la buena" (derrota a la Trituradora) · `nova_intocable` "Intocable" (un nivel sin recibir daño) · `nova_combo` "Reacción en cadena" (combo de 100) · `nova_roce` "Rozando el metal" (100 roces en un nivel) · `nova_legendaria` "Pieza legendaria" (consigue una modificación legendaria) · `nova_final` "Supernova" (derrota a NOVA) · `nova_pesadilla` "Duermes tranquilo" (supera NOVA en Pesadilla; secreto).
XP: nivel superado 15 + 3·nivel (+10 si nota S), jefe intermedio 30, jefe de sector 50, NOVA 60, contrato diario 40. Nunca por frame; valores 5–60 por llamada.

## 15. Pruebas (obligatorias)
```
python tools/new/nova/assemble.py --out <scratch>/nova.html
python tools/preview.py <scratch>/nova.html nova <scratch>/shot.png --wait 5000 --js "N.play(3);;WAIT500;;N.ff(20);;WAIT1500;;SHOT:<scratch>/n4.png;;JSON.stringify(N.state())"
python tools/preview.py <scratch>/nova.html nova <scratch>/mob.png --mobile --wait 5000
```
SwiftShader va a 1–3 fps: usa `N.ff()` para avanzar la simulación y `WAIT` para que el render alcance. "ERRORES: ninguno" es requisito. Mira las capturas con Read (escritorio y móvil). Usa la carpeta scratch que te indiquen, nunca escribas capturas dentro del proyecto salvo `tools/shots/`.
