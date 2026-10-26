# -*- coding: utf-8 -*-
"""Tests unitarios del JS de la ficha (Playwright, Chromium headless).

Cada test abre la ficha construida en un contexto nuevo (localStorage
limpio) y llama a las funciones globales directamente; las funciones
internas de los bloques (function(){...})() se prueban por su efecto
en el DOM. Cualquier error JS en la pagina hace fallar el test.

Uso:  python -m pytest tests/test_unit_js.py -v
"""
import json
import pathlib

import pytest

pytest.importorskip("playwright.sync_api")

SPELL_ROWS = 35


@pytest.fixture
def pg(abrir, ficha):
    return abrir(ficha)


@pytest.fixture
def pv(abrir, index):
    return abrir(index)


def ev(page, js, arg=None):
    return page.evaluate(js, arg)


def filas(page):
    return ev(page, """()=>[...document.querySelectorAll('#spellrows .srow')].map(r=>({
        nv:r.querySelector('.nv').value,nm:r.querySelector('.nm').value,tm:r.querySelector('.tm').value,
        rg:r.querySelector('.rg').value,nt:r.querySelector('.nt').value,
        crm:[...r.querySelectorAll('.rh')].map(c=>c.checked)}))""")


def importar(page, ruta):
    with page.expect_file_chooser() as fc:
        page.click("#btn-imp")
    fc.value.set_files(str(ruta))
    page.wait_for_timeout(150)
    page.click("#toastBtns .confirm")
    page.wait_for_timeout(150)
    return page.inner_text("#toastMsg")


def descarga(page, boton):
    with page.expect_download() as dl:
        page.click(boton)
    return dl.value


# ======================================================================
# Utilidades DOM: q, qa, gv, sv
# ======================================================================
class TestUtilidades:
    def test_q_qa(self, pg):
        assert ev(pg, "q('#pg1').id") == "pg1"
        assert ev(pg, "q('#noexiste')") is None
        assert ev(pg, "Array.isArray(qa('.page')) && qa('.page').length") == 4
        assert ev(pg, "qa('.sk', q('.ab[data-ab=FUE]')).length") == 2

    def test_gv_sv(self, pg):
        ev(pg, "sv('[data-k=nombre]','Ana')")
        assert ev(pg, "gv('[data-k=nombre]')") == "Ana"
        ev(pg, "sv('[data-k=nombre]',null)")           # null no toca
        assert ev(pg, "gv('[data-k=nombre]')") == "Ana"
        assert ev(pg, "gv('#noexiste')") == ""
        ev(pg, "sv('#noexiste','x')")                   # no lanza


# ======================================================================
# Navegacion
# ======================================================================
class TestShowPage:
    @pytest.mark.parametrize("n", [1, 2, 3, 4])
    def test_muestra_solo_una(self, pg, n):
        ev(pg, "n=>showPage(n)", n)
        visibles = ev(pg, "qa('.page.show').map(p=>p.id)")
        assert visibles == ["pg%d" % n]
        assert ev(pg, "q('#nav .on').getAttribute('data-nav')") == str(n)
        assert ev(pg, "q('#mb').classList.contains('open')") == (n != 1)

    def test_click_nav(self, pg):
        pg.click('#nav [data-nav="3"]')
        assert ev(pg, "q('#pg3').classList.contains('show')")


# ======================================================================
# Calculo: modOf, fmtMod, profVal, abScore, recalc
# ======================================================================
class TestCalculo:
    @pytest.mark.parametrize("v,m", [("10", 0), ("11", 0), ("9", -1), ("1", -5), ("20", 5), ("30", 10),
                                     ("", 0), ("abc", 0), (15, 2)])
    def test_modOf(self, pg, v, m):
        assert ev(pg, "v=>modOf(v)", v) == m

    @pytest.mark.parametrize("n,s", [(0, "+0"), (3, "+3"), (-1, "−1"), (-5, "−5")])   # signo menos tipografico
    def test_fmtMod(self, pg, n, s):
        assert ev(pg, "n=>fmtMod(n)", n) == s

    @pytest.mark.parametrize("v,n", [("+3", 3), ("4", 4), ("-1", -1), ("", 2), ("abc", 2)])
    def test_profVal(self, pg, v, n):
        ev(pg, "v=>{q('#f-prof').value=v}", v)
        assert ev(pg, "profVal()") == n

    def test_abScore(self, pg):
        ev(pg, "q('.ab[data-ab=CAR] .sc').value='17'")
        assert ev(pg, "abScore('CAR')") == "17"
        assert ev(pg, "abScore('XXX')") == "10"

    def test_recalc_modificadores_y_habilidades(self, pg):
        ev(pg, """()=>{q('.ab[data-ab=FUE] .sc').value='15';q('#f-prof').value='+3';
            var sk=qa('.ab[data-ab=FUE] .sk');sk[0].querySelector('.dot').checked=true;sk[1].querySelector('.dot').checked=false;recalc();}""")
        assert ev(pg, "q('.ab[data-ab=FUE] .circle .m').textContent") == "+2"
        assert ev(pg, "q('#mb [data-ab=FUE]').textContent") == "+2"
        assert ev(pg, "qa('.ab[data-ab=FUE] .sk .bon').map(b=>b.textContent)") == ["+5", "+2"]

    def test_recalc_aptitud_magica(self, pg):
        ev(pg, "()=>{q('#apt-stat').value='CAR';q('.ab[data-ab=CAR] .sc').value='18';q('#f-prof').value='+3';recalc();}")
        assert ev(pg, "[q('#m-mod').textContent,q('#m-dc').textContent,q('#m-atk').textContent]") == ["+4", "15", "+7"]

    def test_recalc_subtitulo_bitacora(self, pg):
        ev(pg, "()=>{sv('[data-k=nombre]','Ana');sv('[data-k=clase]','Mago');recalc();}")
        assert ev(pg, "q('#bita-sub').textContent") == "CRÓNICAS DE ANA · MAGO"
        ev(pg, "()=>{sv('[data-k=nombre]','');sv('[data-k=clase]','');recalc();}")
        assert ev(pg, "q('#bita-sub').textContent") == "CRÓNICAS DE —"

    def test_input_dispara_recalc(self, pg):
        pg.fill(".ab[data-ab=DES] .sc", "16")
        assert ev(pg, "q('.ab[data-ab=DES] .circle .m').textContent") == "+3"


