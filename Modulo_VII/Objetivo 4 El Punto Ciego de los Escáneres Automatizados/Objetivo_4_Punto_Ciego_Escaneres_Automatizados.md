# Objetivo 4 — El Punto Ciego de los Escáneres Automatizados

**Módulo VII · Lógica de Negocio**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. La idea en una frase

Un escáner automatizado (Nessus, Acunetix, el *Active Scan* de Burp) sabe reconocer **patrones técnicos conocidos**, pero **no entiende qué hace tu negocio**. Por eso encuentra un XSS o una cabecera faltante, pero es **ciego** ante una falla donde el código funciona perfecto y, aun así, permite algo que **no debería pasar en el mundo real** (comprar con cantidades negativas, canjear 50 veces un cupón de un solo uso, saltarse un paso del checkout). Esa es la **lógica de negocio**, y es el **mayor punto ciego** de la automatización.

---

## 2. Qué SÍ encuentra bien un escáner (y por qué)

Las herramientas automáticas son excelentes buscando **fallas técnicas** porque esas fallas tienen una **firma reconocible y universal**:

| Falla técnica | Cómo la detecta el escáner |
|---|---|
| **XSS** | Inyecta `<script>` o `"><img onerror=...>` y revisa si vuelve **sin codificar** en la respuesta. Patrón claro. |
| **SQL Injection** | Manda `'` o `1=1` y busca un error de SQL, un cambio booleano o un retardo (time-based). Patrón medible. |
| **Cabeceras inseguras / Misconfiguration** | Lee la respuesta HTTP y chequea si falta `Content-Security-Policy`, `HSTS`, `HttpOnly`, etc. Es un checklist. |
| **Software desactualizado / CVEs** | Compara el *banner* de versión contra una base de vulnerabilidades conocidas. |

Todo esto es **detectable con reglas y firmas**: "si mando X y recibo Y, hay vulnerabilidad". El escáner **no necesita entender el negocio**, solo comparar patrones de entrada/salida. Por eso es rápido, barato y cubre miles de endpoints sin cansarse.

---

## 3. Por qué la lógica de negocio es el punto ciego

Un escáner **no tiene contexto**: no sabe qué es un "cupón", qué significa "un solo uso", que un pedido debe pagarse **antes** de enviarse, ni que una cantidad **no puede ser negativa**. Solo ve peticiones y respuestas HTTP. Las fallas lógicas son invisibles para él por varias razones:

### 3.1 El código "funciona bien" — no hay error que detectar
En una falla lógica **no hay excepción, no hay traza, no hay patrón de error**. Si mando `cantidad = -5` y el total da negativo, el servidor responde `200 OK` **feliz**. El escáner ve un `200` y concluye "todo normal". No tiene forma de saber que un total negativo es un desastre: **para él es solo un número**.

### 3.2 No conoce las reglas del negocio
"Un cupón se usa una sola vez", "el envío cuesta $X", "no se puede comprar más que el stock" son **reglas específicas de cada aplicación**, no estándares universales. El escáner **no las conoce** porque nadie se las programó — y no se las puede programar genéricamente, porque **cambian en cada sistema**. Lo que es válido en una tienda es inválido en otra.

### 3.3 No encadena pasos ni entiende el flujo
Muchas fallas lógicas nacen de **saltarse o reordenar pasos** de un proceso de varios estados: ir directo de "carrito" a "confirmado" **sin pasar por el pago**, o cambiar el método HTTP de `PATCH` a `GET` para asignarse un rol. El escáner **dispara peticiones sueltas**, no razona sobre la **secuencia** ni sobre el **estado** de un flujo de negocio. No sabe que el paso 3 nunca debió ejecutarse sin el paso 2.

### 3.4 No explota la concurrencia ni el tiempo
Una **race condition** (Objetivo 3) requiere mandar 50 peticiones **sincronizadas en la misma ventana TOCTOU** con técnicas como *single-packet attack*. Eso es **creatividad y timing**, no un patrón de firma. El escáner manda sus peticiones **en serie**, una tras otra, así que la ventana de carrera ni siquiera se abre: nunca la va a encontrar.

