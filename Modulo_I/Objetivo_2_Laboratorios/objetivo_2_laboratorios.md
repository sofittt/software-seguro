# Resolución del laboratorio – Ventas

## Objetivo

El objetivo del laboratorio fue analizar el endpoint de ventas para determinar cuántas solicitudes devolvían un código de estado **403 Forbidden**.

Para realizar la prueba se utilizó Python junto con la librería `requests`.

---

## 1. Análisis del endpoint

Se identificó que el endpoint permitía realizar consultas utilizando un parámetro `id`.

Por ejemplo:

```text
/ventas/?id=1
```

Al modificar el valor del `id`, el servidor podía devolver diferentes códigos HTTP.

Durante las pruebas, los principales códigos encontrados fueron:

- **403 Forbidden:** el recurso existe, pero el usuario no tiene autorización para acceder.
- **404 Not Found:** no existe una venta asociada a ese ID.

Por este motivo, se decidió automatizar la consulta de los diferentes IDs.

---

## 2. Automatización de las consultas

Se desarrolló un script en Python utilizando la librería `requests`.

La idea fue comenzar desde el ID `1` e incrementar el valor de uno en uno:

```python
id_venta = 1

while not_found_seguidos < 100:
    response = requests.get(
        URL,
        params={"id": id_venta},
        timeout=10
    )

    id_venta += 1
```

De esta manera no fue necesario establecer manualmente un rango máximo de IDs.

---

## 3. Conteo de respuestas Forbidden

Cada vez que el servidor devolvía un código:

```text
403 Forbidden
```

se incrementaba un contador:

```python
if response.status_code == 403:
    forbidden += 1
```

Esto permitió obtener la cantidad total de IDs que devolvían `403`.

---

## 4. Condición de finalización

Inicialmente no se conocía cuál era el último ID utilizado por la aplicación.

Por este motivo, en lugar de establecer un número máximo arbitrario, se decidió utilizar como condición de corte encontrar **100 respuestas `404 Not Found` consecutivas**.

Se creó la variable:

```python
not_found_seguidos = 0
```

Cuando se encontraba un `404`, el contador aumentaba:

```python
if response.status_code == 404:
    not_found_seguidos += 1
```

Si aparecía una respuesta diferente de `404`, la secuencia se consideraba interrumpida y el contador volvía a cero:

```python
else:
    not_found_seguidos = 0
```

El ciclo continuaba mientras no se hubieran encontrado 100 `404` consecutivos:

```python
while not_found_seguidos < 100:
```

Esto permitió recorrer los IDs existentes sin depender de un rango fijo.

---

## 5. Problema encontrado: Timeout

Durante la primera ejecución se detectaron errores como:

```text
Read timed out. (read timeout=5)
```

El problema era que, cuando ocurría un timeout, el script continuaba directamente con el siguiente ID.

Esto podía provocar que una respuesta `403` no fuera contabilizada.

En la primera ejecución se obtuvo:

```text
Total Forbidden: 1640
```

Sin embargo, se había producido al menos un timeout durante el recorrido, por lo que el resultado no podía considerarse completamente confiable.

---

## 6. Implementación de reintentos

Para solucionar el problema se modificó el script para que, ante un error de conexión o timeout, se volviera a consultar **el mismo ID hasta 3 veces**.

```python
MAX_REINTENTOS = 3

while reintentos < MAX_REINTENTOS and not respuesta_obtenida:

    try:
        response = requests.get(
            URL,
            params={"id": id_venta},
            timeout=10
        )

        respuesta_obtenida = True

    except requests.RequestException:
        reintentos += 1
        time.sleep(1)
```

Además:

- El timeout se aumentó de **5 a 10 segundos**.
- Se agregó una espera de **1 segundo** entre reintentos.
- Se agregó un contador para detectar IDs que no pudieran consultarse después de los tres intentos.

Esto evitó perder respuestas debido a problemas temporales de conexión.

---

## 7. Resultado final

Luego de ejecutar nuevamente el script con los reintentos implementados se obtuvo:

```text
🛑 100 Not Found consecutivos
Último ID analizado: 2692
Total Forbidden: 1641
IDs con error definitivo: 0
```

El resultado final fue:

**1641 respuestas `403 Forbidden`.**

La diferencia respecto de la primera ejecución fue de una respuesta:

```text
Primera ejecución: 1640
Segunda ejecución: 1641
```

