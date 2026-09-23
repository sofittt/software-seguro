# Laboratorio – Apagar IA

## Enunciado

El objetivo del ejercicio consistía en encontrar el código necesario para resolver el desafío **Apagar IA**.

Para resolverlo fue necesario analizar el funcionamiento del endpoint disponible, identificar cómo se generaban los códigos utilizados en las consultas y automatizar el proceso hasta encontrar el valor correcto.

---

## Pasos realizados

### 1. Análisis del endpoint

Primero se analizó el siguiente endpoint:

```text
/codes/
```

Al realizar diferentes pruebas se observó que era posible consultar códigos agregando un valor al final de la URL:

```text
/codes/{codigo}/
```

Se identificó que el código utilizado en la URL estaba representado mediante un **hash MD5**.

Por lo tanto, para realizar las pruebas era necesario convertir primero cada número a MD5.

---

### 2. Generación de los códigos MD5

Para automatizar este proceso se utilizó Python junto con la librería `hashlib`.

Se creó la siguiente función:

```python
import hashlib

def hash_md5(numero):
    return hashlib.md5(
        str(numero).encode("utf-8")
    ).hexdigest()
```

Esta función recibe un número, lo convierte a texto y posteriormente genera su correspondiente hash MD5.

---

### 3. Automatización de las consultas

Una vez obtenidos los hashes, se utilizó la librería `requests` para realizar automáticamente las peticiones `GET`.

El procedimiento realizado para cada número fue:

1. Tomar el número.
2. Convertirlo a MD5.
3. Agregar el MD5 al endpoint `/codes/`.
4. Realizar una petición `GET`.
5. Verificar el código de estado HTTP obtenido.
6. Analizar el contenido de las respuestas exitosas.

Inicialmente se probaron rangos amplios de números para determinar dónde podían encontrarse respuestas relevantes.

---

### 4. Mejora del tiempo de búsqueda

Como realizar las consultas de manera secuencial demoraba demasiado, se utilizó:

```python
ThreadPoolExecutor
```

Esto permitió realizar varias peticiones de manera concurrente.

Se configuró:

```python
MAX_WORKERS = 10
```

De esta manera se podían procesar hasta 10 consultas concurrentemente, reduciendo considerablemente el tiempo necesario para recorrer los diferentes valores.

También se agregó al script información sobre el progreso de ejecución, mostrando:

* Cantidad de consultas procesadas.
* Porcentaje completado.
* Requests por segundo.
* Tiempo transcurrido.
* Tiempo restante estimado.
* Cantidad de respuestas encontradas.
* Cantidad de errores.

---

### 5. Identificación del rango

Luego de realizar las primeras pruebas se detectó que las respuestas de interés se encontraban dentro del rango:

```text
9000 - 12000
```

Por este motivo se modificó el script para analizar específicamente:

```python
INICIO = 9000
FIN = 12000
```

Esto permitió reducir la cantidad de consultas y concentrar la búsqueda en el rango donde se habían encontrado resultados.

---

### 6. Análisis de las respuestas

El siguiente paso fue analizar el contenido de cada respuesta exitosa.

Para esto se modificó la función de consulta para recuperar también:

```python
response.text
```

Dentro de las respuestas se buscó un número compuesto por **16 dígitos**, ya que este correspondía al valor necesario para continuar con el ejercicio.

Para automatizar su detección se utilizó una expresión regular:

```python
import re

numeros_16 = re.findall(
    r'(?<!\d)\d{16}(?!\d)',
    contenido
)
```

De esta manera el programa analizaba automáticamente las respuestas y mostraba cualquier valor formado exactamente por 16 dígitos.

---

## Resultado obtenido

Luego de recorrer y analizar las respuestas se encontró el siguiente código:

```text
5524663362514956
```

Posteriormente se convirtió este valor a MD5 utilizando:

```python
hashlib.md5(
    "5524663362514956".encode("utf-8")
).hexdigest()
```

El MD5 obtenido fue:

```text
a8e0e8ff02dde0f62fdf4de5142d7de0
```

Finalmente se utilizó el valor obtenido para completar la validación del laboratorio.

El resultado fue **correcto**, permitiendo completar exitosamente el ejercicio.

---

## Conclusión

Para resolver el laboratorio primero se analizó el funcionamiento del endpoint `/codes/` y se identificó que los valores utilizados estaban representados mediante MD5.

Luego se desarrolló un script en Python para generar automáticamente los hashes y realizar las peticiones HTTP. Para reducir el tiempo de ejecución se utilizaron consultas concurrentes mediante `ThreadPoolExecutor`.

Después de las primeras pruebas se logró reducir la búsqueda al rango comprendido entre `9000` y `12000`.

Finalmente, se analizaron automáticamente las respuestas utilizando una expresión regular para buscar un número de 16 dígitos. De esta manera se encontró el código `5524663362514956`, se calculó su correspondiente MD5 y se utilizó para completar correctamente el laboratorio.

Con este ejercicio se pusieron en práctica conceptos relacionados con **peticiones HTTP, códigos de estado, automatización con Python, hashes MD5, concurrencia y expresiones regulares**.
