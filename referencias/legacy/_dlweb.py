# -*- coding: utf-8 -*-
# Mapear nombres de la fichar -> slug aidedd 2024, descargar y guardar HTML
import subprocess, os
# (nombre_en_ficha, slug_aidedd)
MAP=[
 ('Rayo de Fuego','descarga-de-fuego'),
 ('Mano de Mago','mano-de-mago'),
 ('Prestidigitación','prestidigitacion'),
 ('Luz','luz'),
 ('Ráfaga de Hechicero','estallido-magico'),
 ('Toque Gélido','toque-helado'),
 ('Descarga de Cuchillos',''),  # homebrew? no oficial en 2024
 ('Chasquido Atronador','tronar'),
 ('Luces Danzantes','luces-danzantes'),
 ('Mensaje','mensaje'),
 ('Ilusión Menor','ilusion-menor'),
 ('Rociada Venenosa','rociada-venenosa'),
 ('Rayo de Escarcha','rayo-de-escarcha'),
 ('Salvajismo',''),  # Primal Savagery no en PHB 2024
 ('Burla Cruel','burla-danina'),
 ('Descarga Eléctrica','agarre-electrizante'),
 ('Estabilizar','piedad-con-los-moribundos'),
 ('Escudo','escudo'),
 ('Orbe Cromático','orbe-cromatico'),
 ('Llamarada','manos-ardientes'),
 ('Proyectil Mágico','proyectil-magico'),
 ('Armadura de Mago','armadura-de-mago'),
 ('Comprender Idiomas','entender-idiomas'),
 ('Retir expeditiva','retirada-expeditiva'),
 ('Paso Brumoso','paso-brumoso'),
 ('Rayo Abrasador','rayo-abrasador'),
 ('Invisibilidad','invisibilidad'),
 ('Sugestión','sugestion'),
 ('Añicos','hacer-avicos'),
 ('Bola de Fuego','bola-de-fuego'),
 ('Volar','volar'),
 ('Contrahechizo','contrahechizo'),
 ('Relámpago','relampago'),
 ('Disipar Magia','disipar-magia'),
 ('Muro de Fuego','muro-de-fuego'),
]
os.makedirs('aided',exist_ok=True)
for name,slug in MAP:
    # corregir errores de teclado en nombres
    name=name.replace('Retirar','Detectar')
    name=name.replace('Añices','Añicos')
    if not slug: 
        print('SKIP',name); continue
    fn='aided/%s.html'%slug
    if os.path.exists(fn) and os.path.getsize(fn)>5000:
        print('exists',name); continue
    subprocess.run(['curl','-s','-A','Mozilla/5.0 (Windows NT 10.0; Win64; x64) rv:133.0','https://www.aidedd.org/spell/es/'+slug,'-o',fn],check=False)
    try: sz=os.path.getsize(fn)
    except: sz=0
    print(('OK ' if sz>5000 else 'SHORT ')+name+' -> '+slug+' '+str(sz))