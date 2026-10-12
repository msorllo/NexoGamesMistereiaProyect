# Beat Lab

> Caja de ritmos con retos de productor

| Campo | Valor |
|---|---|
| Archivo | `src/apps/06-beatlab.html` (16 KB) |
| id (manifest / `data-app`) | `beatlab` / `beatlab` |
| `<title>` | Beat Lab |
| Categorías | creatividad |
| Motor | HTML/CSS/JS puro, sin dependencias |
| Fuentes | Archivo Black, DM Mono |
| Splash | fondo `#e4e4e0` → `#d6d6d1`, texto `#151515`, acento `#ff5a1f` |

## Concepto
Caja de ritmos de 16 pasos y 8 pistas con estética Teenage Engineering y retos de productor que desbloquean kits.

## Cómo está hecha
WebAudio: síntesis de bombo, caja, hi-hats, palmas, tom, bajo y pluck; programador con look-ahead de 120 ms; osciloscopio/espectro con AnalyserNode.

## Mecánicas y recompensas
- 4 patrones (A-D) y 4 presets (House, Hip-hop, Dembow, Techno)
- Pistas melódicas con 5 alturas por paso
- Knobs de tempo, swing y volumen
- 6 retos y 4 kits (808, Lo-fi, Chiptune, Cinta)

**Controles:** Clic en pasos, clic en el nombre de pista para silenciar, arrastrar knobs, ESPACIO play/stop.

## Paleta (`:root`)
`--body` #e4e4e0 · `--panel` #d6d6d1 · `--ink` #151515 · `--orange` #ff5a1f · `--mute` #8a8a84 · `--oled` #0b0b0b · `--white` #fafaf7 · `--blue` #3d6bff · `--yellow` #ffc21a

## Persistencia
Claves `OS.save/load` (localStorage `nexo.beatlab.<clave>`): `ch`, `pats`

## Integración con NEXO
- 2 llamadas a `OS.xp()` (XP que suma en el lanzador).
- 2 logros:
  - `beat_first` **Primer beat** — Le diste al play en Beat Lab
  - `beat_all` **Productor total** — Completaste todos los retos de Beat Lab

## Ideas para escalar
- [ ] Exportar WAV con OfflineAudioContext
- [ ] Cadena de patrones (canción)
- [ ] Samples subidos por el usuario
- [ ] Modo "jam" con teclado

## Registro de cambios
- 2026-09-23 · v1 creada. Probada sin errores en Chromium (escritorio y móvil).

## Notas
- (Añade aquí decisiones, bugs conocidos y pendientes.)
