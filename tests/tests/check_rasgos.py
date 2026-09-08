#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación visual Playwright: líneas fondo vs texto en Rasgos de Clase"""
import os
import sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath('.'))
FICHA = os.path.join(HERE, 'personajes', 'ficha_valerius.html')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(300)

    # Navegar a página 1 (personaje)
    pg.evaluate('showPage(1)')
    pg.wait_for_timeout(200)

    # Obtener la posición y dimensiones del textarea de rasgos de clase
    textarea = pg.query_selector('.cf-col textarea')
    if textarea:
        box = textarea.bounding_box()
        print(f'Textarea box: {box}')

        cf_in = pg.query_selector('.cf-in')
        cf_in_box = cf_in.bounding_box() if cf_in else None
        print(f'cf-in box: {cf_in_box}')

        # Tomar screenshot para verificación visual
        os.makedirs('tests/_out', exist_ok=True)
        pg.screenshot(path='tests/_out/rasgos_clase_check.png')
        print('Screenshot guardado en tests/_out/rasgos_clase_check.png')
    else:
        print('No se encontró .cf-col textarea')

    browser.close()