Esto confirmó que el timeout de la primera prueba había provocado que un ID no fuera contabilizado correctamente.

Al finalizar la segunda ejecución se obtuvieron **0 IDs con error definitivo**, por lo que todas las solicitudes pudieron ser procesadas correctamente.

---

## 8. Código utilizado

```python
import requests
import time

URL = "URL_DEL_LABORATORIO"

id_venta = 1
forbidden = 0
not_found_seguidos = 0
errores = 0

MAX_NOT_FOUND = 100
MAX_REINTENTOS = 3

while not_found_seguidos < MAX_NOT_FOUND:

    reintentos = 0
    respuesta_obtenida = False

    while reintentos < MAX_REINTENTOS and not respuesta_obtenida:

        try:
            response = requests.get(
                URL,
                params={"id": id_venta},
                timeout=10
            )

            respuesta_obtenida = True

        except requests.RequestException as e:
            reintentos += 1

            print(
                f"Error en ID {id_venta} - "
                f"Reintento {reintentos}/{MAX_REINTENTOS}"
            )

            time.sleep(1)

    if not respuesta_obtenida:
        errores += 1
        not_found_seguidos = 0
        id_venta += 1
        continue

    if response.status_code == 404:

        not_found_seguidos += 1

        print(
            f"ID {id_venta}: Not Found "
            f"({not_found_seguidos}/{MAX_NOT_FOUND} consecutivos)"
        )

    else:

        not_found_seguidos = 0

        if response.status_code == 403:
            forbidden += 1

        else:
            print(f"ID INTERESANTE: {id_venta}")
            print(f"Status: {response.status_code}")
            print(f"Respuesta: {response.text[:1000]}")

    id_venta += 1

print("==============================")
print("100 Not Found consecutivos")
print(f"Último ID analizado: {id_venta - 1}")
print(f"Total Forbidden: {forbidden}")
print(f"IDs con error definitivo: {errores}")
print("==============================")
```

---

## Conclusión

Para resolver el laboratorio se automatizó la consulta secuencial de los IDs de ventas y se contabilizaron aquellas solicitudes que devolvían el código HTTP `403 Forbidden`.

Como no se conocía previamente el último ID existente, se utilizó como condición de finalización encontrar **100 respuestas `404 Not Found` consecutivas**.

Durante la primera ejecución se detectó que los errores de timeout podían alterar el resultado. Por este motivo se incorporó un mecanismo de reintentos que permitió consultar nuevamente el mismo ID ante errores temporales.

Finalmente, el script recorrió hasta el **ID 2692**, terminó al detectar **100 `404` consecutivos** y obtuvo un total de **1641 respuestas `403 Forbidden`**, sin registrar errores definitivos de conexión.


# Informe de resolución – Laboratorio Presupuesto

## 1. Objetivo

El objetivo del laboratorio fue analizar el funcionamiento de la aplicación **Presupuesto**, identificar cómo se procesaban los datos enviados al servidor y modificar los valores necesarios para cumplir con las condiciones establecidas por el desafío.

Para resolverlo se utilizaron las herramientas de desarrollador del navegador, principalmente la pestaña **Network**, desde donde fue posible analizar las solicitudes realizadas por la aplicación y los datos intercambiados con el Backend.

---

## 2. Análisis inicial

En primer lugar, se accedió a la aplicación y se analizaron los registros disponibles en el presupuesto.

Luego se abrieron las herramientas de desarrollador del navegador mediante `F12` y se ingresó a la pestaña **Network**.

Desde allí se observaron las solicitudes realizadas por la aplicación, analizando principalmente:

- Método HTTP utilizado.
- Endpoint de la API.
- Request enviado.
- Body de la petición.
- Response del servidor.
- Identificadores de los registros.
- Valores correspondientes a cada gasto.
- Estado del campo `revisado`.

El análisis permitió determinar que los valores enviados hacia el Backend podían ser modificados desde el cliente.

---

## 3. Condiciones del desafío

Para completar correctamente el laboratorio era necesario modificar los datos del presupuesto hasta conseguir que se cumplieran simultáneamente las condiciones solicitadas.

No era suficiente modificar valores al azar, ya que los cambios debían permitir alcanzar los promedios, valores mínimos y máximos requeridos por el ejercicio.

Por este motivo, antes de realizar las modificaciones se analizaron los valores existentes y se calcularon los cambios necesarios.

---

## 4. Gastos modificados

Luego de analizar los datos, se determinó que solamente era necesario modificar cuatro registros.

