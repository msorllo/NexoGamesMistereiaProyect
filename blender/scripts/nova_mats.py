"""Materiales compartidos de Nova Surge (app 31). Tabla ÚNICA: todos los scripts nova_* usan M('Nombre').
El código de la app busca algunos por nombre (Casco para las pinturas, Motor, Enemigo_Luz, Punto_Debil, Escudo_Energia...).
Formato: nombre: (color, roughness, metallic, emisivo|None, fuerza_emisiva, alpha)"""
from blib import mat

T = {
    # jugador (Casco se recolorea en código con las pinturas)
    'Casco':            ('#d9ddd0', .36, .55, None, 0, 1),
    'Casco_Acento':     ('#1f241b', .45, .60, None, 0, 1),
    'Cabina':           ('#0c1510', .08, .30, '#4a7a12', .8, 1),
    'Motor':            ('#c8ff1f', .30, 0.0, '#c8ff1f', 8, 1),
    # enemigos
    'Enemigo':          ('#2b2f36', .42, .75, None, 0, 1),
    'Enemigo_Panel':    ('#6e1f2b', .50, .35, None, 0, 1),
    'Enemigo_Luz':      ('#ff2e4d', .30, 0.0, '#ff2e4d', 7, 1),
    'Oro_Elite':        ('#d8a531', .25, 1.0, None, 0, 1),
    'Escudo_Energia':   ('#ffb000', .20, 0.0, '#ffb000', 3, .65),
    'Metal_Oscuro':     ('#15171b', .50, .80, None, 0, 1),
    'Sierra':           ('#9aa3ad', .22, 1.0, None, 0, 1),
    'Punto_Debil':      ('#ff7a1a', .30, 0.0, '#ffae3d', 9, 1),
    'Peligro_Amarillo': ('#ffb000', .50, .10, None, 0, 1),
    'Peligro_Negro':    ('#121212', .60, .10, None, 0, 1),
    'Luz_Blanca':       ('#ffffff', .30, 0.0, '#ffffff', 6, 1),
    # asteroides / entorno
    'Hielo':            ('#a9dcf2', .18, 0.0, '#2a6a8a', .25, 1),
    'Roca':             ('#3a4150', .85, 0.0, None, 0, 1),
    'Estructura':       ('#454b52', .55, .70, None, 0, 1),
    'Azufre':           ('#c9a227', .60, 0.0, '#ffb000', 2.5, 1),
    # recogibles
    'Chatarra':         ('#ffb000', .28, 1.0, None, 0, 1),
    'Potencia':         ('#c8ff1f', .30, 0.0, '#c8ff1f', 4, 1),
    'Bomba':            ('#ff5a2a', .35, .30, '#ff5a2a', 2, 1),
    'Reparacion':       ('#eef2e4', .40, 0.0, '#c8ff1f', .6, 1),
    # NOVA
    'Nova_Plasma':      ('#fff2c0', .20, 0.0, '#fff2c0', 10, 1),
    'Nova_Costura':     ('#ff8a1c', .30, 0.0, '#ff8a1c', 8, 1),
    'Nova_Blindaje':    ('#1c1a1f', .35, .90, None, 0, 1),
}

def M(name):
    if name not in T: raise KeyError(f'Material {name} no está en nova_mats.T (añádelo a la tabla, no lo inventes suelto)')
    c, r, m, e, es, a = T[name]
    return mat(name, c, rough=r, metal=m, emit=e, emit_str=es, alpha=a)
