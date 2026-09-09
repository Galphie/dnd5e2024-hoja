#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación layout página 2 - cajas y solapamientos"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FICHA = os.path.join(HERE, '..', 'resultado-hermes', 'ficha_dnd_hermes.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(500)
    pg.evaluate('showPage(2)')
    pg.wait_for_timeout(300)
    
    # Obtener rects de todas las cajas de página 2
    rects = pg.evaluate('''() => {
        const boxes = [
            'apt', 'p2b', 'slots', 'spell', 'apar-block', 'hist-blk', 'idiom', 'equip2'
        ];
        const results = {};
        boxes.forEach(cls => {
            const el = document.querySelector(`.blk.${cls}, .${cls}`);
            if (el) results[cls] = el.getBoundingClientRect();
        });
        // También el slotgrid interno
        const sg = document.querySelector('.sg');
        if (sg) results['slotgrid'] = sg.getBoundingClientRect();
        return results;
    }''')
    
    print("=== LAYOUT PÁGINA 2 - RECTS DE CAJAS ===")
    for k, v in rects.items():
        if v:
            print(f"  {k}: left={v['left']:.1f}, top={v['top']:.1f}, right={v['right']:.1f}, bottom={v['bottom']:.1f}, w={v['width']:.1f}, h={v['height']:.1f}")
    
    # Verificar solapamientos
    print("\n=== VERIFICACIÓN SOLAPAMIENTOS ===")
    boxes_list = ['apt', 'p2b', 'slots', 'spell', 'apar-block', 'hist-blk', 'idiom', 'equip2']
    for i, a in enumerate(boxes_list):
        for b in boxes_list[i+1:]:
            if a in rects and b in rects:
                ra, rb = rects[a], rects[b]
                # Check overlap
                overlap_x = not (ra['right'] <= rb['left'] or rb['right'] <= ra['left'])
                overlap_y = not (ra['bottom'] <= rb['top'] or rb['bottom'] <= ra['top'])
                if overlap_x and overlap_y:
                    print(f"  ❌ SOLAPAMIENTO: {a} ∩ {b}")
                    print(f"     {a}: l={ra['left']:.1f} r={ra['right']:.1f} t={ra['top']:.1f} b={ra['bottom']:.1f}")
                    print(f"     {b}: l={rb['left']:.1f} r={rb['right']:.1f} t={rb['top']:.1f} b={rb['bottom']:.1f}")
    
    browser.close()