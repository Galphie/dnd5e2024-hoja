#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación del botón Vaciar hoja"""
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
    
    # Cargar datos de Valerius
    with open(os.path.join(HERE, '..', 'personajes', 'valerius_cogsworth.json'), 'r', encoding='utf-8') as f:
        valerius = json.load(f)
    
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(valerius)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    # Verificar que hay datos
    antes = pg.evaluate('''
        () => {
            const nombre = document.querySelector('[data-k="nombre"]').value;
            const clase = document.querySelector('[data-k="clase"]').value;
            const ca = document.querySelector('#f-ca').value;
            const hp = document.querySelector('.hp-act input').value;
            return {nombre, clase, ca, hp, hasData: nombre && clase && ca && hp};
        }
    ''')
    print(f"ANTES: {antes}")
    
    # Click en botón vaciar (usar toast modal)
    pg.click('#btn-clear')
    pg.wait_for_timeout(300)
    # Click en "Confirmar" en el toast
    pg.click('.toast-btn.confirm')
    pg.wait_for_timeout(500)
    
    # Verificar que se vació
    despues = pg.evaluate('''
        () => {
            const nombre = document.querySelector('[data-k="nombre"]').value;
            const clase = document.querySelector('[data-k="clase"]').value;
            const ca = document.querySelector('#f-ca').value;
            const hp = document.querySelector('.hp-act input').value;
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked').length;
            return {nombre, clase, ca, hp, checkboxes, isEmpty: !nombre && !clase && !ca && !hp};
        }
    ''')
    print(f"DESPUÉS: {despues}")
    
    browser.close()
    
    if despues['isEmpty'] and despues['checkboxes'] == 0:
        print("\n✅ VACIAR HOJA FUNCIONA - Todo limpio")
        exit(0)
    else:
        print("\n❌ VACIAR HOJA NO FUNCIONA BIEN")
        exit(1)