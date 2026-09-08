#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación del recuadro visual de slots"""
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
    
    # Verificar el recuadro visual (.slots) y sus bordes
    rects = pg.evaluate('''() => {
        const slots = document.querySelector('.slots');
        const sg = document.querySelector('.sg');
        const slotCols = document.querySelectorAll('.slot');
        
        return {
            slots: slots?.getBoundingClientRect(),
            sg: sg?.getBoundingClientRect(),
            slot0: slotCols[0]?.getBoundingClientRect(),
            slot1: slotCols[1]?.getBoundingClientRect(),
            slot2: slotCols[2]?.getBoundingClientRect(),
        };
    }''')
    
    print("=== RECUADRO VISUAL SLOTS ===")
    for k, v in rects.items():
        if v:
            print(f"  {k}: left={v['left']:.1f}, right={v['right']:.1f}, width={v['width']:.1f}")
    
    # Verificar último checkbox de cada slot vs right edge del slot
    checkboxes_vs_slot = pg.evaluate('''() => {
        const slotCols = document.querySelectorAll('.slot');
        const results = [];
        slotCols.forEach((slot, si) => {
            const slotRect = slot.getBoundingClientRect();
            const rows = slot.querySelectorAll('.r');
            const lastRow = rows[rows.length - 1];
            const checkboxes = lastRow.querySelectorAll('.dslot');
            const lastCb = checkboxes[checkboxes.length - 1];
            const cbRect = lastCb.getBoundingClientRect();
            results.push({
                slot: si,
                slotRight: slotRect.right,
                lastCbRight: cbRect.right,
                inside: cbRect.right <= slotRect.right
            });
        });
        return results;
    }''')
    
    print("\n=== ÚLTIMO CHECKBOX vs RECUADRO SLOT ===")
    for r in checkboxes_vs_slot:
        status = "✅ DENTRO" if r['inside'] else "❌ FUERA"
        print(f"  Slot {r['slot']}: slot.right={r['slotRight']:.1f}, lastCb.right={r['lastCbRight']:.1f} -> {status}")
    
    browser.close()