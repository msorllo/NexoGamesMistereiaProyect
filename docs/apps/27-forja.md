# Forja

> Calienta, golpea y templa armas legendarias

| Campo | Valor |
|---|---|
| Archivo | `src/apps/27-forja.html` (105 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `forja` / `forja` |
| `<title>` | Forja |
| Categorías | 3d juegos creatividad |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader + kit FX premium (EffectComposer, UnrealBloom, partículas, tweens, audio) |
| Fuentes | Alegreya Sans SC, Grenze Gotisch |
| Splash | fondo `#0f0b09` → `#2a1710`, texto `#f4e9dc`, acento `#ff5a1f` |

## Concepto
Taller de herrero de noche en 3D. Cada arma es una partida de 30-45 s: calientas el lingote en la fragua con el fuelle, lo golpeas en el yunque al ritmo de un anillo, lo templas en el barril y la fragua 'tira los dados' de la rareza. Encargos diarios con clientes, un encargo real con recompensa doble y una armería que llenar (4 armas x 4 rarezas).

## Cómo está hecha
Modelos de Blender (b_forja.py): yunque con cuerno, tocón con anillos, fragua de ladrillo con boca en arco, dovelas, base de sillares y campana, brasas, fuelle articulado (base, cuero y tapa con origen en la bisagra), barril de duelas con aros y agua, martillo, tenazas, daga, espada, hacha, mandoble (hoja con material 'Hoja'), lingote, pared de tablones, ventana, soporte, piedra de afilar, antorcha, cubo y suelo de losas (GLB 682 KB). En Three.js: la hoja tiene un morph target generado en tiempo real (lingote -> hoja) que avanza con cada golpe; material de metal con color de cuerpo negro (blackbody) + oxidación + vetas emisivas del meteorito + barrido de pulido por shader; texturas procedurales de hierro, acero, damasco y meteorito; brasas con ruido 3D animado en el emisivo; llamas por shader fbm; chispas como estelas LineSegments con gravedad y rebote en yunque y suelo; humo y vapor con sprites reutilizados; polvo en el haz de luna; foco de la fragua con sombras 2048 que sale por la boca; haz de revelación por shader y órbita de cámara; audio 100 % sintetizado (fragua, fuelle, yunque, siseo del temple, coro legendario).

## Assets 3D (Blender)
- Script: `blender/scripts/b_forja.py` (usa `blib.py`) → exporta `blender/glb/forja.glb`, guarda `blender/blend/forja.blend` y renderiza `blender/renders/forja.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- Encargos diarios: 3 en el tablón (uno real con recompensa doble), se reponen al cumplirlos hasta 7 al día; forja libre con arma y metal a elegir
- Calentar: mantén el fuelle; la temperatura sube con retardo, hay ventana óptima por metal y si te pasas el metal se quema (−20 % de calidad)
- Golpear: anillo de ritmo que se cierra sobre el metal; perfecto/bueno/fallo, combo de perfectos, el metal se enfría con cada golpe y puedes recalentar
- Templar: mantén para sumergir y suelta en la franja azul; vapor, ondas y siseo
- Revelación: ruleta de rareza (común, rara, épica, legendaria) ponderada por la calidad y el metal, con 'casi' explícito
- Favor de la fragua: cada arma no legendaria suma 1; a 20 la siguiente es legendaria garantizada
- Armería: 16 huecos (tipo x rareza) con siluetas; toca un arma para ver su historia
- Progresión: monedas para desbloquear metales (Acero, Damasco, Meteorito) y armas (Espada, Hacha, Mandoble), nivel de herrero con títulos y bonus
- Racha diaria: la primera forja del día paga +50 %

**Controles:** Ratón/táctil: mantén el botón Fuelle, toca el metal (o cualquier punto) para golpear, mantén Templar. Teclado: espacio (fuelle / golpe / templar), Enter (al yunque), R (recalentar), Esc (cerrar).

## Paleta (`:root`)
`--bg` #0f0b09 · `--bg2` #2a1710 · `--fg` #f4e9dc · `--acc` #ff5a1f · `--mol` #ffcf73 · `--steel` #8ea2b5 · `--stone` #5b5148 · `--mut` #b9a896 · `--r0` #b9b3aa · `--r1` #4aa3ff · `--r2` #b35cff · `--r3` #ffb43a

## Persistencia
Claves `OS.save/load` (localStorage `nexo.forja.<clave>`): `s`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 8 logros:
  - `forja_1` **Primer golpe** — Forja tu primera arma
  - `forja_perfect` **Martillo exacto** — Forja un arma con todos los golpes perfectos
  - `forja_legend` **Leyenda de la fragua** — Forja un arma legendaria
  - `forja_orders` **Proveedor real** — Cumple 10 encargos
  - `forja_armory` **Armería completa** — Forja un arma de cada tipo
  - `forja_burnt` **Demasiado caliente** — Quema el metal 3 veces
  - `forja_meteor` **Caído del cielo** — Forja un arma con hierro de meteorito
  - `forja_damasco` **Acero de Damasco** — Desbloquea el acero de Damasco

## Ideas para escalar
- [ ] Temporadas de encargos: un 'Torneo de Morella' semanal con un cliente jefe que pide una espada ≥90 de damasco y da un trofeo único para la armería
- [ ] Grabados: tras la revelación, trazar una runa con el dedo sobre la hoja (reconocimiento de gesto simple) que añade un efecto de aura (fuego, escarcha, rayo)
- [ ] Afilado en la piedra de afilar como minijuego opcional: mantener la hoja en el ángulo correcto sube el Filo hasta +10
- [ ] Aprendiz automático: contratar un aprendiz que forja dagas comunes mientras no estás (motivo para volver: '3 dagas listas')
- [ ] Aleaciones: combinar dos lingotes en el horno (hierro + meteorito = 'Acero estelar') con ventana de temperatura doble
- [ ] Mercado dinámico: el precio de cada tipo de arma cambia por día y hay que decidir si vender o guardar
- [ ] Colección de empuñaduras y pomos (cosméticos) que caen como botín raro y se ven en la armería
- [ ] Modo desafío diario con semilla compartida: mismo encargo para todos y ranking de calidad (necesita backend, p. ej. Supabase)
- [ ] Clientes con historia: un cliente recurrente vuelve con cartas y encargos encadenados (la capitana Urraca asciende si su espada es épica)
- [ ] Exportar la ficha del arma legendaria como imagen para compartir (canvas del render + nombre + estadísticas)

## Registro de cambios
- 2026-09-24 · v1 creada (gama Premium: kit FX con bloom, partículas, tweens y audio; modelos en Blender 5.0, icono Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
