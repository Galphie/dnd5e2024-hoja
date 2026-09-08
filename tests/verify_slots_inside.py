#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación detallada de slots - checkboxes dentro del recuadro visual"""
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
    
    # Verificar el recuadro visual de .slots vs checkboxes
    slots_info = pg.evaluate('''() => {
        const slotsContainer = document.querySelector('.slots');
        const slotsRect = slotsContainer.getBoundingClientRect();
        
        const slots = document.querySelectorAll('.slot');
        const results = [];
        slots.forEach((slot, si) => {
            const rows = slot.querySelectorAll('.r');
            const rowData = [];
            rows.forEach((row, ri) => {
                const rl = row.querySelector('.rl');
                const ds = row.querySelector('.ds');
                const checkboxes = row.querySelectorAll('.dslot');
                
                const rowRect = row.getBoundingClientRect();
                const dsRect = ds?.getBoundingClientRect();
                
                const cbData = [];
                checkboxes.forEach((cb, ci) => {
                    const cbRect = cb.getBoundingClientRect();
                    cbData.push({
                        index: ci,
                        left: cbRect.left,
                        right: cbRect.right,
                        insideSlots: cbRect.right <= slotsRect.right
                    });
                });
                
                rowData.push({
                    nivel: rl?.textContent?.trim(),
                    rowRight: rowRect.right,
                    slotsRight: slotsRect.right,
                    checkboxes: cbData
                });
            });
            results.push({slotIndex: si, rows: rowData});
        });
        return {slotsRect: {left: slotsRect.left, right: slotsRect.right}, slots: results};
    }''')
    
    print("=== VERIFICACIÓN SLOTS - CHECKBOXES DENTRO DEL RECTÁNGULO .slots ===")
    print(f".slots rect: left={slots_info['slotsRect']['left']:.1f}, right={slots_info['slotsRect']['right']:.1f}")
    
    all_inside = True
    for slot in slots_info['slots']:
        print(f"\nSlot {slot['slotIndex']}:")
        for r in slot['rows']:
            print(f"  {r['nivel']}: row.right={r['rowRight']:.1f}, slots.right={r['slotsRight']:.1f}")
            for cb in r['checkboxes']:
                status = "✅" if cb['insideSlots'] else "❌ FUERA"
                print(f"    checkbox[{cb['index']}]: right={cb['right']:.1f} {status}")
                if not cb['insideSlots']:
                    all_inside = False
    
    browser.close()
    
    if all_inside:
        print("\n✅ TODOS LOS CHECKBOXES DENTRO DEL RECTÁNGULO .slots")
        exit(0)
    else:
        print("\n❌ HAY CHECKBOXES FUERA DEL RECTÁNGULO")
        exit(1)