# CONTINUAR — Conjuros oficiales manual D&D 2024 (modal + descripcionLarga)

Fecha: 2026-08-06. Estado: EN CURSO (tarea pausada por el usuario, se retoma en la siguiente sesión).

## Objetivo (opción 2 aprobada)
- Botón ⓘ junto a cada conjuro → modal con la **descripción completa oficial** del Manual del Jugador 2024 (español, Devir).
- En el modal: referencia a la **página exacta del manual**.
- Añadir a cada entrada de SPELLS el campo `descripcionLarga` (y página).
- El tooltip corto actual (hover) se MANTIENE como está.
- El usuario pidió "aprovecha, y añade cualquiera que falte" → ampliar la base con conjuros que falten (PENDIENTE decidir alcance: ¿solo hechicero?).

## Archivos generados (en C:\Users\algpa\Desktop\hojapersonaje\referencias\)
- `Manual del Jugador 2024.pdf` — el manual completo (388 páginas PDF; el usuario indicó págs. 241-346 = TODOS los conjuros).
- `spells_txt/all_241_346.txt` — texto extraído de páginas 241-346 (106 páginas, 420 KB). Banners: `===== PAGE N (pdf idx M) =====`.
- `spells_txt/spells_parsed.json` — 314 conjuros parseados (parser v4, `_parse5.py`). Campos: nombre(MAYÚS oficial), escuela, nivel ('truco'|'nivel N'), clases, pagina (=pdf_n, 1-based 241-346, la que indicó el usuario), tiempo, alcance, componentes, duracion, descripcion.
- `spells_txt/pool.json` — 314 entradas lista para inyectar: {nombre, norm, niv, tm, rg, M, dl, pg, du, comp}.
- Scripts generadores: CONSERVADO `_parse5.py` (v4→spells_parsed.json). `_pool.py` se borró al limpiar (su código está en el historial de la sesión; es trivial: lee spells_parsed.json y escribe pool.json con {nombre, norm, niv, tm, rg, M, dl, pg, du, comp}). `pool.json` YA está generado (314 entradas).

## Paginación (RESUELTO)
- Página impresa = pdf_idx(0-based) − 1 para idx≥242 (verificado en 9 páginas: idx242→"241", 245→"244", 260→"259", 340→"339").
- PERO el usuario dijo "páginas de la 241 a la 346 del pdf" refiriéndose al visor (1-based). El parser guarda `pagina = pdf_n` (1-based, 241-346) → usar ESO en el modal ("Manual del Jugador 2024, pág. 241"). Es la referencia que el usuario puede verificar en su visor.

## Estado del parseo (RESUELTO en gran parte)
- 314 conjuros, sin duplicados. Distribución: niv1:55, niv2:53, niv3:45, niv4:37, niv5:42, niv6:32, niv7:18, niv8:18, niv9:14, trucos(niv0):FALTAN EN EL COUNTER del pool viejo (regenerar).
- ~22 descripciones "sospechosas" (empiezan en minúscula = continuación de componente material partido, ej: "que se consume como parte del conjuro)"). Corregir a mano en pool.json o con fix post-proceso: si la descripción empieza con minúscula y el componentes termina en "(" sin cerrar, mover el texto al componente.
- 3 campos faltantes (CÍRCULO DE TELETRANSPORTACIÓN tiempo=None, MASTÍN FIEL duracion=None, VIAJAR MEDIANTE PLANTAS duracion=None).

## CRUCE con los 36 conjuros actuales de la ficha (PENDIENTE — clave)
Solo 11/36 matchean por nombre exacto: Orbe Cromático, Proyectil Mágico, Armadura de Mago, Retirada Expeditiva, Paso Brumoso, Sugestión, Bola de Fuego, Volar, Contrahechizo, Relámpago, Muro de Fuego.
Los otros 25 usan nombres NO oficiales de la edición 2024 (nombres de la hoja de Claude/2014). Mapeo conceptual detectado (verificar en pool.json):
- Rayo de Fuego → ? (Fire Bolt 2024, buscar "DESCARGA DE FUEGO")
- Mano de Mago → MANO DE MAGO (está en el texto, el pool viejo no lo tenía; regenerar pool con _parse5)
- Prestidigitación → PRESTIDIGITACIÓN
- Luz → Luz (truco, nombre con minúscula inicial en el texto — el parser exige isupper, verificar)
- Ráfaga de Hechicero → ? (Sorcerous Burst → "ESTALLIDO MÁGICO"?)
- Toque Gélido → TOQUE HELADO (confirmado en lista de trucos)
- Descarga de Cuchillos → ? (no está en lista de trucos; buscar)
- Chasquido Atronador → TRONAR? (buscar; thunderclap)
- Luces Danzantes → LUCES DANZANTES (truco, en texto)
- Mensaje → MENSAJE (truco, en texto)
- Ilusión Menor → ILUSIÓN MENOR (truco, en texto)
- Rociada Venenosa → ? (poison spray; no apareció en búsqueda "veneno")
- Rayo de Escarcha → RAYO DE ESCARCHA (truco, en texto)
- Salvajismo → ? (primal savagery)
- Burla Cruel → BURLA DAÑINA (truco, confirmado)
- Descarga Eléctrica → ? (shocking grasp; buscar "AGARRE ELECTRIZANTE")
- Estabilizar → ? (spare the dying; buscar "PIEDAD CON LOS MORIBUNDOS")
- Escudo → ESCUDO (nivel 1; el pool busca "escudo" y no lo dio → verificar: existe "ESCUDO" a secas)
- Llamarada → MANOS ARDIENTES (burning hands, confirmado en texto)
- Comprender Idiomas → ENTENDER IDIOMAS (confirmado)
- Detectar Magia → ? (detect magic; no apareció — buscar "DETECTAR MAGIA" directo)
- Rayo Coruscante → SAETA GUÍA (guiding bolt, confirmado en texto)
- Invisibilidad → ? (invisibility; no apareció — buscar "INVISIBILIDAD" directo)
- Añicos → HACER AÑICOS (confirmado)
- Disipar Magia → DISIPAR MAGIA (está en texto línea 3020; verificar en pool)

NOTA: el pool.json actual está regenerado con _parse5 (314 entradas) PERO el Counter no mostró niv 0 (trucos). VERIFICAR que _pool.py lee spells_parsed.json (v4) y que los trucos entran con niv=0. Si no, revisar la condición `sp["nivel"]=='truco'`.

## Decisiones pendientes para la siguiente sesión (preguntar al usuario)
1. **Alcance de "añadir los que falten"**: ¿solo conjuros de hechicero (lista de clases del manual), o todos los 314? La ficha tiene grid de 36 filas fijas; añadir filas rompe la geometría calibrada de la página 2. Propuesta: ampliar el POOL de autocompletado (el acbox ya sugiere) y que el modal funcione para cualquier conjuro, SIN añadir filas visibles (o con botón "añadir fila" opcional).
2. **Implementación UI**: botón ⓘ en cada fila `.srow` (junto a `.nm`), modal nuevo (CSS + div oculto), datos por nombre → lookup en SPELLDB. Ver líneas actuales: spellRow() ~745-753, autocompletado/tooltip ~788-861, SPELLS 707-744.
3. Mantener compat: `aplicar()` de import no necesita cambios (los campos nuevos van en SPELLS/SPELLDB, no en el JSON del personaje).

## Verificación final pendiente
- Playwright: modal abre con descripción completa + "Manual del Jugador 2024, pág. N" + cierra correctamente.
- Geometría página 2 intacta (36 filas).
- Sin errores JS.
