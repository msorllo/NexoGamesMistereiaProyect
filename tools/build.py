"""Build de NEXO.
1) Inyecta los GLB de blender/glb (base64) en las apps 3D que tienen el marcador __GLB__.
2) Genera dist/apps/*.html (apps sueltas con helper OS, favicon y splash).
3) Genera site/ (web publicable: index ligero + apps bajo demanda en site/apps/ID.html).
4) Genera dist/Nexo.html (lanzador completo, doc HTML entero) y dist/nexo-artifact.html (sin <html>/<head>/<body>, para publicar como Artifact).
Uso:  python tools/build.py
"""
import json, re, os, base64, urllib.parse, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from manifest import APPS
SRC, DIST, SITE = os.path.join(ROOT, 'src'), os.path.join(ROOT, 'dist'), os.path.join(ROOT, 'site')
os.makedirs(os.path.join(DIST, 'apps'), exist_ok=True)
os.makedirs(os.path.join(SITE, 'apps'), exist_ok=True)
OSJS = open(os.path.join(SRC, 'os.js'), encoding='utf-8').read()
GLB = {'21-faro.html': 'faro', '22-golf.html': 'golf', '23-acuario.html': 'acuario', '24-caja.html': 'caja', '25-excava.html': 'excava'}
GLB.update({a['file']: a['glb'] for a in APPS if a.get('glb')})

def fav(icon):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><clipPath id="r"><rect width="64" height="64" rx="14"/></clipPath><g clip-path="url(#r)">{icon}</g></svg>'
    return 'data:image/svg+xml,' + urllib.parse.quote(svg)

NEXO_ICON = '<rect width="64" height="64" fill="#0f1013"/>' + ''.join(
    f'<circle cx="{14+c*18}" cy="{14+r*18}" r="7" fill="{col}"/>' for (r, c), col in zip([(r, c) for r in range(3) for c in range(3)],
    ['#ff2e88', '#ffb800', '#19e3c0', '#4776e6', '#efeee9', '#c471f5', '#7ccf6a', '#ff6b5a', '#f2d38a']))

sources, catalog = {}, []
for a in APPS:
    html = open(os.path.join(SRC, 'apps', a['file']), encoding='utf-8').read()
    if a['file'] in GLB:
        b = base64.b64encode(open(os.path.join(ROOT, 'blender', 'glb', GLB[a['file']] + '.glb'), 'rb').read()).decode()
        html = html.replace('__GLB__', b)
    sources[a['id']] = html
    open(os.path.join(SITE, 'apps', a['id'] + '.html'), 'w', encoding='utf-8', newline='\n').write(html)
    for code, name, desc in re.findall(r"OS\.achieve\('([^']+)','([^']+)'(?:,'([^']*)')?", html):
        catalog.append(dict(app=a['id'], code=code, name=name, desc=desc or 'Logro de ' + a['name']))
    if a['id'] == 'hucha':
        for k, n in re.findall(r"\['(\w+)','([^']+)'\]", html.split('const BD=')[1].split(';')[0]):
            catalog.append(dict(app='hucha', code='hucha_' + k, name=n, desc='Insignia de Hucha'))
    splash = (f'<div id="nx-splash" style="position:fixed;inset:0;z-index:2147483000;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;'
              f'background:radial-gradient(circle at 50% 40%,{a["bg2"]},{a["bg"]});color:{a["fg"]};transition:opacity .5s;font-family:system-ui,sans-serif;text-align:center;padding:16px">'
              f'<div style="width:120px;height:120px;border-radius:32px;overflow:hidden;box-shadow:0 30px 60px -20px rgba(0,0,0,.6)"><svg viewBox="0 0 64 64" style="width:100%;height:100%;display:block">{a["icon"]}</svg></div>'
              f'<div style="font-family:{a["font"]};font-size:44px;line-height:1">{a["name"]}</div><div style="opacity:.75;font-size:15px">{a["tag"]}</div></div>'
              '<script>setTimeout(function(){var s=document.getElementById("nx-splash");if(s){s.style.opacity=0;s.style.pointerEvents="none";setTimeout(function(){s.remove()},600)}},1100)</script>')
    sa = html.replace('<head>', f'<head><script>{OSJS}</script><link rel="icon" href="{fav(a["icon"])}">', 1)
    sa = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + splash, sa, count=1)
    open(os.path.join(DIST, 'apps', a['file']), 'w', encoding='utf-8').write(sa)

manifest = [dict({k: a[k] for k in ('id', 'name', 'cat', 'tag', 'bg', 'bg2', 'fg', 'acc', 'font', 'icon')}, new=a.get('new', 0)) for a in APPS]
def js(o): return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
tpl = open(os.path.join(SRC, 'launcher.html'), encoding='utf-8').read()
out = (tpl.replace('__NEXO_ICON__', fav(NEXO_ICON)).replace('__MANIFEST__', js(manifest)).replace('__CATALOG__', js(catalog))
          .replace('__OSJS__', json.dumps(OSJS)).replace('__SOURCES__', js(sources)))
open(os.path.join(DIST, 'nexo-artifact.html'), 'w', encoding='utf-8').write(out)
head, rest = out.split('<style>', 1); css, body = rest.split('</style>', 1)
full = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        + head + '<style>' + css + '</style>\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
open(os.path.join(DIST, 'Nexo.html'), 'w', encoding='utf-8').write(full)
print(f'OK · {len(APPS)} apps · {len(catalog)} logros · Nexo.html {round(len(full.encode())/1024)} KB')

# --- site/index.html: lanzador sin apps embebidas (se piden con fetch al abrirlas)
META = ('<meta name="description" content="NEXO: 30 apps y juegos web en un lanzador con XP, niveles y logros. Juegos 3D, creatividad, bienestar y mente. Un proyecto de Mistereia.">\n'
        '<meta name="theme-color" content="#0f1013">\n<meta property="og:title" content="NEXO · 30 apps web en un lanzador">\n'
        '<meta property="og:description" content="Juegos 3D, estudios creativos, bienestar y retos mentales con XP y logros compartidos. Proyecto de Mistereia.">\n'
        '<meta property="og:type" content="website">\n<meta name="robots" content="index,follow">\n')
site_out = (tpl.replace('__NEXO_ICON__', fav(NEXO_ICON)).replace('__MANIFEST__', js(manifest)).replace('__CATALOG__', js(catalog))
               .replace('__OSJS__', json.dumps(OSJS)).replace('__SOURCES__', '{}'))
h2, r2 = site_out.split('<style>', 1); c2, b2 = r2.split('</style>', 1)
page = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        + META + h2 + '<style>' + c2 + '</style>\n</head>\n<body>\n' + b2 + '\n</body>\n</html>\n')
open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
open(os.path.join(SITE, '.nojekyll'), 'w').close()
open(os.path.join(SITE, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n')
open(os.path.join(SITE, '_headers'), 'w').write('/apps/*\n  Cache-Control: public, max-age=86400\n/index.html\n  Cache-Control: public, max-age=600\n')
print(f'SITE · index {round(len(page.encode())/1024)} KB + {len(APPS)} apps bajo demanda')
