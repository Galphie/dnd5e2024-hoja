# -*- coding: utf-8 -*-
"""Tests unitarios de las funciones Python del build (sin navegador).

Cubre: _fix_pool (limpieza del pool), _build_pool.build_rows,
_build_info.build_info, _assemble (need/apply/replace_var_block/
aplicar_parches/inject_pwa/inject_version), _verify_pool.verificar y
build.vaciar_html.

Uso:  python -m pytest tests/test_unit_py.py -v
"""
import json
import pathlib

import pytest

import _assemble
import _build_info
import _build_pool
import _fix_pool as fp
import _verify_pool
import build

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = (ROOT / "referencias" / "_ficha_backup_pool.html").read_text(encoding="utf-8")


# ======================================================================
# _fix_pool
# ======================================================================
class TestFixPool:
    @pytest.mark.parametrize("entrada,esperado", [
        ("Ánima Ñandú", "anima nandu"),
        ("", ""),
        (None, ""),
    ])
    def test_norm(self, entrada, esperado):
        assert fp.norm(entrada) == esperado

    @pytest.mark.parametrize("entrada,esperado", [
        ("bola de fuego de la muerte", "Bola de Fuego de la Muerte"),
        ("DE LA NADA", "De la Nada"),                 # primera palabra siempre en mayuscula
        ("“mano” de mago", "Mano de Mago"),  # comillas tipograficas fuera
        ("   ", ""),
        (None, ""),
    ])
    def test_title_es(self, entrada, esperado):
        assert fp.title_es(entrada) == esperado

    @pytest.mark.parametrize("entrada,esperado", [
        ("Texto final 339 2 Xx", "Texto final"),
        ("Texto final 12 e", "Texto final"),
        ("Texto Pg.", "Texto"),
        ("Texto 241", "Texto"),
        ("Sin basura", "Sin basura"),
    ])
    def test_strip_trailing_junk(self, entrada, esperado):
        assert fp._strip_trailing_junk(entrada) == esperado

    def test_strip_trailing_junk_banner_conjuros(self):
        assert fp._strip_trailing_junk("Texto CONJUROS 309") == "Texto"

    @pytest.mark.parametrize("entrada,esperado", [
        ("Hola. CON SU CONJURO, basura", "Hola."),
        ("Fin li ABCDEF resto", "Fin"),
        ("a AFECTADO POR EL CONJURO x", "a"),
        ("a APÉNDICE A EL MULTIVERSO x", "a"),
        ("texto 343 /", "texto"),
        ("intacto", "intacto"),
    ])
    def test_cut_glued(self, entrada, esperado):
        assert fp._cut_glued(entrada) == esperado

    @pytest.mark.parametrize("entrada,esperado", [
        ("uno | 241 | dos", "uno dos"),
        ("uno 243 sigue", "uno sigue"),
        ("tira 100 Dados", "tira 100 Dados"),      # mayuscula detras: no es pagina
    ])
    def test_strip_mid_pages(self, entrada, esperado):
        assert fp._strip_mid_pages(entrada) == esperado

    @pytest.mark.parametrize("entrada,esperado", [
        ("1410 y 1412", "1d10 y 1d12"),
        ("íd10 o í d10", "1d10 o 1d10"),
        ("Tira 148", "Tira 1d8"),
        ("tira 148 para", "tira 1d8 para"),
        ("velocidad de O", "velocidad de 0"),
        ("sus puntos de golpe se reducen a O", "sus puntos de golpe se reducen a 0"),
        ("a O m de altura", "a 0 m de altura"),
        ("hasta que llegue a O m", "hasta que llegue a 0 m"),
        ("fin cas AS", "fin "),
    ])
    def test_fix_ocr(self, entrada, esperado):
        assert fp._fix_ocr(entrada) == esperado

    @pytest.mark.parametrize("entrada,esperado", [
        ("1 minuto Este conjuro", "Este conjuro"),
        ("10 horas. Texto", "Texto"),
        ("2 días Texto", "Texto"),
        ("Este conjuro dura 1 minuto", "Este conjuro dura 1 minuto"),
    ])
    def test_strip_leading_du(self, entrada, esperado):
        assert fp._strip_leading_du(entrada) == esperado

    def test_clean_dl_combina_limpiezas(self):
        assert fp.clean_dl("  1 minuto Hace 1410 de dano | 241 | fin 339  ") == "Hace 1d10 de dano fin"

    def test_clean_dl_vacio(self):
        assert fp.clean_dl(None) == ""
        assert fp.clean_dl("") == ""

    def test_clean_dl_pipes_y_corchetes(self):
        assert fp.clean_dl("por | aptitud mágica. ] Con algo] fin") == "por aptitud mágica. Con algo fin"

    @pytest.mark.parametrize("dl,esperado", [
        ("Sufre 8d6 de daño de fuego y 2d6 de daño de frío.", "8d6 fuego + 2d6 frío"),
        ("Recibe 1d10 de daño necrótico.", "1d10 necrótico"),
        ("Infliges 1d6 daño adicional", "1d6 adicional"),
        ("Haces 3d4 de daño", "3d4"),
        ("La criatura recupera 2d8 más tu modificador de aptitud.", "2d8+mod PG"),
        ("El objetivo recupera 1d4 puntos de golpe.", "1d4 PG"),
        ("Creas una alarma contra los intrusos dentro del área elegida por ti, etc.",
         "alarma contra los intrusos dentro"),
        ("Elige.", "—"),
        ("", ""),
    ])
    def test_extract_nota(self, dl, esperado):
        assert fp.extract_nota(dl) == esperado

    def test_extract_nota_max_5_danos(self):
        tipos = ["fuego", "frío", "ácido", "trueno", "veneno", "radiante"]
        dl = " ".join("1d6 de daño de %s." % t for t in tipos)
        assert fp.extract_nota(dl).count(" + ") == 4

    def test_extract_nota_curacion_mayuscula(self):
        assert fp.extract_nota("Recuperas 1d4 puntos de golpe.") == "1d4 PG"
        assert fp.extract_nota("Recupera 2d8 MÁS TU MODIFICADOR de aptitud.") == "2d8+mod PG"

    @pytest.mark.parametrize("entrada,esperado", [("Fuego", "Fuego"), ("FRÍO", "Frio"), ("", "")])
    def test_type_name(self, entrada, esperado):
        assert fp.type_name(entrada) == esperado

    def test_fix_entry_no_muta_entrada(self):
        e = {"nombre": "bola de fuego", "dl": "x"}
        fp.fix_entry(e)
        assert e == {"nombre": "bola de fuego", "dl": "x"}

    def test_fix_entry_title_dl_nota(self):
        r = fp.fix_entry({"nombre": "rayo de escarcha", "dl": "Sufre 1d8 de daño de frío. 241"})
        assert r["nombre"] == "Rayo de Escarcha"
        assert r["dl"] == "Sufre 1d8 de daño de frío."
        assert r["nota"] == "1d8 frío"

    def test_fix_entry_timefix_rangefix(self):
        assert fp.fix_entry({"nombre": "ESCUDO", "dl": "x", "tm": "1 accion"})["tm"] == "Reacción"
        assert fp.fix_entry({"nombre": "castigo tronante", "dl": "x", "rg": "?"})["rg"] == "Lanzador"

    def test_fix_entry_nota_extra(self):
        assert fp.fix_entry({"nombre": "brazos de hadar", "dl": ""})["nota"] == "1d8 necrótico"
        cruzada = {"nombre": "buenas bayas", "dl": "Los objetos inflamables arden 1d4 daño de fuego"}
        assert fp.fix_entry(cruzada)["nota"] == "10 bayas, curan 1 PG"


