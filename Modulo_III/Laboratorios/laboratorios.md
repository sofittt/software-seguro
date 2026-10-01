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


# Laboratorio – El Mejor Secreto

## Enunciado

El objetivo del laboratorio consiste en encontrar la contraseña de un archivo ZIP protegido.

Como pista se cuenta con una secuencia de pulsaciones realizadas sobre cinco símbolos diferentes. A partir de la observación del patrón se identificó la siguiente secuencia de **12 pulsaciones**:

```text
ABCCDADDDDEC
```

Donde cada letra representa un símbolo:

- **A:** Carita
- **B:** Círculo
- **C:** Triángulo
- **D:** Corazón
- **E:** Flor

El problema es que se conoce el orden en el que fueron pulsados los símbolos, pero no qué número del `0` al `9` representa cada uno.

---

## Análisis

Primero se identificó el patrón de pulsaciones:

```text
ABCCDADDDDEC
```

El patrón contiene cinco símbolos diferentes:

```text
A, B, C, D, E
```

Se tomó como hipótesis que cada símbolo representa un número diferente entre `0` y `9`.

Por ejemplo, una posible combinación podría ser:

```text
A = 1
B = 2
C = 3
D = 4
E = 5
```

Con esa combinación, el patrón:

```text
ABCCDADDDDEC
```

se convertiría en:

```text
123341444453
```

Como no se conoce qué número corresponde a cada símbolo, se decidió automatizar la prueba de todas las combinaciones posibles utilizando Python.

Al tener cinco símbolos y diez números disponibles, sin repetir el mismo número para símbolos diferentes, existen:

```text
10 × 9 × 8 × 7 × 6 = 30.240 combinaciones
```

---

## Procedimiento

### 1. Identificación del patrón

A partir de las pulsaciones observadas se obtuvo el siguiente patrón:

```text
ABCCDADDDDEC
```

Este patrón se definió directamente en el script:

```python
PATRON = "ABCCDADDDDEC"
```

También se definieron los posibles números:

```python
DIGITOS = "0123456789"
```

---

### 2. Generación de combinaciones

Para generar las diferentes asignaciones posibles entre las figuras y los números se utilizó `itertools.permutations()`.

```python
for permutacion in itertools.permutations(
    DIGITOS,
    len(simbolos)
):
```

En cada vuelta del ciclo se genera una correspondencia diferente.

Por ejemplo:

```text
A = 5
B = 4
C = 7
D = 9
E = 3
```

Después se reemplaza cada letra del patrón por el número correspondiente:

```python
password = "".join(
    mapa[letra]
    for letra in PATRON
)
```

De esta manera, cada combinación genera automáticamente una contraseña de 12 dígitos.

---

### 3. Prueba de la contraseña

Para comprobar si cada contraseña generada era correcta se utilizó **7-Zip** desde Python.

El script ejecuta el siguiente comando mediante `subprocess`:

```python
resultado = subprocess.run(
    [
        SEVEN_ZIP,
        "t",
        ZIP,
        f"-p{password}",
        "-y"
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
```

La opción `t` de 7-Zip permite probar el archivo sin necesidad de extraerlo.

Si la contraseña es incorrecta, el programa continúa automáticamente con la siguiente combinación.

Si el resultado de 7-Zip es:

```python
resultado.returncode == 0
```

significa que el archivo pudo ser comprobado correctamente y, por lo tanto, se encontró la contraseña.

---

### 4. Seguimiento del proceso

También se agregó información en pantalla para poder controlar el avance de la búsqueda.

Durante la ejecución se obtuvo, por ejemplo:

```text
⏳ 16,700/30,240 (55.2%) | ⚡ 17.8 claves/s | Última: 547765666617
```

Esto permite visualizar:

- Cantidad de claves probadas.
- Total de combinaciones posibles.
- Porcentaje completado.
- Velocidad de prueba.
- Última contraseña analizada.

---

## Código utilizado

```python
import itertools
import subprocess
import time
import os

ZIP = r"C:\Users\sofialourdes_toledoc\Downloads\secreto.zip"
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"

PATRON = "ABCCDADDDDEC"
DIGITOS = "0123456789"

if not os.path.exists(ZIP):
    print("No se encontró el ZIP")
    exit()

if not os.path.exists(SEVEN_ZIP):
    print("No se encontró 7-Zip")
    exit()

simbolos = sorted(set(PATRON))

inicio = time.time()
probadas = 0

for permutacion in itertools.permutations(
    DIGITOS,
    len(simbolos)
):

    mapa = dict(zip(simbolos, permutacion))

    password = "".join(
        mapa[letra]
        for letra in PATRON
    )

    probadas += 1

    resultado = subprocess.run(
        [
            SEVEN_ZIP,
            "t",
            ZIP,
            f"-p{password}",
            "-y"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if resultado.returncode == 0:

        print("¡Contraseña encontrada!")
        print("Password:", password)
        print("Correspondencia:", mapa)

        break

tiempo_total = time.time() - inicio

print("Claves probadas:", probadas)
print("Tiempo:", tiempo_total / 60, "minutos")
```

---

## Resultado

Luego de ejecutar el script se obtuvo:

```text
==================================================
🎯 ¡CONTRASEÑA ENCONTRADA!
==================================================

🔑 Password: 547795999937

🔢 Correspondencia:
carita (A) = 5
círculo (B) = 4
triángulo (C) = 7
corazón (D) = 9
flor (E) = 3
```

Por lo tanto, la correspondencia correcta fue:

| Letra | Símbolo | Número |
|---|---|---:|
| A | Carita | 5 |
| B | Círculo | 4 |
| C | Triángulo | 7 |
| D | Corazón | 9 |
| E | Flor | 3 |

Aplicando estos valores al patrón original:

```text
A B C C D A D D D D E C
5 4 7 7 9 5 9 9 9 9 3 7
```

se obtiene finalmente la contraseña:

```text
547795999937
```

---

## Estadísticas

La ejecución final arrojó los siguientes resultados:

```text
Claves probadas: 16.714
Tiempo: 941.23 segundos
Tiempo: 15.69 minutos
```

De un máximo de **30.240 combinaciones**, fue necesario probar **16.714** hasta encontrar la correcta.

---

## Conclusión

Para resolver el ejercicio primero se identificó el patrón de las 12 pulsaciones:

```text
ABCCDADDDDEC
```

Luego se desarrolló un script en Python que genera las posibles correspondencias entre las cinco figuras y los números del `0` al `9`.

Cada contraseña generada se prueba automáticamente contra el archivo ZIP utilizando 7-Zip, evitando tener que realizar las pruebas manualmente.

Finalmente, después de **16.714 intentos** y aproximadamente **15,69 minutos**, se encontró la contraseña correcta:

```text
547795999937
```

La resolución del laboratorio permitió aplicar generación de permutaciones, automatización mediante Python y ejecución de comandos externos para reducir un problema de prueba manual a un proceso automatizado.
