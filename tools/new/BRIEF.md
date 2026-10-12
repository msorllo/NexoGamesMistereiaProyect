# BRIEF · 5 apps PREMIUM 3D de NEXO (26–30)

Estás construyendo UNA de las 5 apps nuevas de NEXO: un lanzador de mini-apps web (ver `CLAUDE.md` en la raíz del proyecto, léelo entero primero).
Estas 5 son la nueva gama alta: tienen que parecer las más trabajadas visual y técnicamente de las 30, estar MUY animadas, con 3D realista y detallado, y enganchar ("una partida más").

Proyecto: `/home/claude/proj/nexo`. Blender 5.0 disponible como módulo Python en el contenedor: `python3 script.py` con `import bpy` (sin binario `blender`).

## Qué entregas (SOLO estos archivos, no toques ningún otro del proyecto)
1. `blender/scripts/b_<glb>.py` — modela TODOS los assets 3D de la app en Blender (bpy). Usa `blender/scripts/blib.py` (importa con `sys.path.insert(0, HERE)`), no lo modifiques; si necesitas helpers nuevos, defínelos dentro de tu script. Rutas relativas como los scripts existentes (mira `b_faro.py`, `b_caja.py` como referencia):
   `HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)` → escribe `ROOT/glb/<glb>.glb`, `ROOT/blend/<glb>.blend`, `ROOT/renders/<glb>.png`.
   - Cada asset = un objeto con nombre claro (se clona en la app con `FX.get('Nombre')`). Origen bien colocado con `join(..., origin=)`.
   - Materiales PBR cuidados (color, roughness, metallic, emisivos donde brille). Los colores de material se exportan al glTF: elige valores realistas.
   - Detalle real: biseles (`bevel`), subdivisión donde toque, desplazamiento para piedras/orgánicos, geometría con piezas (dientes de engranaje, vetas, etc.). Nada de "cubo con color". Pero vigila polígonos: GLB final ≤ 700 KB (comprueba `ls -la`). Usa `export_apply=True`.
   - Render del icono con Cycles (`render_icon` de blib, 256 px, 48–64 samples): composición bonita y reconocible de los assets, fondo del color de la app. Este PNG es el icono y el favicon de la app → que se lea a 64 px.
   - Ejecuta: `cd /home/claude/proj/nexo/blender/scripts && python3 b_<glb>.py` (tarda: Cycles en CPU). Ejecuta desde esa carpeta o con ruta absoluta, NUNCA desde /tmp/claude-0.
   - Mira el render (`Read` del PNG) y mejóralo hasta que se vea premium.
2. `src/apps/<NN>-<id>.html` — la app. Parte de `tools/templates/premium3d.html` (cópiala y sustituye `__ID__`, `__TITULO__`, la sección APP). El bloque FX (kit compartido) se copia TAL CUAL entre `/* ===== FX` y `/* ===== fin FX ===== */` (puedes ampliarlo solo al final de la sección APP con tus propias funciones, no editar FX).
3. `tools/new/<id>.json` — metadatos para que yo lo integre:
```json
{"manifest": {"id":"...","file":"NN-id.html","name":"...","cat":"3d ...","tag":"frase corta (≤ 48 caracteres)","bg":"#..","bg2":"#..","fg":"#..","acc":"#..","font":"'Fuente',fallback,serif","glb":"<glb>"},
 "appinfo": {"concept":"...","tech":"...","mechanics":["..."],"controls":"...","ideas":["... (mínimo 8 ideas concretas para escalar, con ejemplo)"]},
 "actions": [["wait",1500],["js","..."],["wait",800]]}
```
   `actions` = pasos del smoke test (tipos: click selector, key, wait ms, mouse x y, js expr, drag x1 y1 x2 y2). Deben ejercitar la mecánica principal (p. ej. forzar una victoria con JS) sin lanzar errores.

## Contrato NEXO (obligatorio, ver CLAUDE.md)
- `<html lang="es" data-app="<id>">`, `<title>`, sin `alert/confirm/prompt`, sin `localStorage` directo: usa `OS.load(k,def)` / `OS.save(k,v)`.
- `OS.xp(n,'motivo')` al conseguir cosas (valores 5–60 por acción importante, no spamear cada frame: agrupa).
- `OS.achieve('<id>_codigo','Nombre','Descripción')` con **literales** en el código (el build los extrae con regex `OS\.achieve\('([^']+)','([^']+)'(?:,'([^']*)')?`). 5–8 logros por app, variados (fácil, medio, difícil, secreto/curioso).
- Tres.js SOLO `three@0.147.0` desde `cdn.jsdelivr.net` (los scripts ya están en la plantilla). Fuentes solo de Google Fonts, SIEMPRE con fallback de sistema en el `font-family`.
- Responsive real hasta 390 px de ancho (móvil vertical): nada de UI solapada ni botones < 40 px. Controles táctiles + ratón (+ teclado si aplica).
- La app funciona sola (standalone, el build añade splash y favicon) y dentro de un iframe del lanzador.
- Colores de Three.js escritos en código: `FX.lin('#hex')` (convierte a lineal). Los del GLB ya vienen bien.
- Construye la escena DENTRO del callback de `FX.load(...)`.
- Nada de bucles que creen geometría/materiales cada frame (fuga de memoria). Reutiliza/pools. Si quitas objetos, `dispose` de geometrías creadas en runtime.
- `OS.save` no cada frame: al terminar acciones o como mucho cada pocos segundos.

