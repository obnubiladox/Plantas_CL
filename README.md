# Plantas_CL

Los **datos abiertos** de [Plantas_CL](https://play.google.com/store/apps/details?id=cl.obnubilado.plantascl),
una app para Android con el catálogo de las plantas vasculares de Chile: unas
**5.500 especies** para buscar, filtrar, conocer y fotografiar, en el teléfono
y **sin conexión**. Sin cuentas, sin anuncios, sin pagos y sin enviar datos
tuyos a ninguna parte.

Este repositorio no tiene el código de la app. Aquí está:

| | Qué es |
|---|---|
| [`descripciones/`](descripciones) | Las **descripciones morfológicas**, una ficha por especie. **Cualquiera puede escribirlas o mejorarlas**: [cómo hacerlo](descripciones/CONTRIBUTING.md). |
| [`Updates/`](Updates) | Los manifiestos que la app revisa una vez al día ([qué dice cada uno](Updates/README.md)). |
| [Releases](https://github.com/obnubiladox/Plantas_CL/releases) | Los archivos que la app descarga: catálogo, descripciones, observaciones de iNaturalist y ejemplares de Herbario Digital. |
| [Issues](https://github.com/obnubiladox/Plantas_CL/issues) | Errores en una especie y sugerencias. |
| [`PRIVACIDAD.md`](PRIVACIDAD.md) | La política de privacidad de la app. |

## Los datos

| Datos | Qué trae | Se renueva | Fuente |
|---|---|---|---|
| **Catálogo** (`catalogo-AAAAMMDD`) | Las especies: taxonomía, sinónimos, hábito, origen, distribución por región, altitud, conservación, cruces con WFO, iNaturalist y Herbario Digital | cada 3 meses | [Catálogo de las Plantas Vasculares de Chile](https://catalogoplantas.udec.cl/) (Universidad de Concepción), [MMA](https://clasificacionespecies.mma.gob.cl/), [World Flora Online](https://www.worldfloraonline.org/) |
| **Descripciones** (`descripciones-AAAAMMDD`) | La descripción morfológica de cada especie, con sus fuentes | cuando hay aportes nuevos | Quienes colaboran en [`descripciones/`](descripciones) (dominio público, [CC0 1.0](descripciones/LICENSE)) |
| **Observaciones** (`inaturalist-AAAAMMDD`) | Cuántas observaciones verificables tiene cada especie en Chile, en celdas de ~20 km | cada 3 meses | [iNaturalist](https://www.inaturalist.org/) |
| **Herbario** (`herbariodigital-AAAAMMDD`) | Los ejemplares de herbario georreferenciados de cada especie | cada 3 meses | [Herbario Digital](https://www.herbariodigital.cl/) (Universidad de Concepción) |

- **La versión de cada dato es la fecha en que se publicó** (`20270215` = 15 de
  febrero de 2027). Lo que decide si hay algo nuevo es su huella
  (`contentSha256`): si el contenido no cambió, no se vuelve a publicar.
- Cada Release guarda solo esa versión; quedan la actual y la anterior.
- Si usas estos datos, **cita las fuentes originales** (abajo, en Créditos).
  Cada una conserva su licencia: la app y este repositorio solo los reúnen.

## Colaborar

- **Escribir o mejorar una descripción:** busca la especie en el
  [índice](descripciones/INDICE.md), toca el lápiz y propone el cambio. Una
  revisión automática revisa el formato y cada propuesta se revisa antes de
  llegar a la app. Paso a paso en [cómo escribir una descripción](descripciones/CONTRIBUTING.md).
- **Informar un error:** desde la ficha de la especie en la app, **menú →
  Informar error** (abre un formulario aquí, ya con la especie), o
  [directamente](https://github.com/obnubiladox/Plantas_CL/issues/new/choose).

Necesitas una cuenta de GitHub (es gratis).

---

## La app

La app se instala **solo desde Google Play**:
[Plantas_CL en Google Play](https://play.google.com/store/apps/details?id=cl.obnubilado.plantascl).
Funciona desde **Android 7.0**.

- **La app** se actualiza desde Google Play.
- **Los datos** los revisa sola una vez al día y, si hay nuevos, los baja e
  instala (casi siempre unos KB) y te avisa. La primera vez que la abres con
  conexión baja las descripciones, las observaciones y el herbario. En **menú →
  Actualizaciones** ves qué versión de cada uno tienes.

Siempre se conservan tus marcas, notas, galerías y fotos. Si una especie cambia
de número en el catálogo, se van con ella.

### Primeros pasos: elige una carpeta

Al abrir la app por primera vez, te pide permiso para mostrar notificaciones
(para el avance de las descargas) y que **elijas una carpeta** del teléfono
(puedes crear una nueva, por ejemplo `Plantas`). Si lo dejas para después, te
la vuelve a pedir la primera vez que guardes una foto. Ahí se guardan:

- tus **fotos**, en una carpeta por especie, con su autor y licencia;
- un **respaldo automático** de tus marcas, notas, galerías y colecciones;
- una copia de tus **colores**, si los cambiaste.

Esa carpeta **sigue ahí aunque desinstales la app**. Si reinstalas o cambias
de teléfono (copiando la carpeta), elige la misma carpeta y todo vuelve.
Todo lo de la carpeta está en **menú → Configuración**.

### Catálogo

Todas las especies como tarjetas: nombre científico, nombre común, hábito,
origen (endémica, nativa o introducida), categoría de conservación y fotos.

- **Buscador** por nombre científico, nombre común o tus notas, sin importar
  tildes ni mayúsculas.
- **Filtros:** clase, orden, familia, género, hábito, origen, categoría de
  conservación, distribución por región y rango altitudinal; y **Mostrar
  solo** Avistadas, Favoritas, Con notas, Con fotos, DS68 y Amenazadas. Cada
  opción dice cuántas especies quedarían.
- **Orden** por nombre científico, por clasificación o por familia y género,
  con grupos que se contraen y expanden.
- **Visor de fotos** con zoom: hacia los lados, otra foto; hacia arriba o
  abajo, otra especie.

### Ficha de la especie

Fotos, nombre común, hábito, origen, categoría de conservación y DS68;
botones **Avistada**, **Favorita**, **Nota** y **Agregar a galería**. Debajo,
pestañas con su fuente y un enlace a ella:

- **Descripción:** la descripción morfológica, con sus fuentes, y los botones
  **Escribir en GitHub** o **Mejorar en GitHub**.
- **Catálogo:** taxonomía, sinónimos, **distribución** con un **mapa de
  Chile** (relieve, regiones y, si quieres, las observaciones de iNaturalist y
  los ejemplares de Herbario Digital), rango altitudinal y notas.
- **Conservación:** la clasificación del RCE con todo su detalle.
- **WFO:** nombre aceptado y clasificación según World Flora Online.
- **iNaturalist:** un mapa con las observaciones verificables en Chile.
- **Herbario Digital:** los ejemplares de herbario georreferenciados, en un mapa.

Los mapas se abren en pantalla completa, con zoom. Mantén presionada una
pestaña para cambiar su orden. Desde el menú de la ficha puedes agregar fotos
del teléfono, buscar fotos en iNaturalist, en el Catálogo o en Herbario Digital
y elegir cuáles guardar, e **informar un error**.

### Galerías y colecciones

Listas de especies que armas tú, con su propio buscador, filtros, orden,
marcas y notas.

- **Descargar fotos en lote** (1 a 20 por especie), en segundo plano, con
  pausa y reanudación.
- **Crear una galería desde iNaturalist**, pegando una lista o una búsqueda.
- Agruparlas en **colecciones**.
- **Exportar:** para otro teléfono con la app (`.pvch`) o para ver en un
  computador (`.zip` con una página que funciona sin internet). Solo se
  exportan fotos que se pueden compartir, cada una con su crédito.

### Colores

La app sigue el modo claro u oscuro del teléfono. Mantén presionado el título
**Plantas_CL** para cambiar los colores.

---

## Privacidad

No hay cuentas. Tus marcas, notas, galerías y fotos se guardan solo en tu
teléfono y en la carpeta que eliges. La app se conecta a internet solo para
buscar y bajar fotos, crear galerías desde iNaturalist, bajar y revisar los
datos de este repositorio y mostrar el mapa de especies que no están en la
base; ninguna de esas consultas lleva datos tuyos. Detalle en la
[política de privacidad](PRIVACIDAD.md).

---

## Créditos y fuentes

Plantas_CL reúne información publicada por instituciones, investigadores y
miles de observadores. El trabajo científico y las fotografías son de ellos:
la app solo ensambla esos datos. Si usas esta información, **cita las fuentes
originales**. La app no es un producto oficial de ninguna de estas
instituciones.

- **[Catálogo de las Plantas Vasculares de Chile](https://catalogoplantas.udec.cl/)**
  (Universidad de Concepción): listado de especies, taxonomía, sinónimos,
  hábito, origen, distribución, rango altitudinal, notas y fotografías
  (CC BY-NC-ND 4.0). *Cita:* Rodríguez, R., C. Marticorena, D. Alarcón,
  C. Baeza, L. Cavieres, V.L. Finot, N. Fuentes, A. Kiessling, M. Mihoc,
  A. Pauchard, E. Ruiz, P. Sanchez & A. Marticorena. 2018. Catálogo de las
  plantas vasculares de Chile. *Gayana Botánica* 75(1): 1–430.
- **[Clasificación de Especies según Estado de Conservación](https://clasificacionespecies.mma.gob.cl/)**
  (Ministerio del Medio Ambiente): categorías de conservación (procesos 1.° al
  20.° del RCE). Ante cualquier diferencia, vale lo publicado por el Ministerio.
- **[iNaturalist](https://www.inaturalist.org/)**: taxonomía, observaciones y
  fotos. Cada foto pertenece a su autor y tiene su propia licencia.
- **[Herbario Digital](https://www.herbariodigital.cl/)** (Universidad de
  Concepción): ejemplares de herbario georreferenciados (coordenadas desplazadas
  unos 2 km para proteger especies amenazadas), fotos de campo y pliegos
  (CC BY-NC-ND).
- **[World Flora Online](https://www.worldfloraonline.org/)**: nombres
  aceptados y clasificación.
- **Descripciones morfológicas:** escritas por quienes colaboran en
  [`descripciones`](descripciones), de dominio público
  ([CC0 1.0](descripciones/LICENSE)). Cada texto indica sus obras de origen:
  cítalas a ellas.
- **Mapa:** límites regionales de la Biblioteca del Congreso Nacional (SIIT,
  2019); relieve del modelo Copernicus DEM GLO-90 (© DLR e.V. 2010-2014 y
  © Airbus Defence and Space GmbH 2014-2018, provisto por la Unión Europea y la
  ESA en el marco de COPERNICUS); agua de ESA WorldCover 2021 (CC BY 4.0), y
  colores del terreno de Natural Earth.
