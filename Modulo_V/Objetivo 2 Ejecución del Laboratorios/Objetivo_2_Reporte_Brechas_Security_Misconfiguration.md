# Módulo V — Objetivo 2: Ejecución del Laboratorio

## Reporte y Brechas: Errores de Configuración (Security Misconfiguration)

> **Nota sobre la modalidad.** Este reporte documenta la **metodología**, el **análisis de la brecha** y el **resultado** del laboratorio "Asistencia", resuelto de forma individual. El procedimiento se desarrolla paso a paso para que sea reproducible y auditable.

---

## 1. Enunciado

Se dispone de una aplicación web de verificación de asistencia con esta interfaz:

- Campo **Código (3 dígitos)** (`name="codigo"`, `pattern="[0-9]{3}"`)
- Campo **Clave** (`name="clave"`, tipo password)
- Botón **Verificar** → `POST index.php`

La consigna pide **averiguar cuántos asistentes hay sin disponer de la clave** de consulta, sabiendo que **los asistentes no superan los 200**. Una vez obtenida la cantidad, se genera el **MD5** de ese número y ese valor es el código ganador.

URL del entorno (challenge del curso):

```text
https://chl-<id>-asistencia.softwareseguro.com.ar/
```

---

## 2. Reconocimiento del objetivo

Analizando la petición de verificación con las herramientas de desarrollador del navegador (**DevTools → Network**) y/o un proxy interceptor, se obtiene:

| Dato | Valor |
|---|---|
| Endpoint | `POST /index.php` |
| Content-Type | `application/x-www-form-urlencoded` |
| Cuerpo | `codigo=NNN&clave=XXXX` (23 bytes de ejemplo) |
| Backend | `x-powered-by: PHP/8.0.30` |
| Respuesta | `200 OK`, `text/html` |
| Infra | Cloudflare delante (headers `cf-ray`, `cdn-cgi/rum`) |

> **Ruido a descartar:** la petición `POST /cdn-cgi/rum` (status `204`) es telemetría RUM de Cloudflare; no tiene relación con la verificación.

### Respuesta ante clave incorrecta

Para cualquier código con una clave inválida, el servidor devuelve **el mismo HTML**, que incluye el bloque:

```html
<div class="note" style="color: red; font-size: 20px">
    No se puede acceder a esta información
</div>
```

El contenido de la respuesta es **idéntico** se trate de un código válido o inexistente. Por lo tanto, **el cuerpo de la respuesta NO sirve como discriminador**: no hay diferencia de mensaje ni de longitud útil entre un código que corresponde a un asistente y uno que no.

---

## 3. Clasificación de la brecha

| Aspecto | Detalle |
|---|---|
| Categoría OWASP | **A05:2021 – Security Misconfiguration** (divulgación de información por comportamiento observable) |
| Debilidad asociada (CWE) | **CWE-208** (Observable Timing Discrepancy), **CWE-203** (Observable Discrepancy), **CWE-200** (Exposure of Sensitive Information) |
| Mecanismo | **Canal lateral de temporización**: el tiempo de respuesta revela si un código corresponde a un asistente, aunque la clave sea incorrecta. |
| Impacto | Permite **enumerar** el universo de códigos válidos sin la clave y, con ello, **inferir la cantidad total de asistentes** (dato que debería requerir autenticación). |

El núcleo del problema no es "adivinar la clave", sino que la aplicación **procesa de forma distinta** un código válido frente a uno inexistente, y esa diferencia es **medible desde afuera por el tiempo de respuesta**.

---

## 4. Razonamiento (cómo el enunciado acota el ataque)

Dos datos de la consigna definen la superficie de prueba:

1. **Código de 3 dígitos** → espacio de valores `000`–`999`.
2. **Los asistentes no superan 200** → el rango relevante es **`000`–`199`** (200 valores).

Si cada asistente se corresponde con un código válido:

```text
cantidad de códigos válidos  ==  cantidad de asistentes
```

El objetivo se reduce a **contar** cuántos de esos 200 códigos la aplicación reconoce como válidos, usando el canal lateral de temporización como criterio.

---

## 5. Explicación técnica del canal lateral

El comportamiento observado del backend PHP es, conceptualmente:

