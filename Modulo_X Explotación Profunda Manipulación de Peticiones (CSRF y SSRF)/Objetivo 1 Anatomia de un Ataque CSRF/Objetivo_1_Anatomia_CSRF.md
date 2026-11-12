# Objetivo 1 — Anatomía de un Ataque CSRF (Cross-Site Request Forgery)

**Módulo X · Manipulación de Peticiones (CSRF y SSRF)**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. ¿Qué es un CSRF, en una frase?

Un **CSRF (Cross-Site Request Forgery / Falsificación de Petición en Sitios Cruzados)** engaña al navegador de una víctima **ya autenticada** para que **envíe, sin que la víctima lo sepa, una petición a un sitio donde tiene sesión abierta**, ejecutando una acción que el atacante quiere (cambiar el email, transferir plata, cambiar la contraseña). El atacante **no roba la sesión**: **la usa a distancia**, aprovechando que el navegador adjunta solo las cookies de sesión.

La idea central: el atacante no ataca al servidor directamente, **usa a la víctima como "control remoto"** de su propia sesión.

---

## 2. El flujo exacto de un ataque CSRF exitoso

Imaginemos que el banco `banco.com` permite cambiar el email de la cuenta con esta petición:

```http
POST /cambiar-email HTTP/1.1
Host: banco.com
Cookie: session=abc123...
Content-Type: application/x-www-form-urlencoded

email=nuevo@correo.com
```

### Paso a paso

**1) La víctima inicia sesión en el sitio legítimo.**
Entra a `banco.com`, pone su usuario y contraseña. El servidor le devuelve una **cookie de sesión** (`session=abc123`) que el navegador **guarda**. La víctima **no cierra sesión** (la cookie sigue viva).

**2) El atacante prepara una página maliciosa.**
En otro sitio (`sitio-malicioso.com`, o un email, o un anuncio), el atacante arma una página que **dispara automáticamente** la petición al banco. Por ejemplo, un formulario que se autoenvía con JavaScript:

```html
<!-- En sitio-malicioso.com -->
<form id="ataque" action="https://banco.com/cambiar-email" method="POST">
    <input type="hidden" name="email" value="atacante@evil.com">
</form>
<script>document.getElementById("ataque").submit();</script>
```

O incluso, para un `GET`, basta una imagen invisible:

```html
<img src="https://banco.com/cambiar-email?email=atacante@evil.com" width="0" height="0">
```

**3) El atacante hace que la víctima visite esa página.**
Mediante **ingeniería social** (un email tentador, un link en redes, un anuncio), convence a la víctima de **hacer clic** o simplemente **abrir** la página maliciosa. La víctima **cree que entró a un sitio cualquiera**.

**4) El navegador de la víctima dispara la petición al banco… CON las cookies.**
Acá está el corazón del ataque. Al cargar el formulario/imagen, el navegador de la víctima manda la petición a `banco.com`. Y por el **comportamiento automático de los navegadores** (ver sección 3), **adjunta automáticamente la cookie de sesión `session=abc123`** de la víctima, porque la petición va dirigida a `banco.com`.

**5) El servidor del banco ejecuta la acción como si fuera legítima.**
El banco recibe una petición **con una cookie de sesión válida**. Desde su punto de vista, **es la víctima real haciendo el pedido**. No tiene forma de distinguir que la petición la **originó otro sitio**. Entonces **cambia el email** a `atacante@evil.com`.

**6) El atacante toma control.**
Con el email cambiado, el atacante pide un "reset de contraseña", que llega a **su** correo → **se queda con la cuenta**. La víctima nunca vio nada: todo pasó en segundo plano.

> **Resumen del flujo:** víctima logueada + visita a página maliciosa + navegador que adjunta cookies solo → el servidor ejecuta una acción forjada creyendo que es legítima.

---

## 3. Por qué ocurre: el comportamiento automático del navegador con las cookies

El CSRF existe por **una característica de diseño de los navegadores**, no por un bug del código:

> **El navegador adjunta AUTOMÁTICAMENTE las cookies de un dominio en CADA petición dirigida a ese dominio — sin importar desde qué sitio se originó la petición.**

Es decir: si hay una cookie de `banco.com` guardada, **cualquier** petición que vaya a `banco.com` la lleva pegada, aunque esa petición haya nacido en `sitio-malicioso.com`. El navegador **no se pregunta "¿quién está pidiendo esto?"**, solo "¿a qué dominio va? Ah, a banco.com → le pongo sus cookies".

Esto, que fue pensado para comodidad (no tener que loguearte en cada clic), es **justo lo que explota el CSRF**. El atacante **no necesita leer ni robar la cookie** (no puede, por otras protecciones) — **le alcanza con que el navegador la mande sola**. El servidor confía en la cookie como prueba de identidad, y la cookie **llega igual** venga de donde venga la petición.

El problema de fondo: el servidor **confía en que "tener la cookie" = "la víctima quiso hacer esto"**, pero eso es falso. Tener la cookie solo prueba **quién** es, no que **haya querido** realizar la acción. CSRF rompe esa suposición.

---

## 4. Cómo mitiga el atributo `SameSite` (Lax y Strict)

