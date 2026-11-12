# Objetivo 5 — El Espejismo del Cifrado en el Cliente (Frontend Encryption)

**Módulo VII · Lógica de Negocio**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. El escenario

Una aplicación financiera cifra, con **JavaScript en el navegador del usuario**, todo el cuerpo de las peticiones `POST` y los parámetros sensibles **antes de enviarlos** al backend. Los arquitectos afirman:

> *"Como todo viaja encriptado, es imposible que un atacante intercepte o manipule los valores con un proxy como Burp Suite."*

Esa afirmación es **una falsa sensación de seguridad**. Veamos por qué.

---

## 2. El fallo fundamental de diseño

El error de raíz es uno solo, y es un principio básico de seguridad:

> **Nunca se puede confiar en nada que se ejecute del lado del cliente.**

El navegador del usuario **es territorio del atacante**. Todo lo que llega ahí —el HTML, el CSS y, sobre todo, **el JavaScript que cifra**— está **100% bajo su control**: lo puede leer, pausar, modificar y ejecutar a mano. Si el código que cifra corre en el navegador, entonces **la lógica de cifrado, el algoritmo y la clave también están en el navegador**, y por lo tanto **en manos del atacante**.

Esto deriva en tres verdades que rompen el esquema:

### 2.1 La clave viaja con el candado
Para que el JavaScript pueda cifrar, necesita **la clave de cifrado** (o la clave pública, o el algoritmo con su secreto). Esa clave **se descarga al navegador** junto con el resto del código. Es como mandar un cofre cerrado con llave… **pegándole la llave al cofre con cinta**. Quien recibe el cofre tiene las dos cosas. El atacante abre las DevTools y **lee la clave y el algoritmo directamente del código fuente**.

### 2.2 El cifrado es reversible por quien tiene el código
Como el atacante tiene el algoritmo **y** la clave, puede **cifrar y descifrar él mismo** cualquier valor, exactamente igual que lo hace la aplicación legítima. El cifrado no lo detiene: le da **la herramienta** para fabricar peticiones cifradas válidas con los datos que él quiera.

### 2.3 Confunde cifrado de transporte con validación de integridad
El cifrado en el cliente pretende **evitar la manipulación**, pero manipular datos **no es un problema de cifrado, es un problema de confianza y validación**. El transporte seguro **ya lo da HTTPS/TLS** (y mejor). Impedir que el usuario mande valores maliciosos es trabajo de la **validación del lado del servidor**, no de ofuscar el cuerpo de la petición. El esquema ataca el problema equivocado.

### 2.4 Es "seguridad por oscuridad"
Todo el modelo se apoya en **que el atacante no descubra cómo funciona el cifrado**. Pero el código está **ahí, a la vista, en el navegador**. La seguridad por oscuridad no es seguridad: es un secreto que ya está publicado.

> **El punto exacto donde se rompe:** el cifrado ocurre **antes** de salir del navegador, es decir, **después** del único lugar donde el atacante tiene control total. El atacante no necesita romper el cifrado en la red: **se mete antes de que el cifrado ocurra, o usa el mismo código de la app para cifrar sus propios valores manipulados.**

---

## 3. Por qué Burp "no sirve" … y por qué eso no importa

Es cierto lo único que dicen los arquitectos: si el atacante mira el tráfico en Burp, verá el cuerpo **ya cifrado** y no podrá editarlo *ahí, en ese punto*. Pero eso es **irrelevante**, porque el atacante **no ataca en la red**: ataca **dentro del navegador**, donde los datos todavía están **en texto plano** (antes de cifrar) o donde vive el **código que cifra**. El proxy es solo una de muchas herramientas, y acá se usa **al final**, no en el medio.

---

## 4. Pasos tácticos del atacante (cómo evade la protección)

El objetivo del atacante es doble: **(A) leer los datos** y **(B) enviar valores manipulados que el servidor acepte**. Hay varias vías; en la práctica se combinan.

### Táctica 1 — Interceptar ANTES de cifrar (atacar el punto plano)
Los datos nacen en texto plano en el formulario y **recién después** los cifra el JavaScript. El atacante se mete **en ese momento intermedio**:

1. Abre **DevTools → Sources** y busca la función que cifra (`encrypt(...)`, `cifrarBody(...)`, uso de `CryptoJS`, `window.crypto.subtle`, etc.).
2. Pone un **breakpoint** justo **antes** de la llamada a cifrar.
3. Rellena el formulario (ej. `monto: 100`) y envía. La ejecución **se frena** en el breakpoint, con los datos **todavía en texto plano**.
4. Desde la **consola**, **modifica la variable en caliente**: `monto = 999999` (o `monto = -5`).
5. Deja correr la ejecución (`Resume`). El propio JavaScript de la app **cifra el valor manipulado** y lo manda **perfectamente firmado y cifrado**. El servidor lo recibe como legítimo.

> Acá la propia protección del sitio trabaja para el atacante: **él pone el dato malo, la app se lo cifra gratis.**

