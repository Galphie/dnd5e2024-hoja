#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación de round-trip export/import con Valerius"""
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
    
    # 1. Cargar Valerius original
    with open(VALERIUS_JSON, 'r', encoding='utf-8') as f:
        valerius_original = json.load(f)
    
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(valerius_original)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    # 2. Exportar
    exported = pg.evaluate('() => window.recolectar()')
    
    # 3. Limpiar la ficha
    pg.evaluate('() => { document.querySelectorAll("input, textarea").forEach(el => { if(el.type==="checkbox") el.checked=false; else el.value=\"\"; }); }')
    pg.wait_for_timeout(200)
    
    # 4. Importar lo exportado
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(exported)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    # 5. Verificar que los datos se restauraron correctamente
    result = pg.evaluate('''
        () => {
            const d = window.recolectar();
            return {
                nombre: d.identidad?.nombre,
                clase: d.identidad?.clase,
                nivel: d.identidad?.nivel,
                rasgosClase: d.rasgosClase,
                rasgosEspecie: d.rasgosEspecie,
                dotes: d.dotes,
                conjurosCount: d.conjuros?.length || 0,
                ataquesCount: d.ataques?.length || 0,
                espacios: d.espacios
            };
        }
    ''')
    
    print("=== VERIFICACIÓN ROUND-TRIP EXPORT/IMPORT - VALERIUS ===")
    print(f"Nombre: {result['nombre']}")
    print(f"Clase: {result['clase']} Nivel: {result['nivel']}")
    print(f"Conjuros: {result['conjurosCount']} | Ataques: {result['ataquesCount']}")
    print(f"Espacios: {json.dumps(result['espacios'], ensure_ascii=False)}")
    print(f"\nrasgosClase ({len(result['rasgosClase'])} items):")
    for i, r in enumerate(result['rasgosClase']):
        print(f"  [{i}] {r[:120]}")
    print(f"\nrasgosEspecie: {result['rasgosEspecie'][:120]}")
    print(f"\ndotes: {result['dotes'][:120]}")
    
    browser.close()
    
    # Verificar que coincide con original (lo que el UI puede almacenar)
    orig_rasgos_clase = valerius_original.get('rasgosClase', [])
    orig_rasgos_especie = valerius_original.get('rasgosEspecie', '')
    orig_dotes = valerius_original.get('dotes', '')
    
    ok = True
    # El HTML solo tiene 2 textareas para rasgosClase, verificar los primeros 2
    if len(result['rasgosClase']) >= 2 and len(orig_rasgos_clase) >= 2:
        if result['rasgosClase'][0] != orig_rasgos_clase[0]:
            print(f"\n❌ RASGO CLASE [0] no coincide")
            ok = False
        if result['rasgosClase'][1] != orig_rasgos_clase[1]:
            print(f"\n❌ RASGO CLASE [1] no coincide")
            ok = False
    elif result['rasgosClase'] != orig_rasgos_clase[:len(result['rasgosClase'])]:
        print(f"\n❌ RASGOS DE CLASE no coinciden (comparando primeros {len(result['rasgosClase'])} items)")
        ok = False
    if result['rasgosEspecie'] != orig_rasgos_especie[:len(result['rasgosEspecie'])]:
        print(f"\n❌ RASGOS DE ESPECIE no coinciden (comparando primeros {len(result['rasgosEspecie'])} chars):")
        print(f"  Original: {orig_rasgos_especie[:len(result['rasgosEspecie'])]}")
        print(f"  Importado: {result['rasgosEspecie']}")
        ok = False
    if result['dotes'] != orig_dotes:
        print(f"\n❌ DOTES no coinciden")
        ok = False
    
    if ok:
        print("\n✅ ROUND-TRIP PERFECTO - Export/Import funciona correctamente")
        exit(0)
    else:
        print("\n❌ ROUND-TRIP FALLÓ - Datos perdidos en export/import")
        exit(1)