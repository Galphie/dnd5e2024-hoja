#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación labels (NIVEL X) dentro del rectángulo .slots"""
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
    
    # Verificar labels .rl vs .slots
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
                const rlRect = rl?.getBoundingClientRect();
                
                rowData.push({
                    nivel: rl?.textContent?.trim(),
                    rlRight: rlRect?.right,
                    rlLeft: rlRect?.left,
                    slotsRight: slotsRect.right,
                    slotsLeft: slotsRect.left,
                    inside: rlRect ? (rlRect.right <= slotsRect.right && rlRect.left >= slotsRect.left) : false
                });
            });
            results.push({slotIndex: si, rows: rowData});
        });
        return {slotsRect: {left: slotsRect.left, right: slotsRect.right}, slots: results};
    }''')
    
    print("=== VERIFICACIÓN LABELS .rl DENTRO DE .slots ===")
    print(f".slots rect: left={slots_info['slotsRect']['left']:.1f}, right={slots_info['slotsRect']['right']:.1f}")
    
    all_inside = True
    for slot in slots_info['slots']:
        print(f"\nSlot {slot['slotIndex']}:")
        for r in slot['rows']:
            status = "✅" if r['inside'] else "❌ FUERA"
            print(f"  {r['nivel']}: rl.right={r['rlRight']:.1f}, rl.left={r['rlLeft']:.1f}, slots.right={r['slotsRight']:.1f}, slots.left={r['slotsLeft']:.1f} {status}")
            if not r['inside']:
                all_inside = False
    
    browser.close()
    
    if all_inside:
        print("\n✅ TODOS LOS LABELS DENTRO DEL RECTÁNGULO .slots")
        exit(0)
    else:
        print("\n❌ HAY LABELS FUERA DEL RECTÁNGULO")
        exit(1)