# ======================================================================
# Persistencia: newId, staticFields, resStatic, saveNow, saveStatic, isField
# ======================================================================
class TestPersistencia:
    def test_newId_unico(self, pg):
        ids = ev(pg, "Array.from({length:200},newId)")
        assert len(set(ids)) == 200
        assert all(i.isalnum() and i == i.lower() for i in ids)

    def test_staticFields(self, pg):
        assert ev(pg, "staticFields().length") == ev(pg, "document.querySelectorAll('#pg1 .E, #pg2 .E').length")
        assert ev(pg, "staticFields().every(f=>f.classList.contains('E'))")

    def test_resStatic(self, pg):
        ev(pg, """()=>{var n=staticFields().length,a=new Array(n).fill(null);
            var f=staticFields();var i=f.findIndex(x=>x.dataset.k==='nombre');a[i]='Res';
            var j=f.findIndex(x=>x.classList.contains('inspd'));a[j]=1;resStatic(a);}""")
        assert ev(pg, "gv('[data-k=nombre]')") == "Res"
        assert ev(pg, "q('.inspd').checked") is True
        assert ev(pg, "gv('[data-k=clase]')") == "Hechicero"     # null = no se toca

    def test_saveNow(self, pg):
        ev(pg, "()=>{localStorage.clear();sv('[data-k=nombre]','Guardado');saveNow();}")
        d = json.loads(ev(pg, "localStorage.getItem('hermes_ficha_v2')"))
        assert d["identidad"]["nombre"] == "Guardado" and d["_tipo"] == "ficha-dnd2024"

    def test_saveStatic_debounce(self, pg):
        ev(pg, "()=>{localStorage.clear();saveStatic();}")
        assert ev(pg, "localStorage.getItem('hermes_ficha_v2')") is None
        pg.wait_for_timeout(450)
        assert ev(pg, "localStorage.getItem('hermes_ficha_v2')") is not None

    def test_pagehide_vacia_pendiente(self, pg):
        ev(pg, "()=>{localStorage.clear();saveStatic();window.dispatchEvent(new Event('pagehide'));}")
        assert ev(pg, "localStorage.getItem('hermes_ficha_v2')") is not None

    def test_isField(self, pg):
        assert ev(pg, "isField(q('[data-k=nombre]'))") is True
        assert ev(pg, "isField(q('#spellrows .rh'))") is True
        assert ev(pg, "isField(q('#btn-exp'))") is False
        assert ev(pg, "isField(null)") is False

    def test_cambio_crm_guarda(self, pg):
        ev(pg, "localStorage.clear()")
        pg.click('#nav [data-nav="2"]')
        pg.locator("#spellrows .srow .rh").nth(0).click()
        pg.wait_for_timeout(450)
        d = json.loads(ev(pg, "localStorage.getItem('hermes_ficha_v2')"))
        assert d["conjuros"][0]["c"] == ev(pg, "q('#spellrows .rh').checked")


# ======================================================================
# Bloques dinamicos: buildSlots, buildAtk, buildEspe, buildCoins
# ======================================================================
class TestBloques:
    def test_buildSlots(self, pg):
        assert ev(pg, "qa('#slotgrid .slot').length") == 3
        assert ev(pg, "qa('#slotgrid .r').map(r=>r.querySelectorAll('.dslot').length)") == [4, 4, 3, 3, 3, 3, 2, 1, 1]
        assert ev(pg, "qa('#slotgrid .r .rl').map(e=>e.textContent)") == ["NIVEL %d" % i for i in range(1, 10)]
        assert ev(pg, "qa('#slotgrid .tl input').map(i=>i.value)") == ["4", "3"] + [""] * 7

    def test_buildAtk(self, pg):
        rows = ev(pg, "qa('#atkrows .r').map(r=>[...r.querySelectorAll('input')].map(i=>i.value))")
        assert len(rows) == 8 and all(len(r) == 4 for r in rows)
        assert rows[0] == ["Rayo de Fuego", "+6", "2d10 fuego", "Truco"]
        assert rows[-1] == ["", "", "", ""]

    def test_buildEspe(self, pg):
        assert ev(pg, "q('#especRows').value").startswith("Resistencia enana")

    def test_buildCoins(self, pg):
        assert ev(pg, "qa('#coinrows .coin-cell').map(c=>[c.querySelector('.coin-lb').textContent,c.querySelector('input').value])") == \
            [["PC", ""], ["PP", "12"], ["PE", ""], ["PO", "1475"], ["PPT", "8"]]

    def test_rebuild_idempotente(self, pg):
        ev(pg, "()=>{buildSlots();buildAtk();buildCoins();}")
        assert ev(pg, "[qa('#slotgrid .r').length,qa('#atkrows .r').length,qa('#coinrows .coin-cell').length]") == [9, 8, 5]


class TestFichaVacia:
    def test_flag(self, pv, pg):
        assert ev(pv, "FICHA_VACIA") is True
        assert ev(pg, "FICHA_VACIA") is False

    def test_sin_datos_de_ejemplo(self, pv):
        assert ev(pv, "qa('#atkrows input').every(i=>i.value==='')")
        assert ev(pv, "qa('#coinrows input').every(i=>i.value==='')")
        assert ev(pv, "qa('#slotgrid .tl input').every(i=>i.value==='')")
        assert ev(pv, "q('#especRows').value") == ""
        assert all(not f["nm"] for f in filas(pv)) and len(filas(pv)) == SPELL_ROWS
        assert ev(pv, "qa('#bitaList .ses-card').length") == 0
        assert ev(pv, "qa('#compList .comp-card').length") == 0
        assert ev(pv, "q('#compList').classList.contains('has-empty')")
        assert ev(pv, "gv('[data-k=nombre]')") == ""
        assert pv.title() == "Ficha D&D 2024"


