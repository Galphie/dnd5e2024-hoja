#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación visual de slots nivel 7/8/9 - margen derecho"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FICHA = os.path.join(HERE, '..', 'resultado-hermes', 'ficha_dnd_hermes.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(500)
    
    # Verificar el tercer .slot (niveles 7, 8, 9)
    styles = pg.evaluate('''() => {
        const slots = document.querySelectorAll('.slot');
        const thirdSlot = slots[2]; // 0-indexed: 0=niv1-3, 1=niv4-6, 2=niv7-9
        if (!thirdSlot) return {error: 'No third slot'};
        
        const rows = thirdSlot.querySelectorAll('.r');
        const results = [];
        rows.forEach((row, i) => {
            const ds = row.querySelector('.ds');
            const rl = row.querySelector('.rl');
            const csDs = window.getComputedStyle(ds);
            const csRl = window.getComputedStyle(rl);
            results.push({
                nivel: rl?.textContent?.trim(),
                dsMarginRight: csDs.marginRight,
                dsMarginLeft: csDs.marginLeft,
                dsWidth: csDs.width,
                rlWidth: csRl.width,
                rowRect: row.getBoundingClientRect().toJSON()
            });
        });
        return {slots: results};
    }''')
    
    print("=== VERIFICACIÓN SLOTS NIVEL 7/8/9 - MARGEN DERECHO ===")
    if 'error' in styles:
        print(f"Error: {styles['error']}")
    else:
        for s in styles['slots']:
            print(f"  {s['nivel']}: ds.marginRight={s['dsMarginRight']}, ds.marginLeft={s['dsMarginLeft']}, ds.width={s['dsWidth']}")
            print(f"    row.rect: right={s['rowRect']['right']:.1f}, width={s['rowRect']['width']:.1f}")
    
    browser.close()