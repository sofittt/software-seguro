# Objetivo 3 — Anatomía de una Condición de Carrera (Race Condition)

**Módulo VII · Lógica de Negocio**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. ¿Qué es una Race Condition? (con mis palabras)

Una **condición de carrera** (*race condition*) pasa cuando el resultado de una operación **depende del orden y del tiempo** en que llegan varias peticiones que tocan **el mismo recurso al mismo tiempo**. El sistema fue pensado para que las cosas pasen **una después de la otra** (en secuencia), pero si dos o más peticiones entran **en paralelo**, se "pisan" entre ellas y el resultado se rompe.

La imagen mental: una **puerta giratoria pensada para una persona**. Si una sola persona pasa, todo bien. Pero si **50 personas se tiran al mismo tiempo**, la puerta se traba y por un instante **todas pasan sin pagar el boleto**, porque el molinete todavía no alcanzó a sumar el primer pase.

### TOCTOU: el corazón del problema

La causa técnica tiene nombre: **TOCTOU — Time-Of-Check to Time-Of-Use** (del momento del chequeo al momento del uso). Es la **ventana de tiempo** que existe entre:

- **TOC (Time Of Check):** el servidor **verifica** una condición → "¿este cupón ya se usó? No → está libre".
- **TOU (Time Of Use):** el servidor **actúa** sobre esa condición → "ok, aplico el descuento y marco el cupón como usado".

Entre esos dos momentos hay **microsegundos**. Si el atacante logra **meter 50 peticiones dentro de esa ventana**, las 50 hacen el "check" **antes** de que ninguna haya terminado el "use". Todas leen "el cupón está libre", y todas aplican el descuento. El servidor recién actualiza la base **después**, cuando ya es tarde.

---

## 2. El escenario: cupón de un solo uso canjeado 50 veces

Un e-commerce tiene un código de descuento `PROMO50` que da **$50 de regalo** y está marcado como **"un solo uso por cuenta"**. La lógica del servidor es, en pseudocódigo:

```python
def canjear_cupon(usuario, codigo):
    cupon = db.cupones.get(codigo)          # (A) leer

    if cupon.usado == True:                  # (B) CHECK ← TOC
        return error("Cupón ya utilizado")

    aplicar_descuento(usuario, cupon.valor)  # (C) acción
    cupon.usado = True                       # (D) USE  ← TOU
    db.guardar(cupon)                        # (E) escribir en la base
```

El problema está en el **hueco entre (B) y (D)**. Si entre que una petición hace el `if cupon.usado == True` (B) y que escribe `cupon.usado = True` en la base (E) pasan otras 49 peticiones, **todas van a leer `usado == False`** y van a pasar el chequeo.

### Qué ve el atacante

- **1 petición normal** → 1 descuento de $50. Correcto.
- **50 peticiones en paralelo, en la misma ventana** → el servidor puede llegar a aplicar **$50 × 50 = $2.500** de descuento (o acreditar ese saldo), porque las 50 leyeron el cupón "libre" antes de que la primera lo marcara como usado.

El sistema **no está roto a nivel de código** (el `if` está bien escrito). Está roto a nivel de **concurrencia**: nunca se garantizó que la secuencia leer → chequear → escribir fuera **atómica** (indivisible).

---

## 3. Cómo lo explota un atacante con Turbo Intruder

El enemigo número uno de una race condition es la **latencia de red** (jitter): si las 50 peticiones llegan con diferencia de milisegundos, la primera ya cerró la ventana antes de que lleguen las demás. Por eso el atacante necesita que las 50 lleguen **lo más pegadas posible**, idealmente **en el mismo instante**. Herramientas como el **Turbo Intruder** de Burp Suite (o el "Send group in parallel" del Repeater) existen justamente para eso.

### Paso a paso

**1) Capturar la petición legítima.**
Con Burp Proxy interceptamos el canje real:

```http
POST /api/cupon/canjear HTTP/1.1
Host: tienda.com
Content-Type: application/json
Cookie: session=abc123...

{ "codigo": "PROMO50" }
```

**2) Mandarla a Turbo Intruder** (click derecho → *Extensions → Turbo Intruder → Send to Turbo Intruder*).

**3) Escribir el script de disparo paralelo.** Turbo Intruder usa un pequeño script en Python. La idea: **encolar 50 copias idénticas** de la misma petición y **dispararlas juntas**:

```python
def queueRequests(target, wordlists):
    # Un motor pensado para concurrencia alta
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=50,     # 50 conexiones abiertas a la vez
        requestsPerConnection=1,
        pipeline=False
    )
    # Encolamos 50 veces la MISMA petición
    for i in range(50):
        engine.queue(target.req, gate='canje')  # todas en la misma "compuerta"

    # Abrimos la compuerta: las 50 salen al mismo tiempo
    engine.openGate('canje')

def handleResponse(req, interesting):
    table.add(req)
```

**4) La técnica clave — el "gate" (compuerta):**
`engine.queue(..., gate='canje')` **no manda** las peticiones: las deja **cargadas y esperando**. Recién con `engine.openGate('canje')` **todas se liberan juntas**. Esto reduce al mínimo el jitter y maximiza la probabilidad de que las 50 caigan **dentro de la misma ventana TOCTOU**.

**5) Técnicas avanzadas para cerrar aún más la ventana** (vistas en el Módulo VII):

- **Last-Byte Synchronization:** Turbo Intruder manda **casi toda** cada petición (todo menos el último byte), las deja a todas esperando, y después manda el último byte de las 50 **de un saque**. Así el servidor recibe las 50 peticiones completas **en el mismo milisegundo**, neutralizando la diferencia de red.
- **Single-Packet Attack:** usando HTTP/2, se meten **las 50 peticiones en un solo paquete TCP**. Como llegan en el mismo paquete, el servidor las empieza a procesar **prácticamente a la vez** — es la forma más efectiva de eliminar el jitter de red.

