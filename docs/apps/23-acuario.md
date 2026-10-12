# Arrecife

> Tu acuario 3D: cuida, decora y colecciona peces

| Campo | Valor |
|---|---|
| Archivo | `src/apps/23-acuario.html` (24 KB, GLB se inyecta en build) |
| id (manifest / `data-app`) | `arrecife` / `acuario` |
| `<title>` | Arrecife |
| Categorías | 3d bienestar |
| Motor | Three.js r147 (CDN jsdelivr) + GLTFLoader |
| Fuentes | Lilita One, Mulish |
| Splash | fondo `#0a7fa8` → `#3ec5e8`, texto `#ffffff`, acento `#ff5d8f` |

## Concepto
Acuario 3D que cuidas: das de comer, compras peces y decoración, limpias el cristal frotando y cumples misiones.

## Cómo está hecha
Three.js + modelos Blender (5 peces, corales, alga, cofre, castillo, concha, roca). Cáusticas con canvas animado, suciedad del cristal en canvas borrable con destination-out, peces con steering hacia objetivos/comida.

## Assets 3D (Blender)
- Script: `blender/scripts/b_acuario.py` (usa `blib.py`) → exporta `blender/glb/acuario.glb`, guarda `blender/blend/acuario.blend` y renderiza `blender/renders/acuario.png` (icono).
- En la app se clonan por nombre de objeto con `get('Nombre')`. Si renombras un objeto en Blender, cambia también el código.
- Blender Z-arriba → glTF Y-arriba: (x, y, z)ᴮˡᵉⁿᵈᵉʳ → (x, z, −y)ᵗʰʳᵉᵉ. El origen de cada objeto se fija en `join(..., origin=)`.

## Mecánicas y recompensas
- Perlas: por comer, cofre (cada 3 min), pasivo y al volver
- Tienda de 5 peces y 7 decoraciones (colocar en la arena)
- 6 misiones
- Luz nocturna

**Controles:** Clic en agua para echar comida, modo limpiar para frotar, arrastrar para orbitar.

## Paleta (`:root`)
`--aqua` #0a7fa8 · `--deep` #043a52 · `--sand` #e9d6a8 · `--coral` #ff5d8f · `--pearl` #fff6e8

## Persistencia
Claves `OS.save/load` (localStorage `nexo.acuario.<clave>`): `s`

## Integración con NEXO
- 3 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 3 logros:
  - `acu_all` **Biólogo marino** — Completaste todas las misiones del Arrecife
  - `acu_5sp` **Arrecife completo** — Tienes las 5 especies
  - `acu_night` **Bioluminiscencia** — Encendiste la luz nocturna del acuario

## Ideas para escalar
- [ ] Crías de peces
- [ ] Plantas que crecen
- [ ] Temperatura/pH simplificados
- [ ] Foto del acuario para compartir

## Registro de cambios
- 2026-09-23 · v1 creada (modelos 3D en Blender 5.0, render Cycles). Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
