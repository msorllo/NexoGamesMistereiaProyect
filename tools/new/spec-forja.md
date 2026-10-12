# 27 · FORJA — herrería de leyenda (id `forja`, archivo `27-forja.html`, glb `forja`)
Tagline: "Calienta, golpea, templa: forja armas legendarias"
Tipo: artesanía de timing + botín por rareza (categorías "3d juegos creatividad").
Fuentes: 'Grenze Gotisch' (display) + 'Alegreya Sans SC' (texto/UI, small caps). Fallbacks: 'Grenze Gotisch',Georgia,serif / 'Alegreya Sans SC',system-ui,sans-serif.
Paleta: hollín #0f0b09 → #2a1710 (bg/bg2), brasa #ff5a1f (acc), metal fundido #ffcf73, acero frío #8ea2b5, piedra #5b5148, fg #f4e9dc. Rarezas: común #b9b3aa, raro #4aa3ff, épico #b35cff, legendario #ffb43a (con destello).
Ambiente: taller de herrero de noche, fragua encendida como única luz principal (luz cálida parpadeante con sombras), yunque en primer plano, humo y chispas. Realismo: hierro forjado rugoso, carbón con brasas emisivas animadas (emissiveIntensity con ruido), metal que cambia de color con la temperatura (radiación de cuerpo negro: negro→rojo cereza→naranja→amarillo→blanco; implementa `blackbody(t)`), vapor al templar.

## Mecánica (bucle de 30–45 s por arma)
1. ENCARGO: eliges un pedido de 3 disponibles (cliente con nombre + arma pedida + calidad mínima + recompensa en monedas y XP). Hay también "Forja libre".
2. CALENTAR: el lingote está en la fragua. Mantén pulsado (botón fuelle grande / barra espaciadora) para bombear el fuelle: sube la temperatura (el metal cambia de color de verdad, brasas se avivan, partículas de chispa suben, sonido de soplido). Hay una ventana óptima (p.ej. 1050–1150 °C) marcada en un termómetro curvo; si te pasas → "metal quemado" (penaliza calidad), si te quedas corto → golpes rinden menos. La temperatura baja sola.
3. GOLPEAR: el lingote pasa al yunque (animación con tenazas). Aparece un anillo de timing que se cierra sobre el metal; toca/clic cuando coincide → golpe PERFECTO / BUENO / FALLO. Cada golpe: el martillo cae (animación con anticipación y rebote), FX.shake, gran ráfaga de chispas, sonido metálico (tono + ruido), el metal se deforma progresivamente (morph de escala hacia la forma del arma: interpolar entre lingote y hoja con escala/posiciones de piezas), se enfría (color baja) → puedes volver a calentar. 6–9 golpes según arma; combo de perfectos multiplica calidad.
4. TEMPLAR: arrastra/toca para sumergir en el barril de agua → nube de vapor (partículas blancas grandes), siseo (ruido filtrado), color del metal se apaga a acero. Timing del temple (soltar a tiempo) añade bonus.
5. REVELACIÓN: cámara hace un giro dramático alrededor del arma terminada flotando en un haz de luz; la rareza se revela con una "tirada" (el marco cambia de color rápido y se frena en la rareza final — calidad sube probabilidades), estadísticas (filo, peso, aura) con contadores animados, nombre generado ("Colmillo del Alba", "Hoja de Ceniza"...). Legendario: haz de luz dorado + bloom intenso + sonido coral.
- ARMERÍA (colección): pared con soportes donde se cuelgan las armas conseguidas (hasta 24 huecos por tipo/rareza), contador de colección.
- Progresión: monedas para desbloquear materiales (Hierro → Acero → Damasco (patrón ondulado en la hoja con CanvasTexture) → Meteorito (negro con vetas azules emisivas)) y tipos de arma (Daga → Espada → Hacha → Mandoble). Nivel de herrero con barra de progreso.
- Motivo para volver: encargos se renuevan cada día; "Encargo real" diario con recompensa doble.
- XP: por arma (10 + rareza·10), encargo cumplido +20.
- Logros: forja_1 "Primer golpe" (primera arma), forja_perfect "Martillo exacto" (arma con todos los golpes perfectos), forja_legend "Leyenda de la fragua" (arma legendaria), forja_damasco "Acero de Damasco" (desbloquear), forja_orders "Proveedor real" (10 encargos), forja_armory "Armería completa" (una de cada tipo), forja_burnt "Demasiado caliente" (quemar el metal 3 veces; logro curioso).

## Assets Blender
`Yunque` (forma clásica con cuerno, pie de tronco `Tocón` con anillos y corteza), `Fragua` (horno de ladrillo/piedra con boca, campana de humos; interior `Brasas` separado: montón de carbones desplazados con material emisivo naranja), `Martillo` (cabeza de hierro + mango de madera con cuero), `Tenazas`, `Fuelle` (cuero + madera, con origen en bisagra para animar apertura), `Barril` (duelas de madera con aros de hierro y agua `Agua` como disco), `Lingote` (barra con biseles), hojas: `Daga`, `Espada`, `Hacha`, `Mandoble` (hoja con bisel de filo, guarda, empuñadura con cuero en espiral, pomo) con la HOJA como material aparte nombrado "Hoja" para poder cambiar su color/emisivo en código, `Soporte` (gancho de pared) y `Pared` (tablones o piedra) para la armería, `Piedra afilar` decorativa, suelo `Suelo` de losas.
Render icono: yunque con espada al rojo encima y chispas (emisivo) sobre fondo #2a1710.

## Escena
- Cámara a la altura del yunque, fragua al fondo a la izquierda. Transiciones de cámara con tweens entre CALENTAR (encuadre fragua), GOLPEAR (encuadre cenital del yunque), TEMPLAR (barril), REVELAR (orbitando).
- Luz de la fragua: PointLight naranja con intensidad parpadeante (ruido) + sombras; luz de luna fría por la ventana; niebla cálida; humo (sprites grandes transparentes que suben girando) + chispas constantes de la fragua.
- UI: medidor de temperatura curvo (SVG) con zona óptima, anillo de timing (SVG superpuesto centrado sobre el metal proyectado a pantalla), combo "×3 PERFECTO" con tipografía gótica que salta, tarjeta de revelación de rareza, armería como panel.
- Exponer `window.F={forgeAuto(q)}` (completa un arma con calidad q 0..1 para test), `F.state()`.
