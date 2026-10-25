# -*- coding: utf-8 -*-
"""Fixtures comunes: build en un directorio temporal y navegador Playwright.

- ``build_dir``: build.py --out <tmp>/ficha.html  (genera tambien index.html)
- ``abrir(ruta)``: pagina en un contexto NUEVO (localStorage limpio) que
  falla el test si la pagina lanza errores JS.
"""
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "referencias"))


@pytest.fixture(scope="session")
def build_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("build") / "ficha.html"
    r = subprocess.run([sys.executable, str(ROOT / "build.py"), "--out", str(out)],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return out.parent


@pytest.fixture(scope="session")
def ficha(build_dir):
    return build_dir / "ficha.html"


@pytest.fixture(scope="session")
def index(build_dir):
    return build_dir / "index.html"


@pytest.fixture(scope="session")
def browser():
    sync_api = pytest.importorskip("playwright.sync_api")
    with sync_api.sync_playwright() as pw:
        b = pw.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def contexto(browser):
    ctx = browser.new_context(accept_downloads=True, viewport={"width": 1400, "height": 1300})
    yield ctx
    ctx.close()


@pytest.fixture
def abrir(contexto):
    """abrir(ruta) -> page. Todas las paginas comparten el contexto del test
    (mismo localStorage). Al terminar, exige 0 errores JS."""
    paginas = []

    def _abrir(ruta):
        pg = contexto.new_page()
        pg.errores = []
        pg.on("pageerror", lambda e: pg.errores.append(str(e)))
        pg.goto(pathlib.Path(ruta).resolve().as_uri())
        pg.wait_for_timeout(150)
        paginas.append(pg)
        return pg

    yield _abrir
    errores = [e for pg in paginas for e in pg.errores]
    assert not errores, "errores JS: %s" % errores
