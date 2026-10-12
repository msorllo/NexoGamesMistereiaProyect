# NEXO · 30 apps web en un lanzador

Proyecto de Marco (Mistereia, "El míster de la IA", Benicarló). NEXO es un lanzador con estética de sistema operativo que reúne 30 apps web independientes: juegos 3D, estudios creativos, bienestar, productividad y retos mentales. Las apps comparten XP, niveles, logros y retos diarios.

- Idioma de la interfaz y de los textos: **español de España**.
- Idioma para hablar con Marco: español, informal, directo y práctico. Dile claramente si algo está mal, es contraproducente o se contradice, y propón ideas de mejora que no haya pedido.
- Estado: v3 (20 apps 2D + 5 apps 3D + 5 apps 3D **Premium** con kit FX). Todo compila y las 30 pasan `tools/test.py` sin errores. `dist/Nexo.html` ≈ 7,9 MB.
- La versión publicada es el Artifact "Nexo" en claude.ai (se publica `dist/nexo-artifact.html`).

## Encargo original (requisitos que siguen vigentes)
1. Cada app es **única**: no se repiten categoría ni juego.
2. Cada app tiene **estilo visual y paleta propios**: no se repiten fuentes ni paletas entre apps.
3. **Variedad** de tipos: juegos, 3D, creatividad, música, bienestar, finanzas, hábitos y mente.
4. Los juegos llevan **metas**: niveles, misiones, estrellas, rangos, coleccionables o rachas. No se repite el mismo sistema en todas.
5. Cada app tiene **título**, **favicon propio** (el icono en la pestaña) y **pantalla de arranque (splash)**, como al abrir una app de móvil.
6. Todo funciona en **un único HTML** (`dist/Nexo.html`) y además cada app **suelta** en `dist/apps/`.
7. Las apps 3D usan **modelos creados en Blender**. El usuario pidió hacerlo con el MCP de Blender; en la v2 se usó Blender 5.0 (bpy) en la nube porque el MCP local no estaba arrancado. Desde Claude Code, el MCP de Blender ya puede usarse directamente (ver "Flujo Blender").
8. Evitar el look "hecho con IA": nada de crema + serif + terracota, degradado morado→azul, Inter o Space Grotesk, emojis como marcadores ni todo centrado con `rounded-lg` en todo.

## Estructura
```
CLAUDE.md                ← este archivo
docs/apps/NN-id.md       ← ficha de cada app: qué tiene, cómo está hecha, logros, claves, ideas y registro de cambios
src/os.js                ← helper compartido window.OS (xp, achieve, save, load)
src/launcher.html        ← plantilla del lanzador (se rellena en el build; no tiene <html>/<body>)
src/apps/NN-id.html      ← código fuente de cada app (HTML autocontenido). Las 3D llevan el marcador __GLB__
blender/scripts/blib.py  ← utilidades de modelado (materiales, primitivas, join, lathe, export, render de icono)
blender/scripts/b_*.py   ← un script por app 3D: modela → exporta GLB → guarda .blend → renderiza icono
blender/{blend,glb,renders}/
tools/manifest.py        ← lista de apps (nombre, categorías, eslogan, colores del splash, fuente, icono SVG)
tools/build.py           ← build: inyecta GLB, genera dist/apps/*, dist/Nexo.html y dist/nexo-artifact.html
tools/test.py            ← smoke test con Playwright y capturas en tools/shots/
tools/preview.py         ← vista previa de UNA app sin build (inyecta os.js + GLB), captura y errores; admite --mobile y --js "expr;;WAIT800;;SHOT:ruta.png"
tools/templates/premium3d.html ← plantilla de app Premium con el kit FX (copiar para apps nuevas)
tools/new/               ← BRIEF.md (listón de calidad Premium), spec-*.md (diseño de cada app 26-30) y *.json (metadatos de alta)
tools/actions.json       ← acciones del test por app
tools/appinfo.py         ← textos de diseño de cada app (concepto, mecánicas, ideas)
tools/gen_docs.py        ← regenera docs/apps/*.md (conserva "Registro de cambios" y "Notas")
vendor/three@0.147.0/    ← copia local de Three.js, solo para los tests sin internet
dist/                    ← salida (no editar a mano)
```

## Comandos
```bash
pip install playwright pillow && playwright install chromium   # una vez
python tools/build.py          # compila todo
python tools/test.py           # prueba las 30 apps (o: python tools/test.py 21-faro 07-tiza)
python tools/gen_docs.py       # regenera las fichas de docs/apps
# Blender (modelos de una app 3D; Blender 4.2+ o `pip install bpy`):
blender -b -P blender/scripts/b_faro.py      # o: python blender/scripts/b_faro.py con bpy instalado
```
**Regla:** después de tocar una app → `build` → `test` → actualizar su `docs/apps/*.md` (registro de cambios) → `gen_docs` si cambiaste mecánicas o logros.

