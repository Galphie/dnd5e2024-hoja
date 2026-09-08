#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de exportación JSON con rasgos, especie y dotes"""
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
    
    # Cargar datos de prueba (Valerius)
    pg.evaluate('''
        () => {
            fetch('file:///C:/Users/algpa/.galphies_workspace/ai/dnd-hoja-personaje/personajes/valerius_cogsworth.json')
                .then(r => r.json())
                .then(d => {
                    window.recalc = () => {};
                    if (window.aplicar) window.aplicar(d);
                });
        }
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
                sampleRasgosClase: d.rasgosClase?.[0]?.substring(0, 80),
                sampleRasgosEspecie: d.rasgosEspecie?.substring(0, 80),
                sampleDotes: d.dotes?.substring(0, 80)
            };
        }
    ''')
    
    print("=== VERIFICACIÓN EXPORTACIÓN JSON ===")
    print(f"rasgosClase: {result['rasgosClaseCount']} items - {'✅' if result['hasRasgosClase'] else '❌'}")
    print(f"  Ejemplo: {result['sampleRasgosClase']}")
    print(f"rasgosEspecie: {result['rasgosEspecieLength']} chars - {'✅' if result['hasRasgosEspecie'] else '❌'}")
    print(f"  Ejemplo: {result['sampleRasgosEspecie']}")
    print(f"dotes: {result['dotesLength']} chars - {'✅' if result['hasDotes'] else '❌'}")
    print(f"  Ejemplo: {result['sampleDotes']}")
    
    browser.close()
    
    if result['hasRasgosClase'] and result['hasRasgosEspecie'] and result['hasDotes']:
        print("\n✅ EXPORTACIÓN COMPLETA - Todos los campos presentes")
        exit(0)
    else:
        print("\n❌ FALTAN CAMPOS EN EXPORTACIÓN")
        exit(1)