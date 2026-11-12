# Objetivo 2 — Análisis de Manipulación Transaccional (Cantidades Negativas)

**Módulo VII · Lógica de Negocio**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. El escenario

Un e-commerce deja agregar productos al carrito. La petición que viaja al servidor es algo así:

```http
POST /api/carrito/agregar HTTP/1.1
Host: tienda.com
Content-Type: application/json
Cookie: session=...

{ "productoId": 55, "cantidad": 1 }
```

Interceptamos esa petición (con Burp Suite, por ejemplo) y **cambiamos la cantidad de `1` a `-5`**:

```json
{ "productoId": 55, "cantidad": -5 }
```

El servidor la procesa sin chequear el signo. El precio del producto es $1.000, así que la línea del carrito calcula:

```
subtotal = precio × cantidad = 1000 × (-5) = -5000
```

El total del carrito queda en **−$5.000**. Dependiendo de cómo esté armada la pasarela de pago o el sistema de saldos, eso puede terminar **acreditándote $5.000 en lugar de cobrarte**, o bajando el total de una compra real de $8.000 a $3.000.

> ⚠️ Esto **no es un bug de código clásico** (no hay un `NullPointerException` ni una inyección). Es una **falla de lógica de negocio**: el código funciona "bien", hace la multiplicación perfecta… el problema es que nadie le dijo que una cantidad negativa **no tiene sentido en el mundo real**. No existe comprar "menos cinco" productos.

---

## 2. Por qué ocurre (explicación técnica)

### 2.1 La causa raíz: el servidor confía en el dato del cliente

La regla de oro del pentesting: **todo lo que viene del cliente es hostil hasta que el servidor lo valide.** El navegador, el formulario, el JavaScript del front, el `<input type="number" min="1">`… **nada de eso es una defensa real**. Son comodidad para el usuario honesto, pero un atacante **no usa el formulario**: manda la petición HTTP cruda y escribe lo que quiere.

Acá el desarrollador asumió que la cantidad siempre iba a ser un entero positivo "porque el input del HTML tiene `min="1"`". Pero esa validación vive **del lado del cliente**, y el cliente está bajo control del atacante. El servidor nunca volvió a chequearlo.

### 2.2 El tipo de dato traiciona

El campo `cantidad` casi siempre se guarda como un **entero con signo** (`int`, `Int32`, `number`). Un entero con signo acepta valores negativos por definición: `-5` es un `int` perfectamente válido. El lenguaje **no se va a quejar**, porque a nivel técnico `-5` es un número correcto. La "incorrección" es **semántica** (de negocio), no de tipo.

### 2.3 La aritmética propaga el error silenciosamente

El cálculo del total es una simple multiplicación:

```python
total = sum(item.precio * item.cantidad for item in carrito)
```

Matemáticamente, `precio × (−5)` da un negativo. El código hace exactamente lo que le pidieron. **No hay excepción, no hay error, no hay log.** El número negativo viaja limpio por toda la cadena: carrito → resumen → orden → cobro. Cada capa confía en que la anterior ya validó, y **ninguna lo hizo**. Esto se llama **falta de validación defensiva** o ausencia de *defense in depth*.

### 2.4 El impacto real depende de la pasarela de pago

- Si el sistema maneja **saldo / billetera / crédito de tienda**, un total negativo puede interpretarse como "la tienda te debe plata" → **te acreditan saldo gratis**.
- Si se mezcla con productos positivos, baja fraudulentamente el total → **pagás mucho menos de lo que te llevás**.
- Si hay reembolsos automáticos, el negativo puede disparar una **devolución a tu tarjeta** de dinero que nunca pusiste.

### 2.5 Primo hermano: la misma falla aparece de otras formas

Esta vulnerabilidad es una familia. El mismo descuido se explota con:

- **Precios negativos o decimales raros:** `cantidad = 0.5`, `precio` manipulado (si viene del cliente — error gravísimo).
- **Overflow / desbordamiento de enteros:** `cantidad = 999999999999` que da la vuelta al contador y termina en negativo.
- **Cupones apilados / abuso de descuentos:** `descuento = 150%` → total negativo.
- **Race conditions** (visto en Módulo VII): mandar 50 veces en paralelo "canjear cupón" para que se aplique varias veces.

Todas comparten la raíz: **la lógica de negocio no definió ni validó los límites reales del dominio.**

### 🔍 Cómo verlo en el software

1. Agregás un producto normal al carrito y abrís **Burp Suite → Proxy** (o DevTools → Network).
2. Capturás la petición de "agregar al carrito" o "actualizar cantidad" y la mandás al **Repeater** (`Ctrl+R`).
3. Cambiás `"cantidad": 1` por `"cantidad": -5` (y en otra prueba, por `0`, por `0.5`, por un número gigante).
4. Mirás la **respuesta** y el **total del carrito**.
   - **Señal que confirma el bug:** el servidor responde `200 OK`, acepta el valor y el **subtotal/total se vuelve negativo** (o baja de lo que debería). Si en cambio te devuelve `400 Bad Request` con un mensaje tipo "cantidad inválida" y **no** modifica el carrito, está bien protegido.