## Contrato de una app (obligatorio)
- `<html lang="es" data-app="ID">`: el `data-app` da nombre a las claves de guardado (`nexo.ID.*`). Ojo: Arrecife tiene id `arrecife` en el manifiesto pero `data-app="acuario"`; no lo cambies o se pierde el progreso guardado.
- Usar solo `window.OS`, que lo inyecta el build (no lo incluyas en el fuente):
  - `OS.xp(n, 'motivo')` → suma XP en NEXO (el lanzador limita a 1-300 por llamada).
  - `OS.achieve('codigo', 'Nombre', 'Descripción')` → logro único. **Escríbelo con comillas simples y literales**: el build lo detecta por regex para el catálogo de logros.
  - `OS.save(k, v)` / `OS.load(k, def)` → localStorage con try/catch y copia en memoria. Nunca uses localStorage directamente.
- Debe funcionar dentro de un iframe `srcdoc` (el lanzador) y como archivo suelto.
- Sin `alert`, `confirm` ni `prompt` (el visor de Artifacts no los muestra). El audio solo arranca tras un gesto del usuario.
- Responsive hasta 390 px **sin scroll horizontal** (el test lo vigila).
- Arrancar con contenido visible: datos de ejemplo marcados como EJEMPLO, nunca pantallas vacías.
- Fuentes de Google Fonts, siempre con fallback (`'Fuente',Georgia,serif`, etc.).
- Librerías externas **solo** desde cdnjs.cloudflare.com o cdn.jsdelivr.net/npm (política CSP de los Artifacts). Three.js va fijado a `three@0.147.0` (la última versión con `examples/js` sin módulos).

## Apps 3D (21-25)
- Plantilla: scripts de three.min.js + GLTFLoader (+ OrbitControls / RoomEnvironment), luego `const GLB="__GLB__";`. Se carga con `new THREE.GLTFLoader().parse(b64(GLB), '', cb)`, se guardan los hijos por nombre en `LIB` y se clonan con `get('Nombre')`. **Crea la escena dentro del callback** (usar `get()` antes rompe la app; ya pasó en Yacimiento).
- Colores asignados por código: `color.set(hex).convertSRGBToLinear()` (r147 sin gestión de color); si no, salen lavados.
- Renderer: `outputEncoding=sRGB`, ACESFilmic, sombras PCFSoft. Ajusta la exposición por app; con la luz por defecto todo sale sobreexpuesto.
- Pesos actuales de los GLB: faro 230 KB, golf 411, acuario 362, caja 190, excava 452. `dist/Nexo.html` pesa unos 2,6 MB (límite del Artifact: 16 MB).

## Apps Premium (26-30) · kit FX
- Parten de `tools/templates/premium3d.html`. Entre `/* ===== FX` y `/* ===== fin FX ===== */` va el kit compartido, **idéntico en las 5** (si lo mejoras, cópialo en todas):
  - `FX.init({bg,exposure,bloom:[fuerza,radio,umbral],fog})` → renderer ACES + sRGB + sombras PCFSoft, RoomEnvironment, EffectComposer (RenderPass → UnrealBloomPass → GammaCorrection) con MSAA x4.
  - `FX.tween(obj,{prop:v},dur,'out|inOut|back|elastic',done)`, `FX.burst(pos,{count,color,speed,gravity,life})` (pool de 1400 partículas aditivas), `FX.shake(a)`, `FX.buzz(ms)`, `FX.tone/FX.noise` (audio sintetizado), `FX.count(el,n)`, `FX.lin('#hex')`.
  - `FX.load(cb)` carga el GLB y rellena `FX.LIB`; `FX.get('Nombre')` clona. Calidad adaptativa (baja pixelRatio y luego quita bloom si va lento; `?hq` la desactiva). Pausa el bucle con la pestaña oculta.
- Cada app expone una API global para tests y depuración: `T` (Tourbillon), `F` (Forja), `H` (Colmena), `C` (Cairn), `Q` (Quilate). Muchas tienen `ff(seg)` para avanzar el tiempo (útil en SwiftShader, que va a 1-3 fps).
- Fila "Premium" del lanzador para `new=2`. El manifiesto lleva `glb=` y el build inyecta el GLB por ese campo.
- Pesos GLB: tourbillon 673 KB, forja 682, colmena 627, cairn 686, quilate 1006 (el más pesado: gemas facetadas + halos; candidato a Draco/cuantización).
- Nombres con espacio en Blender llegan a three con guion bajo (`Piedra afilar` → `Piedra_afilar`).

