# Cómo escribir una descripción

Gracias por ayudar a describir la flora de Chile. Cada especie de la app
[Plantas_CL](https://play.google.com/store/apps/details?id=cl.obnubilado.plantascl)
tiene aquí su ficha, un archivo de texto en la carpeta [`Fichas`](Fichas). Lo
que escribas aparece en la pestaña **Descripción** de la app después de que se
revise y se publique (más o menos una vez al mes).

Necesitas una cuenta de GitHub (es gratis). No hace falta instalar nada: todo
se hace en el navegador.

## Paso a paso

1. **Busca la especie.** En el [índice](INDICE.md) elige su familia y toca su
   nombre. También puedes apretar la tecla `t` en la página del repositorio y
   escribir el nombre o el número de ficha. Desde la app, en la pestaña
   Descripción, el botón **Escribir en GitHub** o **Mejorar en GitHub** te
   lleva directo.
2. **Toca el lápiz (✏️)**, arriba a la derecha del archivo. GitHub te ofrece
   hacer una copia del repositorio (un *fork*): acepta, es para guardar tu
   propuesta.
3. **Escribe** siguiendo el formato de abajo. En la pestaña **Preview** ves cómo
   queda.
4. **Commit changes… → Propose changes**: escribe en una línea qué cambiaste
   («Descripción de *Vachellia caven*»).
5. **Create pull request.** En la descripción del pull request (PR) **marca las
   tres casillas** (cambia `[ ]` por `[x]`) y crea el PR.
6. Una **revisión automática** dice en unos segundos si el formato está bien. Si
   algo falla, en la pestaña **Files changed** del PR verás qué línea y por qué:
   corrígelo en tu archivo (✏️ otra vez) y el PR se actualiza solo.
7. Se revisa tu propuesta y, si está todo bien, se une. Llega a la app con la
   siguiente publicación.

Puedes proponer varias especies en el mismo PR: después del primer archivo,
edita los demás en la rama de tu propuesta antes de crear el PR, o crea un PR
por especie (lo más simple).

## Formato

Cada ficha es un archivo **Markdown**. Un ejemplo completo:

```markdown
# Vachellia caven

## Morfología

### Hojas
Alternas, **bipinnadas**, con espinas estipulares. Se parece a *Vachellia
farnesiana*, de la que se distingue por…

> Fuente: Rodríguez et al. 2018

### Flores
- Cáliz campanulado.
- Corola amarilla.

> Fuente: Marticorena & Quezada 1985
```

| Escribes | Es |
|---|---|
| `# Nombre` | La primera línea: el nombre de la especie. **No la cambies.** |
| `## Morfología` | Un título. |
| `### Hojas` | Un subtítulo. |
| Texto normal | Un párrafo. Las líneas seguidas se juntan; una **línea en blanco** separa párrafos. |
| `> Fuente: Autor año` | La fuente de lo que está justo arriba. Puede haber varias en una ficha. |
| `- ítem` o `1. ítem` | Una lista, un ítem por línea. |
| `*cursiva*` | Cursiva: para los nombres científicos. |
| `**negrita**` | Negrita. |

**No se aceptan** (la revisión avisa): enlaces o direcciones web, imágenes,
tablas, HTML, código, llaves `{ }`, notas al pie y más de dos niveles de título
(`####`). La app no los muestra y en GitHub se verían distinto.

## Qué escribir

- **Con tus palabras.** No copies textos de libros, floras, fichas ni sitios
  web, aunque cites la fuente: los textos tienen autor. Puedes basarte en ellos
  y citarlos con `> Fuente: …`.
- **Cita tus fuentes** junto a lo que tomaste de cada una, con autor y año.
  Si es una observación propia, puedes poner `> Fuente: observación personal`.
- Un orden sugerido: hábito y tamaño, tallos, hojas, flores (inflorescencia,
  cáliz, corola, androceo, gineceo), fruto y semilla, y lo que la distingue de
  especies parecidas.
- Español neutro y términos botánicos precisos. Medidas con su unidad
  (`2-5 cm`, `10-25 m`).
- **No cambies el nombre del archivo** ni la primera línea: los pone al día una
  herramienta cuando cambia el catálogo.
- Para quitar una descripción, deja el archivo solo con su primera línea (no lo
  borres).

## Licencia y créditos

Todo lo que se publica en `Fichas` queda en el **dominio público**
([CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/deed.es)):
cualquiera puede copiarlo, modificarlo y usarlo, también con fines comerciales,
sin pedir permiso. Al enviar tu propuesta confirmas que el texto es tuyo (o ya
era de dominio público) y que lo dedicas al dominio público.

Tu **nombre público de GitHub** (el de tu perfil, o tu usuario si no tienes uno)
aparece en los créditos de la app, en **Créditos y fuentes**, junto a quienes
escriben las descripciones.

## Dudas

Abre un [issue](https://github.com/obnubiladox/Plantas_CL/issues) o comenta en
tu pull request.