# ======================================================================
# Conjuros: spellRow, spellEmpty, setSpells, buildSpells
# ======================================================================
class TestConjuros:
    def test_spellRow(self, pg):
        r = ev(pg, """()=>{var d=document.createElement('div');d.innerHTML=spellRow(['Luz',0,'Accion','Toque',1,0,1,'ilumina','x']);
            var s=d.firstChild;return {cls:s.className,nv:s.querySelector('.nv').value,nm:s.querySelector('.nm').value,
            tm:s.querySelector('.tm').value,rg:s.querySelector('.rg').value,nt:s.querySelector('.nt').value,
            E:s.querySelectorAll('input.E').length,crm:[...s.querySelectorAll('.rh')].map(c=>c.checked),
            btn:[...s.querySelectorAll('button')].map(b=>b.className)};}""")
        assert r == {"cls": "srow", "nv": "Truco", "nm": "Luz", "tm": "Accion", "rg": "Toque", "nt": "ilumina",
                     "E": 5, "crm": [True, False, True], "btn": ["infoX", "clearX"]}

    def test_spellRow_nivel_y_blanco(self, pg):
        assert ev(pg, "()=>{var d=document.createElement('div');d.innerHTML=spellRow(['X',3,'','',0,0,0,'']);return d.querySelector('.nv').value}") == "3"
        assert ev(pg, "()=>{var d=document.createElement('div');d.innerHTML=spellRow(SPELL_BLANK);return [...d.querySelectorAll('input')].every(i=>i.type==='checkbox'?!i.checked:i.value==='')}")

    @pytest.mark.parametrize("s,vacio", [
        (None, True), ({}, True), ({"nombre": "  ", "notas": ""}, True),
        ({"nombre": "Luz"}, False), ({"c": True}, False), ({"m": 1}, False),
        ({"nivel": 0}, False), ({"rango": "9 m"}, False),
    ])
    def test_spellEmpty(self, pg, s, vacio):
        assert ev(pg, "s=>spellEmpty(s)", s) is vacio

    def test_setSpells_rellena_y_mantiene_35(self, pg):
        sobran = ev(pg, "setSpells([{nivel:'1',nombre:'A',tiempo:'t',rango:'r',c:true,r:false,m:true,notas:'n'}])")
        f = filas(pg)
        assert sobran == 0 and len(f) == SPELL_ROWS
        assert f[0] == {"nv": "1", "nm": "A", "tm": "t", "rg": "r", "nt": "n", "crm": [True, False, True]}
        assert all(not x["nm"] and x["crm"] == [False] * 3 for x in f[1:])

    def test_setSpells_conserva_huecos(self, pg):
        ev(pg, "setSpells([{nombre:'A'},{},{nombre:'B'},{},{}])")
        assert [x["nm"] for x in filas(pg)[:3]] == ["A", "", "B"]

    def test_setSpells_desborde_compacta_huecos(self, pg):
        # 34 conjuros + 2 huecos = 36 > 35: se quita un hueco (el primero), el otro se queda
        lista = [{"nombre": "C%d" % i} for i in range(34)]
        lista.insert(5, {})
        lista.insert(10, {})
        assert ev(pg, "l=>setSpells(l)", lista) == 0
        f = filas(pg)
        assert len(f) == SPELL_ROWS and sum(1 for x in f if not x["nm"]) == 1

    def test_setSpells_mas_que_filas_no_pierde(self, pg):
        lista = [{"nombre": "C%d" % i} for i in range(40)] + [{}] * 5
        assert ev(pg, "l=>setSpells(l)", lista) == 40
        assert [x["nm"] for x in filas(pg)] == ["C%d" % i for i in range(40)]

    def test_setSpells_tipos_y_nulos(self, pg):
        ev(pg, "setSpells([{nivel:0,nombre:'T',tiempo:null}]);")
        f = filas(pg)[0]
        assert f["nv"] == "0" and f["tm"] == ""
        ev(pg, "setSpells(null)")
        assert len(filas(pg)) == SPELL_ROWS

    def test_buildSpells(self, pg):
        ev(pg, "buildSpells()")
        f = filas(pg)
        n = ev(pg, "SPELLS.length")
        assert len(f) == SPELL_ROWS and sum(1 for x in f if x["nm"]) == n
        assert f[0]["nm"] == ev(pg, "SPELLS[0][0]") and f[0]["nv"] == "Truco"

    def test_tabla_cabe_en_el_bloque(self, pg):
        ev(pg, "showPage(2)")
        assert ev(pg, "q('#spellrows .srow:last-child').getBoundingClientRect().bottom<=q('.spin').getBoundingClientRect().bottom")


