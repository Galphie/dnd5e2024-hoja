#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de estilos RASGOS DE CLASE"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FICHA = os.path.join(HERE, '..', 'resultado-hermes', 'ficha_dnd_hermes.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(500)
    
    # Cargar datos de Valerius
    import json
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

    styles = pg.evaluate('''() => {
        const ta = document.querySelector('.cf-col textarea');
        const cs = window.getComputedStyle(ta);
        return {
            fontSize: cs.fontSize,
            lineHeight: cs.lineHeight,
            backgroundImage: cs.backgroundImage,
        };
    }''')
    print('RASGOS DE CLASE textarea:')
    for k, v in styles.items():
        print(f'  {k}: {v}')
    
    browser.close()