"""Ensambla Nova Surge (app 31) desde las partes de tools/new/nova/ en un único HTML.
Uso:  python tools/new/nova/assemble.py                 -> src/apps/31-nova.html
      python tools/new/nova/assemble.py --out x.html    -> otra ruta (pruebas)
      python tools/new/nova/assemble.py --skip 30-,40-  -> excluye partes cuyo nombre empiece así
Cada js/*.js va en su propio <script> (un fallo no tumba a los demás). Los css/*.css se concatenan en <style>.
"""
import os, glob, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ap = argparse.ArgumentParser()
ap.add_argument('--out', default=os.path.join(ROOT, 'src', 'apps', '31-nova.html'))
ap.add_argument('--skip', default='')
a = ap.parse_args()
skip = [s for s in a.skip.split(',') if s]
rd = lambda p: open(p, encoding='utf-8').read()

def parts(sub, ext):
    fs = sorted(glob.glob(os.path.join(HERE, sub, '*.' + ext)))
    return [f for f in fs if not any(os.path.basename(f).startswith(s) for s in skip)]

LIBS = ['build/three.min.js', 'examples/js/loaders/GLTFLoader.js', 'examples/js/environments/RoomEnvironment.js',
        'examples/js/shaders/CopyShader.js', 'examples/js/shaders/LuminosityHighPassShader.js', 'examples/js/shaders/GammaCorrectionShader.js',
        'examples/js/postprocessing/EffectComposer.js', 'examples/js/postprocessing/RenderPass.js', 'examples/js/postprocessing/ShaderPass.js',
        'examples/js/postprocessing/UnrealBloomPass.js']
css = '\n'.join(f'/* ---- {os.path.basename(f)} ---- */\n' + rd(f) for f in parts('css', 'css'))
js = ''
for f in parts('js', 'js'):
    src = rd(f)
    if '</script' in src.lower(): raise SystemExit(f'ERROR: {os.path.basename(f)} contiene "</script" (rompe el HTML)')
    js += f'<script>/* ==== {os.path.basename(f)} ==== */\n{src}\n</script>\n'
head = rd(os.path.join(HERE, 'head.html'))
if '/*__CSS__*/' not in head: raise SystemExit('ERROR: head.html no tiene el marcador /*__CSS__*/')
html = (head.replace('/*__CSS__*/', css) + rd(os.path.join(HERE, 'body.html'))
        + ''.join(f'<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/{p}"></script>\n' for p in LIBS)
        + '<script>const GLB="__GLB__";</script>\n' + js + '</body>\n</html>\n')
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
open(a.out, 'w', encoding='utf-8').write(html)
print(f'OK {a.out} · {round(len(html.encode()) / 1024)} KB · js: {", ".join(os.path.basename(f) for f in parts("js", "js"))}')