| ID | Concepto | Valor original | Valor modificado |
|---:|---|---:|---:|
| 2 | Alquiler local | $10.000 | $13.000 |
| 7 | Marketing | $10.000 | $12.000 |
| 1 | Flete mercadería | $6.000 | $1.000 |
| 11 | Seguros | $5.000 | $500 |

El resto de los registros se mantuvieron con sus valores originales.

---

## 5. ¿Por qué se modificaron esos valores?

Los valores no se eligieron de forma aleatoria. Se modificaron específicamente estos cuatro registros para conseguir que todas las condiciones matemáticas del desafío se cumplieran simultáneamente.

### Alquiler local

Se modificó:

`$10.000 → $13.000`

Este cambio permitió ajustar el total correspondiente a los gastos clasificados como **esenciales**.

Luego de realizar las modificaciones, se obtuvo:

`$65.500 / 4 = $16.375`

Por lo tanto, el promedio de los gastos esenciales quedó en **$16.375**.

### Marketing

Se modificó:

`$10.000 → $12.000`

Este cambio contribuyó a ajustar los valores correspondientes a la categoría **varios**.

El resultado obtenido fue:

`$36.000 / 6 = $6.000`

De esta manera, el promedio de la categoría varios quedó exactamente en **$6.000**.

### Flete mercadería

Se modificó:

`$6.000 → $1.000`

Este valor se redujo para poder ajustar el total general del presupuesto sin alterar el valor mínimo requerido por el desafío.

### Seguros

Se modificó:

`$5.000 → $500`

Además de contribuir al ajuste del total general, esta modificación permitió establecer el **valor mínimo del presupuesto en $500**.

---

## 6. Verificación de los resultados

Después de realizar las modificaciones se verificaron nuevamente todas las condiciones.

Los resultados finales fueron:

| Condición | Resultado |
|---|---:|
| Promedio gastos esenciales | $16.375 |
| Promedio categoría varios | $6.000 |
| Promedio general | $8.000 |
| Valor mínimo | $500 |
| Valor máximo | $50.000 |

Para el promedio general se obtuvo:

`$104.000 / 13 = $8.000`

Por lo tanto, los cambios realizados permitieron cumplir simultáneamente con todas las condiciones solicitadas por el laboratorio.

---

## 7. Parte práctica – Modificación de las solicitudes

Una vez determinados los valores que debían modificarse, se procedió a realizar la explotación desde el navegador.

### Paso 1 – Abrir las herramientas de desarrollador

Se presionó `F12` para abrir las herramientas de desarrollador del navegador.

Luego se seleccionó:

`Network`

Esto permitió observar las solicitudes HTTP/HTTPS realizadas entre el Frontend y el Backend.

### Paso 2 – Identificar la solicitud

Se realizó una acción desde la aplicación para generar una petición hacia el servidor.

Dentro de **Network** se identificó la solicitud correspondiente y se analizaron sus diferentes componentes:

- Headers
- Request
- Response

Esto permitió observar la estructura de los datos enviados al Backend.

### Paso 3 – Identificar los registros

A partir de la información obtenida se localizaron los identificadores correspondientes a los registros que necesitábamos modificar:

- ID 1 → Flete mercadería
- ID 2 → Alquiler local
- ID 7 → Marketing
- ID 11 → Seguros

Conociendo los IDs fue posible determinar exactamente qué registros debían ser modificados.

### Paso 4 – Modificar los valores

Se modificaron los valores enviados al servidor utilizando los valores previamente calculados:

- Alquiler local: `$13.000`
- Marketing: `$12.000`
- Flete mercadería: `$1.000`
- Seguros: `$500`

Los demás registros conservaron sus valores originales.

### Paso 5 – Marcar los registros como revisados

Además de modificar los valores correspondientes, se estableció el campo:

`revisado: true`

en los registros requeridos por el ejercicio.

Esto permitió indicar al sistema que los registros habían sido revisados.

### Paso 6 – Enviar las solicitudes

Una vez modificados los parámetros se enviaron nuevamente las solicitudes al Backend.

El servidor procesó los datos enviados y almacenó los nuevos valores.

### Paso 7 – Verificar el resultado

Finalmente, se volvió a consultar la información del presupuesto y se verificó que los valores hubieran sido modificados correctamente.

Se comprobaron nuevamente los cálculos:

**Esenciales**

`65.500 / 4 = 16.375`

**Varios**

