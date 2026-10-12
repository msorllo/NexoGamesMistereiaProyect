"""Vista previa rápida de UNA app (sin build completo): inyecta os.js + GLB, abre en Chromium (WebGL SwiftShader),
ejecuta pasos opcionales y guarda captura. Muestra errores JS.
Uso: python tools/preview.py src/apps/26-tourbillon.html tourbillon out.png [--mobile] [--wait 3000] [--js "expr1;;WAIT800;;expr2"]
"""
import asyncio, sys, os, base64, argparse, tempfile
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, 'vendor', 'three@0.147.0') + '/'
ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('glb'); ap.add_argument('out')
ap.add_argument('--mobile', action='store_true'); ap.add_argument('--wait', type=int, default=3500); ap.add_argument('--js', default='')
a = ap.parse_args()
h = open(a.src, encoding='utf-8').read()
g = os.path.join(ROOT, 'blender', 'glb', a.glb + '.glb')
if '__GLB__' in h: h = h.replace('__GLB__', base64.b64encode(open(g, 'rb').read()).decode())
h = h.replace('<head>', '<head><script>' + open(os.path.join(ROOT, 'src', 'os.js'), encoding='utf-8').read() + '</script>', 1)
tmp = os.path.join(tempfile.gettempdir(), 'nexo_prev_' + os.path.basename(a.src)); open(tmp, 'w', encoding='utf-8').write(h)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        vp = {'width': 390, 'height': 844} if a.mobile else {'width': 1280, 'height': 800}
        ctx = await b.new_context(viewport=vp, device_scale_factor=1, has_touch=a.mobile); errs = []
        async def route(r):
            u = r.request.url
            if 'three@0.147.0/' in u: await r.fulfill(path=V + u.split('three@0.147.0/')[1], content_type='application/javascript')
            else: await r.abort()   # fuentes de Google: sin red en el contenedor -> se usa el fallback
        await ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else route(r))
        pg = await ctx.new_page()
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        pg.on('console', lambda m: errs.append('CON ' + m.text) if m.type == 'error' and 'net::' not in m.text and 'Failed to load resource' not in m.text else None)
        await pg.goto('file://' + tmp + '?hq'); await pg.wait_for_timeout(a.wait)
        for j in [x for x in a.js.split(';;') if x.strip()]:
            if j.startswith('WAIT'): await pg.wait_for_timeout(int(j[4:])); continue
            if j.startswith('SHOT:'): await pg.screenshot(path=j[5:]); continue
            if j.startswith('CLICK:'): x, y = map(int, j[6:].split(',')); await pg.mouse.click(x, y); continue
            try: print('JS>', str(await pg.evaluate(j))[:400])
            except Exception as e: errs.append('JSERR ' + str(e)[:300])
        await pg.wait_for_timeout(600); await pg.screenshot(path=a.out)
        fps = await pg.evaluate("new Promise(r=>{let n=0,t=performance.now();function f(){n++;if(performance.now()-t<1000)requestAnimationFrame(f);else r(n)}requestAnimationFrame(f)})")
        print('fps(swiftshader, orientativo):', fps); print('ERRORES:', errs[:10] if errs else 'ninguno'); await b.close()
asyncio.run(main())
