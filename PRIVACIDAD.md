# Política de privacidad de Plantas_CL

Última actualización: 23 de noviembre de 2026

Plantas_CL (en adelante, "la app") es un
catálogo gratuito de la flora vascular de Chile, sin anuncios y sin cuentas
de usuario. Esta política explica qué datos maneja la app y adónde van. En
resumen: **la app no recopila, no vende ni comparte datos personales**. Todo lo
que anotas queda en tu teléfono y en la carpeta que tú elijas.

## 1. Datos que se guardan en tu teléfono

La app guarda, solo en el teléfono:

- tus marcas de especies (avistada, favorita) y tus notas;
- tus galerías, colecciones y las especies de iNaturalist que agregues a ellas;
- tus preferencias (orden, filtros, colores del tema) y, si los escribes en
  Configuración, el nombre de autor, la licencia y el enlace que quieres
  que acompañen a las fotos que agregas desde tu teléfono;
- el catálogo de especies y las descripciones morfológicas;
- un registro de cuántas consultas y descargas hizo la app a iNaturalist
  (solo fecha, hora, tipo de consulta y cuánto se descargó), para respetar
  los límites de uso de ese servicio. El detalle se borra solo a los dos
  días, y los totales por día, a los 13 meses.

Nada de esto se envía al autor de la app ni a terceros. Al desinstalar la
app, Android borra estos datos. Las notas y galerías no se incluyen en la
copia de seguridad automática de Android.

## 2. La carpeta que eliges

Si eliges una carpeta para fotos y respaldo, la app guarda en ella:

- las fotos que descargas o importas desde tu galería;
- un respaldo de tus marcas y notas (`plantas_datos_usuario.json`), de tus
  colecciones (`plantas_colecciones.json`) y de cada galería (carpeta
  `galerias`);
- junto a las fotos, de dónde viene cada una, su autor y su licencia
  (`fotos.json` en la carpeta de cada especie), para mostrar el crédito; en
  las que agregas desde tu teléfono, el modelo de la cámara y la fecha de
  la foto, leídos de la foto misma, y el autor, la licencia y el enlace que
  hayas escrito en Configuración;
- una copia de los colores de tu tema (`plantas_tema.json`);
- una copia de las observaciones de iNaturalist que la app bajó para los mapas
  de las fichas (`plantas_inaturalist.db`: solo cuántas observaciones públicas
  hay de cada especie en cada zona de Chile, nada tuyo).

La app solo puede leer y escribir en la carpeta que tú elijas. Si esa
carpeta se sincroniza con un servicio en la nube (por ejemplo, Google Drive),
lo que se sincroniza queda sujeto a la política de ese servicio.

## 3. Conexiones a internet

La app se conecta solo a estos servicios y solo para lo que se indica:

| Servicio | Para qué |
|---|---|
| iNaturalist (`api.inaturalist.org`, `tiles.inaturalist.org` y sus servidores de fotos) | Buscar y descargar fotos de especies, importar listas o búsquedas que tú pegues y, al abrir la ficha de una especie que no viene en la app, cuántas observaciones tiene en Chile para su mapa (las de las especies de la base se descargan juntas desde GitHub; mientras no están, también se consultan así) |
| Catálogo de plantas de la Universidad de Concepción (`catalogoplantas.udec.cl`) | Mostrar y descargar las fotos de la ficha de una especie, cuando lo pides |
| Herbario Digital de la Universidad de Concepción (`www.herbariodigital.cl` e `images.herbariodigital.cl`) | Mostrar y descargar fotos de campo y pliegos de herbario de una especie, cuando lo pides, y abrir la ficha de un ejemplar que tocas en el mapa (los ejemplares de cada especie se descargan juntos desde GitHub) |
| GitHub (`raw.githubusercontent.com` y `github.com`) | Revisar si hay versiones nuevas de la base de datos, de las descripciones, de las observaciones de iNaturalist y de los ejemplares de Herbario Digital para los mapas, y descargarlas. Además, los botones **Escribir en GitHub** y **Mejorar en GitHub** de la pestaña Descripción abren esa página en tu navegador, solo cuando los tocas |

En esas conexiones **no se envían datos personales**: ni tus notas, ni tus
marcas, ni identificadores del teléfono o de la cuenta Google. Lo único que se
envía es lo necesario para la consulta (por ejemplo, el número de una especie
o la lista que pegaste) y un identificador de la app
(`Plantas_CL/<versión>`). Como en cualquier conexión a internet, esos
servicios pueden ver tu dirección IP. Cada uno tiene su propia política de
privacidad.

La app no usa servicios de analítica, publicidad, informes de errores ni
rastreo de ningún tipo.

## 4. Lo que tú decides compartir

- **Exportar una galería:** el archivo (`.pvch` o `.zip`) se crea en el
  teléfono y solo sale de él si tú lo compartes o lo guardas en otro lugar.
  Al exportar eliges si incluye tus marcas, notas y fotos. En un `.pvch`, las
  fotos de iNaturalist, del Catálogo y de Herbario Digital pueden ir como archivos o como
  referencias (el enlace a la foto, con su autor y licencia); las que
  agregaste desde tu teléfono siempre van como archivo, con el modelo de la
  cámara, la fecha y el autor, la licencia y el enlace que les hayas puesto, pero **sin la ubicación GPS** que la cámara haya
  guardado en ellas (la app la quita al exportar). Quien importa una
  galería con referencias descarga esas fotos de iNaturalist, del Catálogo o de Herbario Digital
  en su propio teléfono.
- **Informar un error de la base:** abre un formulario en GitHub, en tu
  navegador, con el nombre y el número de la especie y el texto que escribiste.
  Solo se publica si tú lo envías. Para eso necesitas una cuenta de GitHub,
  y lo publicado es **público** y queda sujeto a la política de GitHub.
- **Escribir o mejorar una descripción:** se hace en GitHub, en tu navegador,
  con tu cuenta; lo que propongas es **público**. Si se publica, la app muestra
  en Créditos el nombre público de tu perfil de GitHub (o tu usuario), que es lo
  que GitHub ya muestra de ti. La app no recibe ni guarda nada más de quienes
  escriben.
- **Fotos desde tu teléfono:** se copian tal cual a tu carpeta (con todos
  sus datos, incluida la ubicación si la tienen); nunca se suben a ningún
  servidor.
- **Enlaces externos** (fichas en iNaturalist, la Universidad de Concepción, Herbario Digital,
  World Flora Online y el Ministerio del Medio Ambiente): se abren en tu
  navegador. Lo que hagas ahí queda sujeto a la política de cada sitio.

## 5. Permisos

- **Internet:** para las conexiones descritas arriba.
- **Notificaciones:** para mostrar el avance de las descargas de fotos.
  Puedes negarlo y la app sigue funcionando.
- **Servicio en primer plano (sincronización de datos):** para que una
  descarga de fotos larga no se corte con la pantalla apagada.

La app no pide acceso a tu ubicación, cámara, micrófono, contactos ni a todo
el almacenamiento.

## 6. Menores de edad

La app no recopila datos de nadie, tampoco de menores de edad.

## 7. Cambios a esta política

Si la app cambia lo que hace con los datos, esta política se actualizará y
cambiará la fecha del comienzo. Las versiones anteriores quedan en el
historial del repositorio.

## 8. Contacto

Puedes hacer preguntas sobre esta política abriendo un *issue* en
https://github.com/obnubiladox/Plantas_CL/issues.
