#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstruye SPELL_INFO (385) con descripcion larga+pagina+slug
y deja el bloque JS en <html>.info_tmp para _assemble.py.
Corre despues de _build_pool.py.

Uso:  python _build_info.py
      FICHA_HTML=ruta python _build_info.py   (para tests/otros destinos)
"""
import json, unicodedata, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fix_pool import fix_entry, title_es

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.environ.get("FICHA_HTML", os.path.join(BASE, "resultado-hermes", "ficha_dnd_hermes.html"))
POOL = os.environ.get("POOL_JSON", os.path.join(BASE, "referencias", "spells_txt", "pool.json"))
FICHA_WEB = os.environ.get("FICHA_WEB_JSON", os.path.join(BASE, "referencias", "spells_ficha_web.json"))

html = open(HTML, encoding="utf-8").read()
pool = [fix_entry(e) for e in json.load(open(POOL, encoding="utf-8"))]
ficha_web = json.load(open(FICHA_WEB, encoding="utf-8"))

def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                   if unicodedata.category(c) != "Mn")

# slug y pagina fiables vienen de spells_ficha_web.json (los 34 ya verificados)
ficha_slug = {}
for e in ficha_web:
    n = norm(e.get("ficha"))
    if n:
        ficha_slug[n] = (e.get("slug", ""), e.get("pagina"))

# --- Nuevo SPELL_INFO completo (385) ---
info = {}
for e in pool:
    nombre = e.get("nombre")
    dl = e.get("dl") or ""
    pg = e.get("pg")
    if not dl or pg is None:
        continue
    k = norm(nombre)
    slug, sp = ficha_slug.get(k, ("", pg))
    info[k] = {"n": nombre, "p": pg, "d": dl,
               "u": "https://www.aidedd.org/spell/es/" + slug if slug else ""}

info_js = "var SPELL_INFO=" + json.dumps(info, ensure_ascii=False) + ";"
print("SPELL_INFO items:", len(info))

open(HTML + ".info_tmp", "w", encoding="utf-8").write(info_js)
print("info_js bytes:", len(info_js.encode("utf-8")))