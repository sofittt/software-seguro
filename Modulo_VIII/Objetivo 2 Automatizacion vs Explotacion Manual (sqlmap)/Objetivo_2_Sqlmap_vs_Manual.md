# Objetivo 2 — Automatización vs. Explotación Manual (sqlmap)

**Módulo VIII · SQL Injection**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. Por qué depender solo de sqlmap es "de novatos"

**sqlmap** es la herramienta de explotación de SQL Injection más potente que hay: detecta, confirma y extrae datos (bases, tablas, columnas) de forma automática, y soporta decenas de motores y técnicas (boolean, time-based, UNION, error-based, out-of-band). Es imbatible en lo que hace bien.

Pero sqlmap es, al final, un **motor de patrones y payloads estándar**. Funciona genial cuando la inyección es "de manual": un parámetro directo, sin defensas raras, sin lógica de aplicación de por medio. El problema es que **el mundo real casi nunca es de manual**. sqlmap **no razona, no entiende el contexto de la aplicación y no improvisa**: aplica su catálogo de técnicas y, si la vulnerabilidad está "escondida" detrás de algo que su catálogo no contempla, **pasa de largo y reporta "not injectable"** — aunque la falla esté ahí.

El pentester humano, en cambio, **entiende el contexto, observa cómo responde la app y adapta el payload a mano**. Por eso la regla: sqlmap es una **herramienta**, no un reemplazo del criterio. Abajo, los escenarios donde sqlmap fracasa y el ataque manual gana.

---

## 2. Escenario 1 — El dato va cifrado / codificado / firmado antes de llegar al parámetro vulnerable

### La situación
Muchas apps **no mandan el valor en texto plano**. Antes de que el parámetro llegue al backend (y al punto inyectable), el valor pasa por una transformación: se **cifra en el cliente** (como vimos en el Objetivo 5 del Módulo VII), se codifica en **Base64**, se arma un **JWT**, o la petición lleva un **hash/firma de integridad** (ej. un parámetro `sign` = HMAC del resto).

Ejemplo: el `id` del producto no viaja como `?id=5`, sino como `?data=eyJpZCI6NX0=` (que es `{"id":5}` en Base64), y adentro de ese JSON está el campo realmente inyectable.

### Por qué sqlmap falla
sqlmap inyecta sus payloads **en el parámetro tal como lo ve**: le mete `' OR 1=1--` **al string Base64 entero**. Resultado: rompe la codificación, el backend no puede decodificar el `data`, y el payload **nunca llega** al campo `id` vulnerable. Peor aún, si hay una **firma de integridad**, cualquier cosa que sqlmap toque **invalida la firma** y el servidor **rechaza la petición antes de llegar al SQL**. sqlmap prueba, recibe siempre "error / rechazado", y concluye **"no inyectable"**. (sqlmap tiene algunos *tamper scripts* y puede codificar en base64, pero no reconstruye firmas dinámicas, ni descifra esquemas propios del cliente, ni navega estructuras anidadas que no conoce.)

### Cómo gana el atacante manual
El pentester, en **Burp Suite**:
1. **Entiende la transformación**: ve que `data` es Base64, lo **decodifica** y descubre el `{"id":5}` adentro.
2. Inyecta el payload **en el lugar correcto, por dentro**: arma `{"id":"5' OR 1=1--"}`.
3. **Rehace la transformación**: lo vuelve a codificar en Base64 (y si hay firma, **la recalcula** con la clave que extrajo del cliente, como en el Objetivo 5).
4. Manda la petición ya cifrada/firmada/codificada **correctamente**. Ahora el payload **sí** llega limpio al campo inyectable y la inyección funciona.

> El humano hace lo que sqlmap no sabe: **colocar el payload en el punto exacto, por debajo de la capa de codificación/firma, y reconstruir esa capa.** Incluso puede automatizarlo con una **extensión de Burp** (decode → inyectar → re-encode/re-sign) para seguir usando sqlmap "por encima" si quiere.

---

## 3. Escenario 2 — La inyección depende de una SECUENCIA / estado de la lógica de negocio (multi-paso)

### La situación
El parámetro vulnerable **no es explotable con una sola petición aislada**. La inyección solo se dispara si antes ocurrió **un flujo de varios pasos** con un estado concreto. Ejemplos:

- El valor inyectable se **guarda en el paso 1** (ej. un campo del perfil o un ítem del carrito) y recién se usa en una consulta SQL **en el paso 3** (un reporte, un resumen, el checkout). Es una **SQLi de segundo orden (second-order)**: se inserta en un lado y detona en otro.
- La inyección requiere estar **logueado con un token que rota**, haber hecho un **POST previo** que setea una cookie/estado, o seguir un **orden exacto** (A → B → C) sin el cual el endpoint vulnerable ni siquiera se alcanza.

### Por qué sqlmap falla
sqlmap razona **petición por petición**: toma UNA request y la bombardea con payloads esperando ver el efecto **en esa misma respuesta**. **No entiende flujos de negocio ni estado de varios pasos.** En una second-order:
- sqlmap inyecta en el paso 1, mira la respuesta del paso 1 → **no ve nada** (el payload todavía no detonó) → marca "no inyectable".
- El efecto real aparece **en otra pantalla, en otra petición, más tarde** — un lugar donde sqlmap **ni siquiera está mirando**.

Tampoco sabe reproducir "primero hacé A, después B, después dispará en C con el token que te dio B". No tiene el **contexto de la aplicación** para armar esa coreografía.

