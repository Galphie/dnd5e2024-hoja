#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación selector Aptitud Mágica"""
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
    pg.evaluate('showPage(2)')
    pg.wait_for_timeout(300)
    
    # 1. Verificar que el select existe y tiene las 6 opciones
    select_info = pg.evaluate('''() => {
        const sel = document.getElementById('apt-stat');
        if (!sel) return {error: 'No select'};
        const options = Array.from(sel.options).map(o => ({value: o.value, text: o.textContent, selected: o.selected}));
        return {exists: true, value: sel.value, options, classList: Array.from(sel.classList)};
    }''')
    
    print("=== VERIFICACIÓN SELECTOR APTITUD MÁGICA ===")
    if 'error' in select_info:
        print(f"❌ {select_info['error']}")
        browser.close()
        exit(1)
    
    print(f"Select existe: ✅")
    print(f"Clase E: {'E' in select_info['classList']}")
    print(f"Valor inicial: {select_info['value']} {'✅ (INT por defecto)' if select_info['value'] == 'INT' else '❌'}")
    print(f"Opciones ({len(select_info['options'])}):")
    for opt in select_info['options']:
        mark = ' ← seleccionado' if opt['selected'] else ''
        print(f"  {opt['value']}: {opt['text']}{mark}")
    
    # 2. Test cambio de característica y recálculo
    print("\n--- Test recálculo al cambiar característica ---")
    
    # Cargar datos de prueba con INT=19, CAR=10, SAB=12
    with open(os.path.join(HERE, '..', 'personajes', 'valerius_cogsworth.json'), 'r', encoding='utf-8') as f:
        valerius = json.load(f)
    
    pg.evaluate(f'''
        () => {{
            if (window.aplicar) window.aplicar({json.dumps(valerius)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    # Verificar valores con INT (mod +4, prof +3)
    vals_int = pg.evaluate('''() => ({
        mMod: document.getElementById('m-mod').textContent,
        mDc: document.getElementById('m-dc').textContent,
        mAtk: document.getElementById('m-atk').textContent,
        selectVal: document.getElementById('apt-stat').value
    })''')
    print(f"\nCon INT (mod +4, prof +3): MOD={vals_int['mMod']}, DC={vals_int['mDc']}, ATK={vals_int['mAtk']}")
    # DC = 8 + 3 + 4 = 15, ATK = 3 + 4 = +7
    int_ok = vals_int['mMod']=='+4' and vals_int['mDc']=='15' and vals_int['mAtk']=='+7'
    print(f"  {'✅' if int_ok else '❌'} (esperado +4, 15, +7)")
    
    # Cambiar a CAR (mod +0)
    pg.select_option('#apt-stat', 'CAR')
    pg.wait_for_timeout(300)
    
    vals_car = pg.evaluate('''() => ({
        mMod: document.getElementById('m-mod').textContent,
        mDc: document.getElementById('m-dc').textContent,
        mAtk: document.getElementById('m-atk').textContent,
        selectVal: document.getElementById('apt-stat').value
    })''')
    print(f"\nCon CAR (mod +0, prof +3): MOD={vals_car['mMod']}, DC={vals_car['mDc']}, ATK={vals_car['mAtk']}")
    # DC = 8 + 3 + 0 = 11, ATK = 3 + 0 = +3
    car_ok = vals_car['mMod']=='+0' and vals_car['mDc']=='11' and vals_car['mAtk']=='+3'
    print(f"  {'✅' if car_ok else '❌'} (esperado +0, 11, +3)")
    
    # Cambiar a SAB (mod +1)
    pg.select_option('#apt-stat', 'SAB')
    pg.wait_for_timeout(300)
    
    vals_sab = pg.evaluate('''() => ({
        mMod: document.getElementById('m-mod').textContent,
        mDc: document.getElementById('m-dc').textContent,
        mAtk: document.getElementById('m-atk').textContent,
        selectVal: document.getElementById('apt-stat').value
    })''')
    print(f"\nCon SAB (mod +1, prof +3): MOD={vals_sab['mMod']}, DC={vals_sab['mDc']}, ATK={vals_sab['mAtk']}")
    # DC = 8 + 3 + 1 = 12, ATK = 3 + 1 = +4
    sab_ok = vals_sab['mMod']=='+1' and vals_sab['mDc']=='12' and vals_sab['mAtk']=='+4'
    print(f"  {'✅' if sab_ok else '❌'} (esperado +1, 12, +4)")
    
    # 3. Test export/import round-trip
    print("\n--- Test export/import aptitudEstadistica ---")
    exported = pg.evaluate('() => window.recolectar()')
    print(f"Exportado aptitudEstadistica: {exported['identidad'].get('aptitudEstadistica', 'FALTA')}")
    
    # Limpiar y reimportar
    pg.evaluate('() => { document.querySelectorAll("input, textarea, select").forEach(el => { if(el.type==="checkbox") el.checked=false; else if(el.tagName==="SELECT") el.selectedIndex=0; else el.value=""; }); }')
    pg.wait_for_timeout(200)
    
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(exported)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    imported = pg.evaluate('''() => ({
        selectVal: document.getElementById('apt-stat').value,
        mMod: document.getElementById('m-mod').textContent,
        mDc: document.getElementById('m-dc').textContent,
        mAtk: document.getElementById('m-atk').textContent
    })''')
    print(f"Importado: select={imported['selectVal']}, MOD={imported['mMod']}, DC={imported['mDc']}, ATK={imported['mAtk']}")
    print(f"  {'✅ Round-trip OK' if imported['selectVal']==exported['identidad']['aptitudEstadistica'] and imported['mMod']==vals_sab['mMod'] else '❌ Round-trip FALLÓ'}")
    
    # 3. Test export/import round-trip
    print("\n--- Test export/import aptitudEstadistica ---")
    exported = pg.evaluate('() => window.recolectar()')
    print(f"Exportado aptitudEstadistica: {exported['identidad'].get('aptitudEstadistica', 'FALTA')}")
    
    # Limpiar y reimportar
    pg.evaluate('() => { document.querySelectorAll("input, textarea, select").forEach(el => { if(el.type==="checkbox") el.checked=false; else if(el.tagName==="SELECT") el.selectedIndex=0; else el.value=""; }); }')
    pg.wait_for_timeout(200)
    
    pg.evaluate(f'''
        () => {{
            if (window.aplicar) window.aplicar({json.dumps(exported)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    imported = pg.evaluate('''() => ({
        selectVal: document.getElementById('apt-stat').value,
        mMod: document.getElementById('m-mod').textContent,
        mDc: document.getElementById('m-dc').textContent,
        mAtk: document.getElementById('m-atk').textContent
    })''')
    print(f"Importado: select={imported['selectVal']}, MOD={imported['mMod']}, DC={imported['mDc']}, ATK={imported['mAtk']}")
    roundtrip_ok = imported['selectVal']==exported['identidad']['aptitudEstadistica'] and imported['mMod']==vals_sab['mMod']
    print(f"  {'✅ Round-trip OK' if roundtrip_ok else '❌ Round-trip FALLÓ'}")
    
    browser.close()
    
    # Validaciones finales
    ok = True
    if select_info['value'] != 'INT':
        print("❌ Valor por defecto no es INT")
        ok = False
    if len(select_info['options']) != 6:
        print("❌ No hay 6 opciones")
        ok = False
    if not ('E' in select_info['classList']):
        print("❌ Select no tiene clase E")
        ok = False
    if not int_ok:
        print("❌ Cálculo INT incorrecto")
        ok = False
    if not car_ok:
        print("❌ Cálculo CAR incorrecto")
        ok = False
    if not sab_ok:
        print("❌ Cálculo SAB incorrecto")
        ok = False
    if exported['identidad'].get('aptitudEstadistica') != 'SAB':
        print("❌ Export no incluye aptitudEstadistica correcta")
        ok = False
    if imported['selectVal'] != exported['identidad']['aptitudEstadistica']:
        print("❌ Import no restaura select")
        ok = False
    if not roundtrip_ok:
        print("❌ Round-trip falló")
        ok = False
    
    if ok:
        print("\n✅ APTITUD MÁGICA SELECTOR FUNCIONA PERFECTAMENTE")
        exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        exit(1)