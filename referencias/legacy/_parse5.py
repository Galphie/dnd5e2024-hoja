# -*- coding: utf-8 -*-
# Parser v6: FLUJO CONTINUO. Un conjuro puede cruzar el limite de pagina (descripcion en pag siguiente).
# Se ignoran banners, cabeceras "CAPITULO 7 | CONJUROS" y paginas de relleno. Se guarda la pagina de inicio.
import re, json
src="C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/all_241_346.txt"
raw=open(src,encoding="utf-8").read().replace('\r','')

ESCOLAS = ['Abjuración','Conjuración','Adivinación','Encantamiento','Evocación','Ilusionismo','Ilusión','Nigromancia','Transmutación','Metamorfosis','Paralelismo']
ESC=re.compile(r'^(?:(?:Truco de (?P<esc_truco>'+r'|'.join(ESCOLAS)+r'))|(?:(?P<esc>'+r'|'.join(ESCOLAS)+r') de (?P<nivel>nivel \d+|nivel)))(?P<rest>.*)$', re.IGNORECASE)
CAMPO=re.compile(r'^(Tiempo de lanzamiento|Alcance|Componentes|Duración):\s*(.*)$')
KEYMAP={"Tiempo de lanzamiento":"tiempo","Alcance":"alcance","Componentes":"componentes","Duración":"duracion"}
PAG=r'===== PAGE (\d+) \(pdf idx (\d+)\) ====='

def es_titulo(l):
    l2=l.strip()
    if len(l2)<2 or re.search(r'\d', l2): return False
    if l2.isupper(): return True
    return l2[0].isupper() and l2[1:].islower()

def _get_clases(rest, lines, k):
    txt=rest.strip()
    while True:
        m=re.search(r'\((?P<g>[^)]+)\)', txt)
        if m:
            return m.group('g').strip(), k
        if txt.count('(') > txt.count(')'):
            if k<len(lines):
                nxt=lines[k].strip()
                if not nxt or CAMPO.match(nxt) or ESC.match(nxt) or nxt.startswith('CAPÍTULO') or nxt.startswith('CAPITULO'):
                    return None, k
                txt=txt+' '+nxt; k+=1
            else:
                return None, k
        else:
            return None, k

# --- Construir flujo continuo: lista de (texto_linea, pagina) omitiendo banners y cabeceras ---
flow=[]
cur_pg=None
for line in raw.split('\n'):
    line=line.rstrip()
    pm=re.match(PAG, line)
    if pm:
        cur_pg=int(pm.group(1)); continue
    s=line.strip()
    if s.startswith('CAPÍTULO') or s.startswith('CAPITULO'):
        continue
    if not s:
        flow.append(('', cur_pg)); continue
    flow.append((s, cur_pg))

lines=[f[0] for f in flow]
pg=[f[1] for f in flow]

spells=[]
j=0
while j<len(lines):
    t=lines[j]
    m=ESC.match(t)
    if not m:
        j+=1; continue
    if m.group('esc_truco'):
        school=m.group('esc_truco').strip(); level='truco'
        classes, k = _get_clases(m.group('rest') or '', lines, j+1)
    else:
        school=m.group('esc').strip()
        level_raw=m.group('nivel').strip().lower()
        if level_raw=='truco':
            level='truco'; classes, k = _get_clases(m.group('rest') or '', lines, j+1)
        else:
            dd=re.search(r'\d', level_raw)
            if dd:
                level='nivel '+dd.group(0); classes, k = _get_clases(m.group('rest') or '', lines, j+1)
            else:
                level='nivel ?'
                nxt=lines[j+1].strip() if j+1<len(lines) else ''
                nm=re.match(r'^(\d+)\s*(?:\((.+)\))?$', nxt)
                if nm:
                    level='nivel '+nm.group(1); classes=nm.group(2); k=j+2
                else:
                    classes, k = _get_clases(m.group('rest') or '', lines, j+1)
    # nombre hacia atras (puede cruzar banner: buscar linea de titulo antes de j)
    name=None
    h=j-1
    while h>=0 and (lines[h]=='' ):
        h-=1
    if h>=0 and es_titulo(lines[h]):
        name=lines[h].strip()
    if name is None:
        h2=h-1
        while h2>=0 and lines[h2]=='':
            h2-=1
        if h2>=0 and es_titulo(lines[h2]):
            name=lines[h2].strip()
    if name is None:
        # nombre pudo venir 2 lineas atras (rejilla de pagina); buscar la primera linea no vacia de la pagina anterior
        j=k; continue
    pagina=pg[j]  # pagina del conjuro (la de la linea de escuela)
    fields={"tiempo":None,"alcance":None,"componentes":None,"duracion":None}
    desc=[]
    while k<len(lines):
        t2=lines[k].strip()
        if t2=='':
            k+=1; continue
        fm=CAMPO.match(t2)
        if fm:
            key=KEYMAP[fm.group(1)]; val=fm.group(2).strip(); k+=1
            if key!='duracion':
                while k<len(lines):
                    nxt=lines[k].strip()
                    if not nxt or ESC.match(nxt) or CAMPO.match(nxt):
                        break
                    if nxt.startswith('CAPÍTULO') or nxt.startswith('CAPITULO') or es_titulo(nxt):
                        break
                    val=val+' '+nxt; k+=1
            fields[key]=val
            continue
        if ESC.match(t2):
            break
        if t2.isupper() and len(t2)>1 and k+1<len(lines) and ESC.match(lines[k+1].strip()):
            break
        if t2.startswith('CAPÍTULO') or t2.startswith('CAPITULO') or t2=='—$' or t2=='—':
            k+=1; continue
        desc.append(t2)
        k+=1
    j=k
    spells.append({"nombre":name,"escuela":school,"nivel":level,"clases":classes,"pagina":pagina,
                   "tiempo":fields["tiempo"],"alcance":fields["alcance"],"componentes":fields["componentes"],
                   "duracion":fields["duracion"],"descripcion":" ".join(desc).strip()})
print("SPELLS PARSED v6 continua:", len(spells))
json.dump(spells, open("C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/spells_parsed.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
names=[s["nombre"] for s in spells]
print("duplicados:", {n for n in names if names.count(n)>1} or "ninguno")
from collections import Counter
print("niveles:", Counter(s["nivel"] for s in spells))
# descripciones vacias o que empiezan en minuscula
bad=[s["nombre"] for s in spells if not s["descripcion"] or s["descripcion"][0].islower()]
print("desc. malas/vacias:", len(bad), bad[:12])