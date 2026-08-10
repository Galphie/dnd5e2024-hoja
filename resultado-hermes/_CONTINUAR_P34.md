# PÁGINAS 3-4 (BITÁCORA · COMPAÑEROS) — estado 2026-08-05

Archivo: ficha_dnd_hermes.html
Estado global: P1 APROBADA · P2 ESTRUCTURA ALINEADA CON REFERENCIA · P3 Y P4 RENDERIZAN SIN ERRORES.

## QUÉ SE HA HECHO ESTA SESIÓN (P3 y P4 auditadas)
Comparadas contra la referencia de Claude (dnd_sheet_v19_editable.html):
- P3 BITÁCORA: 2 cards de sesión de 740px (mías 222 alto vs REF 225 — casi idéntico).
  Título "BITÁCORA DE SESIONES", sub "CRÓNICAS DE NAKE NICKY · HECHICERO", toolbar
  "+ Añadir sesión", lista #bitaList (generada por JS). Sin errores JS.
- P4 COMPAÑEROS: 2 cards mías (REF tiene 1; diferencia de CONTENIDO, no de layout).
  Título "COMPAÑEROS", sub "ANIMALES · CONSTRUCTOS · INVOCACIONES · FAMILIARES",
  toolbar "+ Añadir compañero", lista #compList. Sin errores JS.
- Diferencia estructural con REF: la referencia HORNEA los datos en el HTML (data-baked),
  la mía los genera por JS con build*. Son equivalentes en resultado.
- Capturas guardadas: _shots/my_p3.png y _shots/my_p4.png (escala 2).

## PENDIENTE — REVISIÓN VISUAL HUMANA (la más importante, falta TODO esto)
La validación geométrica/estructural está hecha, pero NINGUNA página ha pasado aún la
REVISIÓN VISUAL del usuario (tamaños de fuente, grosores de borde, estética general,
colores, proporciones percibidas). Eso es lo que decide si está "lo más parecido posible".

Plan recomendado para próxima sesión:
1. El usuario ABRE el html y revisa P2, P3 y P4 visualmente (o reviso capturas _shots/*.png).
2. Ajustar los detalles que marque (fuentes, bordes, espaciados, alturas).
3. Ajustes finos pendientes detectados:
   - Tabla conjuros: alto fila 23px vs REF 32px (voluntario, por los 36 conjuros). Si se reducen
     SPELLS[] se puede airear.
   - Algunos datos de SPELLS[] difieren de REF (Rayo de Fuego "1d10 fuego" mio vs "2d10 fuego" REF;
     revisar lista de conjuros completa).
   - Banner logo D&D igualado a 325px de ancho (como REF).
4. Pasar a revisar detalles estéticos de todas las páginas según feedback del usuario.

## Scrips conservados
- _shots.py: capturas reutilizable.
- Las capturas estan en _shots/: my_p3.png, my_p4.png (nuevas); (my_p2/ref_p2 las limpie al cerrar P2).

## Invariantes técnicas (mantener)
- line-height ENTERO en textareas con gradiente de fondo (14px), no fraccionario.
- Ocultar flechas de inputs numericos (::webkit spin button + -moz-appearance).
- Línea subrayada de números = <div class="ln"> real.
- Scripts efimeros _*.py y borrarlos al terminar.
- Verificaciones geometricas en navegador (Playwright) + capturas deviceScaleFactor:2.