# ======================================================================
# Conjuros: ordenar, vaciar fila, autocompletado, post-it, modal
# ======================================================================
class TestConjurosUI:
    def test_ordenar_por_nivel(self, pg):
        ev(pg, "setSpells([{nivel:'3',nombre:'C'},{nivel:''},{nivel:'Truco',nombre:'T'},{nivel:'1',nombre:'U'},{nivel:'2*',nombre:'D'}])")
        ev(pg, "showPage(2)")
        pg.click("#btn-sort")
        assert [x["nm"] for x in filas(pg)[:4]] == ["T", "U", "D", "C"]

    def test_vaciar_fila(self, pg):
        ev(pg, "showPage(2)")
        pg.locator("#spellrows .srow").first.hover()
        pg.locator("#spellrows .srow .clearX").first.click()
        assert filas(pg)[0] == {"nv": "", "nm": "", "tm": "", "rg": "", "nt": "", "crm": [False] * 3}

    def test_autocompletado_lista_completa(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([]);}")
        pg.locator("#spellrows .nm").first.focus()
        assert pg.is_visible("#acbox")
        assert ev(pg, "qa('#acbox .ac-item').length") == ev(pg, "Math.min(SPELL_POOL.length,1000)")

    def test_autocompletado_filtra_sin_tildes(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([]);}")
        pg.locator("#spellrows .nm").first.fill("rafaga")
        nombres = ev(pg, "qa('#acbox .ac-item .n').map(e=>e.textContent)")
        assert nombres and all("fag" in n.lower() for n in nombres)

    def test_autocompletado_sin_resultados(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([]);}")
        pg.locator("#spellrows .nm").first.fill("zzzzqqq")
        assert not pg.is_visible("#acbox")

    def test_autocompletado_teclado_rellena(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([]);}")
        nm = pg.locator("#spellrows .nm").first
        nm.fill("bola de fuego")
        nm.press("ArrowDown")
        elegido = ev(pg, "q('#acbox .ac-item.sel .n').textContent")
        nm.press("Enter")
        s = ev(pg, "n=>SPELL_POOL.find(s=>s[0]===n)", elegido)
        f = filas(pg)[0]
        assert f["nm"] == s[0] and f["tm"] == s[2] and f["rg"] == s[3] and f["nt"] == (s[7] or "")
        assert f["nv"] == ("Truco" if s[1] == 0 else str(s[1]))
        assert f["crm"] == [bool(s[4]), bool(s[5]), bool(s[6])]
        assert not pg.is_visible("#acbox")

    def test_autocompletado_escape_y_raton(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([]);}")
        nm = pg.locator("#spellrows .nm").first
        nm.fill("escudo")
        nm.press("Escape")
        assert not pg.is_visible("#acbox")
        nm.fill("escudo")
        pg.locator("#acbox .ac-item").first.dispatch_event("mousedown")
        assert filas(pg)[0]["nm"].lower().startswith("escudo")

    def test_postit_al_pasar_raton(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([{nombre:SPELLS[0][0]},{nombre:'Inventado'}]);}")
        pg.locator("#spellrows .nm").nth(0).hover()
        assert pg.is_visible("#tip") and ev(pg, "SPELLS[0][0]") in pg.inner_text("#tip")
        pg.locator("#spellrows .nm").nth(1).hover()
        assert not pg.is_visible("#tip")

    def test_modal_info(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([{nombre:'Bola de Fuego'}]);}")
        fila = pg.locator("#spellrows .srow").first
        fila.hover()
        fila.locator(".infoX").click()
        assert ev(pg, "q('#mdlOv').classList.contains('open')")
        assert pg.inner_text("#mdlT") == ev(pg, "SPELL_INFO['bola de fuego'].n")
        assert "pág." in pg.inner_text("#mdlP")
        pg.keyboard.press("Escape")
        assert not ev(pg, "q('#mdlOv').classList.contains('open')")

    def test_modal_cierre_y_sin_info(self, pg):
        ev(pg, "()=>{showPage(2);setSpells([{nombre:'Bola de Fuego'},{nombre:'No existe'}]);}")
        filas_ = pg.locator("#spellrows .srow")
        filas_.nth(0).hover()
        filas_.nth(0).locator(".infoX").click()
        pg.click("#mdlX")
        assert not ev(pg, "q('#mdlOv').classList.contains('open')")
        filas_.nth(0).hover()
        filas_.nth(0).locator(".infoX").click()
        pg.mouse.click(5, 5)                                   # click en el overlay
        assert not ev(pg, "q('#mdlOv').classList.contains('open')")
        filas_.nth(1).hover()
        filas_.nth(1).locator(".infoX").click()
        assert not ev(pg, "q('#mdlOv').classList.contains('open')")

    def test_modal_enlace_oculto_sin_slug(self, pg):
        sin_slug = ev(pg, "Object.keys(SPELL_INFO).find(k=>!SPELL_INFO[k].u)")
        con_slug = ev(pg, "Object.keys(SPELL_INFO).find(k=>SPELL_INFO[k].u)")
        for k, visible in ((sin_slug, False), (con_slug, True)):
            ev(pg, "k=>{showPage(2);setSpells([{nombre:SPELL_INFO[k].n}]);}", k)
            fila = pg.locator("#spellrows .srow").first
            fila.hover()
            fila.locator(".infoX").click()
            assert pg.is_visible("#mdlL") is visible
            pg.keyboard.press("Escape")

    @pytest.mark.parametrize("tt,texto", [("crm", "Concentración"), ("nivel", "NIVEL"), ("atk-bono", "BONIFICADOR")])
    def test_tooltips_cabecera(self, pg, tt, texto):
        ev(pg, "showPage(%d)" % (1 if tt.startswith("atk") else 2))
        pg.hover('span[data-tt="%s"]' % tt)
        assert pg.is_visible("#tip") and texto in pg.inner_text("#tip")


# ======================================================================
# Bitacora y companeros
# ======================================================================
class TestBitacora:
    def test_ejemplo_inicial(self, pg):
        assert ev(pg, "qa('#bitaList .ses-card').length") == 2

    def test_anadir_numerar_guardar(self, pg):
        ev(pg, "showPage(3)")
        pg.click("#btn-addses")
        assert ev(pg, "qa('#bitaList .ses-num').map(e=>e.textContent)") == ["SESIÓN 1", "SESIÓN 2", "SESIÓN 3"]
        pg.locator("#bitaList .ses-ti").last.fill("Nueva")
        assert json.loads(ev(pg, "localStorage.getItem('hermes_bitacora_v1')"))[-1]["titulo"] == "Nueva"
        assert ev(pg, "__sesData()")[-1]["titulo"] == "Nueva"

    def test_eliminar_con_confirmacion(self, pg):
        ev(pg, "showPage(3)")
        pg.locator("#bitaList .ses-x").first.click()
        pg.click("#toastBtns .cancel")
        assert ev(pg, "qa('#bitaList .ses-card').length") == 2
        pg.locator("#bitaList .ses-x").first.click()
        pg.click("#toastBtns .confirm")
        assert ev(pg, "qa('#bitaList .ses-num').map(e=>e.textContent)") == ["SESIÓN 1"]

    def test_edicion_entra_en_snapshot(self, pg):
        ev(pg, "showPage(3)")
        pg.locator("#bitaList .ses-te").first.fill("Texto editado")
        pg.wait_for_timeout(450)
        d = json.loads(ev(pg, "localStorage.getItem('hermes_ficha_v2')"))
        assert d["bitacora"][0]["texto"] == "Texto editado"


class TestCompaneros:
    def test_ejemplo_inicial(self, pg):
        assert ev(pg, "__compData().map(c=>c.nombre)") == ["Cría de dragón (ejemplo)"]

    def test_anadir_campos_y_guardar(self, pg):
        ev(pg, "showPage(4)")
        pg.click("#btn-addcomp")
        card = pg.locator("#compList .comp-card").last
        card.locator(".comp-nombre").fill("Lobo")
        card.locator(".cf-fue").fill("+2")
        card.locator(".cf-notas").fill("leal")
        d = ev(pg, "__compData()")[-1]
        assert d["nombre"] == "Lobo" and d["fue"] == "+2" and d["notas"] == "leal"
        assert set(d) == {"nombre", "tipo", "tamano", "origen", "ca", "pg", "vel", "ini", "fue", "des",
                          "con", "int", "sab", "car", "ataques", "rasgos", "notas"}
        assert json.loads(ev(pg, "localStorage.getItem('hermes_companeros_v1')"))[-1]["nombre"] == "Lobo"

    def test_eliminar_y_estado_vacio(self, pg):
        ev(pg, "showPage(4)")
        assert not ev(pg, "q('#compList').classList.contains('has-empty')")
        pg.locator("#compList .comp-del").first.click()
        pg.click("#toastBtns .confirm")
        assert ev(pg, "qa('#compList .comp-card').length") == 0
        assert ev(pg, "q('#compList').classList.contains('has-empty')")