`36.000 / 6 = 6.000`

**Promedio general**

`104.000 / 13 = 8.000`

**Valor mínimo**

`500`

**Valor máximo**

`50.000`

Al cumplirse todas las condiciones simultáneamente, el laboratorio quedó resuelto correctamente.

---

## 8. Vulnerabilidad identificada

Durante el laboratorio se observó que la aplicación permitía manipular información enviada desde el cliente antes de que fuera procesada por el servidor.

Este comportamiento está relacionado con una vulnerabilidad de **manipulación de parámetros (Parameter Tampering)** y con una validación insuficiente de los datos recibidos por el Backend.

Un usuario no debería poder modificar valores sensibles simplemente alterando una petición enviada desde el navegador.

---

## 9. Mitigación

Para reducir este riesgo, el Backend debería considerar todos los datos provenientes del cliente como información no confiable.

Entre las principales medidas de mitigación se encuentran:

- Validar los valores recibidos del cliente.
- Aplicar las reglas de negocio en el Backend.
- Verificar los permisos del usuario antes de permitir una modificación.
- No confiar únicamente en controles implementados en el Frontend.
- Validar rangos y tipos de datos.
- Recalcular del lado del servidor cualquier valor sensible.
- Rechazar solicitudes que contengan valores no permitidos.

---

## 10. Conclusión

El laboratorio permitió comprobar de forma práctica que los datos enviados por una aplicación web pueden ser inspeccionados y, dependiendo de la implementación, modificados desde el cliente.

También permitió observar que **HTTPS no evita este tipo de vulnerabilidad**. HTTPS protege la información durante su transmisión entre el cliente y el servidor, pero no impide que el propio usuario modifique los datos antes de enviarlos.

Por este motivo, las aplicaciones web no deben confiar en la información recibida desde el Frontend. Las validaciones críticas, controles de autorización y reglas de negocio deben implementarse principalmente del lado del Backend.


# Resolución del laboratorio – Turnero

## Objetivo

El objetivo del ejercicio era **identificar y eliminar todos los turnos reservados por el usuario `xdalvik`**, sin afectar los turnos pertenecientes al resto de los usuarios.

## Pasos realizados

### 1. Identificación del rango de búsqueda

Como ayuda para resolver el laboratorio, se informó en el grupo que los turnos correspondientes al usuario `xdalvik` se encontraban aproximadamente entre los IDs **90 y 105**.

A partir de esta información, se decidió revisar los turnos dentro de ese rango.

### 2. Consulta de los turnos mediante GET

Se utilizó el endpoint de turnos realizando peticiones HTTP `GET` para consultar los IDs comprendidos entre **90 y 105**.

```http
GET /api/1/appointments/90
GET /api/1/appointments/91
GET /api/1/appointments/92
...
GET /api/1/appointments/105
```

Para cada respuesta se verificó principalmente el campo `user`, con el objetivo de encontrar aquellos turnos que pertenecieran a:

```json
{
  "user": "xdalvik"
}
```

También se tuvo en cuenta el campo `id`, ya que posteriormente sería necesario para realizar la eliminación del turno.

### 3. Identificación de los turnos de `xdalvik`

Al recorrer los IDs comprendidos entre **90 y 105**, se encontraron las respuestas correspondientes al usuario `xdalvik`.

Una vez identificados, se anotaron únicamente los `id` de sus turnos.

Esto fue importante para evitar eliminar accidentalmente turnos pertenecientes a otros usuarios.

### 4. Eliminación de los turnos mediante DELETE

Una vez obtenidos los IDs correspondientes a los turnos de `xdalvik`, se realizó una petición HTTP `DELETE` para cada uno.

```http
DELETE /api/1/appointments/{id}
```

Donde `{id}` fue reemplazado por cada uno de los IDs que previamente se había confirmado que pertenecían a `xdalvik`.

### 5. Verificación final

Finalmente, se volvieron a realizar consultas mediante `GET` para verificar que los turnos correspondientes a `xdalvik` habían sido eliminados correctamente y que los turnos pertenecientes al resto de los usuarios no habían sido afectados.

## Resultado

La secuencia utilizada para resolver el ejercicio fue:

```text
Ayuda: IDs entre 90 y 105
        ↓
GET de cada appointment
        ↓
Verificar el campo "user"
        ↓
Encontrar los turnos de "xdalvik"
        ↓
Guardar los IDs correspondientes
        ↓
DELETE de cada uno de esos IDs
        ↓
Verificar el resultado
```

