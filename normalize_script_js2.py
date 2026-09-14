#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normaliza solo caracteres no-ASCII DENTRO de string literals en <script> tags.
Preserva comentarios JS (usados como anclas) y contenido HTML fuera de scripts."""
import re

with open('referencias/_ficha_backup_pool.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replacements for non-ASCII -> ASCII
replacements = {
    'ó': 'o', 'á': 'a', 'é': 'e', 'í': 'i', 'ú': 'u',
    'ñ': 'n', 'Ó': 'O', 'Á': 'A', 'É': 'E', 'Í': 'I', 'Ú': 'U', 'Ñ': 'N',
    'ü': 'u', 'Ü': 'U',
    '—': '--', '–': '-', '…': '...', '·': '.',
    '¿': '?', '¡': '!',
    '×': 'x', '÷': '/',
    'ⓘ': '(i)', '✕': 'x',
    '▲': '^', '▼': 'v',
    '“': '"', '”': '"', '‘': "'", '’': "'",
    'º': 'o', 'ª': 'a',
    '©': '(c)', '®': '(r)', '™': '(tm)',
    '§': 'S', '¶': 'P',
    '±': '+/-',
    '¼': '1/4', '½': '1/2', '¾': '3/4',
}

# Protect these anchor comments from normalization
protected = [
    '/* ---------- Bitácora ---------- */',
    '/* ---------- Tooltips de cabecera de tablas',
    '/* ---------- Compañeros ---------- */',
]

# Find all <script>...</script> blocks
script_pattern = re.compile(r'(<script[^>]*>)(.*?)(</script>)', re.DOTALL)

def normalize_js_content(content):
    """Normalize non-ASCII in JS string literals and template literals only.
    Preserve comments (// and /* */)."""
    # First, protect comments by replacing them with placeholders
    protected_placeholders = {}
    
    # Protect /* ... */ comments
    def protect_block_comment(match):
        placeholder = f'__PROTECTED_COMMENT_{len(protected_placeholders)}__'
        protected_placeholders[placeholder] = match.group(0)
        return placeholder
    
    content = re.sub(r'/\*[\s\S]*?\*/', protect_block_comment, content)
    
    # Protect // comments
    def protect_line_comment(match):
        placeholder = f'__PROTECTED_LINE_COMMENT_{len(protected_placeholders)}__'
        protected_placeholders[placeholder] = match.group(0)
        return placeholder
    
    content = re.sub(r'//.*', protect_line_comment, content)
    
    # Now normalize string literals (single, double, backtick)
    def normalize_string(match):
        quote = match.group(1)
        string_content = match.group(2)
        for k, v in replacements.items():
            string_content = string_content.replace(k, v)
        return quote + string_content + quote
    
    # Double-quoted strings (handle escaped quotes)
    content = re.sub(r'"((?:[^"\\]|\\.)*)"', lambda m: '"' + m.group(1).translate(str.maketrans(replacements)) + '"', content)
    # Single-quoted strings
    content = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda m: "'" + m.group(1).translate(str.maketrans(replacements)) + "'", content)
    # Template literals (backticks)
    content = re.sub(r'`((?:[^`\\]|\\.)*)`', lambda m: '`' + m.group(1).translate(str.maketrans(replacements)) + '`', content)
    
    # Restore comments
    for placeholder, original in protected_placeholders.items():
        content = content.replace(placeholder, original)
    
    return content

def replace_script(match):
    before = match.group(1)  # <script...>
    content = match.group(2)  # JS content
    after = match.group(3)    # </script>
    normalized = normalize_js_content(content)
    return before + normalized + after

html = script_pattern.sub(replace_script, html)

with open('referencias/_ficha_backup_pool.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Normalized non-ASCII to ASCII only inside JS string literals (preserving comments)')