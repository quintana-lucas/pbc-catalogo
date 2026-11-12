# Diseño: portada, navegación y comanda (Catálogo / Catering)

Estado: acordado con Lucas el 2026-11-12. Sin código todavía; las tareas de implementación están en la cola (`/cola`).

## Problema

- El cotizador (`pedidos-especiales.html`) se trata como un desvío del catálogo: por eso existe el
  "← Volver al catálogo" y la navegación general no está pensada.
- Hoy se llega al cotizador por un ícono suelto entre los de redes en el header (`redes()` en `build.py`),
  por el banner del catálogo y por el aviso con el botón "Pedir presupuesto". Un ícono sin texto no le dice
  nada a quien tiene un evento.
- Los dos módulos son conceptos distintos (viandas del día a día vs. eventos y pedidos especiales) y la página
  no los separa. Dos tabs tampoco sirven: ponen a los dos al mismo nivel sin que el usuario elija qué necesita.

## Decisiones

### 1. Nombres

- **Catálogo**: viandas y productos.
- **Catering**: eventos y pedidos especiales (hoy "Pedidos especiales").
- El mismo nombre en la portada, el header, el título de página y los botones.
- La clave de `config.json` (`pedidos_especiales`) no se renombra; solo cambia lo que se ve.

### 2. Portada con dos puertas

Una página de entrada liviana, solo para elegir.

```
[logo]
¿Qué necesitás?
[ Catálogo ]        [ Catering ]
viandas y           eventos y pedidos
productos           especiales
```

- La portada es la página de entrada (`/`). El catálogo pasa a su propia página.
- El logo de cualquier página lleva a la portada.
- Hay que cuidar las URLs que ya circulan (WhatsApp, redes, Google): el link al catálogo no puede romperse.
  Ver "Preguntas abiertas".

### 3. Header por módulo, sin "Volver"

```
Catálogo:  [logo → portada]   Catálogo   [Catering]   [redes]
Catering:  [logo → portada]   Catering   [Catálogo]   [redes]
```

- Cada módulo muestra su título y un único botón con texto hacia el otro módulo.
- Desaparece el "← Volver al catálogo".
- Los dos headers comparten la misma estructura, lo que absorbe la tarea de que los botones del header coincidan.
- El ícono suelto del cotizador entre las redes se reemplaza por el botón con texto.

### 4. La comanda como papel donde se escribe

Dirección elegida: hoja rayada, no ticket térmico.

- Renglones a intervalo fijo con `--linea`; un margen vertical en `--principal` con baja opacidad.
- Encabezado "Tu comanda" con los datos del evento que se completan mientras se tipea: fecha, invitados y zona.
- Cada opción elegida aparece como una línea "escrita" en tipografía manuscrita legible; los montos van en números
  tabulares para leerse bien. La fuente se decide al implementar (se carga vía `{{FUENTES}}`).
- Al destildar una opción, la línea se tacha. Es la única animación y responde a una acción del usuario;
  se apaga con `prefers-reduced-motion`.
- Total estimado con doble subrayado y el "por invitado" debajo.
- Se mantiene lo que ya funciona: `aria-live`, "Copiar resumen" y el botón verde de WhatsApp.
- **Celular**: la comanda deja de ir debajo del formulario y pasa a una barra fija abajo con el total; al tocarla
  se abre el papel completo. Lo contrario no sirve: mientras se eligen opciones la comanda queda fuera de vista.

### 5. Pista del carrito (segunda etapa)

Cuando el carrito del catálogo es muy grande, un aviso chico ("¿Es para un evento? Pedí presupuesto en Catering")
lleva al cotizador. Reemplaza al banner actual (`.banner-pedidos`). Umbral por definir al implementar.

## Preguntas abiertas

- **URLs existentes**: si la portada es `/`, el catálogo cambia de dirección. Definir al implementar si el catálogo
  queda en `catalogo.html` y se mantiene un redirect, o si hay otra solución compatible con el hosting actual.
- **¿Quiénes somos?**: hoy está oculto en PBC, pero el diseño tiene que tener un lugar para él si se reactiva.

## Tareas de implementación

1. Portada y renombrar a Catálogo / Catering (incluye la decisión de URLs).
2. Header y navegación nuevos (sin "Volver", un botón al otro módulo, logo a portada).
3. Comanda como papel rayado, con barra fija en celular.
4. Pista del carrito (después).
