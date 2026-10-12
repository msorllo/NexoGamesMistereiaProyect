# NEXO · 30 apps web en un lanzador

> Proyecto de **Mistereia** · «El míster de la IA» · Benicarló

NEXO es un lanzador con estética de sistema operativo que reúne **30 apps y juegos web independientes**: juegos 3D, estudios creativos, bienestar, productividad y retos mentales. Todas comparten **XP, niveles, logros y retos diarios**.

**Jugar ahora:** https://msorllo.github.io/NexoGamesMistereiaProyect/

## Qué incluye

| Bloque | Apps |
|---|---|
| 20 apps 2D | Neón Runner, Planetario, La Cripta, Voxel Isla, Jardín Focus, Beat Lab, Tiza, Arcana, Bitácora, Hucha, Flujo, Cerebro Bauhaus, Ladrillos, Eco, Gesta, Plano, La Coctelera, Tono, Reflejo, Mochi |
| 5 apps 3D | Faro, Minigolf Cósmico, Arrecife, Caja de Música, Yacimiento |
| 5 apps 3D Premium (kit FX con bloom y partículas) | Tourbillon, Forja, Colmena, Cairn, Quilate |

- Cada app tiene estilo, paleta y fuentes propias, favicon y pantalla de arranque.
- Los modelos 3D están creados en Blender (`blender/`).
- Sin backend: el progreso se guarda en el navegador (localStorage). **No hay claves, cuentas ni datos de usuario.**
- Interfaz en español de España.

## Rendimiento

- La web publicada (`site/`) carga un lanzador de ~160 KB; **cada app se descarga solo al abrirla** (y se precarga al pasar el ratón).
- Fuentes de Google sin bloquear el primer render.
- El fondo animado del lanzador se pausa mientras juegas, para dejar toda la GPU al juego.
- Las apps 3D adaptan su calidad (resolución y bloom) si detectan pocos fps.
- Three.js (`0.147.0`) se sirve desde jsDelivr, con caché compartida entre sitios.

## Estructura

```
src/launcher.html     plantilla del lanzador
src/os.js             helper compartido window.OS (xp, logros, guardado)
src/apps/NN-id.html   código de cada app (HTML autocontenido)
blender/              scripts, .blend, GLB e iconos de las apps 3D
tools/                build, tests con Playwright, manifiesto y utilidades
docs/apps/            ficha de cada app
site/                 web lista para publicar (salida de build.py)
vendor/               copia local de Three.js, solo para tests sin internet
CLAUDE.md             guía de trabajo y contrato de apps
```

## Desarrollo

```bash
pip install playwright pillow && playwright install chromium   # una vez
python tools/build.py          # genera site/ (web) y dist/ (HTML único y apps sueltas)
python tools/test.py           # prueba las 30 apps con Playwright
cd site && python -m http.server 8000   # probar en http://localhost:8000
```

`dist/` no se versiona (se regenera). `dist/Nexo.html` es la versión de un solo archivo (~8 MB) para uso offline o como Artifact.

## Publicación

`site/` es estático: se sirve tal cual en GitHub Pages, Cloudflare Pages, Netlify o Vercel. En GitHub Pages se publica desde la rama `gh-pages` (contiene solo el contenido de `site/`).

## Créditos y licencias

Código y arte: Mistereia. Three.js © sus autores (licencia MIT). Tipografías de Google Fonts (licencias abiertas).
Aún no se ha elegido licencia para el código propio: todos los derechos reservados hasta decidirlo.
