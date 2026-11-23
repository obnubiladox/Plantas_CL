# Updates

Los manifiestos que la app Plantas_CL revisa una vez al día, desde
`https://raw.githubusercontent.com/obnubiladox/Plantas_CL/refs/heads/main/Updates/<archivo>`.
Cada uno dice cuál es la versión publicada de unos datos y dónde está su
archivo (en un [Release](https://github.com/obnubiladox/Plantas_CL/releases)).

**No se editan a mano:** los escriben las herramientas al publicar. Si uno
apunta a un archivo que no existe o con otra huella, la app no lo instala.

| Archivo | Datos | Lo escribe | Release |
|---|---|---|---|
| `catalogo.json` | La base del catálogo | `tools/plantas_cl.py publicar` | `catalogo-AAAAMMDD` |
| `inaturalist.json` | Observaciones de iNaturalist por especie | `tools/plantas_cl.py publicar` | `inaturalist-AAAAMMDD` |
| `herbariodigital.json` | Ejemplares de Herbario Digital por especie | `tools/plantas_cl.py publicar` | `herbariodigital-AAAAMMDD` |
| `descripciones.json` | Descripciones morfológicas | el workflow **Publicar descripciones** | `descripciones-AAAAMMDD` |

## Campos comunes

- `version`: la **fecha de la publicación**, `AAAAMMDD`. Una app con una versión
  más nueva instalada ignora un manifest de fecha menor (puede ser una copia
  vieja en caché).
- `contentSha256`: la **huella del contenido**. Es lo que decide si hay algo
  nuevo: con la misma huella, la app no baja nada aunque cambie la fecha.
- `sha256` / `dbSha256` y `bytes`: los del archivo comprimido; la app los
  verifica antes de instalar.
- `updated`, `notes`, `rows`: fecha de los datos, notas y cuántas especies.

## Lo propio de cada uno

- **catalogo.json:** `sha256` es el del `catalogo.csv` de origen; `db` es el
  archivo; `dbMapper`, el formato de la base (una app que no lo entiende pide
  actualizarse); `renumbered`, cuántas especies cambiaron de N.° de ficha (la
  app mueve con ellas las marcas, notas, galerías y fotos de cada persona).
- **inaturalist.json:** `since`/`updated`, entre qué fechas se bajaron las
  observaciones.
- **herbariodigital.json:** `specimens`, ejemplares en total.
- **descripciones.json:** `full` (todas las fichas) y `changes` (solo lo que
  cambió desde cada una de las últimas publicaciones: la app baja el que le
  corresponde, casi siempre unos KB). Ver [`descripciones/`](../descripciones).
