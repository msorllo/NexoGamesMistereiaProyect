# 29 · CAIRN — equilibrio de piedras (id `cairn`, archivo `29-cairn.html`, glb `cairn`)
Tagline: "Apila piedras junto al río. Respira. Una más."
Tipo: arcade zen de apilar (categorías "3d bienestar juegos").
Fuentes: 'Shippori Mincho' (display) + 'Zen Kaku Gothic New' (texto). Fallbacks: 'Shippori Mincho','Hiragino Mincho ProN',serif / 'Zen Kaku Gothic New',system-ui,sans-serif.
Paleta: niebla #cdd6d2 → #7f948d (bg #56675f, bg2 #aebcb6), musgo #4d6b45, pizarra #3a4148, agua #2d6b6e, farol cálido #ffb865 (acc), fg #f3f5f2.
Ambiente: orilla de un río de montaña al amanecer con niebla, lluvia fina opcional, luciérnagas al anochecer, bambú y un farol de piedra japonés (tōrō) encendido. Realismo: piedras de río húmedas (roughness bajo .25–.4 con variación, clearcoat), agua con ondas animadas y reflejo (plano con vértices animados y material físico), musgo, gotas de lluvia (líneas/partículas), anillos en el agua cuando cae una gota o una piedra.

## Mecánica (bucle 20–90 s)
- Una piedra cuelga/oscila sobre la torre (vaivén lateral pendular + ligera rotación). Toca/clic/espacio para soltarla → cae con gravedad, aterriza sobre la de abajo.
- Física simplificada determinista (SIN motor de física): cada piedra tiene un "radio de apoyo" y centro de masas. Al aterrizar, comprueba si el centro de masas COMBINADO de la pila desde esa piedra hacia arriba cae dentro del radio de apoyo de la inferior (en cada nivel). Si no → la torre se desploma: animación de caída de las piedras superiores (rotan y caen con rebotes hacia el agua, salpicaduras de partículas y anillos, sonido de piedras + agua). Si el offset es pequeño → "PERFECTO" (se centra suavemente, combo); intermedio → la piedra se tambalea (animación de balanceo amortiguado) y se queda.
- Ritmo: cada piedra más alta el vaivén se acelera un poco; formas y tamaños varían (planas, redondas, alargadas); a partir de cierta altura viento (partículas de hojas) que desplaza el vaivén.
- Cámara sube suavemente con la torre.
- Puntuación: altura en piedras + bonus por perfectos seguidos (racha visible "Calma ×4"). Récord personal; la cámara al terminar hace una panorámica de toda la torre (foto final), con opción "Otra vez".
- Recompensa variable: aleatoriamente (≈8 %) aparece una piedra RARA para apilar (Jade verde translúcido, Obsidiana negra brillante, Geoda con cristales morados emisivos, Cuarzo rosa, Ámbar con insecto, Meteorito) → si la apilas bien se añade a tu COLECCIÓN "Piedras del río" (12 especies, con ficha y descripción poética). Las raras dan más puntos.
- Modos: "Río" (normal), "Tormenta" (desbloqueas a 15 piedras: lluvia fuerte, viento racheado, x2 puntos), "Respira" (sin fallo: la piedra baja con el ritmo de respiración guiada 4-7-8, texto "Inspira… exhala…"; para relajarse, da XP por minutos).
- Motivo para volver: "Piedra del día" (una rara garantizada en la primera partida del día) + racha diaria.
- XP: al terminar partida (altura·2 + perfectos, máx 60), piedra rara +10, 5 minutos de Respira +15.
- Logros: cairn_1 "Primer cairn" (5 piedras), cairn_15 "Torre del monje" (15), cairn_30 "Tocar las nubes" (30), cairn_perfect "Pulso de agua" (racha 8 perfectos), cairn_rare "Buscador de piedras" (primera rara), cairn_all "Río completo" (12 especies), cairn_breathe "Respira hondo" (10 min en Respira).

## Assets Blender
`Piedra1`…`Piedra8` (ocho cantos rodados distintos: esferas/cubos subdivididos, escalados y con displace suave; aplanados arriba/abajo para apilar; material gris pizarra con variación de color por piedra), raras `Jade`, `Obsidiana`, `Geoda` (exterior rugoso + interior con cristales puntiagudos emisivos morados), `Cuarzo`, `Ambar`, `Meteorito` (y hasta 12 si puedes: `Lapis`, `Pirita` (cubos metálicos), `Turquesa`, `Malaquita` (bandas), `Opalo`, `Fosil` (con espiral de amonita)), `Roca base` (roca grande plana en la orilla donde empieza la torre), `Orilla` (terreno con displace y guijarros), `Toro` (farol de piedra con ventana emisiva cálida), `Bambu` (varios tallos con nudos y hojas), `Helecho`, `Musgo` (montículos), `Hoja` (para el viento).
Render icono: cairn de 5 piedras con farol detrás en niebla, fondo #aebcb6.

## Escena
- Cámara de lado ligeramente elevada, la torre centrada; el río de fondo con niebla (Fog exponencial) y montañas como siluetas (planos en capas con colores de la niebla → profundidad atmosférica). Intro: cámara se desliza por el río hasta la roca base.
- Luz: amanecer suave (hemisférica + sol bajo cálido con sombras) y el farol con PointLight cálida; si juegas de noche (hora real 21–7) escena nocturna con luciérnagas (partículas verdes-amarillas con bloom).
- Sonido: agua corriendo continua (ruido filtrado lowpass modulado), clic de piedra (tono corto grave + ruido), campanilla suave en perfecto (pentatónica ascendente con la racha).
- UI mínima y elegante: altura grande en Shippori Mincho vertical/horizontal, racha, botón colección (hoja con 12 huecos: silueta si no la tienes), selector de modo, sonido.
- Exponer `window.C={drop(), dropPerfect(), state(), setMode(m)}` para test.
