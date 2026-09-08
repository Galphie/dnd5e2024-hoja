#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de exportación JSON con datos de Valerius"""
import os
import json
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FICHA = os.path.join(HERE, '..', 'resultado-hermes', 'ficha_dnd_hermes.html')
VALERIUS_JSON = os.path.join(HERE, '..', 'personajes', 'valerius_cogsworth.json')

with sync_playwright() as p:
    browser = p.chromium.launch()
    pg = browser.new_page(viewport={'width': 1600, 'height': 1200})
    pg.goto('file:///' + FICHA.replace('\\', '/'))
    pg.wait_for_timeout(500)
    
    # Cargar datos de Valerius
    with open(VALERIUS_JSON, 'r', encoding='utf-8') as f:
        valerius = json.load(f)
    
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(valerius)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    # Exportar y verificar
    result = pg.evaluate('''
        () => {
            const d = window.recolectar();
            return {
                hasRasgosClase: Array.isArray(d.rasgosClase) && d.rasgosClase.length > 0,
                rasgosClaseCount: d.rasgosClase?.length || 0,
                hasRasgosEspecie: typeof d.rasgosEspecie === 'string' && d.rasgosEspecie.length > 0,
                rasgosEspecieLength: d.rasgosEspecie?.length || 0,
                hasDotes: typeof d.dotes === 'string' && d.dotes.length > 0,
                dotesLength: d.dotes?.length || 0,
                sampleRasgosClase: d.rasgosClase?.[0]?.substring(0, 120),
                sampleRasgosEspecie: d.rasgosEspecie?.substring(0, 120),
                sampleDotes: d.dotes?.substring(0, 120),
                allRasgosClase: d.rasgosClase,
                allRasgosEspecie: d.rasgosEspecie,
                allDotes: d.dotes
            };
        }
    ''')
    
    print("=== VERIFICACIÓN EXPORTACIÓN JSON - VALERIUS ===")
    print(f"rasgosClase: {result['rasgosClaseCount']} items - {'✅' if result['hasRasgosClase'] else '❌'}")
    for i, r in enumerate(result['allRasgosClase']):
        print(f"  [{i}] {r[:150]}")
    print(f"\nrasgosEspecie: {result['rasgosEspecieLength']} chars - {'✅' if result['hasRasgosEspecie'] else '❌'}")
    print(f"  {result['allRasgosEspecie'][:200]}")
    print(f"\ndotes: {result['dotesLength']} chars - {'✅' if result['hasDotes'] else '❌'}")
    print(f"  {result['allDotes'][:200]}")
    
    browser.close()
    
    if result['hasRasgosClase'] and result['hasRasgosEspecie'] and result['hasDotes']:
        print("\n✅ EXPORTACIÓN COMPLETA - Todos los campos de Valerius presentes")
        exit(0)
    else:
        print("\n❌ FALTAN CAMPOS EN EXPORTACIÓN")
        exit(1)