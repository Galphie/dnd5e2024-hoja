# PÁGINA 2 (CONJUROS) — CONTINUACIÓN

Archivo: ficha_dnd_hermes.html
Estado: Página 1 APROBADA (sesiones previas).
Página 2: ESTRUCTURA ALINEADA CON LA REFERENCIA (verificado sin solapes ni errores JS).
Página 3 (BITÁCORA) y Página 4 (hojas extra): SIN revisar aún.

## CORREGIDO en la Página 2
### Sesión anterior
1. CSS duplicado en tabla de conjuros (`.sp-hd`/`.srow` x2 + `.srow2sp` corrupto) -> eliminado. Ya 1 sola vez.
2. Líneas verticales desalineadas -> `.sv1{left:42px} .sv2{left:192px}`. Coinciden con grid [43,193,261,319,391].
3. Logo D&D (`.p2b`): position:static -> absolute. Antes ocupaba toda la página.
4. Tabla Ataques (P1): filas 26->21px, fuente 9->8px, 7->8 filas, columnas 38/18/22/22.

### Esta sesión
5. Header de la tabla de conjuros: texto "C/R/M" -> "Concentración, Ritual & Material requerido"
   y padding -> `padding:3px 4px 4px;line-height:1.05` => alto 32px (igual que REF).
6. Título del bloque: "TRUCOS & CONJUROS" -> "TRUCOS & CONJUROS PREPARADOS" (igual que REF).
7. Banner logo D&D (`.p2b`): `right:38px` -> `width:325px` (igual que REF 325px, antes 563px).

## Estado P2 actual (verificado esta sesión)
- 9 bloques, TODOS sin solapes entre sí:
  apt=(30,43,175,177) slots=(215,92,325,128) spell=(30,230,510,905) p2b=(215,8,325,78)
  col derecha x=572: apar=(¬,43,214,150) hist=(¬,205,214,340) idiom=(¬,557,214,55) equip2=(¬,624,214,358) coin=(¬,994,214,144)
- Tabla conjuros: header 32px, 36 filas (1/conjuro en SPELLS[]) a min-height 23px, hueco inferior ~17px.
  Grid columnas: 42px 150px 68px 58px 72px 1fr. Checkboxes C/R/M 7px cada uno.
- Fila ejemplo (Rayo de Fuego): inputs x31/73/223/291, checkboxes x359/376/393 => IDENTICO a REF.
- apt: 3 filas (MODIFICADOR +4, CD 14, BON +6), valores x43 40px, labels x93.
- equip2: textarea .bx hasta ¬y899, atun (SINTONIZACIÓN) en ¬y906-976 con 3 filas.
- coin: 5 celdas (PC/PP/PE/PO/PPT) de 35px c/u, valores /12//1475/8. Posiciones casi identicas a REF.
- botón #btn-sort (x440-529) NO invade el label del bloque (x198-371).
- Sin errores JS (captura Y mediciones validadas).

## DIFERENCIA voluntaria con la REFERENCIA
- Alto de fila de la tabla: 23px (mio) vs 32px (REF). Motivo: tengo 36 conjuros en SPELLS[] vs 25 filas
  que muestra REF (4 trucos + varios niveles + huecos). No se puede subir a 32px sin desbordar (36x32=1152>877).
  Si el usuario reduce SPELLS[] se podria airear mas.

## PENDIENTE para próxima sesión
1. REVISIÓN VISUAL HUMANA de la P2: abrir el html y ¡ver! La estructura geometrica esta validada pero
   falta la confirmacion visual del usuario (tamaños de fuente, grosor bordes, estetica).
   Capturas generadas con _shots.py.
2. REVISAR PAGINA 3 (BITÁCORA, pg3, page-auto) y PAGINA 4 (pg4) - aún sin auditar.
3. Comparar el banner/logo de la referencia (REF usa .p2-banner con logo, revisar si difiere la fuente).
4. Si se desea, comparar los valores de datos de SPELLS[] con los de la referencia (algunos difieren,
   p.ej. Rayo de Fuego '1d10 fuego' mio vs '2d10 fuego' REF; Orden imperiosa no esta en mi lista, etc).

## Comandos utiles
- Ver P2: abrir file:///C:/Users/algpa/Desktop/hojapersonaje/resultado-hermes/ficha_dnd_hermes.html
  (editar pg2 a class="page show" o quitar .show de pg1, o usar nav si existe).
- Scripts: _shots.py hace capturas. _sp2.py mide tabla de conjuros.
- Trabajar con scripts _*.py efímeros y borrarlos al terminar (preferencia del usuario).

## Invariantes a respetar (de sesiones previas)
- Línea subrayada de números = <div class="ln"> real, no border-bottom del input.
- Ocultar flechas de inputs numéricos con ::-webkit-inner/outer-spin-button + -moz-appearance:textfield.
- Líneas de renglón de textareas con line-height ENTERO (px) para cuadrar con el gradiente de fondo
  (lección: 13.6px fraccionario se redondea por fila -> irregular; 14px entero = perfecto).
- En esta ficha las cajas de texto de la col derecha estan bien con su gradiente actual (.grbg).