De esta manera se lograron eliminar **únicamente los turnos correspondientes al usuario `xdalvik`**, sin afectar los turnos del resto de los usuarios.

## Conclusión

El ejercicio permitió comprobar la importancia de **identificar correctamente el propietario de un recurso antes de realizar una operación de eliminación**.

Primero se utilizaron peticiones `GET` para localizar los turnos de `xdalvik` y, una vez confirmados sus IDs, se realizaron las peticiones `DELETE` correspondientes.


# Resolución del laboratorio – La Gran Rifa

## Objetivo

El objetivo del ejercicio era ayudar al usuario **John Backus**, quien se había anotado para comprar un número de la rifa pero todavía figuraba como que no había realizado el pago.

Las credenciales proporcionadas para acceder al sistema fueron:

```text
Usuario: guido
Clave: RIFA_2019
```

El objetivo fue identificar el número correspondiente a **John Backus** y analizar la petición utilizada por la aplicación para modificar su estado de pago.

---

## Pasos realizados

### 1. Ingreso al sistema

Primero se ingresó al sistema de **La Gran Rifa** utilizando las credenciales proporcionadas por el ejercicio.

```text
Usuario: guido
Clave: RIFA_2019
```

Una vez dentro de la aplicación, se revisaron las funcionalidades disponibles y las peticiones realizadas por el sistema.

---

### 2. Consulta de los números de la rifa

Se identificó el endpoint utilizado por la aplicación para obtener el listado de números:

```http
GET /api/numeros/
```

Al realizar la petición `GET`, el servidor devolvió la información de los números de la rifa junto con los usuarios asociados y su estado.

---

### 3. Identificación de John Backus

Se revisó la respuesta obtenida del endpoint `/api/numeros/` hasta encontrar el registro correspondiente a:

```text
John Backus
```

Dentro de la información del registro se identificó que su `id` era:

```text
id = 4
```

También se observó que el número todavía figuraba como **no pagado**.

---

### 4. Análisis del botón Editar

Una vez identificado el registro de John Backus, se analizó qué petición realizaba la aplicación al utilizar el botón **Editar**.

Para esto se observó la petición HTTP generada por el sistema y el endpoint utilizado para modificar la información del registro.

Esto permitió identificar qué datos enviaba el frontend al backend cuando se actualizaba un número de la rifa.

---

### 5. Modificación del estado de pago

Al analizar la petición se identificó el campo encargado de indicar si el número estaba pago.

El valor original indicaba que el pago todavía no había sido realizado.

Se modificó dicho valor a:

```json
{
  "esta_pago": true
}
```

La petición se realizó específicamente sobre el registro identificado anteriormente:

```text
id = 4
```

De esta manera, la modificación se aplicó solamente al número correspondiente a **John Backus**.

---

### 6. Envío de la petición

Luego de modificar el campo `esta_pago`, se envió nuevamente la petición utilizada por el botón **Editar**.

El servidor aceptó la modificación y actualizó el estado del registro.

---

### 7. Verificación

Finalmente, se volvió a consultar:

```http
GET /api/numeros/
```

Se buscó nuevamente el registro con:

```text
id = 4
```

y se verificó que el número correspondiente a **John Backus** ahora figurara con el estado de pago actualizado.

---

## Resumen del procedimiento

```text
Ingresar al sistema con las credenciales
                ↓
Consultar GET /api/numeros/
                ↓
Buscar a "John Backus"
                ↓
Identificar su registro
                ↓
ID = 4
                ↓
Analizar la petición del botón "Editar"
                ↓
Modificar "esta_pago" a true
                ↓
Enviar la petición
                ↓
Consultar nuevamente /api/numeros/
                ↓
Verificar el cambio
```

---

## Resultado

Se logró identificar que el registro correspondiente a **John Backus** tenía el `id = 4`.

Posteriormente, analizando la petición que realizaba el botón **Editar**, se modificó el campo:

```text
esta_pago = true
```

Finalmente, se verificó mediante una nueva consulta que el cambio se hubiera aplicado correctamente.

---

## Conclusión

Este laboratorio permitió observar cómo una aplicación web utiliza peticiones HTTP para consultar y modificar información almacenada en el servidor.

También permitió comprobar la importancia de que el **backend valide correctamente qué campos puede modificar cada usuario**, ya que no se debe confiar únicamente en las restricciones implementadas desde la interfaz gráfica o frontend.
