#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inyecta el POOL completo (385 conjuros) en el buscador de la ficha.
Genera SPELL_POOL (json JS) y lo deja en <html>.pool_tmp para _assemble.py.

Uso:  python _build_pool.py
      FICHA_HTML=ruta python _build_pool.py   (para tests/otros destinos)
"""
import json, unicodedata, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _fix_pool import fix_entry, title_es

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.environ.get("FICHA_HTML", os.path.join(BASE, "resultado-hermes", "ficha_dnd_hermes.html"))
POOL = os.environ.get("POOL_JSON", os.path.join(BASE, "referencias", "spells_txt", "pool.json"))

html = open(HTML, encoding="utf-8").read()
pool = [fix_entry(e) for e in json.load(open(POOL, encoding="utf-8"))]

def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                   if unicodedata.category(c) != "Mn")

# --- 1) Construir SPELL_POOL con el formato REAL que usan spellRow/fill:
# [nombre, niv, tm, rg, conc(0/1), ritual(0/1), material(0/1), nota, desc_corta]
rows = []
for e in pool:
    nombre = title_es(e.get("nombre"))
    if not nombre:
        continue
    conc = 1 if (e.get("du") or "").lower().startswith("concentrac") else 0
    comp = e.get("comp") or ""
    ritual = 1 if "R" in comp else 0
    mat = 1 if e.get("M") else 0
    rows.append([nombre, e.get("niv", 0), e.get("tm", "") or "",
                 e.get("rg", "") or "", conc, ritual, mat,
                 e.get("nota", "") or "", ""])

pool_js = "var SPELL_POOL=" + json.dumps(rows, ensure_ascii=False) + ";"
print("SPELL_POOL items:", len(rows))

open(HTML + ".pool_tmp", "w", encoding="utf-8").write(pool_js)
print("pool_js bytes:", len(pool_js.encode("utf-8")))