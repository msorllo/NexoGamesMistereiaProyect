# Quilate

> Diseña joyas de lujo y cumple cada encargo

| Campo | Valor |
|---|---|
| Archivo | `src/apps/30-quilate.html` (61 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `quilate` / `quilate` |
| `<title>` | Quilate |
| Categorías | 3d creatividad |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader + kit FX premium (EffectComposer, UnrealBloom, partículas, tweens, audio) |
| Fuentes | Bodoni Moda, Jost |
| Splash | fondo `#e6e8ec` → `#ffffff`, texto `#121316`, acento `#0f5c4a` |

## Concepto
Atelier de joyería en 3D con look de foto de producto: configuras anillos, colgantes y pendientes (metal, gema, talla, quilates, engaste, aro pavé y grabado) con precio en tiempo real, y en modo Encargos atiendes clientas con historia, presupuesto y pistas que puntúan de 0 a 100 y suben la reputación del atelier.

## Cómo está hecha
Three.js r147 + kit FX (bloom, partículas, tweens, audio sintetizado). Modelos en Blender (b_quilate.py, bmesh): gemas con facetas reales (brillante, oval, pera, corazón, princesa, esmeralda escalonada), cabezas de garras ajustadas a cada talla con BVH para que abracen la piedra sin atravesarla, halos con posiciones de melee exportadas como extras glTF (userData.q), chatones, aro comfort-fit y pavé, asa, gancho, eslabón, pedestal, busto, soporte, ciclorama y vitrina. En la app: diamante como espejo facetado sobre un entorno de estudio propio (PMREM con tiras de luz), gemas de color con transmisión física, destellos de 4 puntas, alejandrita que cambia de color al girar, cadena en catenaria con InstancedMesh y grabado como textura dentro del aro.

## Assets 3D (Blender)
- Script: `blender/scripts/b_quilate.py` (usa `blib.py`) → exporta `blender/glb/quilate.glb`, guarda `blender/blend/quilate.blend` y renderiza `blender/renders/quilate.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- Atelier libre: 3 piezas, 4 metales, 8 gemas, 6 tallas, 0,5–3 ct, 4 engastes, aro pavé y grabado
- Precio en tiempo real
- Encargos con historia, requisitos y pistas; satisfacción 0–100 con desglose y reseña
- Reputación → 5 niveles (Taller de barrio → Maison) que desbloquean gemas, tallas y engastes
- Clienta VIP del día (reputación ×2)
- Mi vitrina: hasta 12 diseños guardados

**Controles:** Pestañas del panel; arrastrar para orbitar y rueda/pellizco para zoom; Entregar en modo Encargos.

## Paleta (`:root`)
`--pearl` #eceef1 · `--white` #fafbfc · `--ink` #121316 · `--ink2` #4a4f58 · `--mut` #8a909a · `--em` #0f5c4a · `--em2` #1b7a63 · `--line` #d7dae0

## Persistencia
Claves `OS.save/load` (localStorage `nexo.quilate.<clave>`): `st`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 7 logros:
  - `quilate_rich` **Pieza de museo** — Diseñaste una joya de más de 100.000 €
  - `quilate_1` **Primer encargo** — Entregaste tu primera joya
  - `quilate_100` **Clienta enamorada** — Satisfacción del 100 %
  - `quilate_vip` **Trato VIP** — Cinco clientas VIP satisfechas
  - `quilate_alex` **Camaleón** — Desbloqueaste la alejandrita
  - `quilate_maison` **Maison** — Tu atelier alcanzó el nivel Maison
  - `quilate_vitrina` **Coleccionista** — Doce diseños en tu vitrina

## Ideas para escalar
- [ ] Probador AR sobre la mano (WebXR o MediaPipe Hands)
- [ ] Exportar ficha del diseño a PDF con render y presupuesto (demo para joyerías reales)
- [ ] Comparador de dos diseños lado a lado
- [ ] Certificado simulado (color, pureza) que cambie precio y aspecto
- [ ] Clientes recurrentes con aniversarios
- [ ] Temporadas: San Valentín, bodas, Navidad
- [ ] Más piezas: pulsera tenis, gemelos, tiara
- [ ] Reto contrarreloj: tres encargos en 90 s
- [ ] Vista macro animada del grabado

## Registro de cambios
- 2026-09-24 · v1 creada (gama Premium: kit FX con bloom, partículas, tweens y audio; modelos en Blender 5.0, icono Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