# ======================================================================
# Export / import: recolectar, aplicar, avisoSobran
# ======================================================================
CLAVES = {"_tipo", "_fecha", "_id", "identidad", "estado", "caracteristicas", "habilidades", "ataques",
          "conjuros", "espacios", "textos", "monedas", "entrenamiento", "rasgosClase", "rasgosEspecie",
          "dotes", "sintonizacion", "bitacora", "companeros", "foto"}


class TestRecolectar:
    def test_estructura(self, pg):
        d = ev(pg, "recolectar()")
        assert set(d) == CLAVES
        assert d["_id"] == ev(pg, "FICHA_ID") and d["_tipo"] == "ficha-dnd2024"
        assert set(d["identidad"]) == {"nombre", "trasfondo", "clase", "especie", "subclase", "nivel", "px",
                                       "aptitudEstadistica"}
        assert set(d["estado"]) == {"iniciativa", "velocidad", "tamano", "percepcion", "ca", "competencia",
                                    "pg", "dados", "inspiracion", "escudo", "salvMuerte"}
        assert len(d["estado"]["pg"]) == 3 and len(d["estado"]["dados"]) == 2
        assert len(d["estado"]["salvMuerte"]) == 6
        assert len(d["ataques"]) == 8 and len(d["espacios"]) == 9 and len(d["sintonizacion"]) == 3
        assert list(d["caracteristicas"]) == ["FUE", "DES", "CON", "INT", "SAB", "CAR"]
        assert set(d["monedas"]) == {"PC", "PP", "PE", "PO", "PPT"}
        assert len(d["habilidades"]) == ev(pg, "qa('.sk').length")
        assert set(d["entrenamiento"]["armaduras"]) == {"Ligeras", "Pesadas", "Medianas", "Escudos"}
        assert len(d["rasgosClase"]) == 2

    def test_conjuros_sin_vacios_al_final(self, pg):
        ev(pg, "setSpells([{nombre:'A'},{},{nombre:'B'}])")
        assert [c["nombre"] for c in ev(pg, "recolectar().conjuros")] == ["A", "", "B"]
        ev(pg, "setSpells([])")
        assert ev(pg, "recolectar().conjuros") == []

    def test_valores(self, pg):
        ev(pg, "()=>{q('.esc-d').checked=true;qa('.sv .dslot')[4].checked=true;var r=qa('.atun-r')[1];r.querySelector('.d').checked=true;r.querySelector('.line').value='Anillo';}")
        d = ev(pg, "recolectar()")
        assert d["estado"]["escudo"] is True
        assert d["estado"]["salvMuerte"] == [False, False, False, False, True, False]
        assert d["sintonizacion"][1] == {"check": True, "texto": "Anillo"}


class TestAplicar:
    def test_ida_y_vuelta(self, pg):
        d = ev(pg, "recolectar()")
        ev(pg, "vaciarHoja()")
        ev(pg, "d=>aplicar(d)", d)
        d2 = ev(pg, "recolectar()")
        for k in ("_fecha", "_id"):
            d.pop(k), d2.pop(k)
        assert d2 == d

    def test_parcial_solo_toca_lo_que_trae(self, pg):
        antes = ev(pg, "recolectar()")
        ev(pg, "aplicar({identidad:{nombre:'Solo nombre'}})")
        despues = ev(pg, "recolectar()")
        assert despues["identidad"]["nombre"] == "Solo nombre"
        for k in ("estado", "caracteristicas", "conjuros", "bitacora", "companeros", "textos"):
            assert despues[k] == antes[k], k

    @pytest.mark.parametrize("d", [None, 5, "texto"])
    def test_no_objeto_no_hace_nada(self, pg, d):
        antes = ev(pg, "recolectar().identidad")
        assert ev(pg, "d=>aplicar(d)", d) is None
        assert ev(pg, "recolectar().identidad") == antes

    def test_competencias_alias(self, pg):
        ev(pg, "aplicar({competencias:{'FUE:Atletismo':true,'CAR:Persuasión':false}})")
        assert ev(pg, "qa('.ab[data-ab=FUE] .sk')[1].querySelector('.dot').checked") is True
        assert ev(pg, "qa('.ab[data-ab=CAR] .sk')[4].querySelector('.dot').checked") is False

    def test_alineamiento_en_identidad(self, pg):
        ev(pg, "aplicar({identidad:{alineamiento:'Legal Bueno'}})")
        assert ev(pg, "gv('.algn input')") == "Legal Bueno"

    def test_companeros_cada_uno_en_su_ficha(self, pg):
        ev(pg, "aplicar({companeros:[{nombre:'A',ca:'10'},{nombre:'B',ca:'11'},{nombre:'C',ca:'12'}]})")
        assert ev(pg, "__compData().map(c=>[c.nombre,c.ca])") == [["A", "10"], ["B", "11"], ["C", "12"]]
        ev(pg, "aplicar({companeros:[]})")
        assert ev(pg, "q('#compList').classList.contains('has-empty')")

    def test_bitacora(self, pg):
        ev(pg, "aplicar({bitacora:[{fecha:'1/1',lugar:'L',titulo:'T',texto:'X'}]})")
        assert ev(pg, "__sesData()") == [{"fecha": "1/1", "lugar": "L", "titulo": "T", "texto": "X"}]
        assert json.loads(ev(pg, "localStorage.getItem('hermes_bitacora_v1')"))[0]["titulo"] == "T"

    def test_vacios_explicitos_limpian(self, pg):
        ev(pg, "aplicar({rasgosEspecie:'',dotes:''})")
        assert ev(pg, "q('#especRows').value") == "" and ev(pg, "gv('.dt-l textarea')") == ""

    def test_escudo_salvaciones_sintonizacion(self, pg):
        ev(pg, "aplicar({estado:{escudo:true,salvMuerte:[true,false,true]},sintonizacion:[{check:true,texto:'Capa'}]})")
        assert ev(pg, "q('.esc-d').checked") is True
        assert ev(pg, "qa('.sv .dslot').slice(0,3).map(c=>c.checked)") == [True, False, True]
        assert ev(pg, "[qa('.atun-r .d')[0].checked,qa('.atun-r .line')[0].value]") == [True, "Capa"]

    def test_devuelve_sobrantes(self, pg):
        assert ev(pg, "aplicar({conjuros:[{nombre:'A'}]})") == 0
        assert ev(pg, "aplicar({conjuros:Array.from({length:37},(_, i)=>({nombre:'C'+i}))})") == 37

    def test_avisoSobran(self, pg):
        assert ev(pg, "avisoSobran(0)") == ""
        txt = ev(pg, "avisoSobran(40)")
        assert "40" in txt and "35" in txt