### 3.5 No entiende "autorización por objeto" (IDOR)
Para detectar un **IDOR** hay que saber que la factura `/invoice?id=1025` **pertenece a otro usuario** y que yo **no debería** verla. El escáner recibe un `200 OK` con datos y piensa "respuesta válida". **No tiene idea de quién es el dueño legítimo** del recurso, porque eso es conocimiento del negocio, no un patrón técnico.

> **Resumen del punto ciego:** el escáner responde "¿la respuesta tiene una firma de vulnerabilidad conocida?". La lógica de negocio pregunta otra cosa: **"¿esto debería estar permitido según las reglas del negocio?"** — y esa pregunta requiere **entender el propósito**, algo que una firma automática no tiene.

---

## 4. Por qué la auditoría manual es indispensable

Donde el escáner es ciego, el **pentester humano** aporta lo que ninguna firma puede:

1. **Entiende el negocio.** Lee la aplicación, mapea los roles, los recursos y las reglas ("esto es un cupón de un solo uso", "esto es plata"), y **piensa cómo abusar de esas reglas**.
2. **Razona sobre el flujo y el estado.** Se pregunta "¿qué pasa si me salto el pago?", "¿y si reenvío el paso 2 con el token del paso 1?", "¿y si mando el `PATCH` como `GET`?". Encadena pasos que el escáner nunca conecta.
3. **Es creativo e intencional.** Prueba **casos que el desarrollador nunca imaginó**: cantidades negativas, precios manipulados, descuentos apilados, 50 canjes en paralelo. La falla lógica vive justo ahí, en lo que **nadie previó**.
4. **Interpreta el impacto, no solo el patrón.** Ve un `200 OK` con total negativo y entiende que eso significa **plata regalada**. El escáner ve un `200` y sigue de largo.
5. **Combina y escala.** Encadena un IDOR con una escalada de privilegios, o una race condition con una manipulación de precio, construyendo un ataque real que ninguna herramienta arma sola.

### El rol correcto de cada uno (no es "humano vs. máquina")

La automatización y la auditoría manual **no compiten, se complementan**:

- **El escáner** barre rápido la **superficie técnica** (XSS, SQLi, cabeceras, CVEs) en miles de endpoints. Hace el trabajo repetitivo y libera tiempo.
- **El humano** se concentra en lo que la máquina **no puede ver**: la **lógica de negocio**, donde están las fallas más graves, más silenciosas y más caras.

Por eso, en la etapa de lógica de negocio, **la auditoría manual es indispensable**: es la única capaz de responder la pregunta que al escáner se le escapa — *"el sistema hace esto… pero, según las reglas del negocio, ¿debería?"*.

---

## 5. Conclusión

Los escáneres automatizados son imbatibles encontrando fallas con **firma reconocible** (XSS, SQLi, configuraciones inseguras), porque solo necesitan comparar patrones de entrada y salida sin entender qué hace la aplicación. Pero esa misma fortaleza es su límite: **no tienen contexto de negocio**. No saben que una cantidad no puede ser negativa, que un cupón es de un solo uso, que un pedido debe pagarse antes de enviarse, ni que una factura tiene dueño. Las fallas de **lógica de negocio** no dejan error, no tienen firma y requieren **entender el propósito y encadenar pasos** — exactamente lo que una firma automática no hace.

Por eso la **auditoría manual** es indispensable en esta etapa: solo un pentester humano entiende las reglas del negocio, razona sobre el flujo, es creativo para probar lo impensado e interpreta el impacto real. Lo ideal es la combinación: **la máquina cubre la superficie técnica a gran escala; la persona cubre el punto ciego donde viven las vulnerabilidades más peligrosas.**

---

*Fin del Objetivo 4 — Módulo VII.*