### Táctica 2 — Usar el código de la app como oráculo de cifrado
El atacante no necesita entender el algoritmo: **le alcanza con llamar a las funciones que ya existen** en la página.

1. En **DevTools → Console**, invoca directamente la función de cifrado del sitio:
   ```js
   // la misma función que usa la app, ya cargada en la página
   const payload = encrypt(JSON.stringify({ monto: 999999, cupon: "x" }));
   console.log(payload);
   ```
2. Obtiene el **cuerpo cifrado válido** de su valor manipulado.
3. Lo pega en **Burp Repeater** y lo reenvía al endpoint. El servidor lo descifra y lo procesa como auténtico.

### Táctica 3 — Extraer la clave y el algoritmo del código fuente
Como la clave vive en el navegador, el atacante la cosecha:

1. **DevTools → Sources / Network** → descarga los `.js` de la app.
2. Si está **minificado/ofuscado**, lo pasa por un *beautifier* (prettify) y busca strings tipo clave, IV, `AES`, `RSA public key`, etc.
3. Reconstruye el cifrado **fuera del navegador** (un script propio en Python/Node con la misma clave y algoritmo) y genera **todos los payloads cifrados que quiera**, automatizando el ataque (incluso con Turbo Intruder para race conditions).

### Táctica 4 — Burp con un plugin de "descifrar/recifrar"
Para no hacerlo a mano cada vez, el atacante automatiza el pipeline en el propio proxy:

1. Con la clave y el algoritmo ya extraídos, escribe una **extensión de Burp** (o usa herramientas como *Hackvertor* / *Piper*) que **descifra el cuerpo entrante**, lo muestra en texto plano para editarlo, y **lo vuelve a cifrar** antes de reenviarlo.
2. Resultado: Burp vuelve a ser totalmente útil. El atacante edita `monto`, `rol`, `cantidad` como si no hubiera cifrado, y el plugin recifra transparentemente.

### 🔍 Cómo verlo en el software

1. Abrís **DevTools → Network** y mandás una petición: ves el `body` **cifrado** (base64/hex ilegible). Hasta acá "parece" seguro.
2. Vas a **DevTools → Sources**, buscás la función de cifrado y ponés un **breakpoint antes** de cifrar; o directamente llamás `encrypt(...)` desde la **Console**.
   - **Señal que confirma la falla:** podés **leer el algoritmo y la clave** en el código, **modificar el valor en texto plano** antes de que se cifre, y el servidor **acepta** el payload manipulado (devuelve éxito con `monto: 999999`). Si el servidor **rechaza** valores fuera de regla pese a venir bien cifrados, entonces la seguridad real está —correctamente— **en el backend**, no en el cifrado del cliente.

---

## 5. Lo que SÍ hay que hacer (la arquitectura correcta)

El cifrado en el cliente no agrega seguridad real contra la manipulación. La protección verdadera es:

1. **HTTPS/TLS para el transporte.** Ya cifra todo el canal de punta a punta, resuelve el *man-in-the-middle* en la red y está **probado y estandarizado**. No hace falta reinventarlo con JavaScript.
2. **Validación y autorización estrictas en el SERVIDOR.** Es la defensa de verdad: el backend valida **cada** campo (tipo, rango, reglas de negocio) y verifica permisos **sin confiar jamás** en lo que mandó el cliente, venga cifrado o no. Un `monto` negativo o un `rol=admin` se rechazan **en el servidor**, que es la única fuente de verdad.
3. **El precio, el saldo, los permisos y el estado los decide el servidor**, nunca el cliente. El cliente solo elige *qué* quiere hacer; el *cuánto cuesta* y el *si está permitido* son autoridad del backend.
4. **Integridad con firmas del lado del servidor** cuando se necesita (ej. tokens firmados/HMAC con clave que **nunca** sale del servidor), no con "cifrado" cuya clave se reparte al navegador.

> Regla de oro: **ninguna validación que corra en el cliente es una defensa.** Sirve para la experiencia de usuario; la seguridad se impone **siempre** en el servidor.

---

## 6. Conclusión

Cifrar el cuerpo de las peticiones con JavaScript en el navegador es un **espejismo de seguridad**. El fallo de diseño es confiar en código que se ejecuta en un entorno **totalmente controlado por el atacante**: el navegador descarga el algoritmo **y** la clave, así que el atacante puede leer los datos antes de cifrarlos, usar las propias funciones del sitio como oráculo de cifrado, o extraer la clave y recifrar lo que quiera. Burp parece inútil mirando el tráfico cifrado, pero el ataque no ocurre en la red: ocurre **dentro del navegador**, antes del cifrado, o reutilizando el mismo código de la app.

El cifrado de cliente no reemplaza **ni** al TLS (que ya protege el transporte) **ni** —y esto es lo crítico— a la **validación del lado del servidor** (que es lo único que impide la manipulación). Autenticar no es autorizar, y cifrar en el cliente no es validar: la seguridad real vive **siempre en el backend**, nunca en el navegador del usuario.

---

*Fin del Objetivo 5 — Módulo VII.*