# ======================================================================
# Botones: exportar, importar, guardar, vaciar; toast/confirm
# ======================================================================
class TestBotones:
    def test_slugNombre(self, pg):
        casos = {"Ñandú  el Grande!": "Nandu_el_Grande", "Parry Cogsworth": "Parry_Cogsworth",
                 "": "ficha", "***": "ficha", "  Ana  ": "Ana"}
        for nombre, slug in casos.items():
            ev(pg, "n=>sv('[data-k=nombre]',n)", nombre)
            assert ev(pg, "slugNombre()") == slug, nombre

    def test_jsonInScript(self, pg):
        d = {"a": "</script><!-- & ñ   >", "b": [1, None, True]}
        s = ev(pg, "d=>jsonInScript(d)", d)
        assert s.isascii() and "<" not in s and ">" not in s and "&" not in s
        assert json.loads(s) == d

    def test_descargar(self, pg):
        with pg.expect_download() as dl:
            ev(pg, "descargar('hola','text/plain','x.txt')")
        assert dl.value.suggested_filename == "x.txt"
        assert pathlib.Path(dl.value.path()).read_text() == "hola"

    def test_exportar(self, pg, tmp_path):
        ev(pg, "sv('[data-k=nombre]','José Pérez')")
        d = descarga(pg, "#btn-exp")
        assert d.suggested_filename == "datos_Jose_Perez.json"
        dest = tmp_path / "x.json"
        d.save_as(dest)
        assert set(json.loads(dest.read_text(encoding="utf-8"))) == CLAVES

    def test_importar(self, pg, tmp_path):
        f = tmp_path / "in.json"
        f.write_text(json.dumps({"identidad": {"nombre": "Importado"}, "conjuros": [{"nombre": "A"}]}), encoding="utf-8")
        id_antes = ev(pg, "FICHA_ID")
        msg = importar(pg, f)
        assert "importados correctamente" in msg and "Ojo" not in msg
        assert ev(pg, "gv('[data-k=nombre]')") == "Importado"
        assert ev(pg, "FICHA_ID") != id_antes

    def test_importar_aviso_desborde(self, pg, tmp_path):
        f = tmp_path / "big.json"
        f.write_text(json.dumps({"conjuros": [{"nombre": "C%d" % i} for i in range(36)]}), encoding="utf-8")
        assert "Ojo" in importar(pg, f)

    def test_importar_cancelar_no_cambia(self, pg, tmp_path):
        f = tmp_path / "in.json"
        f.write_text(json.dumps({"identidad": {"nombre": "No"}}), encoding="utf-8")
        with pg.expect_file_chooser() as fc:
            pg.click("#btn-imp")
        fc.value.set_files(str(f))
        pg.wait_for_timeout(150)
        pg.click("#toastBtns .cancel")
        assert ev(pg, "gv('[data-k=nombre]')") == "Nake Nicky"

    def test_importar_json_invalido(self, pg, tmp_path):
        f = tmp_path / "mal.json"
        f.write_text("{no es json", encoding="utf-8")
        with pg.expect_file_chooser() as fc:
            pg.click("#btn-imp")
        fc.value.set_files(str(f))
        pg.wait_for_timeout(150)
        assert "JSON no válido" in pg.inner_text("#toastMsg")

    def test_guardar_html(self, pg, tmp_path):
        ev(pg, "sv('[data-k=nombre]','Ana Ruiz')")
        id_antes = ev(pg, "FICHA_ID")
        d = descarga(pg, "#btn-guardar")
        assert d.suggested_filename == "ficha_Ana_Ruiz.html"
        assert ev(pg, "FICHA_ID") != id_antes
        dest = tmp_path / "g.html"
        d.save_as(dest)
        html = dest.read_text(encoding="utf-8")
        assert html.startswith("<!DOCTYPE html>")
        assert html.count('<script type="application/json" id="ficha-data">') == 1
        assert 'class="ses-card"' not in html and 'class="comp-card"' not in html
        datos = json.loads(html.split('id="ficha-data">', 1)[1].split("</script>", 1)[0])
        assert datos["identidad"]["nombre"] == "Ana Ruiz" and datos["_id"] == ev(pg, "FICHA_ID")
        assert json.loads(ev(pg, "localStorage.getItem('hermes_ficha_v2')"))["_id"] == datos["_id"]

    def test_vaciarHoja(self, pg):
        id_antes = ev(pg, "FICHA_ID")
        pg.click("#btn-clear")
        pg.click("#toastBtns .confirm")
        assert ev(pg, "qa('#pg1 input:not([type=checkbox]),#pg1 textarea,#pg2 input:not([type=checkbox]),#pg2 textarea').every(e=>e.value==='')")
        assert ev(pg, "qa('input[type=checkbox]').every(c=>!c.checked)")
        assert ev(pg, "q('#apt-stat').selectedIndex") == 0
        assert ev(pg, "FICHA_ID") != id_antes

    def test_showToast(self, pg):
        ev(pg, "showToast('Hola','info')")
        assert ev(pg, "q('#toastOv').classList.contains('open')") and pg.inner_text("#toastMsg") == "Hola"
        assert ev(pg, "qa('#toastBtns button').map(b=>b.textContent)") == ["OK"]
        pg.click("#toastBtns button")
        assert not ev(pg, "q('#toastOv').classList.contains('open')")

    @pytest.mark.parametrize("boton,llamado", [(".cancel", False), (".confirm", True)])
    def test_showConfirm(self, pg, boton, llamado):
        ev(pg, "showConfirm('Seguro?',function(){window.__ok=true})")
        assert ev(pg, "qa('#toastBtns button').map(b=>b.textContent)") == ["Cancelar", "Confirmar"]
        pg.click("#toastBtns " + boton)
        assert ev(pg, "!!window.__ok") is llamado
        assert not ev(pg, "q('#toastOv').classList.contains('open')")


