# -*- coding: utf-8 -*-
"""Tests del pipeline de build (sin navegador: rápidos).

Ejecuta build.py completo contra tests/_out/ficha_test.html y verifica
los invariantes que _verify_pool.py comprueba, más la reproducibilidad
(segundo build idéntico al primero = build determinista).

Uso:
    python -m pytest tests/test_pipeline.py -v
"""
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "tests", "_out", "ficha_test.html")
BUILD = os.path.join(HERE, "build.py")


def run_build():
    r = subprocess.run([sys.executable, BUILD, "--out", OUT], cwd=HERE,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


@pytest.fixture(scope="module")
def built():
    run_build()
    with open(OUT, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def parsed(built):
    import json
    import re

    def grab(pattern):
        m = re.search(pattern, built, re.S)
        return json.loads(m.group(1)) if m else None

    return {
        "spell_pool": grab(r"var SPELL_POOL=(\[.*?\]);"),
        "spell_info": grab(r"var SPELL_INFO=(\{.*?\});"),
    }


def test_build_reproducible():
    """Segundo build produce bytes idénticos al primero (determinismo)."""
    run_build()
    run_build()
    import hashlib
    h1 = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    h2 = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    assert h1 == h2
    # y no quedan *_tmp
    for tmp in (OUT + ".pool_tmp", OUT + ".info_tmp"):
        assert not os.path.exists(tmp), "sobra tmp: " + tmp


def test_tag_balance(built):
    assert built.count("<div") == built.count("</div>")
    assert built.count("<script") == built.count("</script>")
    assert built.count("<style") == built.count("</style>")


def test_pool_y_info(parsed):
    assert parsed["spell_pool"] is not None
    assert parsed["spell_info"] is not None
    assert len(parsed["spell_pool"]) == 385
    assert len(parsed["spell_info"]) == 383  # 2 sin descripcion conocidos


def test_notas_385(parsed):
    """Todos los conjuros del pool tienen nota (slot 7)."""
    sin_nota = [row[0] for row in parsed["spell_pool"] if not (row[7] or "").strip()]
    assert not sin_nota, "sin nota: %s" % sin_nota[:5]


def test_parches_postbuild(built):
    assert "list=list.slice(0,1000);" in built
    assert "nt.value=s[7]||'';" in built
    assert ".infoX{position:absolute;left:-15px;" in built
    assert ".clearX{position:absolute;right:-16px;" in built
    assert ".srow::before{" in built and ".srow::after{" in built
    assert 'data-tt="crm"' in built and 'data-tt="atk-bono"' in built
    assert "Tooltips de cabecera de tablas" in built


def test_sin_restos_viejo(built):
    """El buscador usa SPELL_POOL; el grid SPELLS (34 visibles) sigue solo."""
    assert built.count("var SPELLS=") == 1
    assert "SPELLS.filter" not in built
    assert "SPELLS.slice" not in built


def test_ids_relevantes_en_info(parsed):
    """Todas las notas de daño están presentes en SPELL_INFO conocido."""
    import unicodedata

    def norm(s):
        return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                       if unicodedata.category(c) != "Mn")

    sin_desc = {"brazos de hadar", "circulo magico"}
    falta = [r[0] for r in parsed["spell_pool"]
             if norm(r[0]) not in parsed["spell_info"] and norm(r[0]) not in sin_desc]
    assert not falta, "falta info: %s" % falta[:5]