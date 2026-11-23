# Descripciones morfológicas

Las descripciones de la pestaña **Descripción** de la app Plantas_CL: una ficha
por especie, en Markdown, que cualquiera puede escribir o mejorar.

- **[Índice](INDICE.md):** todas las especies por familia, con las que ya
  tienen descripción.
- **[Cómo escribir una descripción](CONTRIBUTING.md):** paso a paso, formato y
  qué escribir.
- **[Licencia](LICENSE):** dominio público (CC0 1.0).

## Cómo llegan a la app

1. Cada ficha está en [`Fichas`](Fichas), con el número de ficha del
   [Catálogo de las Plantas Vasculares de Chile](https://catalogoplantas.udec.cl/)
   y el nombre de la especie: `4534 Vachellia caven.md`.
2. Las propuestas llegan como *pull requests*; una revisión automática revisa el
   formato y cada una se revisa antes de unirla.
3. Más o menos una vez al mes se **publican**: un Release
   `descripciones-AAAAMMDD` con todas las fichas y, aparte, solo los cambios
   desde cada una de las últimas publicaciones. La app revisa una vez al día y
   baja solo lo que le falta (casi siempre unos KB).

La carpeta [`Fichas`](Fichas) tiene más de 5.000 archivos y la web de GitHub
muestra solo los primeros 1.000: para encontrar una especie usa el
[índice](INDICE.md) o la tecla `t` en la página del repositorio.

## Para quien mantiene el repositorio

- `scripts/descripciones.py`: la única lógica que lee las fichas (revisar,
  plantillas, índice y publicar). Solo librería estándar de Python. Sus tests:
  `python -m unittest descripciones/scripts/test_descripciones.py`.
- Workflows (`.github/workflows/`): **Revisar descripciones** (cada PR; es el
  chequeo obligatorio `revisar`), **Publicar descripciones** y **Plantillas de
  descripciones** (los dos a mano, desde la pestaña Actions).
- `INDICE.md` y `Familias/` los rehacen los workflows: no se editan a mano.
