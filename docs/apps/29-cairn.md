# Cairn

> Apila piedras junto al río. Respira. Una más.

| Campo | Valor |
|---|---|
| Archivo | `src/apps/29-cairn.html` (51 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `cairn` / `cairn` |
| `<title>` | Cairn |
| Categorías | 3d bienestar juegos |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader + kit FX premium (EffectComposer, UnrealBloom, partículas, tweens, audio) |
| Fuentes | Shippori Mincho, Zen Kaku Gothic New |
| Splash | fondo `#56675f` → `#aebcb6`, texto `#f3f5f2`, acento `#ffb865` |

## Concepto
Arcade zen de apilar piedras en la orilla de un río de montaña con niebla. Una piedra oscila sobre la torre y tú eliges el momento de soltarla. Si el centro de masas de lo que queda encima sale del apoyo, la torre se desploma al agua.

## Cómo está hecha
Three.js r147 + kit FX + modelos Blender (8 cantos rodados, 12 piedras raras, roca base, orilla, farol tōrō, bambú, helecho, musgo, hoja). Física determinista sin motor: apoyo por raycast sobre la malla real de la piedra de abajo (sin interpenetraciones), estabilidad por centro de masas acumulado nivel a nivel y derrumbe con caída balística, rebotes, salpicaduras y anillos en el agua. Río con olas por vértices, lluvia con LineSegments, luciérnagas de noche (hora real), montañas en capas con perspectiva atmosférica y audio ambiente de río sintetizado.

## Assets 3D (Blender)
- Script: `blender/scripts/b_cairn.py` (usa `blib.py`) → exporta `blender/glb/cairn.glb`, guarda `blender/blend/cairn.blend` y renderiza `blender/renders/cairn.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- Soltar en el momento justo: perfecta (se centra sola) o tambaleo amortiguado
- Racha de calma: cada perfecta seguida suma más puntos y sube la escala pentatónica
- Derrumbe por centro de masas fuera del apoyo (cualquier nivel de la torre)
- 8,5 % de piedras raras (12 especies) que van a la colección 'Piedras del río'
- Piedra del día: una rara garantizada en la primera partida del día y racha diaria
- Modos: Río, Tormenta (se desbloquea con 15; lluvia, viento y puntos ×2) y Respira (4-7-8 sin fallos)
- Viento desde 12 piedras: desplaza el vaivén y trae hojas
- De noche (21-7 h) la escena cambia: farol encendido y luciérnagas

**Controles:** Toca/clic en la escena o pulsa Espacio para soltar la piedra. En Respira no hay que tocar: sigue el ritmo.

## Paleta (`:root`)
`--mist` #cdd6d2 · `--mist2` #aebcb6 · `--moss` #4d6b45 · `--slate` #3a4148 · `--water` #2d6b6e · `--lamp` #ffb865 · `--fg` #f3f5f2 · `--ink` #1d2622

## Persistencia
Claves `OS.save/load` (localStorage `nexo.cairn.<clave>`): `st`

## Integración con NEXO
- 3 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 8 logros:
  - `cairn_perfect` **Pulso de agua** — Ocho piedras perfectas seguidas
  - `cairn_rare` **Buscador de piedras** — Encontraste tu primera piedra rara
  - `cairn_all` **Río completo** — Reuniste las doce piedras raras
  - `cairn_1` **Primer cairn** — Una torre de cinco piedras
  - `cairn_15` **Torre del monje** — Quince piedras sin caer
  - `cairn_30` **Tocar las nubes** — Treinta piedras apiladas
  - `cairn_storm` **Ojo de la tormenta** — Diez piedras en plena tormenta
  - `cairn_breathe` **Respira hondo** — Diez minutos en el modo Respira

## Ideas para escalar
- [ ] Foto final de la torre descargable (canvas.toDataURL) con marco de la app para compartir
- [ ] Ranking semanal de altura con la misma semilla de piedras para todos
- [ ] Estaciones del año: cerezos en primavera, hojas rojas en otoño, nieve en invierno según la fecha
- [ ] Piedras con propiedades: pirita pesa el doble, ópalo es resbaladiza, geoda tiene el centro de masas desplazado
- [ ] Modo 'desafío': una forma objetivo (silueta) que hay que imitar con las piedras
- [ ] Sonido binaural de río y lluvia más rico, con cuencos tibetanos en las perfectas
- [ ] Respira conectada al reloj: recordatorio diario y estadística de minutos por semana
- [ ] Coleccionables de temporada (piedras de playa de la Costa Azahar como guiño local)
- [ ] Vibración háptica graduada según el tambaleo en móviles
- [ ] Modo cooperativo por turnos en el mismo dispositivo

## Registro de cambios
- 2026-09-24 · v1 creada (gama Premium: kit FX con bloom, partículas, tweens y audio; modelos en Blender 5.0, icono Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
