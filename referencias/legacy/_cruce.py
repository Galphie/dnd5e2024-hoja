# -*- coding: utf-8 -*-
import json, unicodedata
def norm(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
pool=json.load(open("C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/pool.json",encoding="utf-8"))
idx={p['norm']:p for p in pool}
# ficha -> nombre oficial 2024 (si difieren)
F2O={
 'Rayo de Fuego':'DESCARGA DE FUEGO','Mano de Mago':'MANO DE MAGO','Prestidigitación':'PRESTIDIGITACIÓN',
 'Luz':'Luz','Ráfaga de Hechicero':'ESTALLIDO MÁGICO','Toque Gélido':'TOQUE HELADO',
 'Descarga de Cuchillos':'GUARDIA DE CUCHILLAS','Chasquido Atronador':'TRONAR','Luces Danzantes':'LUCES DANZANTES',
 'Mensaje':'MENSAJE','Ilusión Menor':'ILUSIÓN MENOR','Rociada Venenosa':'ROCIADA VENENOSA',
 'Rayo de Escarcha':'RAYO DE ESCARCHA','Salvajismo':'?ESSAVAS?','Burla Cruel':'BURLA DAÑINA',
 'Descarga Eléctrica':'AGARRE ELECTRIZANTE','Estabilizar':'PIEDAD CON LOS MORIBUNDOS','Escudo':'?NO?',
 'Orbe Cromático':'ORBE CROMÁTICO','Llamarada':'MANOS ARDIENTES','Proyectil Mágico':'PROYECTIL MÁGICO',
 'Armadura de Mago':'ARMADURA DE MAGO','Comprender Idiomas':'ENTENDER IDIOMAS','Detectar Magia':'DETECTAR MAGIA',
 'Retirada Expeditiva':'RETIRADA EXPEDITIVA','Paso Brumoso':'PASO BRUMOSO','Rayo Coruscante':'SAETA GUÍA',
 'Invisibilidad':'INVISIBILIDAD','Sugestión':'SUGESTIÓN','Añicos':'HACER AÑICOS','Bola de Fuego':'BOLA DE FUEGO',
 'Volar':'VOLAR','Contrahechizo':'CONTRABORUNDO','Relámpago':'RELÁMPAGO','Disipar Magia':'DISIPAR MAGIA',
 'Muro de Fuego':'MURO DE FUEGO'}
for f,o in F2O.items():
    p=idx.get(norm(o))
    print((f+' -> '+o).ljust(48), 'OK pg'+str(p['pg'])+' p'+str(p['niv']) if p else 'NO EN POOL')