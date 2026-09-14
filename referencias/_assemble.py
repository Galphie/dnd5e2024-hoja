#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ensambla SPELL_POOL + SPELL_INFO en la ficha y aplica TODOS los
parches posteriores (slice 1000, fill incondicional, botones flotantes,
tooltips de cabecera). Build completo en una sola pasada.

Uso:  python _assemble.py            (usa ruta por defecto)
      FICHA_HTML=ruta python _assemble.py   (para tests/otros destinos)
Requiere: _build_pool.py y _build_info.py ejecutados antes (generan .pool_tmp/.info_tmp).
Idempotente: si el HTML ya tiene un parche aplicado, lo salta sin romper.
"""
import json, os, re, sys, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.environ.get("FICHA_HTML", os.path.join(BASE, "resultado-hermes", "ficha_dnd_hermes.html"))
OUT_DIR = os.path.dirname(HTML)

# Read version from package.json
pkg_path = os.path.join(BASE, "package.json")
VERSION = "0.1.0"
if os.path.exists(pkg_path):
    try:
        with open(pkg_path, encoding="utf-8") as f:
            pkg = json.load(f)
            VERSION = pkg.get("version", "0.1.0")
    except Exception:
        pass

pool_js = open(HTML + ".pool_tmp", encoding="utf-8").read().strip()
info_js = open(HTML + ".info_tmp", encoding="utf-8").read().strip()

html = open(HTML, encoding="utf-8").read()

def need(tag, cond, ok):
    assert cond, f"[{tag}] ancla no encontrada"
    if ok: print("[OK]", tag)

def apply(text, old, new, tag):
    """Reemplaza old->new si old está; si new ya está, salta (idempotente)."""
    if new in text:
        print("[SKIP]", tag, "(ya aplicado)")
        return text
    need(tag, old in text, True)
    return text.replace(old, new, 1)

# 1) Reemplazar SPELL_INFO actual por el completo (385).
#    Balanceo de llaves (robusto ante ; dentro de las descripciones).
def replace_var_block(text, marker, payload):
    """Reemplaza `var MARKER={` ... `};` por payload. Busca el bloque balanceado."""
    start = text.find(marker)
    assert start != -1, f"ancla {marker}"
    brace = text.find("{", start)
    depth = 0
    i = brace
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    end = text.find(";", i) + 1  # incluye el ';' de cierre
    return text[:start] + payload + text[end:]

html = replace_var_block(html, "var SPELL_INFO=", info_js)
print("[OK] SPELL_INFO reemplazado (balanceo de llaves)")

# 2) Insertar SPELL_POOL justo antes de "function spellRow(s){"
anchor = "function spellRow(s){"
assert anchor in html, "ancla spellRow"
html = html.replace(anchor, pool_js + "\n" + anchor, 1)
print("[OK] SPELL_POOL insertado")

# 3) El buscador debe usar SPELL_POOL en vez de SPELLS
old_filtro = "else{list=SPELLS.filter(function(s){var n=norm(s[0]);return n.indexOf(qq)===0||n.indexOf(qq)>0;});}"
new_filtro = "else{list=SPELL_POOL.filter(function(s){var n=norm(s[0]);return n.indexOf(qq)===0||n.indexOf(qq)>0;});}"
html = apply(html, old_filtro, new_filtro, "filtro -> SPELL_POOL")

# 4) SORTED (lista base cuando campo vacio) tambien debe usar SPELL_POOL
old_sorted = "var SORTED=SPELLS.slice().sort(function(a,b){return a[1]-b[1]||a[0].localeCompare(b[0],'es');});"
new_sorted = "var SORTED=SPELL_POOL.slice().sort(function(a,b){return a[1]-b[1]||a[0].localeCompare(b[0],'es');});"
html = apply(html, old_sorted, new_sorted, "SORTED -> SPELL_POOL")

# 5) El modal debe ocultar el enlace si no hay slug (campo u vacio)
html = apply(html, "l.href=info.u;", "l.href=info.u||'#';l.style.display=info.u?'inline':'none';", "modal link condicional")

# 6) Subir max-height del autocompletado para ver mas de un vistazo
html = apply(html, "max-height:240px", "max-height:360px", ".ac max-height 240->360")
html = apply(html, "top+240>window.innerHeight-6)top=r.top-242",
             "top+360>window.innerHeight-6)top=r.top-362", "posicion .ac ajustado")

# 7) buildSpells debe usar SPELL_POOL en vez de SPELLS
html = apply(html,
    "SPELLS.forEach(function(s){html+=spellRow(s);});",
    "SPELL_POOL.forEach(function(s){html+=spellRow(s);});",
    "buildSpells -> SPELL_POOL")

# 8) Mostrar puntos los 385 al abrir el buscador vacio (slice 200 -> 1000)
html = apply(html, "list=list.slice(0,200);", "list=list.slice(0,1000);", "slice(0,200)->slice(0,1000)")

# 8) Notas: fill incondicional (pool nota SIEMPRE sobreescribe el campo)
html = apply(html, "var nt=row.querySelector('.nt');if(!nt.value&&s[7])nt.value=s[7];",
             "var nt=row.querySelector('.nt');nt.value=s[7]||'';", "fill nota incondicional")

# 9) Botones flotantes: infoX cuelga a la izquierda, clearX a la derecha,
#    y franjas ::before/::after extienden el hover de la fila hacia fuera.
html = apply(html,
    ".infoX{position:absolute;right:21px;top:50%;transform:translateY(-50%);width:15px;height:15px;border:none;background:transparent;color:#6b5837;font-size:11px;font-weight:700;cursor:pointer;line-height:1;display:none;z-index:4;font-family:inherit}",
    ".infoX{position:absolute;left:-15px;top:50%;transform:translateY(-50%);width:15px;height:15px;border:none;background:transparent;color:#6b5837;font-size:11px;font-weight:700;cursor:pointer;line-height:1;display:none;z-index:5;font-family:inherit}",
    ".infoX left:-15px")
html = apply(html,
    ".clearX{position:absolute;right:0;top:50%;transform:translateY(-50%);width:16px;height:16px;border:none;background:transparent;color:#9a3a2a;font-weight:700;font-size:11px;cursor:pointer;line-height:1;display:none;z-index:4}",
    ".clearX{position:absolute;right:-16px;top:50%;transform:translateY(-50%);width:16px;height:16px;border:none;background:transparent;color:#9a3a2a;font-weight:700;font-size:11px;cursor:pointer;line-height:1;display:none;z-index:5}",
    ".clearX right:-16px")
html = apply(html,
    ".srow{display:grid;grid-template-columns:42px 150px 68px 58px 72px 1fr}",
    ".srow{display:grid;grid-template-columns:42px 150px 68px 58px 72px 1fr}"
    "\n.srow::before{content:\"\";position:absolute;top:0;bottom:0;left:-18px;width:18px}"
    "\n.srow::after{content:\"\";position:absolute;top:0;bottom:0;right:-18px;width:18px}",
    "franjas hover .srow ::before/::after")

# 10) Tooltips de cabecera: data-tt en cada span de ambas tablas + bloque JS
html = apply(html,
    '<div class="sp-hd"><span>Nivel</span><span>Nombre</span><span>Tiempo</span><span>Rango</span><span>Concentración, Ritual &amp; Material requerido</span><span>Notas</span></div>',
    '<div class="sp-hd"><span data-tt="nivel">Nivel</span><span data-tt="nombre">Nombre</span><span data-tt="tiempo">Tiempo</span><span data-tt="rango">Rango</span><span data-tt="crm">Concentración, Ritual &amp; Material requerido</span><span data-tt="notas">Notas</span></div>',
    "data-tt en .sp-hd")
html = apply(html,
    '<div class="atk-hd"><span>Nombre</span><span>Bonificador</span><span>Daño y tipo</span><span>Notas</span></div>',
    '<div class="atk-hd"><span data-tt="atk-nombre">Nombre</span><span data-tt="atk-bono">Bonificador</span><span data-tt="atk-danyo">Daño y tipo</span><span data-tt="atk-notas">Notas</span></div>',
    "data-tt en .atk-hd")

TOOLTIPS_JS = """/* ---------- Tooltips de cabecera de tablas (conjuros + ataques) ---------- */
(function(){
  var pop=document.getElementById('tip');
  var T={
    nivel:'<b>NIVEL</b><span class="meta">Nivel del conjuro</span>0 = truco (se lanza sin gastar espacio). 1-9 = nivel del conjuro. Se rellena automaticamente al elegir el conjuro.',
    nombre:'<b>NOMBRE</b><span class="meta">Busqueda</span>Escribe aqui para buscar entre los 385 conjuros del Manual 2024. Al elegir uno se rellenan el resto de columnas.',
    tiempo:'<b>TIEMPO</b><span class="meta">Tiempo de lanzamiento</span>Accion, Accion bonus, Reaccion o mas (1 minuto, 1 hora...). Si el conjuro es ritual, al lanzarlo como ritual tarda 10 minutos mas.',
    rango:'<b>RANGO</b><span class="meta">Alcance</span>Personal, Toque o distancia en metros (9 m, 30 m...). Indica desde donde puedes lanzar el conjuro.',
    crm:'<b>C . R . M</b><span class="meta">Requisitos del conjuro</span><b>C</b> Concentracion: solo una a la vez; si recibes dano, salvacion de CON (CD 10 o la mitad del dano, la mayor, max. 30) o el conjuro termina.<br><b>R</b> Ritual: puede lanzarse como ritual: +10 min y sin gastar espacio de conjuro.<br><b>M</b> Material: requiere un componente material. Si tiene coste o se consume, no puede sustituirse por un foco de conjuro.',
    notas:'<b>NOTAS</b><span class="meta">Anotaciones</span>Notas personales del personaje: dano, efectos, usos. Se rellenan automaticamente al anadir el conjuro y puedes editarlas.',
    'atk-nombre':'<b>NOMBRE</b><span class="meta">Ataque o arma</span>Nombre del ataque o arma usada (p. ej. baston enano, cuchillo, bola de fuego).',
    'atk-bono':'<b>BONIFICADOR</b><span class="meta">Total al ataque</span>Bonificador total al ataque: competencia + modificador de caracteristica + otros ajustes (arma magica, etc.).',
    'atk-danyo':'<b>DANO Y TIPO</b><span class="meta">Dados del ataque</span>Dados de dano y tipo (p. ej. 1d6 contundente). En conjuros, suele ser el dano del lanzamiento.',
    'atk-notas':'<b>NOTAS</b><span class="meta">Anotaciones</span>Notas personales del ataque: efectos extra, condiciones que provoca, usos limitados.'
  };
  document.addEventListener('mouseover',function(e){
    var s=e.target.closest&&e.target.closest('span[data-tt]');
    if(!s)return;
    var txt=T[s.getAttribute('data-tt')];
    if(!txt){pop.style.display='none';return;}
    pop.innerHTML=txt;
    pop.style.display='block';
    var r=s.getBoundingClientRect(),tw=pop.offsetWidth;
    var left=r.left;
    if(left+tw>window.innerWidth-8)left=r.right-tw-8;
    if(left<8)left=8;
    var top=r.bottom+6;
    if(top+pop.offsetHeight>window.innerHeight-8)top=r.top-pop.offsetHeight-6;
    pop.style.left=Math.round(left)+'px';pop.style.top=Math.round(top)+'px';
  });
  document.addEventListener('mouseout',function(e){
    if(e.target.closest&&e.target.closest('span[data-tt]'))pop.style.display='none';
  });
})();"""

BLOCK = "/* ---------- Bitacora ---------- */"
if "span[data-tt]" in html and "Tooltips de cabecera de tablas" in html:
    print("[SKIP] bloque tooltips (ya aplicado)")
else:
    need("ancla Bitacora", BLOCK in html, True)
    html = html.replace(BLOCK, TOOLTIPS_JS + "\n\n" + BLOCK, 1)
    print("[OK] bloque tooltips insertado")

open(HTML, "w", encoding="utf-8").write(html)
print("HTML final bytes:", len(html.encode("utf-8")))

# ---- PWA: inyectar manifest + SW registration ----
def inject_pwa(html_text):
    """Inyecta <link rel=manifest> y registro de SW en el <head>."""
    # 1. manifest link
    manifest_link = '<link rel="manifest" href="manifest.json">'
    if manifest_link not in html_text:
        html_text = html_text.replace('<head>', '<head>\n' + manifest_link)
    
    # 2. SW registration script (inline, al final del head)
    sw_reg = '''
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}
</script>'''
    if 'serviceWorker.register' not in html_text:
        html_text = html_text.replace('</head>', sw_reg + '\n</head>')
    
    # 3. meta theme-color (para Chrome/Android)
    meta_theme = '<meta name="theme-color" content="#6b5837">'
    if meta_theme not in html_text:
        html_text = html_text.replace('<head>', '<head>\n' + meta_theme)
    
    # 4. apple-mobile-web-app capable (iOS PWA hints)
    apple_meta = '''<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="D&D 2024">'''
    if 'apple-mobile-web-app-capable' not in html_text:
        html_text = html_text.replace('<head>', '<head>\n' + apple_meta)
    
    return html_text

# ---- Version injection in sidebar ----
def inject_version(html_text):
    """Inyecta la versión + autor en el sidebar (nav), al final."""
    version_html = f'<div class="ttl" style="margin-top:auto;padding-top:8px;border-top:1px solid #5c4c30">v{VERSION} · Galphie</div>'
    # Lo ponemos al final del nav, antes del cierre
    if version_html not in html_text:
        html_text = html_text.replace('</nav>', f'  {version_html}\n</nav>')
    return html_text

html = inject_pwa(html)
html = inject_version(html)
open(HTML, "w", encoding="utf-8").write(html)
print("[OK] PWA manifest + SW registration inyectado")

# Copiar manifest.json y sw.js al directorio de salida
for asset in ("manifest.json", "sw.js"):
    src = os.path.join(BASE, "referencias", asset)
    dst = os.path.join(OUT_DIR, asset)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"[OK] {asset} -> {dst}")
    else:
        print(f"[WARN] {asset} no encontrado en referencias/")