```text
si el codigo NO existe:
    responde de inmediato  "No se puede acceder a esta información"   (~95 ms)

si el codigo SÍ existe (asistente):
    ejecuta la verificación costosa de la clave
    (hash tipo bcrypt / consulta a base de datos / comparación cara)
    la clave es incorrecta -> igual responde "No se puede acceder..."  (~1000 ms)
```

El mensaje final es el mismo, pero el **trabajo que hace el servidor** no: solo gasta tiempo en verificar la clave cuando el código es real. Ese tiempo extra es lo que se filtra. Es el mismo principio por el que una comparación de contraseñas mal diseñada permite distinguir usuarios existentes de inexistentes por la demora.

---

## 6. Metodología de la prueba (enumeración por timing)

### 6.1. Preparación

Se envía una verificación real (`codigo=123&clave=xxxx`) a **Burp Suite → Intruder**:

- **Attack type:** Sniper.
- **Positions:** marcar únicamente el valor del código → `codigo=§123§&clave=xxxx` (la clave queda fija e inválida).
- **Payloads:** tipo *Numbers*, rango `0`–`199`, paso `1`, con **mínimo 3 dígitos** (`000`, `001`, … `199`). El formato de 3 dígitos es obligatorio: el `pattern="[0-9]{3}"` rechaza valores sin ceros a la izquierda.

### 6.2. Captura de la señal

En los resultados del ataque, la columna relevante es el **tiempo de respuesta** (*Response received*, en ms), **no** la de `Length` (que es casi constante porque el HTML no cambia).

Se observan dos poblaciones claramente separadas:

| Población | Tiempo aproximado | Interpretación |
|---|---|---|
| Mayoría de los códigos | **~90–110 ms** | Código inexistente (corte inmediato) |
| Subconjunto minoritario | **~900–1300 ms** | Código de asistente válido (verifica la clave) |

### 6.3. Conteo y validación

1. Ordenar los resultados por la columna de **tiempo** en forma descendente: aparece un **salto neto** entre el bloque de ~1 s y el de ~100 ms.
2. **Descartar falsos positivos por jitter de red.** Las muestras intermedias (p. ej. ~130–400 ms) suelen ser ruido, no válidos. Se reenvían 2–3 veces (Repeater) o se re-corre el ataque:
   - un **válido** se mantiene consistentemente en ~1 s;
   - un **falso** vuelve a ~95 ms.
3. La cantidad de códigos que permanecen en ~1 s es la **cantidad de asistentes**.

> **Rigor en ataques de timing:** nunca concluir con una sola muestra. Un pico aislado puede ser la red. Lo que confirma un válido es que **repite** la demora.

### 6.4. Obtención del código ganador

```text
md5( "<cantidad de asistentes>" )  →  código ganador
```

(El conteo final y el cálculo del MD5 quedan a cargo de la persona que resuelve.)

---

## 7. Evidencia a documentar

Para el informe de entrega conviene registrar, con capturas:

- La petición `POST /index.php` con su payload (`codigo`, `clave`).
- La respuesta ante clave inválida mostrando el mensaje rojo idéntico para códigos distintos (prueba de que el **cuerpo no discrimina**).
- La tabla de **Intruder ordenada por tiempo**, resaltando las dos poblaciones (~100 ms vs ~1 s).
- La **re-ejecución** de los códigos candidatos confirmando que los válidos repiten la demora.
- El **MD5** resultante aceptado por la aplicación.

---

## 8. Resultado obtenido

Barriendo el **espacio completo `000`–`999`** y aplicando el criterio de temporización (dos fases: barrido + confirmación por mediana de 5 muestras), se identificaron los códigos válidos.

### 8.1. Hallazgo clave: los códigos NO son secuenciales

Un barrido limitado a `000`–`199` habría sido **incorrecto**. Los códigos de asistente están **dispersos por todo el rango** `000`–`999` (hay válidos en `205`, `447`, `683`, `997`, etc.). El dato "no superan los 200" acota la **cantidad**, no el **rango de valores**; asumir lo contrario deja afuera la mayoría de los asistentes.

### 8.2. Cantidad de asistentes

- **Códigos válidos confirmados: 159** (todos con mediana de respuesta ~940–1300 ms, frente a ~95 ms de los inexistentes).
- 159 ≤ 200 → consistente con la cota del enunciado.

### 8.3. Validación del resultado

