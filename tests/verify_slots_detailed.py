#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación detallada slots - row widths"""
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
    
    # Verificar widths detallados
    info = pg.evaluate('''() => {
        const slots = document.querySelector('.slots');
        const sg = document.querySelector('.sg');
        const slotsRect = slots.getBoundingClientRect();
        const sgRect = sg.getBoundingClientRect();
        
        const slotCols = document.querySelectorAll('.slot');
        const results = [];
        slotCols.forEach((slot, si) => {
            const slotRect = slot.getBoundingClientRect();
            const rows = slot.querySelectorAll('.r');
            const rowData = [];
            rows.forEach((row, ri) => {
                const rowRect = row.getBoundingClientRect();
                const rl = row.querySelector('.rl');
                const tl = row.querySelector('.tl');
                const ds = row.querySelector('.ds');
                rowData.push({
                    nivel: rl?.textContent?.trim(),
                    row: {left: rowRect.left, right: rowRect.right, width: rowRect.width},
                    rl: rl?.getBoundingClientRect(),
                    tl: tl?.getBoundingClientRect(),
                    ds: ds?.getBoundingClientRect(),
                });
            });
            results.push({slotIndex: si, slotRect: {left: slotRect.left, right: slotRect.right, width: slotRect.width}, rows: rowData});
        });
        return {slotsRect, sgRect, slots: results};
    }''')
    
    print("=== DETAILED SLOT WIDTHS ===")
    print(f".slots: left={info['slotsRect']['left']:.1f}, right={info['slotsRect']['right']:.1f}, width={info['slotsRect']['width']:.1f}")
    print(f".sg: left={info['sgRect']['left']:.1f}, right={info['sgRect']['right']:.1f}, width={info['sgRect']['width']:.1f}")
    
    for slot in info['slots']:
        print(f"\nSlot {slot['slotIndex']} (col): left={slot['slotRect']['left']:.1f}, right={slot['slotRect']['right']:.1f}, width={slot['slotRect']['width']:.1f}")
        for r in slot['rows']:
            if r['row']:
                print(f"  {r['nivel']}: row.right={r['row']['right']:.1f}, row.width={r['row']['width']:.1f}")
            if r['tl']:
                print(f"    TL: left={r['tl']['left']:.1f}, right={r['tl']['right']:.1f}, w={r['tl']['width']:.1f}")
            if r['ds']:
                print(f"    DS: left={r['ds']['left']:.1f}, right={r['ds']['right']:.1f}, w={r['ds']['width']:.1f}")
    
    browser.close()