# ======================================================================
# _build_pool / _build_info
# ======================================================================
FICHA_WEB = [{"nombre_pool": "rayo de fuego", "ficha": "Rayo de Fuego Oficial",
              "slug": "rayo-de-fuego", "pagina": 270}]


def _pool_entry(**kw):
    e = {"nombre": "Rayo de Fuego", "niv": 0, "tm": "Acción", "rg": "36 m", "du": "Instantáneo",
         "comp": "V, S", "M": "", "nota": "1d10 fuego", "dl": "Lanzas una mota.", "pg": 270}
    e.update(kw)
    return e


class TestBuildPool:
    def test_norm(self):
        assert _build_pool.norm("Ácido") == "acido"

    def test_nombre_oficial_y_formato(self):
        rows = _build_pool.build_rows([_pool_entry()], FICHA_WEB)
        assert rows == [["Rayo de Fuego Oficial", 0, "Acción", "36 m", 0, 0, 0, "1d10 fuego", ""]]

    def test_sin_oficial_usa_title_es(self):
        rows = _build_pool.build_rows([_pool_entry(nombre="muro de fuego")], FICHA_WEB)
        assert rows[0][0] == "Muro de Fuego"

    def test_flags_conc_ritual_material(self):
        e = _pool_entry(du="Concentración, hasta 1 minuto", comp="V, S, M, R", M="un rubí")
        assert _build_pool.build_rows([e], [])[0][4:7] == [1, 1, 1]

    def test_descarta_sin_nombre_y_rellena_vacios(self):
        rows = _build_pool.build_rows([_pool_entry(nombre=""), _pool_entry(tm=None, rg=None, nota=None)], [])
        assert len(rows) == 1
        assert rows[0][2:4] == ["", ""] and rows[0][7] == ""

    def test_pool_js_ascii(self):
        js = _build_pool.pool_js_de([["Acción ñ", 1]])
        assert js.startswith("var SPELL_POOL=") and js.endswith(";")
        assert js.isascii()
        assert json.loads(js[len("var SPELL_POOL="):-1]) == [["Acción ñ", 1]]