| Verificación | Resultado |
|---|---|
| Coincidencia Burp ↔ script en `000`–`199` | Los mismos 20 códigos en ambas herramientas |
| Falsos positivos por jitter (`064`, `097`, `136`, `186`) | Descartados: no repiten la demora |
| Separación de poblaciones | Bimodal limpia: ~95 ms vs ~1 s, sin valores intermedios |
| Re-test en Repeater de códigos válidos vs inexistentes | Confirmado |

### 8.4. Código ganador

El código ganador se obtiene como:

```text
md5( "159" )  →  código ganador  (aceptado por la plataforma)
```

---

## 9. Análisis del impacto

- **Confidencialidad:** se expone un dato agregado (cantidad de asistentes) protegido tras una clave; la misma técnica revela **qué códigos existen**, habilitando ataques dirigidos posteriores (p. ej. fuerza bruta de clave solo sobre códigos reales).
- **Integridad / Disponibilidad:** no se ven afectadas directamente, pero la enumeración es la **fase de reconocimiento** que habilita abusos mayores.
- **Severidad:** en el laboratorio el impacto demostrado es **divulgación de información** (bajo-medio). El patrón subyacente (enumeración por canal lateral) es el que, en producción, suele escalar a **enumeración de usuarios** y **ataques de credenciales** más eficientes.

---

## 10. Mitigación

El objetivo es que la aplicación sea **indistinguible** entre código válido e inválido ante una consulta no autenticada:

1. **Tiempo de respuesta constante.** Ejecutar siempre el mismo trabajo (verificar un hash *dummy* cuando el código no existe) para que válidos e inexistentes tarden lo mismo. Es la mitigación central para CWE-208.
2. **Respuestas uniformes.** Ante código o clave incorrectos, devolver el mismo mensaje y el mismo código de estado, sin delatar cuál de los dos falló (ya se cumple en el cuerpo; falta en el tiempo).
3. **Autenticación/autorización previa a la consulta.** Exigir una sesión válida antes de evaluar la existencia del código.
4. **Rate limiting y detección de enumeración.** Limitar intentos por IP/sesión y alertar sobre recorridos secuenciales del espacio de códigos (200 peticiones en segundos es un patrón detectable).
5. **Diseño del identificador.** Evitar identificadores **cortos y secuenciales** (3 dígitos) fácilmente enumerables; preferir valores no predecibles (p. ej. UUID) cuando no deban ser adivinables.
6. **Endurecimiento de configuración (A05).** Revisar que el framework no introduzca diferencias observables (tiempos, cabeceras, mensajes) entre caminos de éxito y de error.

---

## 11. Conclusión

El laboratorio ilustra un **error de configuración (Security Misconfiguration, A05)** materializado como **canal lateral de temporización**: aunque el mensaje de error es idéntico para todos los códigos, el servidor **tarda más** cuando el código corresponde a un asistente real, porque solo entonces verifica la clave. Midiendo ese tiempo se **enumeran** los códigos válidos sin la clave y se **infiere la cantidad de asistentes**. La lección central es que la seguridad no depende solo del mensaje que se muestra: si el sistema **se comporta de forma observablemente distinta** (tiempo, tamaño, cabeceras) entre casos válidos e inválidos, filtra información. La mitigación pasa por **uniformar el tiempo de respuesta**, **autorizar antes de consultar** y **endurecer la configuración** para no delatar la validez de los identificadores.

---

## 12. Referencias técnicas

- OWASP Top 10 — A05:2021 Security Misconfiguration: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
- OWASP Web Security Testing Guide — Testing for Account Enumeration and Guessable User Account: https://owasp.org/www-project-web-security-testing-guide/
- CWE-208 — Observable Timing Discrepancy: https://cwe.mitre.org/data/definitions/208.html
- CWE-203 — Observable Discrepancy: https://cwe.mitre.org/data/definitions/203.html
- CWE-200 — Exposure of Sensitive Information to an Unauthorized Actor: https://cwe.mitre.org/data/definitions/200.html

---

**Modalidad del trabajo:** ejecución en el entorno de laboratorio autorizado del curso. El desafío se resolvió identificando un **canal lateral de temporización** que permite enumerar los códigos válidos sin la clave; la cantidad de asistentes hallada (**159**) se validó por coincidencia entre herramientas, descarte de jitter y separación bimodal de tiempos, y su MD5 fue aceptado por la plataforma.