## Listón de calidad "premium" (lo que diferencia estas 5)
- **Primer segundo**: al cargar, intro cinematográfica de cámara (1.5–2.5 s, `FX.tween` sobre la cámara o un objeto con easing `inOut`) + UI que entra con stagger (CSS transitions). Nada estático: siempre hay algo vivo (partículas ambientales, luz que respira, objetos que flotan, agua, polvo, luciérnagas…).
- **Juice en cada acción**: animación con easing (back/elastic), partículas `FX.burst`, sonido sintetizado `FX.tone/FX.noise` (cada app con su identidad sonora), `FX.buzz` en móvil, `FX.shake` en impactos. Botones con estados hover/active/transition.
- **Luz realista**: `scene.environment` ya trae RoomEnvironment (reflejos PBR). Añade luz clave con sombras suaves (`castShadow`, mapSize 2048, bias), rellenos de color, niebla atmosférica si encaja. Bloom calibrado para que SOLO brille lo emisivo (threshold alto ~.8–.9; strength .4–.9). Materiales físicos cuando aporten (`MeshPhysicalMaterial` con clearcoat, transmission, sheen, iridescence NO existe en r147 → no uses iridescence).
- **UI de revista**: tipografía con carácter (par display + texto), jerarquía clara, paneles de vidrio (`.glass`), números con `FX.count`, iconografía SVG inline propia (sin emojis como iconos principales). Paleta propia distinta de todas las demás apps. Microcopy en español con gracia.
- **Enganche** (sin trampas oscuras): bucle principal de 10–60 s, recompensa variable (rarezas, sorpresas), progreso siempre visible (barra/nivel), colección que se llena, metas a corto/medio/largo plazo, "casi lo consigues" (near-miss) explícito, racha diaria o motivo para volver mañana (recompensa diaria, algo que crece mientras no estás…). Botón de sonido on/off (`FX.muted`) y guardarlo.
- **Rendimiento**: 60 fps en un portátil normal. InstancedMesh para muchos objetos iguales. Sombras solo en lo que se ve. El kit baja calidad solo si va lento.
- **Accesibilidad**: `aria-label` en botones, `prefers-reduced-motion` (FX.reduced → reduce sacudidas/partículas), contraste suficiente, foco visible.

## Cómo probar (obligatorio antes de entregar)
```
cd /home/claude/proj/nexo
python3 tools/preview.py src/apps/NN-id.html <glb> /home/claude/scratch/<id>-desk.png --wait 4000 --js "expr JS;;WAIT1000;;SHOT:/home/claude/scratch/<id>-2.png;;otra expr"
python3 tools/preview.py src/apps/NN-id.html <glb> /home/claude/scratch/<id>-mob.png --mobile --wait 4000
```
- WebGL es por software (SwiftShader): va a 1–5 fps y las fuentes de Google no cargan (se ve el fallback). Es normal. Usa `WAIT` generosos para que las animaciones avancen, y funciones expuestas (globales) para forzar estados desde `--js`.
- Mira TODAS las capturas con `Read` (escritorio y móvil, varios estados: inicio, jugando, victoria/recompensa, colección). Corrige: solapes, textos cortados, cosas que se salen, objetos flotando mal, colores lavados, zonas negras, z-fighting, sombras raras, UI ilegible sobre el 3D.
- "ERRORES: ninguno" es requisito. También prueba con JS casos límite (repetir acción muy rápido, cambiar de nivel en mitad de animación, completar todo, estado guardado corrupto → `OS.save('x',null)` y recargar lógica).

## Al terminar
Responde con: ruta de los archivos, tamaño del GLB, lista de logros, 3 capturas que mejor representen la app (rutas), bugs conocidos (si queda alguno) y qué harías después. Sé honesto: si algo no ha quedado bien, dilo.

## Recordatorios de estilo (de CLAUDE.md)
- NO repetir fuentes ya usadas (tabla "Apps y estilos" de CLAUDE.md). Nada de Inter ni Space Grotesk. Sin emojis como iconos.
- Evitar el look "hecho con IA": crema+serif+terracota, degradado morado→azul, todo centrado con esquinas iguales.
- Usa exactamente las fuentes y paleta que te indico en tu ficha (ya están comprobadas para no chocar con las otras 29 apps).
