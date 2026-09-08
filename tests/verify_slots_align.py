#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación alineación labels Totales/Gastados con inputs/checkboxes"""
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
    
    # Verificar alineación .hd spans con .tl input y .ds checkboxes
    align_info = pg.evaluate('''() => {
        const slots = document.querySelectorAll('.slot');
        const results = [];
        slots.forEach((slot, si) => {
            const hd = slot.querySelector('.hd');
            const hdSpans = hd?.querySelectorAll('span') || [];
            const rows = slot.querySelectorAll('.r');
            const rowData = [];
            rows.forEach((row, ri) => {
                const rl = row.querySelector('.rl');
                const tl = row.querySelector('.tl input');
                const ds = row.querySelector('.ds');
                const checkboxes = row.querySelectorAll('.dslot');
                
                const tlRect = tl?.getBoundingClientRect();
                const dsRect = ds?.getBoundingClientRect();
                const cbRects = Array.from(checkboxes).map(cb => cb.getBoundingClientRect());
                
                rowData.push({
                    nivel: rl?.textContent?.trim(),
                    tl: tlRect ? {left: tlRect.left, right: tlRect.right, center: tlRect.left + tlRect.width/2} : null,
                    ds: dsRect ? {left: dsRect.left, right: dsRect.right, center: dsRect.left + dsRect.width/2} : null,
                    checkboxes: cbRects.map(r => ({left: r.left, right: r.right, center: r.left + r.width/2}))
                });
            });
            results.push({slotIndex: si, rows: rowData});
        });
        return results;
    }''')
    
    print("=== VERIFICACIÓN ALINEACIÓN TOTALES/GASTADOS ===")
    for slot in align_info:
        print(f"\nSlot {slot['slotIndex']}:")
        for r in slot['rows']:
            if r['tl'] and r['ds']:
                # hd spans: first is "Totales", second is "Gastados"
                print(f"  {r['nivel']}:")
                print(f"    TL input: center={r['tl']['center']:.1f} (left={r['tl']['left']:.1f}, right={r['tl']['right']:.1f})")
                print(f"    DS checkboxes: center={r['ds']['center']:.1f} (left={r['ds']['left']:.1f}, right={r['ds']['right']:.1f})")
                for i, cb in enumerate(r['checkboxes']):
                    print(f"    checkbox[{i}]: center={cb['center']:.1f}")
    
    browser.close()