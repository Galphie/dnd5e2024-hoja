#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build de la ficha D&D 2024 en una sola pasada, reproducible.

Flujo:
  1. copia el backup pristino (_ficha_backup_pool.html) sobre la ficha destino
  2. _build_pool.py  -> genera SPELL_POOL (385)    (.pool_tmp)
  3. _build_info.py  -> genera SPELL_INFO (383)    (.info_tmp)
  4. _assemble.py    -> ensambla + TODOS los parches (slice1000, fill,
                        botones flotantes, tooltips)  [idempotente]
  5. _verify_pool.py -> comprueba invariantes (tags, 385/383, sin restos)
  6. limpia los *_tmp

Uso:
  python build.py                  (destino por defecto: resultado-hermes/)
  python build.py --out RUTA       (destino alternativo, p. ej. tests/_out/)
  python build.py --no-verify      (solo pasos 1-4,6)
"""
import argparse, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "referencias")
BACKUP = os.path.join(REF, "_ficha_backup_pool.html")
DEFAULT_OUT = os.path.join(HERE, "resultado-hermes", "ficha_dnd_hermes.html")
EMPTY_OUT = os.path.join(HERE, "resultado-hermes", "ficha_dnd_hermes_empty.html")
INDEX_OUT = os.path.join(HERE, "resultado-hermes", "index.html")

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT, help="ruta HTML de salida")
    ap.add_argument("--no-verify", action="store_true", help="omitir _verify_pool")
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    if not os.path.exists(BACKUP):
        sys.exit("ERROR: no existe el backup: " + BACKUP)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    shutil.copyfile(BACKUP, out)
    print("[1/6] backup ->", out)

    env = dict(os.environ, FICHA_HTML=out)
    steps = [
        ("_build_pool.py", "[2/6] SPELL_POOL"),
        ("_build_info.py", "[3/6] SPELL_INFO"),
        ("_assemble.py", "[4/6] ensamblado + parches"),
    ]
    for script, label in steps:
        print(label, script)
        r = subprocess.run([sys.executable, os.path.join(REF, script)],
                           env=env, cwd=HERE)
        if r.returncode != 0:
            sys.exit(f"ERROR en {script} (exit {r.returncode})")

    if not args.no_verify:
        print("[5/6] verificación", "_verify_pool.py")
        r = subprocess.run([sys.executable, os.path.join(REF, "_verify_pool.py")],
                           env=env, cwd=HERE)
        if r.returncode != 0:
            sys.exit("ERROR en _verify_pool.py (exit %d)" % r.returncode)

    for tmp in (out + ".pool_tmp", out + ".info_tmp"):
        if os.path.exists(tmp):
            os.remove(tmp)
    print("[6/6] limpio. OK:", out)
    
    # Copiar la hoja vacía a index.html para Netlify (entry point limpio)
    shutil.copyfile(EMPTY_OUT, INDEX_OUT)
    print("[7/7] copiado index.html vacío ->", INDEX_OUT)

if __name__ == "__main__":
    main()