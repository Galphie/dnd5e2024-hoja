#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación visual de slots de conjuros - separación"""
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
    
    # Verificar estructura de slots
    slots_info = pg.evaluate('''() => {
        const slots = document.querySelectorAll('.slot');
        const results = [];
        slots.forEach((slot, si) => {
            const hd = slot.querySelector('.hd');
            const rows = slot.querySelectorAll('.r');
            const rowData = [];
            rows.forEach((row, ri) => {
                const rl = row.querySelector('.rl');
                const tl = row.querySelector('.tl input');
                const ds = row.querySelector('.ds');
                const csRl = window.getComputedStyle(rl);
                const csTl = window.getComputedStyle(tl);
                const csDs = window.getComputedStyle(ds);
                const rowRect = row.getBoundingClientRect();
                rowData.push({
                    nivel: rl?.textContent?.trim(),
                    tlValue: tl?.value,
                    rlRect: rl?.getBoundingClientRect(),
                    tlRect: tl?.getBoundingClientRect(),
                    dsRect: ds?.getBoundingClientRect(),
                    rowRect: rowRect,
                    gap: csRl.gap || 'N/A'
                });
            });
            results.push({slotIndex: si, rows: rowData});
        });
        return results;
    }''')
    
    print("=== VERIFICACIÓN SLOTS DE CONJUROS - ESTRUCTURA ===")
    for slot in slots_info:
        print(f"\nSlot {slot['slotIndex']} (columnas de 3 niveles):")
        for r in slot['rows']:
            print(f"  {r['nivel']}: tl={r['tlValue']}, row.left={r['rowRect']['left']:.1f}, row.width={r['rowRect']['width']:.1f}, ds.right={r['dsRect']['right']:.1f}")
    
    # Verificar separación visual entre columnas
    slot_rects = pg.evaluate('''() => {
        const slots = document.querySelectorAll('.slot');
        return Array.from(slots).map(s => s.getBoundingClientRect());
    }''')
    print("\n=== RECTS DE CADA COLUMNA .slot ===")
    for i, r in enumerate(slot_rects):
        print(f"  Slot {i}: left={r['left']:.1f}, right={r['right']:.1f}, width={r['width']:.1f}")
    
    browser.close()