# ======================================================================
# Carga inicial: readEmbedded, migrateLegacy, loadInitial
# ======================================================================
class TestCarga:
    def test_readEmbedded(self, pg):
        assert ev(pg, "readEmbedded()") is None
        ev(pg, "()=>{var s=document.createElement('script');s.type='application/json';s.id='ficha-data';s.textContent='{\"a\":1}';document.head.appendChild(s);}")
        assert ev(pg, "readEmbedded()") == {"a": 1}
        ev(pg, "q('#ficha-data').textContent='5'")
        assert ev(pg, "readEmbedded()") is None
        ev(pg, "q('#ficha-data').textContent='{roto'")
        assert ev(pg, "readEmbedded()") is None

    def test_loadInitial_usa_localStorage(self, pg):
        ev(pg, "()=>{sv('[data-k=nombre]','Persistido');saveNow();}")
        pg.reload()
        assert ev(pg, "gv('[data-k=nombre]')") == "Persistido"

    def test_loadInitial_html_guardado_gana_a_otro_localStorage(self, pg, abrir, tmp_path):
        ev(pg, "sv('[data-k=nombre]','Guardada')")
        dest = tmp_path / "g.html"
        descarga(pg, "#btn-guardar").save_as(dest)
        ev(pg, "()=>{FICHA_ID=newId();sv('[data-k=nombre]','Otra');saveNow();}")
        assert ev(abrir(dest), "gv('[data-k=nombre]')") == "Guardada"

    def test_loadInitial_recupera_cambios_sin_guardar(self, pg, abrir, tmp_path):
        dest = tmp_path / "g.html"
        descarga(pg, "#btn-guardar").save_as(dest)
        p2 = abrir(dest)
        ev(p2, "()=>{sv('[data-k=nombre]','Sin guardar');saveNow();}")
        assert ev(abrir(dest), "gv('[data-k=nombre]')") == "Sin guardar"

    def test_loadInitial_html_guardado_sin_localStorage(self, pg, browser, tmp_path):
        ev(pg, "sv('[data-k=nombre]','Limpia')")
        dest = tmp_path / "g.html"
        descarga(pg, "#btn-guardar").save_as(dest)
        ctx = browser.new_context()
        try:
            p = ctx.new_page()
            p.goto(dest.resolve().as_uri())
            assert ev(p, "gv('[data-k=nombre]')") == "Limpia"
        finally:
            ctx.close()

    def _v1(self, pg, n, personaliza):
        """Construye un array v1 (formato posicional antiguo) con n filas de conjuro."""
        return ev(pg, """([n,pers])=>{
            var el=q('#spellrows'),h='';
            for(var i=0;i<n;i++)h+=spellRow(n===SPELL_POOL.length?SPELL_POOL[i]:SPELL_BLANK);
            el.innerHTML=h;
            pers.forEach(function(p){var r=qa('#spellrows .srow')[p[0]];r.querySelector('.nm').value=p[1];r.querySelector('.nv').value=p[2];});
            sv('[data-k=nombre]','Legado');
            return staticFields().map(function(f){return f.type==='checkbox'?(f.checked?1:0):f.value;});}""",
                  [n, personaliza])

    def test_migrateLegacy_34_filas(self, pg):
        v1 = self._v1(pg, 34, [[0, "Escudo", "1"], [3, "Inventado", "2"]])
        ev(pg, "v=>{localStorage.clear();localStorage.setItem('hermes_ficha_v1',JSON.stringify(v));}", v1)
        pg.reload()
        f = filas(pg)
        assert len(f) == SPELL_ROWS and [x["nm"] for x in f[:4]] == ["Escudo", "", "", "Inventado"]
        esc = ev(pg, "SPELL_POOL.find(s=>s[0].toLowerCase()==='escudo')")
        assert f[0]["crm"] == [bool(esc[4]), bool(esc[5]), bool(esc[6])]       # C/R/M desde el pool
        assert ev(pg, "gv('[data-k=nombre]')") == "Legado"
        pg.wait_for_timeout(450)                                             # guardado con debounce
        assert ev(pg, "!!localStorage.getItem('hermes_ficha_v2')")

    def test_migrateLegacy_385_filas_descarta_pool_intacto(self, pg):
        v1 = self._v1(pg, ev(pg, "SPELL_POOL.length"), [[0, "Mio", "1"], [200, "Otro mio", "3"]])
        ev(pg, "v=>{localStorage.clear();localStorage.setItem('hermes_ficha_v1',JSON.stringify(v));}", v1)
        pg.reload()
        f = filas(pg)
        assert len(f) == SPELL_ROWS
        assert [x["nm"] for x in f if x["nm"]] == ["Mio", "Otro mio"]

    def test_migrateLegacy_estructura_desconocida(self, pg):
        ev(pg, "()=>{localStorage.clear();localStorage.setItem('hermes_ficha_v1',JSON.stringify(['x','y']));}")
        pg.reload()
        assert ev(pg, "gv('[data-k=nombre]')") == "Nake Nicky"
        assert ev(pg, "migrateLegacy()") == 0

    def test_migrateLegacy_sin_datos(self, pg):
        ev(pg, "localStorage.clear()")
        assert ev(pg, "migrateLegacy()") == 0

    def test_v2_tiene_prioridad_sobre_v1(self, pg):
        v1 = self._v1(pg, 34, [])
        ev(pg, "v=>{localStorage.setItem('hermes_ficha_v1',JSON.stringify(v));sv('[data-k=nombre]','V2');saveNow();}", v1)
        pg.reload()
        assert ev(pg, "gv('[data-k=nombre]')") == "V2"


