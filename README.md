# Ficha de Personaje D&D 2024 (HTML autocontenido)

Ficha de personaje para D&D 2024 en un único HTML (canvas 816×1180, estética
similar a aidedd.org), con buscador del compendio completo de conjuros del
Manual 2024 (385), notas automáticas por conjuro, modal de descripción,
botones de fila flotantes y tooltips de cabecera. Autosave en localStorage.

- `resultado-hermes/ficha_dnd_hermes.html` — la ficha final lista para usar.
  Ábrela con doble clic (no necesita servidor).
- `referencias/_ficha_backup_pool.html` — base pristina del build (sin los
  parches; NO se edita a mano).

## Build reproducible (una sola pasada)

```
python build.py                 # regenera resultado-hermes/ficha_dnd_hermes.html
python build.py --out ruta      # destino alternativo (p. ej. tests/_out/)
python build.py --no-verify     # omite la verificación de invariantes
```

El build es determinista: hay un test que lo comprueba (el mismo comando dos
veces produce bytes idénticos). Incluye TODOS los parches que antes había que
aplicar a mano tras cada rebuild: `slice(0,1000)` (buscador con los 385),
fill incondicional de notas, botones flotantes ⓘ/✕ y tooltips de cabecera.

## Pipeline interno

1. `referencias/_build_pool.py` — SPELL_POOL (385) desde `spells_txt/pool.json`
2. `referencias/_build_info.py` — SPELL_INFO (383) + slugs aidedd (34 verificados)
3. `referencias/_assemble.py` — ensambla en el HTML + aplica los parches (idempotente)
4. `referencias/_verify_pool.py` — invariantes (tags, 385/383, parches presentes)

Pueden dirigirse a otro destino con la variable de entorno `FICHA_HTML`
(usada por los tests).

## Tests

```
pip install pytest playwright
playwright install chromium
python -m pytest tests/ -v
```

- `tests/test_pipeline.py` — build completo + invariantes + determinismo (rápido, sin navegador).
- `tests/test_smoke.py` — E2E con Playwright: carga, páginas, buscador, notas,
  modal, botones, tooltips, autosave.

Nota: `SPELL_INFO` tiene 383 claves, no 385 — "Brazos de Hadar" y "Círculo
Mágico" llegaron sin descripción en pool.json (estado conocido y verificado).

## Estructura

```
build.py                  orquestador (pasos 1-6)
referencias/              scripts del build + datos fuente (pool.json, slugs)
referencias/legacy/       scripts históricos de scraping (fuera del build)
tests/                    pytest: pipeline + smoke E2E
resultado-hermes/         ficha final generada
```