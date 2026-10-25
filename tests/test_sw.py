# -*- coding: utf-8 -*-
"""Service worker (PWA): se sirve el build por HTTP en localhost (los SW no
funcionan en file://) y se comprueba registro, uso offline y actualizacion.

"Sin red" = servidor HTTP apagado: el fetch del SW falla y debe responder
la cache.
"""
import functools
import http.server
import re
import shutil
import threading

import pytest


class _Servidor:
    def __init__(self, raiz):
        self.raiz = raiz
        self.httpd = None
        self.puerto = 0

    def arrancar(self):
        handler = functools.partial(_HandlerSilencioso, directory=str(self.raiz))
        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", self.puerto), handler)
        self.puerto = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def parar(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None

    @property
    def url(self):
        return "http://127.0.0.1:%d/" % self.puerto


class _HandlerSilencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture
def servidor(build_dir, tmp_path):
    raiz = tmp_path / "web"
    raiz.mkdir()
    for f in ("index.html", "manifest.json", "sw.js"):
        shutil.copy2(build_dir / f, raiz / f)
    s = _Servidor(raiz)
    s.arrancar()
    yield s
    s.parar()


def _pagina_controlada(contexto, url):
    pg = contexto.new_page()
    pg.errores = []
    pg.on("pageerror", lambda e: pg.errores.append(str(e)))
    pg.goto(url)
    pg.evaluate("navigator.serviceWorker.ready")
    # tras clients.claim() la pagina queda controlada; la siguiente carga ya pasa por el SW
    pg.wait_for_function("navigator.serviceWorker.controller !== null")
    return pg


def _cache_name(raiz):
    return re.search(r"CACHE_NAME = '([^']+)'", (raiz / "sw.js").read_text(encoding="utf-8")).group(1)


def test_sw_versionado(build_dir):
    sw = (build_dir / "sw.js").read_text(encoding="utf-8")
    assert "__BUILD__" not in sw
    assert re.search(r"CACHE_NAME = 'ficha-dnd-2024-[0-9a-f]{12}'", sw)


def test_navegacion_servida_por_sw(contexto, servidor):
    pg = _pagina_controlada(contexto, servidor.url)
    resp = pg.reload()
    assert resp.from_service_worker
    assert pg.evaluate("caches.keys()") == [_cache_name(servidor.raiz)]
    assert not pg.errores


@pytest.mark.parametrize("ruta", ["", "index.html", "index.html?x=1"])
def test_offline_carga_la_ficha(contexto, servidor, ruta):
    pg = _pagina_controlada(contexto, servidor.url)
    servidor.parar()
    resp = pg.goto(servidor.url + ruta)
    assert resp.ok and resp.from_service_worker
    assert pg.evaluate("typeof setSpells") == "function"
    assert not pg.errores


def test_nuevo_despliegue_se_ve_y_borra_cache_vieja(contexto, servidor):
    raiz = servidor.raiz
    pg = _pagina_controlada(contexto, servidor.url)
    vieja = _cache_name(raiz)

    # "nuevo despliegue": cambia la pagina y el hash del SW
    html = (raiz / "index.html").read_text(encoding="utf-8")
    (raiz / "index.html").write_text(html.replace("</body>", "<div id='marca-v2'></div></body>"),
                                     encoding="utf-8")
    sw = (raiz / "sw.js").read_text(encoding="utf-8")
    (raiz / "sw.js").write_text(sw.replace(vieja, vieja[:-1] + ("0" if vieja[-1] != "0" else "1")),
                                encoding="utf-8")
    nueva = _cache_name(raiz)

    # primero red: la recarga ya trae la pagina nueva
    pg.reload()
    assert pg.locator("#marca-v2").count() == 1

    # el SW nuevo se instala, activa y elimina la cache anterior
    pg.evaluate("navigator.serviceWorker.getRegistration().then(r => r.update())")
    pg.wait_for_function("k => caches.keys().then(ks => ks.length === 1 && ks[0] === k)",
                         arg=nueva, timeout=10000)

    # y offline sirve la version nueva
    servidor.parar()
    pg.goto(servidor.url)
    assert pg.locator("#marca-v2").count() == 1
    assert not pg.errores
