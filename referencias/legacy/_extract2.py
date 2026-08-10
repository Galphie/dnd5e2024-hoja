# -*- coding: utf-8 -*-
# Extrae texto por BLOQUES con coordenadas: agrupa lineas por bloque, ordena bloques por (columna, y0).
import pymupdf
doc=pymupdf.open("C:/Users/algpa/Desktop/hojapersonaje/referencias/Manual del Jugador 2024.pdf")
out=[]
for pno in range(240,346):
    page=doc.load_page(pno)
    d=page.get_text("dict")
    W=page.rect.width; mid=W/2
    blocks=[]
    for b in d["blocks"]:
        if b["type"]!=0: continue
        x0=b["bbox"][0]; y0=b["bbox"][1]
        txts=[]
        for ln in b["lines"]:
            t="".join(sp["text"] for sp in ln["spans"]).rstrip()
            if t.strip(): txts.append(t)
        if txts:
            blocks.append((0 if x0<mid else 1, y0, txts))
    blocks.sort(key=lambda t:(t[0], t[1]))
    out.append(f"===== PAGE {pno+1} (pdf idx {pno}) =====")
    for col,y0,txts in blocks:
        out.extend(txts)
open("C:/Users/algpa/Desktop/hojapersonaje/referencias/spells_txt/all_241_346.txt","w",encoding="utf-8").write("\n".join(out))
print("re-extraido por bloques. lineas:", len(out))