class TestBuildInfo:
    def test_norm(self):
        assert _build_info.norm("Ráfaga") == "rafaga"

    def test_clave_oficial_slug_y_pagina(self):
        info = _build_info.build_info([_pool_entry()], FICHA_WEB)
        assert info == {"rayo de fuego oficial": {
            "n": "Rayo de Fuego Oficial", "p": 270, "d": "Lanzas una mota.",
            "u": "https://www.aidedd.org/spell/es/rayo-de-fuego"}}

    def test_sin_oficial_sin_slug(self):
        info = _build_info.build_info([_pool_entry(nombre="Muro de Fuego")], FICHA_WEB)
        assert info["muro de fuego"]["u"] == ""
        assert info["muro de fuego"]["n"] == "Muro de Fuego"

    def test_descarta_sin_descripcion_o_pagina(self):
        assert _build_info.build_info([_pool_entry(dl=""), _pool_entry(pg=None)], []) == {}

    def test_deduplica(self):
        info = _build_info.build_info([_pool_entry(dl="A"), _pool_entry(dl="B")], [])
        assert len(info) == 1 and info["rayo de fuego"]["d"] == "A"

    def test_info_js_ascii(self):
        js = _build_info.info_js_de({"a": {"d": "daño"}})
        assert js.isascii() and js.startswith("var SPELL_INFO=")


