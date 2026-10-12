# 28 · COLMENA — imperio de miel (id `colmena`, archivo `28-colmena.html`, glb `colmena`)
Tagline: "Tu colmena crece incluso cuando no miras"
Tipo: idle / incremental (categorías "3d productividad juegos" — no: pon "3d juegos bienestar").
Fuentes: 'Fraunces' (display, con sus ejes ópticos: usa peso 800 y SOFT) + 'Hanken Grotesk' (texto). Fallbacks: 'Fraunces',Georgia,serif / 'Hanken Grotesk',system-ui,sans-serif.
Paleta: cielo de mañana #bfe3f0 → prado #d9ecc0 (bg #9fd3e6, bg2 #f6e7b0), miel #f2a900 (acc), ámbar oscuro #9c4a00, cera #fff1c9, verde oliva #3f5a22, azahar #fffdf6, fg #2b1a05. Diurna y luminosa (es la única de las 5 con luz de día).
Ambiente: diorama al aire libre, luz dorada de primera hora: un colmenar sobre una loma con campo de flores (azahar de naranjo — guiño a Benicarló —, lavanda, girasol, romero), abejas volando en enjambres reales. Realismo: miel translúcida (MeshPhysicalMaterial transmission .6, ior 1.5, thickness, color ámbar, clearcoat), cera de panal hexagonal, madera envejecida de las colmenas, hierba que se mece (InstancedMesh con shader simple o rotaciones por instancia), mariposas ocasionales, nubes lentas, ciclo día/tarde según la hora real (paleta del cielo cambia).

## Mecánica
- Recursos: Néctar (lo traen las abejas automáticamente), Miel (se fabrica en los panales a partir de néctar), Monedas (vendes miel), Jalea real (prestigio).
- Toca una flor → las abejas cercanas vuelan a ella (boost x3 durante 10 s, partículas de polen). Toca la colmena → recoges miel (tarro que se llena con animación, monedas saltan con partículas y sonido de moneda + zumbido).
- Mejoras (tienda en panel): más abejas (se ven más abejas volando, InstancedMesh hasta 300), nuevas colmenas (aparecen en la escena con animación de construcción: cae, rebota), tipos de flor (cambia el campo y el tipo de miel: azahar, lavanda, romero, brezo, cada una con color de miel distinto), apicultor ahumador (automatiza la recogida), panal extra (se añaden hexágonos al panal visible: el panal 3D grande de la derecha crece celda a celda con miel que rellena las celdas — es el progreso visual principal).
- Costes crecientes exponenciales (base·1.15^n), producción con multiplicadores; formatea números grandes (1,2 K · 3,4 M · 5,6 MM · ...) con coma decimal española.
- Ganancias offline: al volver, calcula el tiempo fuera (máx 8 h) y muestra tarjeta "Mientras no estabas tus abejas hicieron 12,3 K de miel" con opción "Recoger" (animación de lluvia de monedas).
- Prestigio "Enjambrar": al llegar a X monedas totales, la reina se va a fundar colmena nueva: reinicias con Jalea real que da +10 %/unidad permanente. Cinemática: enjambre sale en espiral hacia el cielo.
- Hitos (misiones visibles 3 a la vez): "Ten 25 abejas", "Produce 1 K de miel de lavanda", "Recoge 50 veces"… con recompensas.
- Evento aleatorio cada 1–3 min: "Mariposa dorada" cruza la pantalla → tócala para premio sorpresa (x5 producción 30 s o monedas). Recompensa variable = enganche.
- Recompensa diaria: tarro del día con racha (día 1..7 creciente).
- XP: por hito +20, prestigio +50, mariposa +10, diaria +15 (máx unas pocas por minuto; nunca por tick).
- Logros: colmena_1 "Primera cosecha", colmena_100 "Enjambre" (100 abejas), colmena_azahar "Flor de azahar" (desbloquear azahar), colmena_prestige "Larga vida a la reina" (primer enjambrado), colmena_million "Millonaria en miel" (1 M de monedas totales), colmena_butterfly "Cazamariposas" (10 mariposas doradas), colmena_streak "Apicultor constante" (racha de 7 días).
- Guardado: estado completo cada 5 s y al ocultar la página (visibilitychange).

## Assets Blender
`Colmena` (colmena Langstroth de madera: alzas apiladas con tapas, piquera, techo con chapa; madera pintada desgastada — hazla en 2 colores alternos con materiales), `Panal` (celda hexagonal de cera: prisma hexagonal hueco, se instanciará en código) y `Celda miel` (relleno de miel hexagonal), `Abeja` (cuerpo con rayas negro/amarillo, alas translúcidas separadas como objetos hijos o objeto `Ala`; pequeña y detallada pero pocos polígonos: < 800 tris porque se instancia), `FlorAzahar` (flor blanca 5 pétalos con estambres + hoja), `Lavanda` (espiga), `Girasol`, `Romero`, `Tarro` (tarro de cristal con tapa de tela y cuerda), `Ahumador`, `Apicultor` opcional, `Loma` (terreno ondulado con displace, material hierba), `Arbol naranjo` (tronco + copa con naranjas), `Moneda`, `Mariposa`, `Valla` de madera.
Render icono: panal con miel goteando + abeja, fondo #f6e7b0, luz cálida de tarde.

## Escena
- Cámara orbital suave (autorrotación muy lenta si no interactúas) sobre el diorama; intro: vuelo desde el cielo bajando a la colmena. En móvil, encuadre vertical correcto.
- Abejas: InstancedMesh; cada abeja con trayectoria flor↔colmena en curva con ruido (Bezier + seno), alas aleteando (escala Y del ala oscilando rapidísimo → con instancias: usa 2 InstancedMesh cuerpo/alas). Zumbido suave ambiental (oscilador de 180–220 Hz muy bajo volumen con LFO) solo tras primer gesto y si sonido activo.
- UI: tarjetas de recursos arriba con FX.count, tienda como panel lateral (hoja inferior en móvil) con mejoras en fila (icono SVG, nombre, nivel, coste, producción extra; deshabilitadas con barra de "te falta X"), hitos, botón enjambrar con barra de progreso.
- Exponer `window.H={add(monedas), tick(segundos), state()}` para test.
