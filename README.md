# Ficha de Personaje D&D 2024 (HTML autocontenido)

Ficha de personaje para D&D 2024 en un único HTML (canvas 816×1180, estética
similar a aidedd.org), con buscador del compendio completo de conjuros del
Manual 2024 (385), notas automáticas por conjuro, modal de descripción,
botones de fila flotantes y tooltips de cabecera. Funciona offline (PWA).

## Uso

- **Guardar HTML**: descarga `ficha_<nombre>.html` con los datos embebidos;
  al abrirlo muestra esos datos (o los cambios posteriores sin guardar de ese
  mismo fichero, que quedan en localStorage).
- **Exportar / Importar datos**: JSON `datos_<nombre>.json` con la ficha completa.
- Autoguardado continuo en localStorage (`hermes_ficha_v2`).

## Build

```
python build.py                 # -> resultado-hermes/
python build.py --out ruta      # destino alternativo
python build.py --no-verify     # omite la verificación de invariantes
```

Genera, junto a la salida:

- `ficha_dnd_hermes.html` — ficha con datos de ejemplo.
- `index.html` — ficha vacía (la que se publica en GitHub Pages).
- `ficha_dnd_hermes_empty.html` — copia de `index.html` para descarga.
- `manifest.json`, `sw.js` — PWA.

`resultado-hermes/` es salida del build: no guardes ahí fichas propias
(van en `personajes/`, que no se sube al repo).

### Pipeline

1. `referencias/_build_pool.py` — SPELL_POOL (385) desde `spells_txt/pool.json`
2. `referencias/_build_info.py` — SPELL_INFO (383) + slugs de aidedd
3. `referencias/_assemble.py` — ensambla en la plantilla y aplica los parches
4. `referencias/_verify_pool.py` — invariantes (tags, 385/383, parches)

La plantilla es `referencias/_ficha_backup_pool.html`. El JS de la ficha es
ASCII puro: los textos con tildes van como escapes `ó`.

SPELL_INFO tiene 383 claves, no 385: "Brazos de Hadar" y "Círculo Mágico"
no tienen descripción en pool.json (estado conocido).

## Tests

```
pip install pytest playwright
playwright install chromium
npm test        # o: python -m pytest tests/test_unit_py.py tests/test_unit_js.py tests/test_pipeline.py tests/test_smoke.py tests/test_sw.py
```

- `test_unit_py.py` — funciones Python del build.
- `test_unit_js.py` — funciones JS de la ficha (Playwright).
- `test_pipeline.py` — build completo, invariantes y determinismo.
- `test_smoke.py` — E2E básico.
- `test_sw.py` — service worker: offline y actualización tras un despliegue.

El CI (`.github/workflows/build-and-deploy.yml`) ejecuta la suite antes de
publicar en GitHub Pages; si falla un test, no se despliega.

## Estructura

```
build.py               orquestador del build
referencias/           plantilla, scripts del build y datos de conjuros
tests/                 suite pytest
resultado-hermes/      salida del build (ignorado por git)
personajes/            fichas y JSON propios (ignorado por git)
```