# ======================================================================
# Foto del personaje: fotoValida, setFoto, reducirFoto, botones y modal
# ======================================================================
class TestFoto:
    FOTO = "data:image/jpeg;base64,/9j/AA=="

    def _png(self, page, ruta, w, h):
        import base64
        url = ev(page, """([w,h])=>{var c=document.createElement('canvas');c.width=w;c.height=h;
            var x=c.getContext('2d');x.fillStyle='#a33';x.fillRect(0,0,w,h);return c.toDataURL('image/png');}""", [w, h])
        ruta.write_bytes(base64.b64decode(url.split(",", 1)[1]))
        return ruta

    def _subir(self, page, ruta):
        ev(page, "showPage(2)")
        with page.expect_file_chooser() as fc:
            page.click("#btn-foto")
        fc.value.set_files(str(ruta))
        page.wait_for_selector("#fotoOv.open")

    @pytest.mark.parametrize("v,ok", [(FOTO, True), ("data:image/png;base64,iVBO", True),
                                      ("", False), (None, False), (5, False),
                                      ("javascript:alert(1)", False), ("data:text/html;base64,PGI+", False),
                                      ("https://x/y.jpg", False)])
    def test_fotoValida(self, pg, v, ok):
        assert ev(pg, "v=>fotoValida(v)", v) is ok

    def test_inicial_sin_foto(self, pg):
        assert ev(pg, "FOTO") == "" and ev(pg, "q('#btn-verfoto').disabled")
        assert ev(pg, "recolectar().foto") == ""

    def test_setFoto_habilita_ver(self, pg):
        ev(pg, "v=>setFoto(v)", self.FOTO)
        assert not ev(pg, "q('#btn-verfoto').disabled") and ev(pg, "recolectar().foto") == self.FOTO
        ev(pg, "setFoto('')")
        assert ev(pg, "q('#btn-verfoto').disabled")

    def test_aplicar_con_y_sin_foto(self, pg):
        ev(pg, "v=>aplicar({foto:v})", self.FOTO)
        assert ev(pg, "FOTO") == self.FOTO
        ev(pg, "aplicar({identidad:{nombre:'Otro'}})")  # JSON de otra ficha sin foto
        assert ev(pg, "FOTO") == ""
        ev(pg, "aplicar({foto:'javascript:alert(1)'})")
        assert ev(pg, "FOTO") == ""

    def test_subir_reduce_guarda_y_muestra(self, pg, tmp_path):
        ev(pg, "sv('[data-k=nombre]','Ana Ruiz')")
        self._subir(pg, self._png(pg, tmp_path / "f.png", 2000, 1000))
        assert ev(pg, "FOTO.slice(0,23)") == "data:image/jpeg;base64,"
        dims = ev(pg, "new Promise(r=>{var i=new Image();i.onload=()=>r([i.width,i.height]);i.src=FOTO})")
        assert dims == [1024, 512]
        assert ev(pg, "q('#fotoImg').src") == ev(pg, "FOTO")
        assert pg.inner_text("#fotoT") == "Ana Ruiz"
        assert json.loads(ev(pg, "localStorage.getItem('hermes_ficha_v2')"))["foto"] == ev(pg, "FOTO")
        pg.reload()
        assert ev(pg, "FOTO.slice(0,10)") == "data:image" and not ev(pg, "q('#btn-verfoto').disabled")

    def test_imagen_pequena_no_se_amplia(self, pg, tmp_path):
        self._subir(pg, self._png(pg, tmp_path / "p.png", 40, 30))
        assert ev(pg, "new Promise(r=>{var i=new Image();i.onload=()=>r([i.width,i.height]);i.src=FOTO})") == [40, 30]

    def test_fichero_no_imagen(self, pg, tmp_path):
        f = tmp_path / "x.txt"
        f.write_text("hola", encoding="utf-8")
        ev(pg, "showPage(2)")
        with pg.expect_file_chooser() as fc:
            pg.click("#btn-foto")
        fc.value.set_files(str(f))
        pg.wait_for_selector("#toastOv.open")
        assert "no es una imagen" in pg.inner_text("#toastMsg") and ev(pg, "FOTO") == ""

    def test_modal_cerrar(self, pg):
        ev(pg, "v=>setFoto(v)", self.FOTO)
        ev(pg, "showPage(2)")
        for cerrar in (lambda: pg.click("#fotoX"), lambda: pg.keyboard.press("Escape"),
                       lambda: pg.mouse.click(5, 5)):
            pg.click("#btn-verfoto")
            assert ev(pg, "q('#fotoOv').classList.contains('open')")
            cerrar()
            assert not ev(pg, "q('#fotoOv').classList.contains('open')")
            assert not ev(pg, "q('#fotoImg').hasAttribute('src')")

    def test_ver_sin_foto_no_abre(self, pg):
        ev(pg, "q('#btn-verfoto').click()")
        assert not ev(pg, "q('#fotoOv').classList.contains('open')")

    @pytest.mark.parametrize("boton,queda", [(".cancel", True), (".confirm", False)])
    def test_quitar_foto(self, pg, boton, queda):
        ev(pg, "v=>{setFoto(v);saveNow();}", self.FOTO)
        ev(pg, "showPage(2)")
        pg.click("#btn-verfoto")
        pg.click("#fotoQuitar")
        pg.click("#toastBtns " + boton)
        assert (ev(pg, "FOTO") == self.FOTO) is queda
        assert (json.loads(ev(pg, "localStorage.getItem('hermes_ficha_v2')"))["foto"] == self.FOTO) is queda

    def test_vaciarHoja_quita_foto(self, pg):
        ev(pg, "v=>setFoto(v)", self.FOTO)
        ev(pg, "vaciarHoja()")
        assert ev(pg, "FOTO") == "" and ev(pg, "q('#btn-verfoto').disabled")

    def test_guardar_html_embebe_foto(self, pg, abrir, tmp_path):
        ev(pg, "v=>setFoto(v)", self.FOTO)
        ev(pg, "showPage(2)")
        pg.click("#btn-verfoto")
        pg.keyboard.press("Escape")
        dest = tmp_path / "g.html"
        descarga(pg, "#btn-guardar").save_as(dest)
        html = dest.read_text(encoding="utf-8")
        datos = json.loads(html.split('id="ficha-data">', 1)[1].split("</script>", 1)[0])
        assert datos["foto"] == self.FOTO
        assert html.count(self.FOTO) == 1  # solo en ficha-data, no en el <img> del modal
        ev(pg, "localStorage.clear()")
        assert ev(abrir(dest), "FOTO") == self.FOTO

    def test_exportar_importar_foto(self, pg, tmp_path):
        ev(pg, "v=>setFoto(v)", self.FOTO)
        dest = tmp_path / "x.json"
        descarga(pg, "#btn-exp").save_as(dest)
        assert json.loads(dest.read_text(encoding="utf-8"))["foto"] == self.FOTO
        ev(pg, "setFoto('')")
        importar(pg, dest)
        assert ev(pg, "FOTO") == self.FOTO