# ======================================================================
# _assemble
# ======================================================================
class TestAssemble:
    def test_need(self):
        _assemble.need("x", True, False)
        with pytest.raises(AssertionError, match=r"\[x\] ancla no encontrada"):
            _assemble.need("x", False, True)

    def test_apply_reemplaza_una_vez(self):
        assert _assemble.apply("a a", "a", "b", "t") == "b a"

    def test_apply_idempotente(self):
        assert _assemble.apply("ya b", "a", "b", "t") == "ya b"

    def test_apply_ancla_ausente(self):
        with pytest.raises(AssertionError):
            _assemble.apply("xyz", "a", "b", "t")

    def test_replace_var_block_anidado(self):
        txt = 'antes;var X={"a":{"b":{}},"c":"x;y"};despues'
        assert _assemble.replace_var_block(txt, "var X=", "var X={};") == "antes;var X={};despues"

    def test_replace_var_block_sin_ancla(self):
        with pytest.raises(AssertionError):
            _assemble.replace_var_block("nada", "var X=", "")

    def test_aplicar_parches_sobre_plantilla(self):
        out = _assemble.aplicar_parches(TEMPLATE, "var SPELL_POOL=[];", 'var SPELL_INFO={"k":1};')
        assert 'var SPELL_INFO={"k":1};' in out
        assert out.count("var SPELL_POOL=[];") == 1
        assert out.index("var SPELL_POOL=[];") < out.index("function spellRow(s){")
        assert "SPELLS.filter" not in out and "SPELLS.slice" not in out
        assert "list=list.slice(0,1000);" in out
        assert "nt.value=s[7]||'';" in out
        assert 'data-tt="crm"' in out and 'data-tt="atk-bono"' in out
        assert "Tooltips de cabecera de tablas" in out
        assert "SPELL_POOL.forEach(function(s){html+=spellRow(s);});" not in out  # parche 7 retirado

    def test_inject_pwa_idempotente(self):
        html = "<html><head><title>x</title></head><body></body></html>"
        once = _assemble.inject_pwa(html)
        assert '<link rel="manifest" href="manifest.json">' in once
        assert "serviceWorker.register" in once
        assert 'name="theme-color"' in once and "apple-mobile-web-app-capable" in once
        assert _assemble.inject_pwa(once) == once

    def test_inject_version_idempotente(self):
        html = "<nav>x</nav>"
        once = _assemble.inject_version(html)
        assert "v%s · Galphie" % _assemble.VERSION in once
        assert _assemble.inject_version(once) == once

    def test_tooltips_ascii_con_tildes_escapadas(self):
        # ASCII puro en el fichero, pero las tildes llegan al navegador via \uXXXX
        assert _assemble.TOOLTIPS_JS.isascii()
        assert "Concentraci\\u00f3n" in _assemble.TOOLTIPS_JS

    def test_version_desde_package_json(self):
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        assert _assemble.VERSION == pkg["version"]

    def test_sw_con_version_sustituye_y_es_determinista(self):
        sw = (ROOT / "referencias" / "sw.js").read_text(encoding="utf-8")
        assert sw.count("__BUILD__") == 1, "el placeholder solo debe ir en CACHE_NAME"
        a = _assemble.sw_con_version(sw, "<html>1</html>")
        assert "__BUILD__" not in a
        assert a == _assemble.sw_con_version(sw, "<html>1</html>")
        assert a != _assemble.sw_con_version(sw, "<html>2</html>")

    def test_sw_con_version_sin_placeholder(self):
        with pytest.raises(AssertionError):
            _assemble.sw_con_version("const CACHE_NAME = 'x';", "<html/>")


# ======================================================================
# _verify_pool
# ======================================================================
class TestVerifyPool:
    def test_build_real_pasa(self, ficha):
        res = _verify_pool.verificar(ficha.read_text(encoding="utf-8"))
        assert all(ok for ok, _ in res), [m for ok, m in res if not ok]

    def test_scripts_ascii(self, ficha, index):
        import re
        for f in (ficha, index):
            for s in re.findall(r"<script>(.*?)</script>", f.read_text(encoding="utf-8"), re.S):
                assert s.isascii(), f.name

    def test_detecta_fallos(self, ficha):
        html = ficha.read_text(encoding="utf-8").replace("</div>", "", 1).replace(
            "list=list.slice(0,1000);", "list=list.slice(0,200);")
        fallos = [m for ok, m in _verify_pool.verificar(html) if not ok]
        assert "balance div" in fallos and "slice(0,1000)" in fallos


# ======================================================================
# build.vaciar_html
# ======================================================================
@pytest.fixture(scope="module")
def vacia(ficha):
    return build.vaciar_html(ficha.read_text(encoding="utf-8"))


class TestVaciarHtml:
    def test_title(self, vacia):
        assert "<title>Ficha D&D 2024</title>" in vacia

    def test_inputs_textareas_checks_selects(self, vacia):
        assert 'value="Nake Nicky"' not in vacia
        assert "Expulsado de su clan" not in vacia
        assert '<option value="INT" selected>' not in vacia
        assert 'class="dot E" checked' not in vacia

    def test_flag_ficha_vacia(self, vacia):
        assert "var FICHA_VACIA=true;" in vacia and "var FICHA_VACIA=false;" not in vacia

    def test_texto_bitacora_sin_barras(self, vacia):
        assert "texto:''" in vacia and "texto:\\'" not in vacia
        assert "Nake Nicky se declara" not in vacia

    def test_no_toca_codigo_js(self, ficha, vacia):
        orig = ficha.read_text(encoding="utf-8")
        for frag in ["function spellRow(s){", "(s[4]?'checked':'')", "var SPELL_POOL=", "function aplicar(d){"]:
            assert vacia.count(frag) == orig.count(frag)

    def test_sin_ancla_falla(self):
        with pytest.raises(AssertionError, match="FICHA_VACIA"):
            build.vaciar_html("<html></html>")

    def test_index_generado_igual(self, ficha, index):
        assert index.read_text(encoding="utf-8") == build.vaciar_html(ficha.read_text(encoding="utf-8"))
