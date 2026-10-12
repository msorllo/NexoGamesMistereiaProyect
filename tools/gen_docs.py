"""Genera docs/apps/NN-id.md combinando tools/appinfo.py (diseño) con datos extraídos de src/apps/*.html.
Uso:  python tools/gen_docs.py
Las secciones "Registro de cambios" y "Notas" de cada .md se CONSERVAN al regenerar (todo lo que haya bajo esas cabeceras).
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from manifest import APPS
from appinfo import INFO
OUT = os.path.join(ROOT, 'docs', 'apps'); os.makedirs(OUT, exist_ok=True)
KEEP = ('## Registro de cambios', '## Notas')

for a in APPS:
    f = os.path.join(ROOT, 'src', 'apps', a['file']); html = open(f, encoding='utf-8').read(); i = INFO[a['id']]
    data_app = re.search(r'data-app="([^"]+)"', html).group(1)
    title = re.search(r'<title>([^<]+)</title>', html).group(1)
    fonts = sorted(set(x.replace('+', ' ') for x in re.findall(r'family=([^:&"]+)', html)))
    root = re.search(r':root\{([^}]*)\}', html)
    palette = re.findall(r'(--[\w-]+):(#[0-9a-fA-F]{3,8})', root.group(1)) if root else []
    keys = sorted(set(re.findall(r"OS\.(?:save|load)\('([^']+)'", html)))
    achs = re.findall(r"OS\.achieve\('([^']+)','([^']+)'(?:,'([^']*)')?", html)
    xp = len(re.findall(r'OS\.xp\(', html))
    three = 'three@0.147.0' in html
    glb = a.get('glb') or {'faro': 'faro', 'golf': 'golf', 'arrecife': 'acuario', 'caja': 'caja', 'excava': 'excava'}.get(a['id'])
    kb = round(os.path.getsize(f) / 1024)
    path = os.path.join(OUT, a['file'][:-5] + '.md')
    kept = ''
    if os.path.exists(path):
        old = open(path, encoding='utf-8').read(); idx = min([old.find(k) for k in KEEP if k in old] or [-1])
        if idx >= 0: kept = old[idx:]
    if not kept:
        kept = '## Registro de cambios\n- ' + ('2026-09-24 · v1 creada (gama Premium: kit FX con bloom, partículas, tweens y audio; modelos en Blender 5.0, icono Cycles)' if a.get('new') == 2 else '2026-09-23 · v1 creada' + (' (modelos 3D en Blender 5.0, render Cycles)' if three else '')) + '. Probada sin errores en Chromium (escritorio y móvil).\n\n## Notas\n- (Añade aquí decisiones, bugs conocidos y pendientes.)\n'
    L = [f"# {a['name']}", '', f"> {a['tag']}", '',
         '| Campo | Valor |', '|---|---|',
         f"| Archivo | `src/apps/{a['file']}` ({kb} KB{', GLB se inyecta en build' if three else ''}) |",
         f"| id (manifest / `data-app`) | `{a['id']}` / `{data_app}` |",
         f"| `<title>` | {title} |",
         f"| Categorías | {a['cat']} |",
         f"| Motor | {('Three.js r147 (CDN jsdelivr) + GLTFLoader + kit FX premium (EffectComposer, UnrealBloom, partículas, tweens, audio)' if a.get('new') == 2 else 'Three.js r147 (CDN jsdelivr) + GLTFLoader') if three else 'HTML/CSS/JS puro, sin dependencias'} |",
         f"| Fuentes | {', '.join(fonts)} |",
         f"| Splash | fondo `{a['bg']}` → `{a['bg2']}`, texto `{a['fg']}`, acento `{a['acc']}` |", '',
         '## Concepto', i['concept'], '',
         '## Cómo está hecha', i['tech'], '']
    if glb:
        L += ['## Assets 3D (Blender)', f"- Script: `blender/scripts/b_{glb}.py` (usa `blib.py`) → exporta `blender/glb/{glb}.glb`, guarda `blender/blend/{glb}.blend` y renderiza `blender/renders/{glb}.png` (icono).",
              '- En la app se clonan por nombre de objeto con `get(\'Nombre\')`. Si renombras un objeto en Blender, cambia también el código.',
              '- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.', '']
    L += ['## Mecánicas y recompensas'] + [f'- {m}' for m in i['mechanics']] + ['', f"**Controles:** {i['controls']}", '']
    L += ['## Paleta (`:root`)', ' · '.join(f'`{k}` {v}' for k, v in palette) or '(colores definidos en línea)', '']
    L += ['## Persistencia', f"Claves `OS.save/load` (localStorage `nexo.{data_app}.<clave>`): " + (', '.join(f'`{k}`' for k in keys) or 'ninguna'), '']
    L += ['## Integración con NEXO', f'- {xp} llamadas a `OS.xp()` (XP que suma en el lanzador).', f'- {len(achs)} logros:'] + [f"  - `{c}` **{n}**{(' — ' + d) if d else ''}" for c, n, d in achs] + ['']
    L += ['## Ideas para escalar'] + [f'- [ ] {x}' for x in i['ideas']] + ['', kept.rstrip() + '\n']
    open(path, 'w', encoding='utf-8').write('\n'.join(L))
print('docs generados:', len(APPS))