### Cómo gana el atacante manual
El pentester **entiende el flujo** y lo reproduce a mano en Burp:
1. **Paso 1**: inyecta el payload en el campo que se **almacena** (ej. pone como nombre de usuario `' || (SELECT ...) || '` o un `'` que rompa la consulta futura).
2. **Pasos intermedios**: navega el flujo normal (confirma, avanza, mantiene la sesión/estado).
3. **Paso 3**: entra a la pantalla donde ese dato **se usa en la consulta** (el reporte, el resumen) y **ahí observa el efecto** (error, cambio booleano, retardo).
4. Confirmada la inyección de segundo orden, la explota manualmente, correlacionando **dos puntos distintos** de la aplicación que sqlmap jamás habría conectado.

> El humano aporta lo que a sqlmap le falta: **memoria del flujo y comprensión del negocio.** Sabe que lo que inyectó en la pantalla A va a detonar en la pantalla C, y va a mirar ahí.

---

## 4. Escenario 3 (bonus) — WAF / defensas que exigen evasión creativa y a medida

### La situación
Un **WAF** (Web Application Firewall) o un filtro propio bloquea los payloads "obvios". Los payloads por defecto de sqlmap son **muy conocidos** y las firmas de los WAF los detectan al instante, devolviendo `403 Forbidden` o bloqueando la IP.

### Por qué sqlmap (solo) falla
Con payloads estándar, sqlmap **se choca contra el WAF** y recibe bloqueos. Tiene *tamper scripts* para evadir, pero son **genéricos**: no están hechos a medida de ESE WAF ni de ESA lógica de filtrado. Si la protección es específica (ej. borra la palabra `SELECT` una sola vez, o filtra espacios), el catálogo genérico de sqlmap puede **no dar con la combinación exacta** y rendirse.

### Cómo gana el atacante manual
El pentester **estudia cómo responde el filtro** y construye la evasión **a medida**, probando en Burp Repeater una a una:
- **Ruptura de palabras**: `SEL/**/ECT`, `UNIunionON` (si borra `union` una vez, queda `union`).
- **Alternar mayúsculas**: `SeLeCt`.
- **Reemplazar espacios**: por comentarios `/**/`, tabs, `%0a`, o paréntesis.
- **Codificaciones**: URL doble, hex, Unicode overlong.
- Observa **qué deja pasar el WAF y qué no**, y ajusta el payload hasta colarlo. Una vez encontrado el bypass manual, puede **enseñárselo a sqlmap** con un `--tamper` propio y seguir automatizando.

### 🔍 Cómo verlo en el software

1. Corrés `sqlmap` contra el endpoint y reporta **"not injectable"** o recibe `403`.
2. En **Burp Repeater**, mandás a mano un `'` o `AND 1=1` **en el punto correcto** (decodificando Base64/JWT, o en el paso del flujo donde el dato se usa, o con un payload ofuscado).
   - **Señal que confirma que sqlmap se equivocó:** aparece el **error de SQL, el cambio booleano o el retardo** cuando inyectás manualmente en el lugar/forma correcta, pese a que la herramienta dijo que no era vulnerable.

---

## 5. La moraleja: sqlmap es un martillo, no un cerebro

| | **sqlmap (automático)** | **Pentester manual (Burp)** |
|---|---|---|
| **Fortaleza** | Velocidad, volumen, extracción masiva de datos | Contexto, criterio, creatividad, adaptación |
| **Entiende el negocio / el flujo** | ❌ No | ✅ Sí |
| **Payload en el punto correcto (tras cifrado/firma/anidación)** | ❌ Rompe la capa | ✅ Decodifica, inyecta dentro, reconstruye |
| **Inyección de segundo orden / multi-paso** | ❌ No conecta peticiones | ✅ Correlaciona pantalla A → C |
| **Evasión de WAF a medida** | ⚠️ Solo tampers genéricos | ✅ Bypass artesanal observando el filtro |

Lo ideal **no es elegir uno**: el pentester **encuentra y confirma la vulnerabilidad a mano** (donde sqlmap es ciego), y **después** usa sqlmap para **automatizar la extracción masiva** una vez que entendió dónde y cómo inyectar — incluso pasándole su payload de evasión con `--tamper` o apuntándolo al punto exacto. La herramienta potencia al experto; **no lo reemplaza**.

---

## 6. Conclusión

sqlmap fracasa justamente donde falta lo que una herramienta no tiene: **contexto y criterio**. Falla cuando el dato viaja **cifrado, codificado o firmado** antes de llegar al parámetro vulnerable (rompe la capa y el payload nunca llega), cuando la inyección depende de una **secuencia de varios pasos o es de segundo orden** (no conecta la pantalla donde se inyecta con la pantalla donde detona), y cuando hay un **WAF** que exige una evasión **a medida** que su catálogo genérico no cubre. En los tres casos, el **atacante manual** gana porque **entiende cómo funciona la aplicación**, coloca el payload en el punto exacto, reconstruye las capas de protección y adapta su técnica a lo que observa.

La lección del Módulo VIII: automatizar está bien, pero **depender ciegamente de sqlmap es de novatos**. La herramienta es poderosísima para extraer datos una vez que sabés dónde y cómo inyectar — pero **ese "dónde y cómo" sigue siendo trabajo del cerebro humano.**

---

*Fin del Objetivo 2 — Módulo VIII.*