**6) Leer los resultados.**
En la tabla de Turbo Intruder miramos los códigos de estado:

- Si **varias** peticiones (no una) devuelven `200 OK` con "descuento aplicado" → **la race condition funcionó**: el cupón de un solo uso se canjeó N veces.
- Confirmamos en la cuenta: el saldo/descuento acumulado es **mucho mayor** al que un solo canje debería dar.

### 🔍 Cómo verlo en el software

1. Capturás el canje legítimo en **Burp** y lo mandás a **Turbo Intruder** (o seleccionás la petición en Repeater → *Send group in parallel*).
2. Encolás 20–50 copias idénticas con la **misma `gate`** y las disparás juntas (o usás *Single-Packet Attack* en HTTP/2).
3. Mirás la columna de **status + longitud de respuesta** y el **estado real de la cuenta**.
   - **Señal que confirma el bug:** **más de una** petición responde "éxito / descuento aplicado" y el beneficio se **aplicó N veces** aunque el cupón era de un solo uso. Si el servidor acepta solo la primera y devuelve "ya utilizado" en todas las demás, está protegido.

---

## 4. Por qué el chequeo "normal" no alcanza

El `if cupon.usado == True` falla porque hace **tres operaciones separadas** sobre la base: **leer → evaluar → escribir**. Entre leer y escribir hay un hueco. Cuando 50 hilos corren en paralelo, el sistema operativo y el motor de base de datos los intercalan, y el orden real termina siendo:

```
Hilo 1: lee (usado=False)
Hilo 2: lee (usado=False)   ← todavía nadie escribió
Hilo 3: lee (usado=False)
...
Hilo 1: escribe (usado=True)  ← demasiado tarde, los demás ya pasaron el check
Hilo 2: escribe (usado=True)
...
```

El chequeo **no es atómico**: se puede partir en el medio. Y lo que no es atómico, en concurrencia, es explotable.

---

## 5. Cómo se defiende el desarrollador

La solución es **garantizar atomicidad**: que "leer el cupón, chequear que esté libre y marcarlo como usado" sea **una sola operación indivisible** que nadie pueda interrumpir. Opciones, de mejor a complementaria:

### 5.1 Hacer la operación atómica en la base de datos (la mejor)
Dejar que **la base de datos** resuelva el check y el update en **un solo statement condicionado**. En vez de leer-y-después-escribir, escribir con una condición y ver cuántas filas se modificaron:

```sql
UPDATE cupones
SET usado = TRUE, usado_por = :usuario
WHERE codigo = :codigo AND usado = FALSE;
```

La base garantiza que esto es atómico. **Solo la primera** petición encuentra `usado = FALSE` y modifica 1 fila; **las otras 49** encuentran `usado = TRUE` y modifican **0 filas**. En el código:

```python
filas = db.execute(UPDATE...)   # ExecuteUpdate condicionado
if filas == 0:
    return error("Cupón ya utilizado")   # perdió la carrera → rechazado
aplicar_descuento(usuario, valor)         # solo quien ganó llega acá
```

> Este es exactamente el patrón **"primero gana, 409 para el resto"** que usamos en Farmacia Tienda para las transiciones de estado de pedidos (`ExecuteUpdate` condicionado al estado origen): la condición viaja **dentro** del `UPDATE`, así dos peticiones nunca ganan las dos.

### 5.2 Bloqueo a nivel de base (locking)
- **Bloqueo pesimista:** `SELECT ... FOR UPDATE` bloquea la fila del cupón; las demás peticiones **esperan en fila** hasta que la primera termina y libera. Cuando les toca, ya ven `usado = TRUE`.
- **Bloqueo optimista:** una columna `version`; al guardar se chequea que la versión no cambió. Si otra petición la cambió primero, la segunda falla y se rechaza.

### 5.3 Restricción de unicidad (constraint)
Un índice único que haga **físicamente imposible** el estado inválido. Por ejemplo, una tabla `canjes` con índice único `(cupon_id, usuario_id)`: el segundo `INSERT` del mismo cupón para el mismo usuario **revienta con error de duplicado** y la base rechaza el canje repetido. La integridad la garantiza la base, no el código de aplicación.

### 5.4 Idempotencia + rate limiting (defensa en profundidad)
- **Clave de idempotencia:** cada canje lleva un identificador único; si llega repetido, se ignora.
- **Rate limiting:** limitar cuántos canjes por segundo acepta una cuenta/IP corta el disparo masivo de 50 peticiones de una.

---

## 6. Conclusión

Una **race condition** es una falla de **concurrencia**, no de sintaxis: el código se ve correcto leído de arriba hacia abajo, pero se rompe cuando muchas peticiones compiten por el mismo recurso en el mismo instante. El atacante explota la **ventana TOCTOU** —los microsegundos entre chequear y actualizar— y herramientas como **Turbo Intruder** (con *gate*, *last-byte sync* o *single-packet attack*) le permiten meter 50 peticiones dentro de esa ventana y canjear N veces un beneficio de un solo uso.

La defensa no es "chequear mejor", es **eliminar la ventana**: hacer que leer-chequear-escribir sea **una sola operación atómica**, garantizada por la base de datos mediante un `UPDATE` condicionado, un bloqueo o un índice único. En sistemas financieros o de inventario esto es crítico: un segundo de descuido en la concurrencia puede significar stock negativo, saldo regalado o dinero perdido.

---

*Fin del Objetivo 3 — Módulo VII.*
