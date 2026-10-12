"""Smoke test de las apps con Playwright (Chromium + WebGL por SwiftShader).
Abre dist/apps/*.html, ejecuta las acciones de tools/actions.json, captura errores de JS y guarda capturas en tools/shots/.
Uso:  python tools/build.py && python tools/test.py [21-faro 07-tiza ...]
Requisitos: pip install playwright && playwright install chromium
"""
import asyncio, os, sys, json, glob
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACT = json.load(open(os.path.join(ROOT, 'tools', 'actions.json'), encoding='utf-8'))
SHOTS = os.path.join(ROOT, 'tools', 'shots'); os.makedirs(SHOTS, exist_ok=True)
async def main(names):
    files = sorted(glob.glob(os.path.join(ROOT, 'dist', 'apps', '*.html')))
    if names: files = [f for f in files if os.path.basename(f)[:-5] in names]
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for f in files:
            n = os.path.basename(f)[:-5]; ctx = await b.new_context(viewport={'width': 1100, 'height': 720}); errs = []
            async def route(r):  # sirve Three.js desde vendor/ (funciona sin internet)
                u = r.request.url
                if 'three@0.147.0/' in u: await r.fulfill(path=os.path.join(ROOT, 'vendor', 'three@0.147.0', u.split('three@0.147.0/')[1]), content_type='application/javascript')
                else: await r.continue_()
            await ctx.route('**/cdn.jsdelivr.net/**', route); pg = await ctx.new_page()
            pg.on('pageerror', lambda e, errs=errs: errs.append('PAGEERR ' + str(e)))
            pg.on('console', lambda m, errs=errs: errs.append('CON ' + m.text) if m.type == 'error' and 'net::' not in m.text else None)
            await pg.goto('file://' + f); await pg.wait_for_timeout(3000 if n[:2] >= '21' else 1500)
            for a in ACT.get(n, []):
                try:
                    k = a[0]
                    if k == 'click': await pg.click(a[1], timeout=2000)
                    elif k == 'key': await pg.keyboard.press(a[1])
                    elif k == 'down': await pg.keyboard.down(a[1])
                    elif k == 'up': await pg.keyboard.up(a[1])
                    elif k == 'wait': await pg.wait_for_timeout(a[1])
                    elif k == 'mouse': await pg.mouse.click(a[1], a[2])
                    elif k == 'js': await pg.evaluate(a[1])
                    elif k == 'drag':
                        await pg.mouse.move(a[1], a[2]); await pg.mouse.down(); await pg.mouse.move(a[3], a[4], steps=10); await pg.mouse.up()
                except Exception as e: errs.append('ACCION ' + str(a)[:60] + ' ' + str(e)[:100])
            await pg.wait_for_timeout(700); await pg.screenshot(path=os.path.join(SHOTS, n + '.png'))
            print(n, 'OK' if not errs else errs[:5]); bad += bool(errs); await ctx.close()
        await b.close()
    sys.exit(1 if bad else 0)
asyncio.run(main(sys.argv[1:]))
