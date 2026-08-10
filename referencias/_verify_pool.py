#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica invariantes del HTML construido. Exit 0 = OK.
Uso:  python _verify_pool.py
      FICHA_HTML=ruta python _verify_pool.py
"""
import json, os, re, sys, unicodedata

HTML = os.environ.get("FICHA_HTML",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "resultado-hermes", "ficha_dnd_hermes.html"))
html = open(HTML, encoding="utf-8").read()

ok = True
def check(cond, msg):
    global ok
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        ok = False

# balance tags
check(html.count("<div") == html.count("</div>"), "balance div")
check(html.count("<script") == html.count("</script>"), "balance script")
check(html.count("<style") == html.count("</style>"), "balance style")

# SPELL_POOL / SPELL_INFO
m = re.search(r"var SPELL_POOL=(\[.*?\]);", html, re.S)
sp = json.loads(m.group(1)) if m else None
m = re.search(r"var SPELL_INFO=(\{.*?\});", html, re.S)
si = json.loads(m.group(1)) if m else None
check(sp is not None and len(sp) == 385, "SPELL_POOL == 385 (got %s)" % (len(sp) if sp else None))
check(si is not None and len(si) == 383, "SPELL_INFO == 383 (got %s)" % (len(si) if si else None))

# restos del viejo: el filtro/busqueda no debe usar SPELLS (el grid SPELLS
# con los 34 visibles sigue siendo legitimo para la tabla de la ficha)
check(html.count("var SPELLS=") == 1, "var SPELLS= solo el grid visible (1)")
check("SPELLS.filter" not in html, "sin SPELLS.filter")
check("SPELLS.slice" not in html, "sin SPELLS.slice")

# parches post-build presentes
check("list=list.slice(0,1000);" in html, "slice(0,1000)")
check("nt.value=s[7]||'';" in html, "fill nota incondicional")
check(".infoX{position:absolute;left:-15px;" in html, "infoX left:-15px")
check(".clearX{position:absolute;right:-16px;" in html, "clearX right:-16px")
check(".srow::before{" in html and ".srow::after{" in html, "franjas hover .srow")
check('data-tt="crm"' in html and 'data-tt="atk-bono"' in html, "data-tt tablas")
check("Tooltips de cabecera de tablas" in html, "bloque JS tooltips")

# emparejamiento: nombres del pool estan en info, salvo los 2 SIN descripcion
# en pool.json (por eso SPELL_INFO == 383, no 385) — estado conocido y correcto.
def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                   if unicodedata.category(c) != "Mn")
SIN_DESCRIPCION = {"brazos de hadar", "circulo magico"}
falta = [row[0] for row in sp if norm(row[0]) not in si
         and norm(row[0]) not in SIN_DESCRIPCION]
check(len(falta) == 0, "pool items sin info (solo 2 conocidos; falta extra %d: %s)"
      % (len(falta), falta[:3]))

sys.exit(0 if ok else 1)