## Flujo Blender (MCP)
1. Arranca Blender → panel N → addon MCP → *Start server* (puerto 9876). Si no está arrancado, las herramientas `execute_blender_code` fallan con "Cannot connect to Blender at localhost:9876".
   - **Ojo (24-09-2026):** en el PC de Marco el addon es *BlenderMCP de ahujasid* pero el servidor MCP configurado en Claude es otro (herramientas `execute_blender_code`, `get_blendfile_summary`…). Conecta al 9876 pero se cuelga 60 s. Solución: en `claude_desktop_config.json` usar `"blender": {"command": "uvx", "args": ["blender-mcp"]}` (el servidor que corresponde a ese addon), o instalar en Blender el addon del servidor actual.
2. Ejecuta el script de la app (`blender/scripts/b_<app>.py`) desde el MCP o con `blender -b -P`.
3. Convenciones de modelado: low-poly y estilizado, con un material Principled por cada color con nombre legible (el código busca algunos por nombre: `Farol barco`, `Nogal`, `Tutú`). Un objeto unido por asset, con el nombre exacto que usa la app. El origen se pone donde hace falta el pivote (la tapa de la caja va en la bisagra).
4. El icono de la app es el render Cycles (`blender/renders/<app>.png`, 256 px). El manifiesto lo convierte a JPEG embebido.
5. Tras exportar: `python tools/build.py && python tools/test.py 2X-app`.

## Lanzador (src/launcher.html)
- Lee el manifiesto, el catálogo de logros y las fuentes de las apps desde `<script type="application/json">` que rellena el build.
- Al abrir una app: splash con icono, nombre en la fuente de la app, eslogan y barra de carga; cambia `document.title` y el favicon; crea el iframe `srcdoc` con el helper OS inyectado.
- Recibe `postMessage({nexo:1,type:'xp'|'ach',...})` **solo** del iframe activo.
- Niveles: el nivel `l` necesita `150 + (l-1)·100` XP. Títulos: Curioso, Explorador, Aventurero, Maestro de apps, Leyenda de Nexo.
- 3 retos diarios elegidos por día de entre 6; +40 XP cada uno y +60 por completar los tres.
- Logros propios de NEXO: explorador, turista, coleccionista, nivel 5, nivel 10 y día redondo.
- Fila "Nuevas en 3D" para las apps con `new=1`. En "Todo", esas apps no se repiten en la cuadrícula.

## Cómo añadir una app nueva
1. Crea `src/apps/26-id.html` cumpliendo el contrato, con paleta y fuentes que no se usen ya (revisa la tabla de abajo).
2. Añade su entrada a `tools/manifest.py`: icono SVG 64×64 o `_img('render')` si es 3D.
3. Añade su texto de diseño en `tools/appinfo.py` y sus acciones de test en `tools/actions.json`.
4. Ejecuta build → test → gen_docs. Actualiza "Estado" en este archivo.

## Apps y estilos (para no repetir)
| # | App | Tipo | Fuentes | Look |
|---|---|---|---|---|
|01|Neón Runner|carreras pseudo-3D|Audiowide, Chakra Petch|outrun morado/rosa/sol|
|02|Planetario 3D|exploración|Cormorant Garamond, IBM Plex Mono|espacio negro, oro pálido|
|03|La Cripta|laberinto raycaster|Pirata One, Crimson Pro|piedra y antorcha|
|04|Voxel Isla|constructor isométrico|Fredoka|cielo pastel|
|05|Jardín Focus|pomodoro|Young Serif, Karla|salvia y arcilla|
|06|Beat Lab|caja de ritmos|Archivo Black, DM Mono|gris Teenage Engineering + naranja|
|07|Tiza|mecanografía|Cabin Sketch, Patrick Hand|pizarra verde|
|08|Arcana|memoria tarot|Cinzel Decorative, EB Garamond|azul noche, oro, carmesí|
|09|Bitácora|diario de ánimo|Instrument Serif, Manrope|gris frío, azul|
|10|Hucha|ahorro|Rubik Mono One, Work Sans|neo-brutalismo amarillo|
|11|Flujo|arte generativo|Syne, Figtree|galería blanca|
|12|Cerebro Bauhaus|trivial|Big Shoulders Display, Outfit|Bauhaus primarios|
|13|Ladrillos|breakout|Chango, Nunito|Memphis rosa|
|14|Eco|Simon|Comfortaa, Quicksand|abisal bioluminiscente|
|15|Gesta|RPG de hábitos|Press Start 2P, VT323|Game Boy verde|
|16|Plano|física dibujada|Share Tech Mono, Architects Daughter|plano técnico azul|
|17|La Coctelera|mezclas|Limelight, Josefin Sans|bar clandestino, neón|
|18|Tono|puzle de color|Lexend|blanco con degradados|
|19|Reflejo|reflejos|Barlow Condensed, Barlow|suizo blanco y rojo|
|20|Mochi|mascota|Mochiy Pop One, Baloo 2|kawaii melocotón|
|21|Faro|puzle de luz 3D|DM Serif Display, Nunito Sans|noche marina, oro|
|22|Minigolf Cósmico|golf 3D|Russo One, Exo 2|violeta espacial, neón|
|23|Arrecife|acuario 3D|Lilita One, Mulish|aguamarina y coral|
|24|Caja de Música|música 3D|Italiana, Libre Franklin|burdeos, nogal y oro|
|25|Yacimiento|excavación 3D|Alfa Slab One, IBM Plex Sans Condensed|ocre desierto|
|26|Tourbillon|puzle de relojería 3D|Michroma, Sora|antracita, acero pavonado, rubí|
|27|Forja|herrería de timing + botín|Grenze Gotisch, Alegreya Sans SC|hollín y brasa|
|28|Colmena|idle incremental 3D|Fraunces, Hanken Grotesk|día de miel, cielo y prado|
|29|Cairn|apilar piedras zen|Shippori Mincho, Zen Kaku Gothic New|niebla de río, musgo, farol|
|30|Quilate|configurador de joyas + encargos|Bodoni Moda, Jost|estudio gris perla, esmeralda|

