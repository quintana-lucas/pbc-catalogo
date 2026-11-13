# Plantilla de catálogo con pedido por WhatsApp

Sitio estático para negocios chicos: un catálogo que se arma solo desde una
planilla de Google Sheets, con carrito y pedido por WhatsApp. Se arma
solo con una Action. Salió del catálogo de Savia y se generalizó para
usarlo con otros clientes.

**Todo lo propio del cliente está en `config.json`.** El resto (`build.py`,
`plantilla/`, el workflow) no se toca para un cliente nuevo.

## Cliente nuevo en 8 pasos

1. **Crear el repo.** En esta plantilla, *Use this template → Create a new
   repository*. Nombre sugerido: `<cliente>-catalogo`.
2. **Logo y fotos.** Subir el logo a `assets/` (SVG, PNG o WebP) y cambiar
   `assets/favicon.ico`, `favicon-512.png`, `apple-touch-icon.png` y
   `compartir.jpg` (1200 × 630, es la vista previa al compartir el link). Las
   fotos de productos van en `img/` con nombres en minúscula, sin espacios.
3. **Editar `config.json`** (tabla de abajo). Como mínimo: `nombre`,
   `whatsapp`, `logo`, `colores` y los textos.
4. **Armar la planilla.** Copiar `data/productos.csv` a una planilla de Google
   con esas columnas: `Categoría, Nombre, Descripción, Presentación, Precio,
   Disponible, Foto`. Solo `Nombre` y `Precio` son obligatorias; un precio
   vacío muestra «Consultar» y `Disponible = no` muestra «Sin stock».
5. **Publicar la planilla.** *Archivo → Compartir → Publicar en la web →* la
   hoja de productos, formato *CSV*. Pegar ese link en `planilla_csv`.
6. **Dominio (opcional).** Poner el dominio en `dominio` y, cuando esté
   funcionando, `indexar: true` para que aparezca en Google.
7. **Probar.** Pestaña *Actions → Publicar catálogo → Run workflow*. Revisar
   la página en el celular: agregar un producto y mandar un pedido de prueba.

Para probar en la compu antes de subir: `python3 build.py` y abrir
`_site/index.html` (la portada con las puertas Catálogo y Catering; el catálogo está en `_site/catalogo.html`). No hace falta instalar nada.

## Qué va en `config.json`

