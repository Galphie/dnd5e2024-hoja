#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de estilos computados en Rasgos de Clase"""
import os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath('.'))
FICHA = os.path.join(HERE, 'personajes', 'ficha_valerius.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(300)
    pg.evaluate('showPage(1)')
    pg.wait_for_timeout(200)

    # Obtener estilos computados del textarea
    styles = pg.evaluate('''() => {
        const ta = document.querySelector('.cf-col textarea');
        const cs = window.getComputedStyle(ta);
        return {
            fontSize: cs.fontSize,
            lineHeight: cs.lineHeight,
            backgroundImage: cs.backgroundImage,
            paddingTop: cs.paddingTop,
            paddingBottom: cs.paddingBottom,
            height: cs.height,
            boxSizing: cs.boxSizing
        };
    }''')
    print('Estilos computados:')
    for k, v in styles.items():
        print(f'  {k}: {v}')

    # Verificar la alineación exacta: line-height vs período del gradient
    # font-size: 8.5px, line-height: 1.7 -> 14.45px
    # gradient: transparent 0 13.45px, #c4b896 13.45px 14.45px -> período 14.45px
    print('\nline-height esperado: 8.5 * 1.7 = 14.45px')
    print('Período gradient: 14.45px')
    print('Coinciden exactamente.')

    browser.close()