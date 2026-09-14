#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Limpieza del pool de conjuros (D&D 2024, pool.json scrapeado).
Provee fix_entry()/title_es() a _build_pool.py y _build_info.py.
- Title-case en espanol (no capitaliza conectivas).
- Overrides manuales para tm/rg de los ~18 registros scrapeados mal.
- Saneador de descripciones (colas de pagina, banners, apendice pegado,
  numeros de pagina incrustados, OCR de dados 1410->1d10).
- Generador de nota de dano para la columna notas de la ficha.
"""
import re, unicodedata

CONECT = {'de', 'la', 'las', 'los', 'el', 'y', 'o', 'u', 'a', 'e', 'con',
          'por', 'para', 'su', 'sus', 'tu', 'que', 'uno', 'un', 'and', 'of',
          'en', 'del', 'al', 'desde', 'hacia', 'sobre', 'bajo', 'entre',
          'tras', 'sin', 'mas', 'menos'}

DANOS_NORM = {'acido', 'contundente', 'cortante', 'frio', 'fuego', 'fuerza',
              'necrot', 'necrotico', 'perforante', 'psiquico', 'radiante',
              'relampago', 'trueno', 'veneno'}
TIPO_DISPLAY = {'acido': 'ácido', 'frio': 'frío', 'necrot': 'necrótico',
                'necrotico': 'necrótico', 'psiquico': 'psíquico',
                'relampago': 'relámpago'}
VERBOS_APERTURA = {'elige', 'creas', 'lanzas', 'tocas', 'preparas', 'bendices',
                   'intentas', 'invocas', 'conjuras', 'haces', 'ciegas',
                   'exhalas', 'disparas', 'desatas', 'conviertes', 'concedes',
                   'impones', 'perturbas', 'atraes', 'encantas', 'manifiestas',
                   'obligas', 'escribes', 'sellas', 'teletransportas',
                   'transformas', 'canalizas', 'recibes', 'comprendes',
                   'obtienes', 'crea', 'elige', 'toca', 'invoca', 'lanza',
                   'bendice', 'conjura', 'haz', 'toma', 'mira', 'apuntas',
                   'envuelves', 'envuelve', 'proteges', 'protege', 'anulas',
                   'reprimes', 'cancelas', 'amplificas', 'liberas', 'dominas',
                   'conviertes', 'cambias', 'adquieres', 'aprendes',
                   'comprendes', 'sabes', 'descubres', 'detectas', 'percibes'}

# --- Overrides manuales: tm/rg rotos por el scrapeo (clave: NOMBRE EN MAYUS) ---
TIMEFIX = {
    'CASTIGO DE CEÑO FRUNCIDO': 'Acción adicional',
    'CASTIGO DE DESTELLO': 'Acción adicional',
    'CASTIGO DE ESTIGIA': 'Acción adicional',
    'CASTIGO DE FUEGO HERALDO': 'Acción adicional',
    'CASTIGO DE GARRAS DE SHADAR': 'Acción adicional',
    'CASTIGO DE GOLPE BRUTAL': 'Acción adicional',
    'CASTIGO DE LA MÁQUINA': 'Acción adicional',
    'CASTIGO DE ONDA TUMULTUOSA': 'Acción adicional',
    'CASTIGO DE PUNTA DE LUZ': 'Acción adicional',
    'CASTIGO DE TORMENTA CERCADORA': 'Acción adicional',
    'CASTIGO DE UMBRAL': 'Acción adicional',
    'CASTIGO DEL JURAMENTO DE VENGANZA': 'Acción adicional',
    'CASTIGO ESPECTRAL': 'Acción adicional',
    'CASTIGO TRONANTE': 'Acción adicional',
    'BOLA DE FUEGO': 'Acción',
    'BOLA DE FUEGO DE EXPLOSIÓN RETARDADA': 'Acción',
    'OLA DESTRUCTORA': 'Acción',
    'OLA ATRONADORA': 'Acción',
    'CAÍDA DE PLUMA': 'Reacción',
    'CONTRAHECHIZO': 'Reacción',
    'ESCUDO': 'Reacción',
    'REPRENSIÓN INFERNAL': 'Reacción',
}
RANGEFIX = {
    'CASTIGO TRONANTE': 'Lanzador',
}


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower())
                   if unicodedata.category(c) != "Mn")


def title_es(s):
    """Title-case espanol: primera palabra + no-conectivas en mayuscula."""
    s = (s or "").replace("\u201c", "").replace("\u201d", "").strip()
    if not s:
        return s
    words = s.lower().split()
    out = []
    for i, w in enumerate(words):
        if i == 0 or w not in CONECT:
            out.append(w.capitalize())
        else:
            out.append(w)
    return " ".join(out)


def _strip_trailing_junk(dl):
    """Quita colas de pagina/banners: '339 2 Xx', 'CONJUROS 309', 'Pg', etc."""
    prev = None
    while prev != dl:
        prev = dl
        dl = re.sub(r'\s+(?:\d{1,3}\s+)?Xx\s*$', '', dl)
        dl = re.sub(r'\s+\d{1,3}\s+e\s*$', '', dl)
        dl = re.sub(r'\s+e\s*$', '', dl)
        dl = re.sub(r'\s+\d{1,3}\s*$', '', dl)
        dl = re.sub(r'\s+CONJUROS\s+\d{1,3}\s*$', '', dl)
        dl = re.sub(r'\s+Pg\.?\s*$', '', dl, flags=re.I)
        dl = dl.rstrip()
    return dl


def _cut_glued(dl):
    """Corta banners de ilustracion y apendices pegados al final."""
    i = dl.find('CON SU CONJURO,')
    if i >= 0:
        dl = dl[:i].rstrip()
    m = re.search(r'\sli\s+[A-ZÁÉÍÓÚÑ]{3,}', dl)
    if m:
        dl = dl[:m.start()].rstrip()
    i = dl.find('AFECTADO POR EL CONJURO')
    if i >= 0:
        dl = dl[:i].rstrip()
    i = dl.find('APÉNDICE A EL MULTIVERSO')
    if i >= 0:
        dl = dl[:i].rstrip()
    # '343 / APÉNDICE...' o pagina suelta antes del apendice
    dl = re.sub(r'\s+\d{1,3}\s*/\s*$', '', dl)
    return dl


def _strip_mid_pages(dl):
    """Numeros de pagina incrustados: '| 241 |', ' 243 S', ' 337 a'."""
    dl = re.sub(r'\s*\|\s*\d{1,3}\s*\|\s*', ' ', dl)
    # numero de 3 cifras (pagina) entre espacios seguido de palabra en minus
    dl = re.sub(r'\s(\d{3})\s(?=[a-záéíóúñ])', ' ', dl)
    return dl


def _fix_ocr(dl):
    """Corrupciones OCR de dados: 1410->1d10, 1412->1d12, íd10->1d10, 'Tira 148'.
    También: 'velocidad de O' -> 'velocidad de 0', 'se reducen a O' -> 'se reducen a 0'.
    También: 'cas AS' -> '' (basura de ilustración OCR).
    También: 'puntos de golpe se reducen a O' -> 'puntos de golpe se reducen a 0'.
    También: 'O m de altura' -> '0 m de altura'.
    También: 'llegue a O m' -> 'llegue a 0 m'."""
    dl = dl.replace('1410', '1d10').replace('1412', '1d12')
    dl = dl.replace('íd10', '1d10').replace('í d10', '1d10')
    dl = dl.replace('Tira 148', 'Tira 1d8')
    dl = dl.replace(' 148 para', ' 1d8 para')
    # OCR: O (letra) -> 0 (cero) en contextos numéricos
    dl = dl.replace('velocidad de O', 'velocidad de 0')
    dl = dl.replace('se reducen a O', 'se reducen a 0')
    dl = dl.replace('puntos de golpe se reducen a O', 'puntos de golpe se reducen a 0')
    dl = dl.replace('O m de altura', '0 m de altura')
    dl = dl.replace('llegue a O m', 'llegue a 0 m')
    dl = dl.replace('llegue a O ', 'llegue a 0 ')
    # Basura de ilustración OCR
    dl = dl.replace('cas AS', '')
    return dl


def _strip_leading_du(dl):
    """El campo du se colo al inicio de dl: '1 minuto Este conjuro...'."""
    return re.sub(r'^\s*\d+\s+(?:minuto|minutos|hora|horas|día|días)\.?\s+',
                  '', dl)


def clean_dl(dl):
    dl = (dl or '').strip()
    dl = _strip_leading_du(dl)
    dl = _fix_ocr(dl)
    dl = _strip_mid_pages(dl)
    dl = _cut_glued(dl)
    # pipes/corchetes sueltos del scrapeo: 'por | aptitud mágica. ] Con...'
    dl = dl.replace(' | ', ' ').replace(' ] ', ' ').replace('] ', ' ')
    dl = _strip_trailing_junk(dl)
    # Invocar Elemental: su bloque de stats termina '...superior al 3';
    # el 3 final se confunde con numero de pagina, asi que va DESPUES de la
    # limpieza de cola (y el 'r |' era ruido de tabla del scrapeo)
    dl = dl.replace('(solo aire). r | PG: 30 + 10 por cada nivel del conjuro superior al',
                    '(solo aire). PG: 30 + 10 por cada nivel del conjuro superior al 3')
    dl = dl.replace('  ', ' ').strip()
    return dl


def extract_nota(dl):
    """Nota breve para la columna notas (estilo de las notas manuales del
    usuario): datos de daño ('8d6 fuego'), curación ('2d8+mod PG'), o una
    etiqueta derivada de la descripción ('alarma contra los intrusos')."""
    if not dl:
        return ''
    # --- daño ---
    pat = re.compile(
        r'(\d+d\d+(?:\+\d+)?)\s+(?:de\s+)?daño(?:\s+de\s+)?\s*([a-záéíóúñ]+)?')
    seen, out = set(), []
    for dice, tipo in pat.findall(dl):
        t = norm(tipo) if tipo else ''
        if t in seen:
            continue
        seen.add(t)
        if t and any(t.startswith(d) for d in DANOS_NORM):
            dsp = TIPO_DISPLAY.get(t, norm(tipo))
            out.append(dice + ' ' + dsp)
        elif t and t.startswith('adicional') and not out:
            out.append(dice + ' adicional')
        elif not t and not out:
            out.append(dice)
        if len(out) >= 5:
            break
    if out:
        return ' + '.join(out)
    # --- curacion ---
    cura = re.search(
        r'(?:recupera|recuperas|recuperará|recuperarán|recuperan|restaura|'
        r'restauras|restaurar|restauran|ganas|gana|vuelve a tener|curas?)'
        r'\s+(?:una cantidad de puntos de golpe igual a\s+)?'
        r'(\d+d\d+(?:\+\d+)?)\s*(?:más tu modificador'
        r'|PG|puntos de golpe)?', dl)
    if cura:
        base = cura.group(1)
        mod = 'más tu modificador' in cura.group(0)
        return base + ('+mod PG' if mod else ' PG')
    # --- utilidad: etiqueta derivada ---
    frase = re.split(r'[.,;]', dl)[0].strip().lower()
    palabras = frase.split()
    if palabras and palabras[0] in VERBOS_APERTURA:
        palabras = palabras[1:]
    while palabras and palabras[0] in {'la', 'las', 'los', 'el', 'un',
                                       'una', 'unos', 'unas', 'a', 'al',
                                       'de', 'del', 'e', 'y', 'o', 'en'}:
        palabras = palabras[1:]
    if not palabras:
        return '—'
    etiqueta = ' '.join(palabras)
    if len(etiqueta) > 34:
        corte = etiqueta[:34].rsplit(' ', 1)[0]
        etiqueta = corte
    return etiqueta


def type_name(w):
    return norm(w).capitalize() if norm(w) else w


# notas manuales para casos donde el pool no permite derivar
NOTA_EXTRA = {
    'BRAZOS DE HADAR': '1d8 necrótico',          # pool.json no trae descripción
    'CÍRCULO MÁGICO': 'barrera contra criaturas',  # pool.json no trae descripción
    'BUENAS BAYAS': '10 bayas, curan 1 PG',      # desc del pool es de Incendiar
}


def fix_entry(e):
    e = dict(e)
    e['nombre'] = title_es(e.get('nombre'))
    e['dl'] = clean_dl(e.get('dl') or '')
    e['nota'] = extract_nota(e['dl'])
    up = (e.get('nombre') or '').upper().replace('“', '').replace('”', '')
    if not e['nota'] and up in NOTA_EXTRA:
        e['nota'] = NOTA_EXTRA[up]
    if up in NOTA_EXTRA and e.get('dl', '').startswith('Los objetos inflamables'):
        e['nota'] = NOTA_EXTRA[up]  # desc del pool cruzada con Incendiar
    if up in TIMEFIX:
        e['tm'] = TIMEFIX[up]
    if up in RANGEFIX:
        e['rg'] = RANGEFIX[up]
    return e