---

## 3. Cómo debe validar el desarrollador (del lado del servidor)

La defensa es **siempre en el servidor**, nunca confiando en el front. La validación tiene que ser **estricta, explícita y por lista blanca** (aceptar solo lo válido, no intentar bloquear lo inválido).

### 3.1 Validación estricta del campo `cantidad`

En el endpoint, **antes de tocar precios o base de datos**, chequear todas estas condiciones:

| Regla | Por qué |
|---|---|
| Es un **entero** (no `-5.5`, no texto, no `null`, no array) | Evita tipos inesperados y errores de parsing |
| Es **mayor o igual a 1** (`cantidad >= 1`) | Mata el negativo y el cero de una |
| Es **menor o igual a un máximo razonable** (ej. `<= 100` o el stock disponible) | Evita overflow y compras absurdas |
| El **producto existe y está activo** | Evita manipular IDs junto con la cantidad |
| El **precio se busca en la base de datos del servidor**, NUNCA se acepta del cliente | El cliente solo manda `productoId` y `cantidad`; el precio es autoritativo del servidor |

### 3.2 Ejemplo de código seguro

**Backend (pseudocódigo / Python-ish):**

```python
def agregar_al_carrito(request, usuario):
    producto_id = request.json.get("productoId")
    cantidad    = request.json.get("cantidad")

    # 1) Tipo correcto: entero, no float, no string, no None
    if not isinstance(cantidad, int):
        return error(400, "La cantidad debe ser un número entero")

    # 2) Rango válido (lista blanca): 1 <= cantidad <= 100
    if cantidad < 1 or cantidad > 100:
        return error(400, "Cantidad fuera del rango permitido")

    # 3) El producto existe y está activo (autoridad del servidor)
    producto = db.productos.get(id=producto_id, activo=True)
    if producto is None:
        return error(404, "Producto no disponible")

    # 4) Chequeo de stock real
    if cantidad > producto.stock:
        return error(409, "No hay stock suficiente")

    # 5) El PRECIO lo pone el servidor, jamás el cliente
    subtotal = producto.precio * cantidad   # ya es imposible que sea negativo

    carrito.agregar(producto_id, cantidad, producto.precio)
    return ok(carrito.total())
```

**Con validación declarativa** (lo ideal en frameworks modernos), por ejemplo en .NET / C#:

```csharp
public class AgregarCarritoRequest
{
    [Required]
    public int ProductoId { get; set; }

    [Range(1, 100, ErrorMessage = "La cantidad debe estar entre 1 y 100")]
    public int Cantidad { get; set; }
}
```

El atributo `[Range(1, 100)]` rechaza `-5`, `0` y `999999` **automáticamente**, antes de que la petición siquiera entre al controlador. Es la misma idea que ya usamos en Farmacia Tienda con `[Range]` sobre `MedioPago` en `CrearPedidoRequest`.

### 3.3 Principios que hay que aplicar siempre

1. **Validación en el servidor, no en el cliente.** El front valida para UX; el back valida para seguridad. Son dos validaciones distintas y las dos tienen que existir.
2. **Lista blanca, no lista negra.** No intentes "bloquear valores malos" (siempre te olvidás uno). Definí **exactamente qué es válido** (entero, 1–100) y rechazá todo lo demás.
3. **El servidor es la única fuente de verdad para precios, descuentos y stock.** El cliente solo elige *qué* y *cuánto*; el *cuánto cuesta* lo decide el backend consultando su propia base de datos.
4. **Defensa en profundidad.** Validar en la entrada (DTO), validar en la lógica de negocio (dominio), y poner un **check final antes del cobro** que corte cualquier total ≤ 0. Si una capa falla, otra lo atrapa.
5. **Fallar seguro (fail-safe).** Ante la duda (tipo raro, valor fuera de rango, producto inexistente), **rechazar** la operación con un error genérico, nunca dejar pasar.

---

## 4. Conclusión

La falla de cantidades negativas es un caso de libro de **vulnerabilidad de lógica de negocio**: el código es técnicamente correcto, pero nunca validó que el dato tuviera sentido en el dominio real. El atacante no rompe el sistema con una inyección, lo rompe **usando el sistema con un dato que el desarrollador nunca imaginó** porque confió en una validación de cliente que es trivial de saltear.

La remediación es simple pero inquebrantable: **validación estricta del lado del servidor, por lista blanca, con el precio y el stock siempre bajo autoridad del backend, y un chequeo final que garantice que ningún total pueda ser cero o negativo.** Autenticar no es autorizar, y recibir un dato no es confiar en él: cada campo que entra del cliente se valida, siempre, en el servidor.

---

*Fin del Objetivo 2 — Módulo VII.*