## Problemas conocidos / pendientes
- Premium sin validar en GPU real: todo se ha probado con SwiftShader (1-3 fps). Revisar fps, sonido y transiciones en un navegador de verdad antes de enseñarlas.
- Forja: suelo algo de bloque en primer plano, el fuelle se lee poco, el agua del barril sin reflejo real. En SwiftShader las transiciones CSS se desactivan (se detecta y se quitan solo ahí).
- Quilate: el diamante es un espejo facetado sobre un entorno de estudio propio (la transmisión real salía lechosa sobre fondo claro). En móvil la tarjeta de clienta tapa parte de la joya.
- Las 10 apps 3D necesitan internet (Three.js por CDN). Pendiente valorar incrustar Three.js (≈600 KB por app) solo en la versión descargable.
- Las pruebas usan WebGL por software (SwiftShader): el splash del lanzador puede tardar más que en un navegador real. Las capturas de los 3D pueden salir más claras que en una GPU.
- Los niveles de Faro se generan por semilla: siempre son los mismos, y cambiar `gen()` cambia todos los niveles (y deja sin sentido las estrellas guardadas).
- Sin backend: el progreso vive en el navegador de cada dispositivo. Para rankings o sincronización haría falta, por ejemplo, Supabase.

## Ideas globales para escalar
- Ranking online y perfil sincronizado (Supabase).
- Animaciones hechas en Blender (peces, bailarina, mar) exportadas en el GLB.
- Versión de marca "El míster de la IA" como demo comercial (hostelería: Coctelera, Hucha; fidelización: Gesta, Mochi).
- PWA instalable (manifest + service worker) cuando salga del entorno Artifact.

## Web pública (site/) · añadido 2026-10-12
- `python tools/build.py` genera además `site/`: `index.html` (~160 KB, lanzador SIN apps embebidas) y `site/apps/ID.html` (fuente de cada app con el GLB inyectado, sin OS ni splash; el lanzador los pide con `fetch` y los pone en el iframe `srcdoc` como antes). Si `#sources` está vacío (`{}`) se usa este modo; el Artifact y `dist/Nexo.html` siguen con todo embebido.
- Optimización del lanzador: CSS de fuentes con `media=print`+`onload` (no bloquea el primer render), precarga de la app en `pointerenter/touchstart`, `body.playing` oculta aurora y ruido mientras hay una app abierta (la animación con `blur(90px)` seguía gastando GPU detrás del juego).
- Publicación: Vercel, proyecto `nexo-games-mistereia` → https://nexo-games-mistereia.vercel.app (`cd site && npx vercel deploy --prod --yes --name nexo-games-mistereia`). GitHub Pages no vale: el repo es privado. NO activar `cleanUrls` (redirige `/apps/x.html` y añade un salto por app). Repo: msorllo/NexoGamesMistereiaProyect. Auditoría de filtraciones hecha: sin claves ni tokens; las rutas personales de `tools/new/nova/_wf/` están en `.gitignore`.
- La raíz de git accidental está en el directorio de usuario: este proyecto tiene su propio repo dentro de `nexo/`.