El atributo **`SameSite`** de las cookies ataca **la causa raíz**: le dice al navegador **cuándo tiene permitido adjuntar la cookie en peticiones que vienen de OTRO sitio** (cross-site). Al limitar eso, el navegador **deja de mandar la cookie** en las peticiones forjadas, y el ataque **se cae solo**.

```http
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
```

### `SameSite=Strict` — la más estricta
- **Qué hace:** el navegador **NUNCA** adjunta la cookie si la petición **viene de un sitio distinto**. Solo la manda si navegás **dentro del propio sitio**.
- **Contra CSRF:** **protección total**. La petición del formulario malicioso de `sitio-malicioso.com` hacia `banco.com` **no lleva la cookie** → el banco la ve como anónima → **rechaza la acción**. El ataque falla.
- **Costo (UX):** es tan estricta que rompe la navegación normal entre sitios. Si un amigo te pasa un **link** a `banco.com` y hacés clic desde WhatsApp, la cookie **tampoco** viaja → aparecés **deslogueado** aunque tengas sesión. Incómodo.

### `SameSite=Lax` — el equilibrio (hoy es el valor por defecto)
- **Qué hace:** la cookie **se adjunta solo en navegaciones de nivel superior (top-level) con métodos seguros**, es decir cuando la víctima **hace clic en un enlace** que la lleva al sitio (un `GET` que cambia la URL en la barra). **NO** se adjunta en peticiones cross-site que sean **`POST`**, ni en las que se disparan **en segundo plano** (formularios automáticos, `fetch`, imágenes, iframes).
- **Contra CSRF:** **mitiga radicalmente** el vector. El ataque clásico usa un **`POST` automático** o una petición en segundo plano desde otro sitio → con `Lax`, el navegador **no manda la cookie** → el banco rechaza. Y el caso de la **imagen con `GET`** disparada en segundo plano tampoco lleva cookie.
- **Ventaja:** conserva la buena UX: si llegás al sitio por un link normal, **seguís logueado**.

### Comparación rápida

| | Petición normal dentro del sitio | Clic en un link externo (GET top-level) | POST/background desde otro sitio (el ataque CSRF) |
|---|---|---|---|
| **Strict** | ✅ manda cookie | ❌ NO manda | ❌ NO manda → **ataque bloqueado** |
| **Lax** | ✅ manda cookie | ✅ manda cookie | ❌ NO manda → **ataque bloqueado** |
| **None** (sin protección) | ✅ | ✅ | ⚠️ ✅ manda → **vulnerable** |

> `SameSite=Lax` es el punto dulce: **corta el CSRF** (porque los ataques son POST/background cross-site) **sin romper** la navegación por enlaces. Por eso los navegadores modernos lo aplican **por defecto** aunque el dev no lo setee.

### 🔍 Cómo verlo en el software
1. En **DevTools → Application → Cookies**, mirás la cookie de sesión y su columna **SameSite**.
   - **Señal buena:** dice `Lax` o `Strict`.
   - **Señal de riesgo:** está **vacía** o dice `None` (sin otras defensas = posible CSRF).
2. Para confirmar la vulnerabilidad: armás una página de prueba con un `<form>` auto-enviado hacia la acción sensible y la abrís estando logueado.
   - **Señal que confirma el CSRF:** la acción **se ejecuta** (el email cambió) → la cookie viajó cross-site. Si el servidor la **rechaza** (o pide un token CSRF), está protegido.

---

## 5. Nota: SameSite no es la única defensa (defensa en profundidad)

`SameSite` es potentísimo, pero lo ideal es combinarlo con el clásico **Token Anti-CSRF (CSRF token)**: un valor **secreto, aleatorio y único por sesión** que el servidor mete en cada formulario legítimo y **exige de vuelta** en la petición. El sitio malicioso **no conoce ese token** (no puede leerlo por la *Same-Origin Policy*), así que **no puede forjar** una petición válida. En Farmacia Tienda, por ejemplo, la cookie de sesión `ft_sesion` es `SameSite=Lax` **y además** el backend ignora la cookie en peticiones que no sean GET si no traen la cabecera `X-Requested-With` — otra barrera anti-CSRF. Capas sobre capas.

---

## 6. Conclusión

Un ataque **CSRF** funciona así: una víctima **logueada** visita una página maliciosa que **dispara en segundo plano** una petición hacia el sitio donde tiene sesión; el **navegador adjunta automáticamente la cookie de sesión** de la víctima; y el servidor, al ver una cookie válida, **ejecuta la acción forjada creyendo que es legítima**. El fallo ocurre por el **comportamiento automático del navegador**, que pega las cookies de un dominio en **toda** petición dirigida a ese dominio **sin importar quién la originó** — y porque el servidor confunde "tener la cookie" con "la víctima quiso esto".

El atributo **`SameSite`** mitiga radicalmente el vector al controlar **cuándo** el navegador manda la cookie en contextos cross-site: **`Strict`** no la manda **nunca** desde otro sitio (protección total, peor UX), y **`Lax`** (hoy el valor por defecto) la manda **solo** en clics a enlaces top-level, **nunca** en los `POST` o peticiones en segundo plano que usa el CSRF — cortando el ataque sin romper la navegación. Combinado con tokens anti-CSRF, cierra el vector por completo.

---

*Fin del Objetivo 1 — Módulo X.*
