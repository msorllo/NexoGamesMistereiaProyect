"""Información de diseño de cada app (lo que no se puede extraer del código).
tools/gen_docs.py combina esto con datos extraídos del HTML y regenera docs/apps/*.md.
Si cambias una app, actualiza aquí su entrada y ejecuta:  python tools/gen_docs.py
"""
INFO = {
'runner': dict(
 concept='Carreras arcade pseudo-3D estilo outrun de 1986: autopista infinita con curvas y colinas, sol de rayas, palmeras y tráfico neón.',
 tech='Canvas 2D con proyección de segmentos (técnica clásica de "pseudo 3D road"). 2400 segmentos en bucle, sprites dibujados por código (coches, palmeras, monedas).',
 mechanics=['Esquivar coches (3 escudos)', 'Monedas: +50 puntos y recargan nitro', 'Nitro con ESPACIO (doble toque en móvil): 34% del depósito, x1,45 de velocidad', 'Cada 3.000 m un sector nuevo más rápido y con otro tono de color', '5 misiones por carrera (monedas, sector 3, 1.500 m sin chocar, nitro x3, 320 km/h)'],
 controls='← → / A D para girar, ESPACIO nitro. Móvil: mitades izquierda/derecha de la pantalla.',
 ideas=['Selector de coches desbloqueables con monedas', 'Túneles y noche/lluvia por sector', 'Fantasma de tu mejor carrera', 'Banda sonora synthwave generada con WebAudio', 'Ranking online']),
'planetario': dict(
 concept='Sistema solar 3D navegable como cuaderno de exploración: visitas los 8 planetas, lees datos reales y respondes preguntas.',
 tech='Canvas 2D con proyección 3D propia (cámara orbital yaw/pitch, esferas con degradado y terminador, anillos, 900 estrellas). Sin librerías.',
 mechanics=['Visitar planetas (+15 XP la primera vez)', 'Pregunta del observatorio por planeta (+20 XP)', 'Tour guiado automático', 'Control de velocidad del tiempo'],
 controls='Arrastrar para orbitar, rueda para zoom, clic en planeta.',
 ideas=['Pasar a Three.js con texturas reales (NASA dominio público)', 'Lunas principales (Ío, Europa, Titán)', 'Escala real conmutable', 'Misiones de sondas históricas (Voyager, Cassini)']),
'cripta': dict(
 concept='Laberinto 3D en primera persona (estilo Wolfenstein) a la luz de una antorcha: recoge llaves doradas y escapa por la puerta sellada.',
 tech='Raycaster DDA sobre ImageData a baja resolución (pixel art escalado), texturas procedurales 64x64 (piedra con musgo, puerta, suelo), sprites de llaves con z-buffer, laberinto generado por backtracking + bucles extra.',
 mechanics=['7 niveles que crecen de tamaño', '1-5 llaves por nivel colocadas en callejones sin salida', 'Estrellas por tiempo (par = 20 + nivel·18 s)', 'Almas = puntuación acumulada', 'Minimapa (tecla M)'],
 controls='WASD / flechas, arrastrar ratón para girar, M minimapa. Móvil: cruceta táctil.',
 ideas=['Enemigos (fantasmas) con IA simple', 'Trampas y palancas', 'Antorcha que se consume (tiempo)', 'Tiendas entre niveles']),
'voxel': dict(
 concept='Constructor isométrico de una isla flotante con bloques; las misiones desbloquean materiales nuevos.',
 tech='Canvas 2D isométrico con 4 rotaciones de vista, orden de pintado por profundidad, picking por polígono de cara visible, mundo en diccionario "x,y,z".',
 mechanics=['11 tipos de bloque (5 iniciales, 6 desbloqueables)', '5 misiones: 10 bloques, altura 10, 3 árboles, lago, 120 bloques', 'Modo borrar, rotar vista, día/noche', 'El mundo se guarda'],
 controls='Clic coloca en la cara señalada, clic derecho o modo ⌫ borra, R rota, E borrar.',
 ideas=['Exportar la isla a GLB para Blender', 'Criaturas que pasean', 'Plantillas y compartir por código', 'Ciclo de agua/cascadas']),
'jardin': dict(
 concept='Pomodoro que hace crecer una planta mientras te concentras; si abandonas, se marchita. Las plantas completadas viven en tu invernadero.',
 tech='Árboles recursivos procedurales en canvas (parámetros por especie: ángulo, profundidad, colores), semilla aleatoria por sesión, girasol con dibujo propio.',
 mechanics=['Sesiones de 15/25/50 min', 'Semillas como moneda: comprar 6 especies', 'Racha diaria de sesiones', 'Modo demostración (1 min = 1 s)'],
 controls='Elegir duración, escribir tarea, Plantar y empezar / Rendirse.',
 ideas=['Descansos cortos/largos automáticos', 'Estadísticas semanales', 'Sonidos ambiente (lluvia, bosque)', 'Jardín compartido por equipo']),
'beatlab': dict(
 concept='Caja de ritmos de 16 pasos y 8 pistas con estética Teenage Engineering y retos de productor que desbloquean kits.',
 tech='WebAudio: síntesis de bombo, caja, hi-hats, palmas, tom, bajo y pluck; programador con look-ahead de 120 ms; osciloscopio/espectro con AnalyserNode.',
 mechanics=['4 patrones (A-D) y 4 presets (House, Hip-hop, Dembow, Techno)', 'Pistas melódicas con 5 alturas por paso', 'Knobs de tempo, swing y volumen', '6 retos y 4 kits (808, Lo-fi, Chiptune, Cinta)'],
 controls='Clic en pasos, clic en el nombre de pista para silenciar, arrastrar knobs, ESPACIO play/stop.',
 ideas=['Exportar WAV con OfflineAudioContext', 'Cadena de patrones (canción)', 'Samples subidos por el usuario', 'Modo "jam" con teclado']),
'tiza': dict(
 concept='Juego de mecanografía en una pizarra verde: las palabras caen y hay que escribirlas antes de que toquen la línea.',
 tech='DOM absoluto para las palabras, canvas para el polvo de tiza, normalización sin tildes para escribir sin acentos, input oculto para teclado móvil.',
 mechanics=['4 bancos de palabras por dificultad', 'Nivel cada 10 palabras, 3 vidas, combo x1-x5', 'Palabras especiales: amarilla limpia todo, azul congela, rosa x3', 'Misiones: nivel 5, combo 15, 40 PPM, 3 rosas'],
 controls='Teclado. Backspace borra, Escape limpia.',
 ideas=['Modo frases/refranes', 'Idiomas (inglés, valenciano)', 'Modo profesor con listas propias', 'Duelo a pantalla partida']),
'arcana': dict(
 concept='Juego de memoria con los 22 arcanos mayores del tarot; cada pareja encontrada entra en tu grimorio con su lectura.',
 tech='Cartas con flip 3D en CSS, símbolos SVG propios por arcano, grid que se adapta al alto de la pantalla.',
 mechanics=['5 tiradas (6 a 15 parejas)', 'Estrellas por movimientos', 'Grimorio coleccionable de 22 cartas'],
 controls='Clic en cartas.',
 ideas=['Modo contrarreloj', 'Arcanos menores como expansión', 'Tirada diaria con mensaje', 'Animación de barajado']),
'bitacora': dict(
 concept='Diario de ánimo de 30 segundos al día con "año en píxeles", curva de 30 días y patrones detectados.',
 tech='Blobs SVG animados con CSS path morph, gráfica SVG, correlación simple de etiquetas con el ánimo. Arranca con datos de EJEMPLO marcados que se borran al registrar el primer día.',
 mechanics=['5 ánimos, energía 1-10, 10 etiquetas, nota', 'Racha y medallas 3/7/30 días', 'Insights: etiqueta que más sube/baja el ánimo, mejor día de la semana'],
 controls='Elegir ánimo → Guardar el día.',
 ideas=['Recordatorio diario (notificación)', 'Exportar CSV', 'Gráfico por etiqueta', 'Frases de reflexión según patrón']),
'hucha': dict(
 concept='Metas de ahorro en estilo neo-brutalista con un bote donde caen monedas con física.',
 tech='Física de círculos (verlet simple) en canvas; nº de monedas proporcional al progreso; confeti en hitos.',
 mechanics=['Varias metas con color propio', 'Hitos 25/50/75/100% con confeti', 'Pronóstico de fecha según ritmo', '6 insignias', 'Metas de ejemplo que se reinician con el primer ingreso real'],
 controls='+5/+20/+50/+100, cantidad libre, Sacar.',
 ideas=['Ingresos recurrentes', 'Reto de las 52 semanas', 'Metas compartidas en pareja', 'Divisas']),
'flujo': dict(
 concept='Estudio de arte generativo: partículas que siguen un campo de ruido Perlin y dejan trazos; la obra se cuelga en una galería.',
 tech='Perlin 2D propio, 200-4000 partículas, simetría espejo/caleidoscopio, remolinos al hacer clic, miniaturas JPEG en localStorage.',
 mechanics=['6 paletas, 5 parámetros', 'Obra del día (paleta + simetría) +50 XP', 'Galería de 12 obras'],
 controls='Clic en lienzo = remolino (Shift invierte). Panel lateral.',
 ideas=['Exportar a alta resolución', 'Animación en bucle (GIF/WebM)', 'Imprimir póster (servicio externo)', 'Más campos (curl noise, atractores)']),
'bauhaus': dict(
 concept='Trivial de cultura general con composición Bauhaus (formas primarias animadas) y rangos.',
 tech='48 preguntas en 4 categorías, temporizador de 15 s, multiplicador por racha, composiciones geométricas en DOM.',
 mechanics=['Rondas de 10', 'Puntos por rapidez x racha', 'Comodines: 50/50, +10 s, saltar', 'Rangos: Aprendiz → Genio Bauhaus', '4 misiones'],
 controls='Clic o teclas 1-4.',
 ideas=['Ampliar a 300 preguntas en JSON aparte', 'Modo duelo', 'Preguntas con imagen', 'Categoría local (Baix Maestrat)']),
'ladrillos': dict(
 concept='Breakout de colores estilo Memphis con power-ups y 6 muros.',
 tech='Canvas 2D, colisiones AABB por sub-pasos, ladrillos de 2 golpes, acero indestructible, bombas.',
 mechanics=['Power-ups: pala ancha, multibola, láser, lento, vida', 'Combo sin tocar la pala', '6 niveles desbloqueables'],
 controls='Ratón/dedo mueve la pala; clic/ESPACIO lanza o dispara.',
 ideas=['Editor de niveles', 'Jefe final', 'Modo infinito', 'Tabla de récords']),
'eco': dict(
 concept='Simon dice con 4 medusas bioluminiscentes; cada acierto te hunde 10 m en el océano.',
 tech='Canvas con medusas animadas por código, zonas de profundidad que oscurecen el fondo, peces linterna que aparecen con la profundidad, notas con armónicos.',
 mechanics=['Modos: Clásico, Espejo (al revés, 80 m), Corriente rápida (120 m)', 'Zonas: iluminada → fosa hadal', 'Récord por modo'],
 controls='Clic en medusas o teclas 1-4.',
 ideas=['Modo zen sin fallo', 'Más criaturas coleccionables', 'Secuencias musicales reconocibles']),
'gesta': dict(
 concept='Tus hábitos diarios convertidos en un RPG pixel art con paleta Game Boy: cumplir hábitos ataca a jefes.',
 tech='Sprites a partir de mapas de caracteres, monstruos procedurales simétricos por semilla, reinicio diario con penalización de vida por hábitos no hechos.',
 mechanics=['Hábitos con dificultad (XP, oro, daño)', '5 jefes (la procrastinación y compañía)', 'Niveles del héroe', 'Tienda: espada, casco, capa, escudo, mascota, corona', 'Racha diaria'],
 controls='Marcar/desmarcar hábitos, añadir nuevos, comprar equipo.',
 ideas=['Hábitos semanales', 'Recordatorios', 'Clases (mago, guerrero)', 'Modo grupo/party']),
'plano': dict(
 concept='Puzle de física sobre un plano técnico azul: dibujas rampas con tinta limitada para llevar bolas al recipiente.',
 tech='Física de círculos contra segmentos con sub-pasos, zonas donde no se puede dibujar, cajetín de plano real.',
 mechanics=['8 láminas', 'Tinta limitada; estrellas según tinta usada', 'Vigas existentes y zonas prohibidas'],
 controls='Arrastrar para dibujar, Soltar bolas, Deshacer, Borrar.',
 ideas=['Muelles y ventiladores', 'Editor de niveles', 'Materiales (goma, hielo)', 'Repetición de la solución']),
'coctelera': dict(
 concept='Bar clandestino: sirves medidas en un vaso, agitas y descubres 12 recetas (3 sin alcohol) mientras atiendes pedidos.',
 tech='Vaso SVG con capas de líquido, mezcla de color ponderada, burbujas animadas, detección de receta por conjunto de ingredientes.',
 mechanics=['17 ingredientes', 'Pedidos de clientes con pista', 'Propinas y racha', 'Recetario secreto'],
 controls='Clic en botellas, Hielo, Agitar, Vaciar, Servir.',
 ideas=['Proporciones exactas', 'Guarniciones', 'Versión para hostelería real (carta del bar del cliente)', 'Modo contrarreloj']),
'tono': dict(
 concept='Puzle de degradados: reordena fichas de color hasta recomponer la transición entre 4 esquinas.',
 tech='Interpolación bilineal de 4 colores, fichas fijas como referencia, intercambio por clic o arrastre con animación elástica.',
 mechanics=['12 niveles de 4x5 a 10x12', 'Estrellas por movimientos vs objetivo', 'Ver solución 2 s (+3 movimientos)'],
 controls='Clic en dos fichas o arrastrar.',
 ideas=['Modo daltónico', 'Niveles diarios', 'Degradados de marcas/fotos']),
'reflejo': dict(
 concept='Entrenador de reflejos con diseño suizo: precisión, reacción y rastreo, con rangos de Bronce a Leyenda.',
 tech='DOM + requestAnimationFrame, medición con performance.now(), rating combinado de los tres modos.',
 mechanics=['Precisión: 30 dianas que encogen', 'Reacción: 5 intentos, media en ms', 'Rastreo: 15 s siguiendo la diana', 'Rangos por rating'],
 controls='Ratón/dedo. Escape vuelve al menú.',
 ideas=['Modo daltónico y sonido', 'Historial y gráfica de progreso', 'Retos diarios']),
'mochi': dict(
 concept='Mascota virtual kawaii con necesidades, minijuego de atrapar estrellas, tienda de sombreros y fondos, y evolución.',
 tech='Mascota en SVG con expresiones según ánimo, degradación de stats con el tiempo (también estando fuera, limitada), minijuego en canvas.',
 mechanics=['Hambre, alegría, energía, limpieza', 'Comer (3 comidas), jugar, dormir, bañar', 'Cariño → niveles (evoluciona en 3 y 6)', 'Tienda: 5 sombreros, 4 fondos', 'Nombre editable (doble clic)'],
 controls='Botones de cuidado, clic para acariciar.',
 ideas=['Más minijuegos', 'Accesorios animados', 'Visitas de otros mochis', 'Notificación cuando tiene hambre']),
'faro': dict(
 concept='Puzle de luz 3D nocturno: giras espejos para que el haz del faro ilumine todos los barcos.',
 tech='Three.js r147 + modelos Blender (faro, espejo, barco, roca, casilla, boya). Niveles generados por semilla con garantía de solución (camino constructivo + verificación por trazado). Mar con vértices animados.',
 mechanics=['8 noches (5x5 a 8x8, hasta 7 espejos, 3 barcos)', 'Objetivo de giros = espejos mal orientados al inicio', 'Estrellas por giros', 'El haz atraviesa barcos y lo bloquean rocas'],
 controls='Clic/toque en espejos; arrastrar para orbitar la cámara.',
 ideas=['Prismas que dividen el haz', 'Espejos fijos y móviles', 'Niebla que cambia', 'Editor de niveles']),
'golf': dict(
 concept='Minigolf en plataformas flotantes entre asteroides con setas de neón, portales y brazos giratorios.',
 tech='Three.js + modelos Blender (bola, bandera, hoyo, asteroides, bumper, portal, planeta, ovni, tee). Hoyos definidos en ASCII; física 2D sobre la rejilla con colisión por celdas, bumpers circulares y brazo giratorio.',
 mechanics=['6 hoyos con par (17)', 'Tiro tipo tirachinas con fuerza', 'Tarjeta de puntuación y récord', 'Reintentar hoyo suma golpe'],
 controls='Arrastrar y soltar; ⟲ ⟳ rotan la cámara.',
 ideas=['Más hoyos (JSON)', 'Rampas y alturas', 'Multijugador por turnos local', 'Pieles de bola']),
'arrecife': dict(
 concept='Acuario 3D que cuidas: das de comer, compras peces y decoración, limpias el cristal frotando y cumples misiones.',
 tech='Three.js + modelos Blender (5 peces, corales, alga, cofre, castillo, concha, roca). Cáusticas con canvas animado, suciedad del cristal en canvas borrable con destination-out, peces con steering hacia objetivos/comida.',
 mechanics=['Perlas: por comer, cofre (cada 3 min), pasivo y al volver', 'Tienda de 5 peces y 7 decoraciones (colocar en la arena)', '6 misiones', 'Luz nocturna'],
 controls='Clic en agua para echar comida, modo limpiar para frotar, arrastrar para orbitar.',
 ideas=['Crías de peces', 'Plantas que crecen', 'Temperatura/pH simplificados', 'Foto del acuario para compartir']),
'caja': dict(
 concept='Caja de música 3D: clavas púas en el tambor para recrear melodías; la bailarina gira y la tapa-espejo la refleja.',
 tech='Three.js + modelos Blender (caja, tapa con bisagra, tambor, púa, peine, manivela, bailarina) + RoomEnvironment para metales. Síntesis de caja de música con armónicos y reverb por convolución. Partitura 16x15 sincronizada con el tambor.',
 mechanics=['4 canciones objetivo (Estrellita, Martinillo, Oda a la alegría, Cumpleaños feliz) + composición libre', 'Validación por orden de notas (sin acordes)', 'Cada canción desbloquea un acabado (cerezo, ébano, marfil, lacado)'],
 controls='Clic en la partitura o en el cilindro 3D, Dar cuerda, tempo.',
 ideas=['Tambor de 32 pasos', 'Compartir melodía por código', 'Más canciones populares españolas', 'Grabar a WAV']),
'excava': dict(
 concept='Excavación arqueológica por vóxeles: retiras tierra capa a capa y extraes fósiles y reliquias para tu museo.',
 tech='Three.js InstancedMesh (9x9x6 vóxeles) + modelos Blender (cráneo, amonites, trilobites, ámbar, ánfora, moneda, geoda, pico, pincel). Miniaturas del museo renderizadas en tiempo real a dataURL.',
 mechanics=['45 de energía por expedición', 'Pico (1 golpe; capas profundas 2) — si golpea una pieza, sale dañada (50%)', 'Pincel: extrae intacto si la pieza está expuesta o sondea caliente/templado/frío', 'Radar: 3 usos, marca columna', 'Destellos cuando una pieza queda expuesta', '3 yacimientos desbloqueables y museo de 7 piezas'],
 controls='Elegir herramienta y clic en bloques; arrastrar para orbitar.',
 ideas=['Piezas multi-bloque (esqueleto completo)', 'Restauración como minijuego', 'Más yacimientos (Atapuerca, íbero)', 'Excavar por capas con cortes transversales']),

 'tourbillon': {'concept': 'Puzle de alta relojería en 3D: montas ruedas dentadas reales sobre los ejes de una platina para llevar la energía del barrilete hasta el escape, que debe girar en el sentido de la flecha. Al acertar, el calibre late: volante oscilando, áncora balanceándose y tic-tac.', 'tech': 'Three.js r147 + kit FX (bloom, partículas, tweens, audio sintetizado) + modelos Blender con engranajes de dientes reales (GLB cuantizado con KHR_mesh_quantization, se descuantiza al cargar). Generador de calibres por semilla con solución garantizada (cadena constructiva + ejes señuelo + ruedas fijas pavonadas + ejes trampa que forman triángulos de bloqueo) y verificación por grafo de engrane (BFS con relación de dientes y sentido). Todas las ruedas giran con fase de engrane exacta (θB = φ + π + π/nB − (θA − φ)·nA/nB); con victoria, el tren avanza a golpes de escape sincronizados con el volante.', 'mechanics': ['12 calibres + calibre del día (semilla = fecha) con racha', 'Bandeja limitada de ruedas S/M/L (12/18/24 dientes)', 'Choques si los dientes no encajan; bloqueo si dos ruedas se empujan en sentidos opuestos', "Sentido obligatorio del escape (near-miss: '¡llega pero gira al revés!')", 'Estrellas por colocaciones vs objetivo y sin choques; pista = máximo 2 estrellas', 'Vitrina con 12 relojes (uno por calibre) que marcan la hora real', 'Complicaciones desbloqueables: fase lunar (18★) y jaula de tourbillon (30★)'], 'controls': 'Toca/clic en un eje para montar la rueda seleccionada (o quitarla). 1/2/3 eligen tamaño, Z deshace. Arrastra para orbitar la cámara.', 'ideas': ["Ruedas compuestas (rueda + piñón en el mismo eje) para retos de relación: 'el segundero debe dar 1 vuelta por minuto'", 'Modo cronómetro: resolver calibres contrarreloj con ranking online (Supabase)', 'Editor de calibres y compartir por enlace con la semilla codificada', 'Más complicaciones visibles en la vitrina: cronógrafo, repetición de minutos con sonido real, calendario perpetuo', 'Personalizar el reloj de la vitrina (esfera, agujas, correa) con estrellas como moneda', 'Lupa de relojero: zoom macro al pulsar prolongado sobre una rueda, con profundidad de campo', 'Sonido: tic-tac grabado o sintetizado por calibre (18.000 / 21.600 / 28.800 alternancias)', "Modo 'restauración': un calibre desmontado desordenado que hay que reordenar pieza a pieza", 'Retos semanales temáticos (Ginebra, Glashütte…) con esferas exclusivas', 'Exportar un render del reloj conseguido como fondo de pantalla']},
 'forja': {'concept': "Taller de herrero de noche en 3D. Cada arma es una partida de 30-45 s: calientas el lingote en la fragua con el fuelle, lo golpeas en el yunque al ritmo de un anillo, lo templas en el barril y la fragua 'tira los dados' de la rareza. Encargos diarios con clientes, un encargo real con recompensa doble y una armería que llenar (4 armas x 4 rarezas).", 'tech': "Modelos de Blender (b_forja.py): yunque con cuerno, tocón con anillos, fragua de ladrillo con boca en arco, dovelas, base de sillares y campana, brasas, fuelle articulado (base, cuero y tapa con origen en la bisagra), barril de duelas con aros y agua, martillo, tenazas, daga, espada, hacha, mandoble (hoja con material 'Hoja'), lingote, pared de tablones, ventana, soporte, piedra de afilar, antorcha, cubo y suelo de losas (GLB 682 KB). En Three.js: la hoja tiene un morph target generado en tiempo real (lingote -> hoja) que avanza con cada golpe; material de metal con color de cuerpo negro (blackbody) + oxidación + vetas emisivas del meteorito + barrido de pulido por shader; texturas procedurales de hierro, acero, damasco y meteorito; brasas con ruido 3D animado en el emisivo; llamas por shader fbm; chispas como estelas LineSegments con gravedad y rebote en yunque y suelo; humo y vapor con sprites reutilizados; polvo en el haz de luna; foco de la fragua con sombras 2048 que sale por la boca; haz de revelación por shader y órbita de cámara; audio 100 % sintetizado (fragua, fuelle, yunque, siseo del temple, coro legendario).", 'mechanics': ['Encargos diarios: 3 en el tablón (uno real con recompensa doble), se reponen al cumplirlos hasta 7 al día; forja libre con arma y metal a elegir', 'Calentar: mantén el fuelle; la temperatura sube con retardo, hay ventana óptima por metal y si te pasas el metal se quema (−20 % de calidad)', 'Golpear: anillo de ritmo que se cierra sobre el metal; perfecto/bueno/fallo, combo de perfectos, el metal se enfría con cada golpe y puedes recalentar', 'Templar: mantén para sumergir y suelta en la franja azul; vapor, ondas y siseo', "Revelación: ruleta de rareza (común, rara, épica, legendaria) ponderada por la calidad y el metal, con 'casi' explícito", 'Favor de la fragua: cada arma no legendaria suma 1; a 20 la siguiente es legendaria garantizada', 'Armería: 16 huecos (tipo x rareza) con siluetas; toca un arma para ver su historia', 'Progresión: monedas para desbloquear metales (Acero, Damasco, Meteorito) y armas (Espada, Hacha, Mandoble), nivel de herrero con títulos y bonus', 'Racha diaria: la primera forja del día paga +50 %'], 'controls': 'Ratón/táctil: mantén el botón Fuelle, toca el metal (o cualquier punto) para golpear, mantén Templar. Teclado: espacio (fuelle / golpe / templar), Enter (al yunque), R (recalentar), Esc (cerrar).', 'ideas': ["Temporadas de encargos: un 'Torneo de Morella' semanal con un cliente jefe que pide una espada ≥90 de damasco y da un trofeo único para la armería", 'Grabados: tras la revelación, trazar una runa con el dedo sobre la hoja (reconocimiento de gesto simple) que añade un efecto de aura (fuego, escarcha, rayo)', 'Afilado en la piedra de afilar como minijuego opcional: mantener la hoja en el ángulo correcto sube el Filo hasta +10', "Aprendiz automático: contratar un aprendiz que forja dagas comunes mientras no estás (motivo para volver: '3 dagas listas')", "Aleaciones: combinar dos lingotes en el horno (hierro + meteorito = 'Acero estelar') con ventana de temperatura doble", 'Mercado dinámico: el precio de cada tipo de arma cambia por día y hay que decidir si vender o guardar', 'Colección de empuñaduras y pomos (cosméticos) que caen como botín raro y se ven en la armería', 'Modo desafío diario con semilla compartida: mismo encargo para todos y ranking de calidad (necesita backend, p. ej. Supabase)', 'Clientes con historia: un cliente recurrente vuelve con cartas y encargos encadenados (la capitana Urraca asciende si su espada es épica)', 'Exportar la ficha del arma legendaria como imagen para compartir (canvas del render + nombre + estadísticas)']},
 'colmena': {'concept': 'Idle incremental en un diorama 3D: un colmenar sobre una loma flotante con campo de flores (margaritas, girasol, romero, lavanda, brezo y azahar, el guiño a Benicarló). Cientos de abejas vuelan entre flores y colmenas, el panal del marco crece celda a celda y se llena de miel translúcida. Luz de día real: la paleta del cielo cambia con la hora (mañana dorada, mediodía, tarde de miel, noche con luciérnagas).', 'tech': 'Three.js r147 + modelos de Blender (b_colmena.py: colmena Langstroth, marco con lámina de cera, celda hexagonal y celda de miel, abeja < 800 tris con alas aparte, seis flores, naranjo, tarro, caja, ahumador, apicultor, loma flotante con faldón de tierra y roca, moneda, mariposa, valla, nube, hierba). Abejas con 2 InstancedMesh (cuerpo multimaterial + alas que aletean por escala) y trayectorias Bézier con ruido; hierba y flores instanciadas con balanceo de viento en el vertex shader (dirección coherente en mundo); miel MeshPhysicalMaterial con transmisión; cielo con shader de degradado y entorno PMREM generado del propio cielo; sombras suaves que solo se recalculan cuando algo cambia; economía pura aislada en el bloque ECO (sanear estado, costes 1,12–40^n, ganancias offline, prestigio) que se puede simular en Node.', 'mechanics': ['Néctar -> miel -> monedas: las abejas traen néctar, las colmenas y el panal lo procesan; si un lado va corto se marca el cuello de botella', 'Toca una colmena, el tarro o el botón Cosechar para vender la miel (8 % de cosecha dorada ×3)', 'Toca un macizo de flores: las abejas cercanas vuelan a él y todo produce ×3 durante 10 s (recarga 20 s)', 'Siete mejoras con coste exponencial y compra ×1 / ×10 / Máx: abejas, colmenas (caen y rebotan), panal extra (celdas nuevas en el marco), seis flores con su miel, apicultor con ahumador (cosecha solo), reina seleccionada (×2) y puesto en el mercado (precio ×1,4)', 'Mariposa dorada cada 1–3 min: frenesí ×5, monedas, enjambre errante o, rara vez, jalea real', 'Hitos: tres a la vez, primero una lista pensada para los 10 primeros minutos y luego procedurales', 'Tarro del día con racha de 7 días (el séptimo trae jalea real)', 'Ganancias sin conexión hasta 8 h con tarjeta de Recoger', 'Enjambrar (prestigio) al ganar 100 M en la temporada: jalea real = +10 % de producción por unidad, cinemática de enjambre en espiral', 'Colección de las seis mieles y estadísticas'], 'controls': 'Ratón o dedo: arrastra para girar la loma, rueda o pellizco para acercar, toque/clic en colmenas, tarro, panal, flores y mariposas. Teclado: Espacio o Intro cosecha; los botones del panel son accesibles con Tab.', 'ideas': ["Temporadas del año reales: en primavera florece el azahar con bonus x2, en verano el girasol, en otoño el brezo (p. ej. del 15 de marzo al 15 de abril, 'Semana del azahar de Benicarló')", 'Plagas y defensa: la avispa asiática aparece de vez en cuando y hay que tocarla antes de que robe miel (minijuego de reflejos de 10 s)', 'Reinas coleccionables con rasgos (italiana: +néctar, carniola: +proceso, negra ibérica: resiste frío) que se consiguen al enjambrar', 'Mercado dinámico: el precio de cada miel sube y baja durante el día y conviene vender en el pico (gráfica en el puesto)', 'Decoración del colmenar con monedas: caminos de piedra, farolillos que se encienden de noche, bebedero con agua animada', 'Ranking semanal de miel producida entre amigos (Supabase) y visitas a la loma de otros jugadores', 'Recetas: combinar mieles para crear productos (turrón, hidromiel, jabón) que se venden mucho más caros', 'Logros de temporada y un álbum de abejas: fotografiar con la cámara 3D a las abejas raras (abeja albina 1/500)', 'Versión de marca para una miel local real: código QR del tarro que desbloquea una miel de la colección y un descuento', 'Modo relajación: música generativa de zumbidos y campanas que suena según las flores del campo']},
 'cairn': {'concept': 'Arcade zen de apilar piedras en la orilla de un río de montaña con niebla. Una piedra oscila sobre la torre y tú eliges el momento de soltarla. Si el centro de masas de lo que queda encima sale del apoyo, la torre se desploma al agua.', 'tech': 'Three.js r147 + kit FX + modelos Blender (8 cantos rodados, 12 piedras raras, roca base, orilla, farol tōrō, bambú, helecho, musgo, hoja). Física determinista sin motor: apoyo por raycast sobre la malla real de la piedra de abajo (sin interpenetraciones), estabilidad por centro de masas acumulado nivel a nivel y derrumbe con caída balística, rebotes, salpicaduras y anillos en el agua. Río con olas por vértices, lluvia con LineSegments, luciérnagas de noche (hora real), montañas en capas con perspectiva atmosférica y audio ambiente de río sintetizado.', 'mechanics': ['Soltar en el momento justo: perfecta (se centra sola) o tambaleo amortiguado', 'Racha de calma: cada perfecta seguida suma más puntos y sube la escala pentatónica', 'Derrumbe por centro de masas fuera del apoyo (cualquier nivel de la torre)', "8,5 % de piedras raras (12 especies) que van a la colección 'Piedras del río'", 'Piedra del día: una rara garantizada en la primera partida del día y racha diaria', 'Modos: Río, Tormenta (se desbloquea con 15; lluvia, viento y puntos ×2) y Respira (4-7-8 sin fallos)', 'Viento desde 12 piedras: desplaza el vaivén y trae hojas', 'De noche (21-7 h) la escena cambia: farol encendido y luciérnagas'], 'controls': 'Toca/clic en la escena o pulsa Espacio para soltar la piedra. En Respira no hay que tocar: sigue el ritmo.', 'ideas': ['Foto final de la torre descargable (canvas.toDataURL) con marco de la app para compartir', 'Ranking semanal de altura con la misma semilla de piedras para todos', 'Estaciones del año: cerezos en primavera, hojas rojas en otoño, nieve en invierno según la fecha', 'Piedras con propiedades: pirita pesa el doble, ópalo es resbaladiza, geoda tiene el centro de masas desplazado', "Modo 'desafío': una forma objetivo (silueta) que hay que imitar con las piedras", 'Sonido binaural de río y lluvia más rico, con cuencos tibetanos en las perfectas', 'Respira conectada al reloj: recordatorio diario y estadística de minutos por semana', 'Coleccionables de temporada (piedras de playa de la Costa Azahar como guiño local)', 'Vibración háptica graduada según el tambaleo en móviles', 'Modo cooperativo por turnos en el mismo dispositivo']},
 'quilate': {'concept': 'Atelier de joyería en 3D con look de foto de producto: configuras anillos, colgantes y pendientes (metal, gema, talla, quilates, engaste, aro pavé y grabado) con precio en tiempo real, y en modo Encargos atiendes clientas con historia, presupuesto y pistas que puntúan de 0 a 100 y suben la reputación del atelier.', 'tech': 'Three.js r147 + kit FX (bloom, partículas, tweens, audio sintetizado). Modelos en Blender (b_quilate.py, bmesh): gemas con facetas reales (brillante, oval, pera, corazón, princesa, esmeralda escalonada), cabezas de garras ajustadas a cada talla con BVH para que abracen la piedra sin atravesarla, halos con posiciones de melee exportadas como extras glTF (userData.q), chatones, aro comfort-fit y pavé, asa, gancho, eslabón, pedestal, busto, soporte, ciclorama y vitrina. En la app: diamante como espejo facetado sobre un entorno de estudio propio (PMREM con tiras de luz), gemas de color con transmisión física, destellos de 4 puntas, alejandrita que cambia de color al girar, cadena en catenaria con InstancedMesh y grabado como textura dentro del aro.', 'mechanics': ['Atelier libre: 3 piezas, 4 metales, 8 gemas, 6 tallas, 0,5–3 ct, 4 engastes, aro pavé y grabado', 'Precio en tiempo real', 'Encargos con historia, requisitos y pistas; satisfacción 0–100 con desglose y reseña', 'Reputación → 5 niveles (Taller de barrio → Maison) que desbloquean gemas, tallas y engastes', 'Clienta VIP del día (reputación ×2)', 'Mi vitrina: hasta 12 diseños guardados'], 'controls': 'Pestañas del panel; arrastrar para orbitar y rueda/pellizco para zoom; Entregar en modo Encargos.', 'ideas': ['Probador AR sobre la mano (WebXR o MediaPipe Hands)', 'Exportar ficha del diseño a PDF con render y presupuesto (demo para joyerías reales)', 'Comparador de dos diseños lado a lado', 'Certificado simulado (color, pureza) que cambie precio y aspecto', 'Clientes recurrentes con aniversarios', 'Temporadas: San Valentín, bodas, Navidad', 'Más piezas: pulsera tenis, gemelos, tiara', 'Reto contrarreloj: tres encargos en 90 s', 'Vista macro animada del grabado']},
}
