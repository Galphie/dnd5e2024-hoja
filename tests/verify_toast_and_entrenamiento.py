#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación del toast modal y importación de entrenamiento"""
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
    
    # 1. Verificar que los elementos del toast existen
    toast_exists = pg.evaluate('''
        () => {
            return {
                toastOv: !!document.getElementById('toastOv'),
                toastBox: !!document.getElementById('toastBox'),
                toastMsg: !!document.getElementById('toastMsg'),
                toastBtns: !!document.getElementById('toastBtns'),
            };
        }
    ''')
    print("=== TOAST ELEMENTS ===")
    for k, v in toast_exists.items():
        print(f"  {k}: {'✅' if v else '❌'}")
    
    # 2. Cargar Valerius y verificar entrenamiento se exporta
    with open(os.path.join(HERE, '..', 'personajes', 'valerius_cogsworth.json'), 'r', encoding='utf-8') as f:
        valerius = json.load(f)
    
    # Añadir datos de entrenamiento al JSON de prueba
    valerius['entrenamiento'] = {
        "armaduras": {"Ligeras": True, "Medianas": True, "Pesadas": False, "Escudos": True},
        "armas": "Armas simples, Armas marciales (espada larga)",
        "herramientas": "Herramientas de ladrón, Herramientas de herrero, Utensilios de alquimista"
    }
    
    pg.evaluate(f'''
        () => {{
            window.recalc = () => {{}};
            if (window.aplicar) window.aplicar({json.dumps(valerius)});
        }}
    ''')
    pg.wait_for_timeout(500)
    
    # Verificar que se importó el entrenamiento
    entren_importado = pg.evaluate('''
        () => {
            const armaduras = {};
            document.querySelectorAll('.ep-c').forEach(lb => {
                const cb = lb.querySelector('input');
                if (cb) armaduras[lb.textContent.trim()] = cb.checked;
            });
            const armas = document.querySelector('.ep-a')?.value || '';
            const herramientas = document.querySelector('.ep-h')?.value || '';
            return {armaduras, armas, herramientas};
        }
    ''')
    print("\n=== ENTRENAMIENTO IMPORTADO ===")
    print(f"  Armaduras: {entren_importado['armaduras']}")
    print(f"  Armas: {entren_importado['armas'][:60]}...")
    print(f"  Herramientas: {entren_importado['herramientas'][:60]}...")
    
    # 3. Exportar y verificar que el entrenamiento está en el JSON
    exportado = pg.evaluate('() => window.recolectar()')
    print("\n=== ENTRENAMIENTO EXPORTADO ===")
    print(f"  Tiene entrenamiento: {'entrenamiento' in exportado}")
    if 'entrenamiento' in exportado:
        print(f"  Armaduras: {exportado['entrenamiento']['armaduras']}")
        print(f"  Armas: {exportado['entrenamiento']['armas'][:60]}...")
        print(f"  Herramientas: {exportado['entrenamiento']['herramientas'][:60]}...")
    
    # 4. Test toast confirm - click vaciar hoja
    print("\n=== TOAST CONFIRM TEST ===")
    pg.on('dialog', lambda dialog: dialog.dismiss())  # dismiss any native dialogs
    
    # Click btn-clear should show toast
    pg.click('#btn-clear')
    pg.wait_for_timeout(300)
    
    toast_visible = pg.evaluate('() => document.getElementById("toastOv").classList.contains("open")')
    toast_msg = pg.evaluate('() => document.getElementById("toastMsg").textContent')
    print(f"  Toast visible: {'✅' if toast_visible else '❌'}")
    print(f"  Mensaje: {toast_msg[:80]}")
    
    # Click cancelar
    pg.click('.toast-btn.cancel')
    pg.wait_for_timeout(200)
    toast_visible_after = pg.evaluate('() => document.getElementById("toastOv").classList.contains("open")')
    print(f"  Toast cerrado tras cancelar: {'✅' if not toast_visible_after else '❌'}")
    
    # 5. Test toast info - click btn-exp (just to trigger, then cancel file dialog)
    # Actually we can't easily test file dialog, so just verify functions exist
    functions_exist = pg.evaluate('''
        () => ({
            showToast: typeof showToast === 'function',
            showConfirm: typeof showConfirm === 'function',
        })
    ''')
    print(f"\n=== TOAST FUNCTIONS ===")
    for k, v in functions_exist.items():
        print(f"  {k}: {'✅' if v else '❌'}")
    
    browser.close()
    
    # Validaciones finales
    ok = True
    if not all(toast_exists.values()):
        print("\n❌ Faltan elementos del toast")
        ok = False
    if not entren_importado['armaduras'].get('Ligeras', False):
        print("\n❌ Entrenamiento armaduras no importado")
        ok = False
    if 'entrenamiento' not in exportado:
        print("\n❌ Entrenamiento no exportado")
        ok = False
    if not toast_visible:
        print("\n❌ Toast no se muestra")
        ok = False
    if toast_visible_after:
        print("\n❌ Toast no se cierra")
        ok = False
    
    if ok:
        print("\n✅ TODO FUNCIONA - Toast + Entrenamiento import/export")
        exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        exit(1)