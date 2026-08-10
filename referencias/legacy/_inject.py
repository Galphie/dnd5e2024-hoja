#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inyecta el sistema de informacion (boton i + modal) ESTILO AIDEDD en la ficha DnD.
Parte de un HTML SIN modal (backup). Mantiene la ficha autocontenida.
"""
import json, unicodedata, shutil

BASE = r"C:\Users\algpa\Desktop\hojapersonaje"
HTML   = BASE + r"\resultado-hermes\ficha_dnd_hermes.html"
BACKUP = BASE + r"\referencias\_ficha_backup_premodal.html"
JSON   = BASE + r"\referencias\spells_ficha_web.json"

# --- Volver al backup limpio (sin modal) para evitar doble inyeccion ---
with open(BACKUP, encoding="utf-8") as f:
    html = f.read()

with open(JSON, encoding="utf-8") as f:
    dets = json.load(f)

def norm(s):
    if not s: return ""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")

DET = {}
for e in dets:
    nombre = e.get("ficha")
    if not nombre: continue
    desc = e.get("descripcion_larga", "")
    pg   = e.get("pagina")
    slug = e.get("slug", "")
    if not desc or pg is None: continue
    DET[norm(nombre)] = {"n": nombre, "p": pg, "d": desc, "u": "https://www.aidedd.org/spell/es/" + slug}

js_data = "var SPELL_INFO=" + json.dumps(DET, ensure_ascii=False) + ";"

# --- CSS del modal estilo aidedd.org ---
MODAL_CSS = """
/* ---------- Informacion de conjuro (modal estilo aidedd.org) ---------- */
.infoX{position:absolute;right:21px;top:50%;transform:translateY(-50%);width:15px;height:15px;border:none;background:transparent;color:#6b5837;font-size:11px;font-weight:700;cursor:pointer;line-height:1;display:none;z-index:4;font-family:inherit}
.srow:hover .infoX{display:block}
.infoX:hover{color:#9a3a2a}
.mdl-ov{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:400;display:none;align-items:center;justify-content:center}
.mdl-ov.open{display:flex}
.mdl{background:#ffffff;border:1px solid #c9c7c0;border-radius:4px;box-shadow:0 6px 28px rgba(0,0,0,.45);max-width:480px;width:calc(100% - 48px);max-height:78vh;display:flex;flex-direction:column;overflow:hidden;position:relative;text-align:left}
.mdl-x{position:absolute;top:6px;right:10px;border:none;background:transparent;color:#999;font-size:16px;cursor:pointer;line-height:1;padding:2px;z-index:5}
.mdl-x:hover{color:#c00000}
.mdl-b{padding:16px 18px 10px;overflow-y:auto}
.mdl-b h1{font-family:Georgia,'Times New Roman',serif;color:#6D0000;font-size:20px;font-weight:700;margin:0 0 8px;line-height:1.2;padding-right:24px}
.mdl-b .sub{font-family:Georgia,'Times New Roman',serif;color:#333;font-size:11px;font-style:italic;margin:0 0 10px}
.mdl-b .desc{font-family:Georgia,'Times New Roman',serif;color:#000;font-size:13px;line-height:1.5;margin:0 0 12px}
.mdl-f{padding:8px 18px 12px;border-top:1px solid #e0ded7;font-family:arial,sans-serif;font-size:11px;color:#000;display:flex;flex-direction:column;gap:5px}
.mdl-f .src{color:#000}
.mdl-f a{color:#B80000;text-decoration:none;font-family:arial,sans-serif;font-size:11px}
.mdl-f a:hover{text-decoration:underline}
"""

MODAL_HTML = """
<div class="mdl-ov" id="mdlOv"><div class="mdl" role="dialog" aria-modal="true">
  <button type="button" class="mdl-x" id="mdlX" title="Cerrar">×</button>
  <div class="mdl-b">
    <h1 id="mdlT"></h1>
    <p class="desc" id="mdlD"></p>
  </div>
  <div class="mdl-f">
    <span class="src" id="mdlP"></span>
    <a id="mdlL" href="#" target="_blank" rel="noopener">Abrir en aidedd.org</a>
  </div>
</div></div>
"""

MODAL_JS = """
/* ---------- Conjuros: informacion (modal estilo aidedd) ---------- */
(function(){
  var ov=q('#mdlOv'),t=q('#mdlT'),d=q('#mdlD'),p=q('#mdlP'),l=q('#mdlL');
  function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
  function show(nombre){
    var k=norm(nombre),info=SPELL_INFO[k];
    if(!info)return;
    t.textContent=info.n;
    d.textContent=info.d;
    p.textContent='Fuente: Player\\'s Handbook 2024 · pág. '+info.p;
    l.href=info.u;
    ov.classList.add('open');
  }
  q('#spellrows').addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('.infoX');if(!b)return;
    var r=b.closest('.srow');
    var nm=r.querySelector('.nm');
    show(nm?nm.value:'');
  });
  function close(){ov.classList.remove('open');}
  q('#mdlX').addEventListener('click',close);
  ov.addEventListener('click',function(ev){if(ev.target===ov)close();});
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape')close();});
})();
"""

# 1) CSS
assert html.count("</style>") == 1, "no unico </style>"
html = html.replace("</style>", MODAL_CSS + "</style>")

# 2) boton infoX en spellRow
assert html.count("'<button type=\"button\" class=\"clearX\" title=\"Vaciar fila\">✕</button></div>';") == 1, "clearX no unico"
html = html.replace(
    "'<button type=\"button\" class=\"clearX\" title=\"Vaciar fila\">✕</button></div>';",
    "'<button type=\"button\" class=\"infoX\" title=\"Ver descripción\">ⓘ</button>'+\n"
    "    '<button type=\"button\" class=\"clearX\" title=\"Vaciar fila\">✕</button></div>';"
)

# 3) datos
assert html.count("function spellRow(s){") == 1, "spellRow no unico"
html = html.replace("function spellRow(s){", js_data + "\nfunction spellRow(s){", 1)

# 4) HTML modal
assert html.count('<div class="tip" id="tip"></div>') == 1, "tip no unico"
html = html.replace('<div class="tip" id="tip"></div>', '<div class="tip" id="tip"></div>' + MODAL_HTML)

# 5) JS modal
assert html.count("</script>") == 1, "no unico </script>"
html = html.replace("</script>", MODAL_JS + "</script>")

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("OK")
print("conjuros con datos:", len(DET))
print("nuevo tamano:", len(html.encode('utf-8')), "bytes")