#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de estilos RASGOS DE ESPECIE vs DOTES"""
import os
import json
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FICHA = os.path.join(HERE, '..', 'resultado-hermes', 'ficha_dnd_hermes.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(500)
    
    # Cargar datos de prueba
    with open(os.path.join(HERE, '..', 'personajes', 'valerius_cogsworth.json'), 'r', encoding='utf-8') as f:
        valerius = json.load(f)
    
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(valerius)});
        }}
    ''')
    pg.wait_for_timeout(500)
    pg.evaluate('showPage(1)')
    pg.wait_for_timeout(200)

    # Verificar ambos textareas
    styles = pg.evaluate('''() => {
        const espec = document.querySelector('#especRows');
        const dotes = document.querySelector('.dt-l textarea');
        const csEspec = window.getComputedStyle(espec);
        const csDotes = window.getComputedStyle(dotes);
        return {
            espec: {
                fontSize: csEspec.fontSize,
                lineHeight: csEspec.lineHeight,
                backgroundImage: csEspec.backgroundImage,
                resize: csEspec.resize,
                width: csEspec.width,
                height: csEspec.height
            },
            dotes: {
                fontSize: csDotes.fontSize,
                lineHeight: csDotes.lineHeight,
                backgroundImage: csDotes.backgroundImage,
                resize: csDotes.resize,
                width: csDotes.width,
                height: csDotes.height
            }
        };
    }''')
    
    print("=== VERIFICACIÓN ESTILOS RASGOS DE ESPECIE vs DOTES ===")
    print("\nRASGOS DE ESPECIE (#especRows):")
    for k, v in styles['espec'].items():
        print(f"  {k}: {v}")
    
    print("\nDOTES (.dt-l textarea):")
    for k, v in styles['dotes'].items():
        print(f"  {k}: {v}")
    
    # Comparar
    match = True
    for k in ['fontSize', 'lineHeight', 'backgroundImage', 'resize']:
        if styles['espec'][k] != styles['dotes'][k]:
            print(f"\n❌ MISMATCH {k}: espec='{styles['espec'][k]}' vs dotes='{styles['dotes'][k]}'")
            match = False
    
    if match:
        print("\n✅ ESTILOS IDÉNTICOS - Rasgos de Especie y Dotes son iguales")
        exit(0)
    else:
        print("\n❌ ESTILOS DIFERENTES")
        exit(1)