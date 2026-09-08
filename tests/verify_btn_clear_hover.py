#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación hover btn-clear rojo"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FICHA = os.path.join(HERE, '..', 'resultado-hermes', 'ficha_dnd_hermes.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(500)
    
    # Hover sobre btn-clear
    btn = pg.locator('#btn-clear')
    btn.hover()
    pg.wait_for_timeout(200)
    
    styles = pg.evaluate('''() => {
        const btn = document.getElementById('btn-clear');
        const cs = window.getComputedStyle(btn);
        return {
            backgroundColor: cs.backgroundColor,
            color: cs.color,
            borderColor: cs.borderColor,
        };
    }''')
    
    print("=== VERIFICACIÓN HOVER BTN-CLEAR ===")
    print(f"  backgroundColor: {styles['backgroundColor']}")
    print(f"  color: {styles['color']}")
    print(f"  borderColor: {styles['borderColor']}")
    
    # Verificar que es rojo (#9a3a2a = rgb(154, 58, 42))
    bg = styles['backgroundColor']
    is_red = '154, 58, 42' in bg or '9a3a2a' in bg.lower() or 'rgb(154, 58, 42)' in bg
    
    if is_red:
        print("\n✅ HOVER ROJO FUNCIONA")
        exit(0)
    else:
        print(f"\n❌ HOVER NO ES ROJO: {bg}")
        exit(1)