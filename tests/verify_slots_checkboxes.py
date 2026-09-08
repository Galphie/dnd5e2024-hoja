#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación detallada de slots - checkboxes vs margen derecho"""
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
    
    # Verificar estructura completa de cada fila de slots
    slots_info = pg.evaluate('''() => {
        const slots = document.querySelectorAll('.slot');
        const results = [];
        slots.forEach((slot, si) => {
            const rows = slot.querySelectorAll('.r');
            const rowData = [];
            rows.forEach((row, ri) => {
                const rl = row.querySelector('.rl');
                const tl = row.querySelector('.tl input');
                const ds = row.querySelector('.ds');
                const checkboxes = row.querySelectorAll('.dslot');
                
                const csRow = window.getComputedStyle(row);
                const csDs = window.getComputedStyle(ds);
                const rowRect = row.getBoundingClientRect();
                const dsRect = ds?.getBoundingClientRect();
                
                // Check each checkbox position
                const cbData = [];
                checkboxes.forEach((cb, ci) => {
                    const cbRect = cb.getBoundingClientRect();
                    cbData.push({
                        index: ci,
                        left: cbRect.left,
                        right: cbRect.right,
                        width: cbRect.width
                    });
                });
                
                rowData.push({
                    nivel: rl?.textContent?.trim(),
                    rowRect: rowRect,
                    dsRect: dsRect,
                    dsMarginRight: csDs.marginRight,
                    dsMarginLeft: csDs.marginLeft,
                    rowPaddingRight: csRow.paddingRight,
                    checkboxes: cbData
                });
            });
            results.push({slotIndex: si, rows: rowData});
        });
        return results;
    }''')
    
    print("=== VERIFICACIÓN DETALLADA SLOTS - CHECKBOXES vs MARGEN ===")
    for slot in slots_info:
        print(f"\nSlot {slot['slotIndex']}:")
        for r in slot['rows']:
            print(f"  {r['nivel']}:")
            print(f"    row: left={r['rowRect']['left']:.1f}, right={r['rowRect']['right']:.1f}, width={r['rowRect']['width']:.1f}")
            print(f"    ds: right={r['dsRect']['right']:.1f}, marginRight={r['dsMarginRight']}, marginLeft={r['dsMarginLeft']}")
            for cb in r['checkboxes']:
                print(f"    checkbox[{cb['index']}]: left={cb['left']:.1f}, right={cb['right']:.1f}, width={cb['width']:.1f}")
                # Check if checkbox is beyond row right edge
                if cb['right'] > r['rowRect']['right']:
                    print(f"      ❌ CHECKBOX SOBRESALE DEL ROW! ({cb['right']:.1f} > {r['rowRect']['right']:.1f})")
    
    browser.close()