| Clave | Para qué |
|---|---|
| `nombre`, `eslogan`, `descripcion` | Título de la pestaña, resultado de Google y vista previa al compartir. |
| `whatsapp` | Número con código de país, sin `+` ni espacios: `5491112345678`. Obligatorio. |
| `instagram` | Link al perfil. Vacío = no se muestra el ícono. |
| `planilla_csv` | Link CSV de la planilla publicada. Vacío = usa `data/productos.csv`. |
| `dominio`, `indexar` | Dominio propio y si Google lo puede indexar. Mientras se prueba: `indexar: false`. |
| `logo` | Archivo y tamaño original (ancho y alto en píxeles, para que no salte al cargar). |
| `colores` | `principal` (botones), `principal_oscuro` (botón al pasar el mouse), `secundario` (categoría elegida), `sobre_secundario` (texto sobre el secundario), `acento` (línea del encabezado y del aviso; si falta, usa el secundario), `fondo`, `tarjetas`, `texto`, `texto_suave`, `bordes` (líneas y divisores), `bordes_controles` (opcional: borde de buscador, categorías y campos; si falta se calcula mezclando `texto` con `tarjetas`, para que se vea con contraste 3:1), `alerta` («Sin stock»). |
| `fuentes` | Dos fuentes de [Google Fonts](https://fonts.google.com): `titulos` y `texto`. |
| `sellos` | Insignias junto al logo («Sin TACC», «Caseras»…). Cada una con `emoji` o `imagen`, y `detalle` opcional. `[]` = ninguna. |
| `mensaje_pedido`, `aviso`, `pie` | Primera línea del mensaje de WhatsApp, cartel de instrucciones y texto del pie. |
| `categorias_primero` | Categorías que van siempre arriba (por ejemplo `Ofertas`). |
| `emojis_categoria`, `emojis_producto`, `emoji_por_defecto` | Emojis que se ven si un producto no tiene foto. Para productos gana la primera palabra que aparezca en el nombre. |
| `quienes_somos`, `quienes_somos_modo` | Párrafos de «¿Quiénes somos?» y si se abren en un cartel (`modal`) o en otra página (`pagina`). `oculto` (o `[]`) = no aparece el botón, ni el cartel, ni la página (se conserva el texto). |
| `pedidos_especiales` | Módulo opcional, ver abajo. |

## Módulos opcionales

### Catering y cotizador (incluido; la clave de config.json sigue siendo `pedidos_especiales`)

Con `"activo": true` en `pedidos_especiales` se suma la página
`pedidos-especiales.html`, un botón en el encabezado y un aviso arriba del
catálogo. Es un cotizador de catering (invitados, opciones, extras, fecha y
zona) que arma el mensaje y lo abre en WhatsApp: no necesita servidor ni base
de datos.

- `titulo`, `texto`, `boton`: textos de la página y del botón. `umbral_pista` (opcional, 30 por defecto): unidades en el carrito del catálogo desde las que aparece "¿Es para un evento?" con un link a Catering.
- `minimo_personas`: por debajo de ese número la página avisa «consultanos»,
  pero deja enviar igual.
- `personas_por_defecto`: invitados que aparecen cargados al entrar (0 = vacío).
- `mensaje`: primera línea del mensaje de WhatsApp.
- `nota`: texto chico debajo del estimado (por ejemplo, que es orientativo).
- `catering_csv`: link CSV de una hoja de Google publicada (Archivo > Compartir
  > Publicar en la web > CSV) con las opciones y extras del cotizador. Se lee
  al armar la página, así que un cambio en la hoja se ve después de volver a
  publicar. Si el link está vacío, no responde o la hoja no trae opciones, se
  usa `data/catering.csv` (mismo formato) y el build avisa. Columnas, una fila
  por opción o extra (los encabezados no distinguen mayúsculas ni tildes):
  - `Tipo`: `Opción` o `Extra`.
  - `Nombre`: lo que ve el cliente.
  - `Descripción`: texto chico opcional (también se acepta el typo `Descipción`).
  - `Precio`: entero en pesos; vacío = «a consultar» y no suma.
  - `Cobro`: `por persona` o `fijo` (las opciones siempre van por persona).

La página muestra las opciones (la primera viene tildada) y los extras para
tildar (se pueden combinar) y, al lado, una **comanda** con el desglose, el
total estimado y el precio por invitado, que se actualiza al instante. El
mensaje de WhatsApp lleva invitados, opciones, extras, fecha, zona y el
estimado, y hay un botón para copiar el resumen. Un precio vacío = «a
consultar» y no suma.

Con `"activo": false` desaparece todo rastro del módulo.

### Ideas para más adelante (no están hechas)

- **Cotizador por cantidades** (por ejemplo 30 empanadas + 2 tartas): ya lo
  resuelve el carrito del catálogo, que suma el total estimado. Si hiciera
  falta un catálogo aparte para catering, se puede leer una segunda hoja de la
  misma planilla con otra URL CSV.
- **Recibir consultas por mail además de WhatsApp**: si el sitio se muda a
  Netlify, sus formularios gratis lo resuelven sin código de servidor.
- **Días de entrega o pedido mínimo** en el carrito: un par de claves más en
  `config.json` y unas líneas en `plantilla/index.html`.

## Cómo se publica

`.github/workflows/publicar.yml` corre `build.py`, que lee la planilla y
arma `_site/`, y guarda el resultado:

- en cada `push` a `main`;
- a mano, desde *Actions → Run workflow* (con la opción «Publicar igual» si
  la planilla quedó con muchos menos productos a propósito);
- cada hora de 8 a 22, solo si la planilla cambió.

Si la planilla pierde las columnas `Nombre` o `Precio`, queda vacía o pierde
más de la mitad de los productos, **no se publica** y la página sigue como
estaba. Si falta una foto, se muestra el emoji y queda un aviso en el log.
