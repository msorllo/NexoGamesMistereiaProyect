# Tourbillon

> Engrana el calibre y haz latir el tiempo

| Campo | Valor |
|---|---|
| Archivo | `src/apps/26-tourbillon.html` (66 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `tourbillon` / `tourbillon` |
| `<title>` | Tourbillon |
| Categorías | 3d mente juegos |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader + kit FX premium (EffectComposer, UnrealBloom, partículas, tweens, audio) |
| Fuentes | Michroma, Sora |
| Splash | fondo `#0c0f14` → `#1b2230`, texto `#eef1f5`, acento `#3d6bff` |

## Concepto
Puzle de alta relojería en 3D: montas ruedas dentadas reales sobre los ejes de una platina para llevar la energía del barrilete hasta el escape, que debe girar en el sentido de la flecha. Al acertar, el calibre late: volante oscilando, áncora balanceándose y tic-tac.

## Cómo está hecha
Three.js r147 + kit FX (bloom, partículas, tweens, audio sintetizado) + modelos Blender con engranajes de dientes reales (GLB cuantizado con KHR_mesh_quantization, se descuantiza al cargar). Generador de calibres por semilla con solución garantizada (cadena constructiva + ejes señuelo + ruedas fijas pavonadas + ejes trampa que forman triángulos de bloqueo) y verificación por grafo de engrane (BFS con relación de dientes y sentido). Todas las ruedas giran con fase de engrane exacta (θB = φ + π + π/nB − (θA − φ)·nA/nB); con victoria, el tren avanza a golpes de escape sincronizados con el volante.

## Assets 3D (Blender)
- Script: `blender/scripts/b_tourbillon.py` (usa `blib.py`) → exporta `blender/glb/tourbillon.glb`, guarda `blender/blend/tourbillon.blend` y renderiza `blender/renders/tourbillon.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- 12 calibres + calibre del día (semilla = fecha) con racha
- Bandeja limitada de ruedas S/M/L (12/18/24 dientes)
- Choques si los dientes no encajan; bloqueo si dos ruedas se empujan en sentidos opuestos
- Sentido obligatorio del escape (near-miss: '¡llega pero gira al revés!')
- Estrellas por colocaciones vs objetivo y sin choques; pista = máximo 2 estrellas
- Vitrina con 12 relojes (uno por calibre) que marcan la hora real
- Complicaciones desbloqueables: fase lunar (18★) y jaula de tourbillon (30★)

**Controles:** Toca/clic en un eje para montar la rueda seleccionada (o quitarla). 1/2/3 eligen tamaño, Z deshace. Arrastra para orbitar la cámara.

## Paleta (`:root`)
`--bg` #0c0f14 · `--bg2` #1b2230 · `--fg` #eef1f5 · `--acc` #3d6bff · `--acc2` #7d9bff · `--gold` #d6b36a · `--ruby` #e0224f · `--mut` #8a93a3

## Persistencia
Claves `OS.save/load` (localStorage `nexo.tourbillon.<clave>`): `st`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 8 logros:
  - `tourbillon_secret` **Contratiempo** — Hiciste girar el escape al revés cinco veces
  - `tourbillon_1` **Primer latido** — Hiciste latir tu primer calibre
  - `tourbillon_3s` **Cronometría** — Cinco calibres con tres estrellas
  - `tourbillon_all` **Maestro relojero** — Completaste los doce calibres
  - `tourbillon_nojam` **Mano de cirujano** — Seis calibres sin un solo choque ni pista
  - `tourbillon_daily` **Puntualidad suiza** — Tres días seguidos con el calibre del día
  - `tourbillon_moon` **Fase lunar** — Desbloqueaste la complicación de fase lunar
  - `tourbillon_cage` **El torbellino** — Desbloqueaste la jaula de tourbillon

## Ideas para escalar
- [ ] Ruedas compuestas (rueda + piñón en el mismo eje) para retos de relación: 'el segundero debe dar 1 vuelta por minuto'
- [ ] Modo cronómetro: resolver calibres contrarreloj con ranking online (Supabase)
- [ ] Editor de calibres y compartir por enlace con la semilla codificada
- [ ] Más complicaciones visibles en la vitrina: cronógrafo, repetición de minutos con sonido real, calendario perpetuo
- [ ] Personalizar el reloj de la vitrina (esfera, agujas, correa) con estrellas como moneda
- [ ] Lupa de relojero: zoom macro al pulsar prolongado sobre una rueda, con profundidad de campo
- [ ] Sonido: tic-tac grabado o sintetizado por calibre (18.000 / 21.600 / 28.800 alternancias)
- [ ] Modo 'restauración': un calibre desmontado desordenado que hay que reordenar pieza a pieza
- [ ] Retos semanales temáticos (Ginebra, Glashütte…) con esferas exclusivas
- [ ] Exportar un render del reloj conseguido como fondo de pantalla

## Registro de cambios
- 2026-09-24 · v1 creada (gama Premium: kit FX con bloom, partículas, tweens y audio; modelos en Blender 5.0, icono Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
