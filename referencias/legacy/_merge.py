# -*- coding: utf-8 -*-
import re, json, os, unicodedata
def norm(s):
    s=s.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
def clean_tags(h):
    h=re.sub(r'<a[^>]*>','',h); h=re.sub(r'</a>','',h)
    h=re.sub(r'<br\s*/?>',' ',h)
    h=re.sub(r'<[^>]+>','',h)
    ent={'&aacute;':'á','&eacute;':'é','&iacute;':'í','&oacute;':'ó','&uacute;':'ú','&ntilde;':'ñ','&uuml;':'ü',
         '&Aacute;':'Á','&Eacute;':'É','&Iacute;':'Í','&Oacute;':'Ó','&Uacute;':'Ú','&Ntilde;':'Ñ','&Uuml;':'Ü',
         '&quot;':'"','&nbsp;':' ','&#39;':"'",'&rsquo;':'’','&lsquo;':'‘','&ldquo;':'“','&rdquo;':'”','&mdash;':'—','&ndash;':'–'}
    for _k,_v in ent.items(): h=h.replace(_k,_v)
    return re.sub(r'\s+',' ',h).strip()

AIDED='C:/Users/algpa/Desktop/hojapersonaje/referencias/aided'
POOL=json.load(open('C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/pool.json',encoding='utf-8'))
poolidx={norm(p['nombre']):p for p in POOL}

MAP=[
 ('Rayo de Fuego','descarga-de-fuego','DESCARGA DE FUEGO'),
 ('Mano de Mago','mano-de-mago','MANO DE MAGO'),
 ('Prestidigitación','prestidigitacion','PRESTIDIGITACIÓN'),
 ('Luz','luz','LUZ'),
 ('Ráfaga de Hechicero','estallido-magico','ESTALLIDO MÁGICO'),
 ('Toque Gélido','toque-helado','TOQUE HELADO'),
 ('Descarga de Cuchillos','',''),
 ('Chasquido Atronador','tronar','TRONAR'),
 ('Luces Danzantes','luces-danzantes','LUCES DANZANTES'),
 ('Mensaje','mensaje','MENSAJE'),
 ('Ilusión Menor','ilusion-menor','ILUSIÓN MENOR'),
 ('Rociada Venenosa','rociada-venenosa','ROCIADA VENENOSA'),
 ('Rayo de Escarcha','rayo-de-escarcha','RAYO DE ESCARCHA'),
 ('Salvajismo','',''),
 ('Burla Cruel','burla-danina','BURLA DAÑINA'),
 ('Descarga Eléctrica','agarre-electrizante','AGARRE ELECTRIZANTE'),
 ('Estabilizar','piedad-con-los-moribundos','PIEDAD CON LOS MORIBUNDOS'),
 ('Escudo','escudo','ESCUDO'),
 ('Orbe Cromático','orbe-cromatico','ORBE CROMÁTICO'),
 ('Llamarada','manos-ardientes','MANOS ARDIENTES'),
 ('Proyectil Mágico','proyectil-magico','PROYECTIL MÁGICO'),
 ('Armadura de Mago','armadura-de-mago','ARMADURA DE MAGO'),
 ('Comprender Idiomas','entender-idiomas','ENTENDER IDIOMAS'),
 ('Detectar Magia','detectar-magia','DETECTAR MAGIA'),
 ('Retirada Expeditiva','retirada-expeditiva','RETIRADA EXPEDITIVA'),
 ('Paso Brumoso','paso-brumoso','PASO BRUMOSO'),
 ('Rayo Abrasador','rayo-abrasador','RAYO ABRASADOR'),
 ('Invisibilidad','invisibilidad','INVISIBILIDAD'),
 ('Sugestión','sugestion','SUGESTIÓN'),
 ('Añicos','hacer-avicos','HACER AÑICOS'),
 ('Bola de Fuego','bola-de-fuego','BOLA DE FUEGO'),
 ('Volar','volar','VOLAR'),
 ('Contrahechizo','contrahechizo','CONTRAHECHIZO'),
 ('Relámpago','relampago','RELÁMPAGO'),
 ('Disipar Magia','disipar-magia','DISIPAR MAGIA'),
 ('Muro de Fuego','muro-de-fuego','MURO DE FUEGO'),
]
out=[]
for fich,slug,pooln in MAP:
    rec={'ficha':fich,'slug':slug,'descripcion_larga':'','pagina':None,'metadatos':'','coincide_nombre':False}
    if slug:
        fn=os.path.join(AIDED,slug+'.html')
        h=open(fn,encoding='utf-8',errors='replace').read()
        md=re.search(r"<div class='description'>(.*?)</div>",h,re.S)
        if md:
            rec['descripcion_larga']=clean_tags(md.group(1))
        e=re.search(r"<div class='ecole'>([^<]*)</div>",h)
        if e: rec['metadatos']=e.group(1).strip()
    if pooln:
        p=poolidx.get(norm(pooln))
        if p:
            rec['pagina']=p['pg']
            rec['nombre_pool']=p['nombre']
            rec['coincide_nombre']=True
    out.append(rec)
json.dump(out,open('C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_ficha_web.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('generados',len(out))
for r in out:
    print('%-24s | pag %-4s | %-16s | desc_len %d' % (r['ficha'], r['pagina'], r['metadatos'][:12], len(r['descripcion_larga'])))