# -*- coding: utf-8 -*-
import json, re, unicodedata
spells=json.load(open("C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/spells_parsed.json",encoding="utf-8"))
def norm(s):
    s=s.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
copy=[]
for sp in spells:
    nivel=0 if sp["nivel"] in ('truco','truco?') else int(re.sub(r'\D','',sp['nivel']) or 0)
    dl=(' '.join((sp['descripcion'] or '').split()))
    copy.append({"nombre":sp["nombre"],"norm":norm(sp["nombre"]),
                 "niv":nivel,"tm":sp['tiempo'],"rg":sp['alcance'],"M":('M' in (sp['componentes'] or '')),
                 "du":sp['duracion'],"comp":sp['componentes'],
                 "dl":dl,"pg":sp['pagina'],"escuela":sp['escuela'],"clases":sp['clases']})
json.dump(copy, open("C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/pool.json","w",encoding="utf-8"), ensure_ascii=False)
from collections import Counter
print("TOTAL:",len(copy))
print("por nivel:",Counter(p['niv'] for p in copy))
# descripciones sospechosas (empiezan en minuscula o 'que ')
bad=[p for p in copy if not p['dl'] or p['dl'][0].islower()]
print("descripciones cortas/vacias:",len(bad))
for b in bad[:15]: print("  *",b['nombre'],b['pg'],'|',(b['dl'] or '')[:45])
# sin descripcion completa
no=[p for p in copy if len(p['dl'])<20]
print("sin descripcion:",len(no),[(p['nombre'],p['pg']) for p in no])