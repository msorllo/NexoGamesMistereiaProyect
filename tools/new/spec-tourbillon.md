# 26 · TOURBILLON — puzle de relojería (id `tourbillon`, archivo `26-tourbillon.html`, glb `tourbillon`)
Tagline: "Engrana el calibre y haz latir el tiempo"
Tipo: puzle mecánico 3D (categorías "3d mente juegos").
Fuentes: 'Michroma' (display, títulos y números grandes) + 'Sora' (texto). Fallbacks: 'Michroma',Eurostile,sans-serif / 'Sora',system-ui,sans-serif.
Paleta: fondo antracita #0c0f14 → #1b2230 (bg / bg2 del splash), rodio/acero #c9ced6, acero pavonado (azul de tornillos) #2446a8, rubí #d0103a, oro solo como detalle #d6b36a (acc = #3d6bff azul pavonado luminoso para UI). fg #eef1f5.
Ambiente: platina de reloj de alta relojería vista en macro, bajo luz de estudio. Muy realista: metales pulidos con reflejos del RoomEnvironment, perlage/Côtes de Genève sugeridas (anillos concéntricos o bandas en la platina: geometría o textura CanvasTexture procedural en la app), rubíes que brillan (emisivo sutil + bloom), tornillos pavonados.

## Mecánica
- Tablero = platina circular con EJES (pivotes con rubí) en posiciones fijas. Hay un BARRIL (fuente de energía, engranaje fijo que gira) y un ESCAPE (rueda de escape + volante/áncora, objetivo). Tienes una bandeja de ruedas: tamaños S/M/L (radios primitivos 0.5 / 0.75 / 1.0 con 12/18/24 dientes; relación de giro = inversa de dientes).
- Toca un eje vacío → coloca la rueda seleccionada en la bandeja (o cicla S→M→L→vacío si tocas repetidamente). Dos ruedas engranan si la distancia entre ejes = rA + rB (tolerancia ±0.04). Si se solapan (dist < rA + rB − 0.04) → "choque": la rueda nueva rebota con animación y sonido metálico, no se coloca.
- La energía se propaga desde el barril por el grafo de engranes (BFS): cada rueda gira en sentido alterno y velocidad = ω_padre · (dientes_padre / dientes_propios). Si en un ciclo hay conflicto de sentido → BLOQUEO (todo el tren conectado tiembla y se para, near-miss explícito "El tren se ha bloqueado: dos ruedas se empujan en sentidos opuestos").
- Victoria: el escape recibe energía girando en el sentido indicado (flecha en el suelo) → el volante empieza a oscilar (animación sinusoidal de balancín con espiral), tic-tac audible (FX.tone/noise cortos alternos), las agujas del reloj de la vitrina avanzan, destello de bloom en rubíes, partículas doradas.
- Niveles: 12 calibres. Generador por semilla con solución garantizada: construye una cadena desde el barril eligiendo tamaños y ángulos, pone ejes en las posiciones resultantes, añade ejes señuelo (que o no encajan o dan sentido incorrecto), bandeja con exactamente las ruedas necesarias + 1–2 extra en niveles altos. Verifica que el estado inicial vacío no gana y que la solución gana (como en Faro, ver src/apps/21-faro.html función gen()). Algunos niveles piden además "relación objetivo" (el escape debe girar a X vueltas/min: se muestra velocímetro) → requiere escoger tamaños concretos.
- Estrellas: 3 si lo resuelves sin choques y con ≤ par colocaciones; 2 con ≤ par+2; 1 al resolver.
- Progreso/colección: cada calibre resuelto añade un RELOJ a tu VITRINA (panel colección): 12 relojes con nombre ("Calibre 01 · Ginebra", …) y una esfera distinta (color de esfera y agujas variadas generadas). En la vitrina el reloj montado gira en 3D con sus agujas marcando la hora REAL. Complicaciones desbloqueables con estrellas: fase lunar (18★), tourbillon giratorio (30★) — se ven en el reloj de la escena principal.
- Motivo para volver: "Calibre del día" (nivel generado con la fecha como semilla) con bonus de XP y racha diaria.
- XP: al resolver (20 + nivel·5 + estrellas·5), calibre del día +30.
- Logros (literales): tourbillon_1 "Primer latido", tourbillon_3s "Cronometría" (5 calibres a 3★), tourbillon_all "Maestro relojero" (12 calibres), tourbillon_daily "Puntualidad suiza" (3 días seguidos de calibre del día), tourbillon_nojam "Mano de cirujano" (6 calibres sin un solo choque), tourbillon_moon "Fase lunar" (desbloquear), tourbillon_secret "Contratiempo" (hacer girar el escape al revés… 5 veces seguidas; secreto divertido).

## Assets Blender (nombres de objeto exactos)
- `Platina` (disco grueso con biselado, rebajes concéntricos, agujeros; material acero rodiado mate satinado roughness .35 metallic 1)
- `Eje` (pivote: chatón dorado + rubí `Rubí` emisivo tenue + tornillo pavonado con ranura)
- `RuedaS`, `RuedaM`, `RuedaL` (engranajes REALES: dientes modelados (12/18/24), llanta, 4–6 radios curvos/cruz de Malta calados, buje; latón dorado pulido metallic 1 roughness .22) — el origen en el centro del eje; plano de giro XY de Blender (→ XZ en three).
- `Barril` (tambor con dientes, tapa con espiral grabada, más grande: radio 1.1)
- `Escape` (rueda de escape con dientes en gancho) + `Volante` (anillo con 4 tornillos de inercia + brazo) + `Ancora` (horquilla con paletas rubí). Origen en su eje.
- `Puente` (puente de acero pulido con biseles anglage brillantes, tornillos pavonados) para decorar sobre ejes.
- `Caja` (caja de reloj completa: bisel, carrura, corona estriada, asas) y `Esfera` (disco de esfera con índices aplicados) y `AgujaH`, `AgujaM`, `AgujaS` para la vitrina.
- Render de icono: rueda L + escape + rubíes sobre fondo #1b2230, luz lateral cálida, macro.

## Escena
- Cámara cenital ligeramente inclinada sobre la platina (OrbitControls limitados, zoom y giro suave; en móvil que la platina entre entera). Intro: cámara baja en espiral desde lejos hasta el calibre (2 s).
- Luz: DirectionalLight cálida con sombras suaves + 2 luces de relleno frías (azules) + un "anillo de luz" (PointLights) que se refleja en los metales. Polvo en suspensión en el haz (partículas lentas). Al ganar: flash y chispas doradas.
- Animaciones constantes: ruedas conectadas girando, volante oscilando cuando hay victoria, rubíes que "respiran", reflejos que se mueven (la luz orbita muy lentamente).
- UI: arriba izquierda título + "Calibre 07"; arriba derecha contador de estrellas totales y botón sonido; abajo bandeja de ruedas (3 botones grandes con icono SVG de engranaje y número restante) + botón deshacer + reiniciar; panel Vitrina (botón) que se abre como hoja inferior en móvil / lateral en escritorio, con la galería de relojes (miniaturas renderizadas como tarjetas con nombre y estado bloqueado).
- Exponer globales para test: `window.T={solve(), level(n), state()}` (solve coloca la solución y gana).
