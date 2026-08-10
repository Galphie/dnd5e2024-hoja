# -*- coding: utf-8 -*-
"""Captura las 4 paginas de mi ficha + P2-4 de la referencia v19 a escala 2."""
import asyncio, os
from playwright.async_api import async_playwright
MINE = "file:///C:/Users/algpa/Desktop/hojapersonaje/resultado-hermes/ficha_dnd_hermes.html"
REF = "file:///C:/Users/algpa/Desktop/hojapersonaje/versiones/dnd_sheet_v19_editable.html"
OUT = r"C:\Users\algpa\Desktop\hojapersonaje\resultado-hermes\_shots"
os.makedirs(OUT, exist_ok=True)

MYJS = """(id)=>{ for(let i=1;i<=4;i++){const p=document.getElementById('pg'+i); if(p) p.classList.toggle('show', i===id);} }"""
REFJS = """(id)=>{ const ps=document.querySelectorAll('.page'); ps.forEach(x=>x.style.display='none');
  const e=document.getElementById('p'+id); if(e) e.style.display='block'; }"""

async def shoot(page, name, pageid, showjs):
    await page.set_viewport_size({"width":1300,"height":1180})
    await page.evaluate(showjs, pageid)
    await page.wait_for_timeout(250)
    await page.screenshot(path=os.path.join(OUT, "%s_p%d.png" % (name, pageid)),
                          clip={"x":0,"y":0,"width":820,"height":1180})

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        ctx = await b.new_context(viewport={"width":1300,"height":1180}, device_scale_factor=2)
        p = await ctx.new_page()
        errs=[]
        p.on("pageerror", lambda e: errs.append("PAGEERR "+str(e)[:200]))
        await p.goto(MINE); await p.wait_for_timeout(800)
        print("== mine ==")
        for i in [1,2,3,4]:
            await shoot(p, "mine", i, MYJS)
        print("  pageerrors:", errs if errs else "none")
        await ctx.close()
        ctx2 = await b.new_context(viewport={"width":1300,"height":1180}, device_scale_factor=2)
        p2 = await ctx2.new_page()
        errs2=[]
        p2.on("pageerror", lambda e: errs2.append("PAGEERR "+str(e)[:200]))
        await p2.goto(REF); await p2.wait_for_timeout(800)
        print("== ref ==")
        for i in [2,3,4]:
            await shoot(p2, "ref", i, REFJS)
        print("  pageerrors:", errs2 if errs2 else "none")
        await ctx2.close()
        await b.close()

asyncio.run(main())
print("DONE")