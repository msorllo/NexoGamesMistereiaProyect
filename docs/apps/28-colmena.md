# Colmena

> Tu colmena crece incluso cuando no miras

| Campo | Valor |
|---|---|
| Archivo | `src/apps/28-colmena.html` (109 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `colmena` / `colmena` |
| `<title>` | Colmena |
| Categorías | 3d juegos bienestar |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader + kit FX premium (EffectComposer, UnrealBloom, partículas, tweens, audio) |
| Fuentes | Fraunces, Hanken Grotesk |
| Splash | fondo `#9fd3e6` → `#f6e7b0`, texto `#2b1a05`, acento `#f2a900` |

## Concepto
Idle incremental en un diorama 3D: un colmenar sobre una loma flotante con campo de flores (margaritas, girasol, romero, lavanda, brezo y azahar, el guiño a Benicarló). Cientos de abejas vuelan entre flores y colmenas, el panal del marco crece celda a celda y se llena de miel translúcida. Luz de día real: la paleta del cielo cambia con la hora (mañana dorada, mediodía, tarde de miel, noche con luciérnagas).

## Cómo está hecha
Three.js r147 + modelos de Blender (b_colmena.py: colmena Langstroth, marco con lámina de cera, celda hexagonal y celda de miel, abeja < 800 tris con alas aparte, seis flores, naranjo, tarro, caja, ahumador, apicultor, loma flotante con faldón de tierra y roca, moneda, mariposa, valla, nube, hierba). Abejas con 2 InstancedMesh (cuerpo multimaterial + alas que aletean por escala) y trayectorias Bézier con ruido; hierba y flores instanciadas con balanceo de viento en el vertex shader (dirección coherente en mundo); miel MeshPhysicalMaterial con transmisión; cielo con shader de degradado y entorno PMREM generado del propio cielo; sombras suaves que solo se recalculan cuando algo cambia; economía pura aislada en el bloque ECO (sanear estado, costes 1,12–40^n, ganancias offline, prestigio) que se puede simular en Node.

## Assets 3D (Blender)
- Script: `blender/scripts/b_colmena.py` (usa `blib.py`) → exporta `blender/glb/colmena.glb`, guarda `blender/blend/colmena.blend` y renderiza `blender/renders/colmena.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- Néctar -> miel -> monedas: las abejas traen néctar, las colmenas y el panal lo procesan; si un lado va corto se marca el cuello de botella
- Toca una colmena, el tarro o el botón Cosechar para vender la miel (8 % de cosecha dorada ×3)
- Toca un macizo de flores: las abejas cercanas vuelan a él y todo produce ×3 durante 10 s (recarga 20 s)
- Siete mejoras con coste exponencial y compra ×1 / ×10 / Máx: abejas, colmenas (caen y rebotan), panal extra (celdas nuevas en el marco), seis flores con su miel, apicultor con ahumador (cosecha solo), reina seleccionada (×2) y puesto en el mercado (precio ×1,4)
- Mariposa dorada cada 1–3 min: frenesí ×5, monedas, enjambre errante o, rara vez, jalea real
- Hitos: tres a la vez, primero una lista pensada para los 10 primeros minutos y luego procedurales
- Tarro del día con racha de 7 días (el séptimo trae jalea real)
- Ganancias sin conexión hasta 8 h con tarjeta de Recoger
- Enjambrar (prestigio) al ganar 100 M en la temporada: jalea real = +10 % de producción por unidad, cinemática de enjambre en espiral
- Colección de las seis mieles y estadísticas

**Controles:** Ratón o dedo: arrastra para girar la loma, rueda o pellizco para acercar, toque/clic en colmenas, tarro, panal, flores y mariposas. Teclado: Espacio o Intro cosecha; los botones del panel son accesibles con Tab.

## Paleta (`:root`)
`--sky` #bfe3f0 · `--meadow` #d9ecc0 · `--bg` #9fd3e6 · `--bg2` #f6e7b0 · `--honey` #f2a900 · `--amber` #9c4a00 · `--wax` #fff1c9 · `--olive` #3f5a22 · `--blossom` #fffdf6 · `--fg` #2b1a05 · `--mut` #6d5634 · `--acc` #f2a900

## Persistencia
Claves `OS.save/load` (localStorage `nexo.colmena.<clave>`): `state`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 8 logros:
  - `colmena_1` **Primera cosecha** — Cosecha tu primera miel del panal
  - `colmena_azahar` **Flor de azahar** — Florece el azahar, el guiño a Benicarló
  - `colmena_butterfly` **Cazamariposas** — Atrapa 10 mariposas doradas
  - `colmena_streak` **Apicultor constante** — Abre el tarro del día 7 días seguidos
  - `colmena_prestige` **Larga vida a la reina** — Enjambra por primera vez
  - `colmena_100` **Enjambre** — Reúne 100 abejas
  - `colmena_million` **Millonaria en miel** — Gana 1 M de monedas en total
  - `colmena_panal` **Marco completo** — Llena el marco con las 180 celdas del panal

## Ideas para escalar
- [ ] Temporadas del año reales: en primavera florece el azahar con bonus x2, en verano el girasol, en otoño el brezo (p. ej. del 15 de marzo al 15 de abril, 'Semana del azahar de Benicarló')
- [ ] Plagas y defensa: la avispa asiática aparece de vez en cuando y hay que tocarla antes de que robe miel (minijuego de reflejos de 10 s)
- [ ] Reinas coleccionables con rasgos (italiana: +néctar, carniola: +proceso, negra ibérica: resiste frío) que se consiguen al enjambrar
- [ ] Mercado dinámico: el precio de cada miel sube y baja durante el día y conviene vender en el pico (gráfica en el puesto)
- [ ] Decoración del colmenar con monedas: caminos de piedra, farolillos que se encienden de noche, bebedero con agua animada
- [ ] Ranking semanal de miel producida entre amigos (Supabase) y visitas a la loma de otros jugadores
- [ ] Recetas: combinar mieles para crear productos (turrón, hidromiel, jabón) que se venden mucho más caros
- [ ] Logros de temporada y un álbum de abejas: fotografiar con la cámara 3D a las abejas raras (abeja albina 1/500)
- [ ] Versión de marca para una miel local real: código QR del tarro que desbloquea una miel de la colección y un descuento
- [ ] Modo relajación: música generativa de zumbidos y campanas que suena según las flores del campo

## Registro de cambios
- 2026-09-24 · v1 creada (gama Premium: kit FX con bloom, partículas, tweens y audio; modelos en Blender 5.0, icono Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
