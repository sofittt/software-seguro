# Objetivo 3 — XSS vs. CSRF (Comparación Técnica)

**Módulo X · Manipulación de Peticiones (CSRF y SSRF)**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. Lo que tienen en común (por eso se confunden)

Tanto el **XSS** como el **CSRF**:
- Involucran al **navegador de la víctima**.
- Buscan **afectar la cuenta** de la víctima en un sitio donde está autenticada.
- Suelen empezar con algo de **ingeniería social** (un link, una página trampa).

Pero ahí termina el parecido. **Sus mecánicas son opuestas**, y entender esa diferencia es clave.

---

## 2. La diferencia fundamental (en una frase)

> **XSS es un abuso de la CONFIANZA que el USUARIO tiene en el SITIO** (el navegador ejecuta código malicioso creyendo que viene del sitio legítimo).
>
> **CSRF es un abuso de la CONFIANZA que el SITIO tiene en el USUARIO** (el servidor ejecuta una acción forjada creyendo que la pidió el usuario legítimo).

Todo lo demás se desprende de esto.

---

## 3. Cómo funciona cada uno (mecánica opuesta)

### XSS — inyecta y EJECUTA código en el navegador de la víctima
El atacante logra **inyectar código JavaScript** en una página en la que la víctima confía. Cuando la víctima la abre, **su navegador ejecuta ese código** como si fuera parte legítima del sitio. El atacante **corre su propio código dentro de la sesión de la víctima**: puede leer el DOM, robar la cookie (si no es `HttpOnly`), modificar la página, hacer peticiones en nombre del usuario, etc.

- **El ataque está en el CLIENTE:** el daño ocurre porque se **ejecuta código** en el navegador.
- **El atacante VE y controla:** puede leer respuestas, robar datos, hacer **cualquier** acción, y adaptarse en tiempo real.

### CSRF — fuerza una PETICIÓN (sin ejecutar código propio)
El atacante **NO inyecta ni ejecuta código** en el sitio víctima. Solo **engaña al navegador** para que **envíe una petición pre-armada** al sitio donde la víctima tiene sesión. El navegador **adjunta automáticamente la cookie** de sesión, y el servidor ejecuta la acción creyendo que es legítima.

- **El ataque apunta al SERVIDOR:** el daño ocurre porque el **servidor procesa una acción forjada**.
- **El atacante es CIEGO:** dispara la petición "a ciegas". **No puede leer la respuesta** (la *Same-Origin Policy* se lo impide); solo logra que la **acción se ejecute**, pero no ve el resultado.

---

## 4. Tabla comparativa directa

| | **XSS (Cross-Site Scripting)** | **CSRF (Cross-Site Request Forgery)** |
|---|---|---|
| **Confianza que abusa** | La del **usuario hacia el sitio** | La del **sitio hacia el usuario** |
| **Qué hace** | **Inyecta y ejecuta código** (JS) en el navegador | **Fuerza una petición** forjada al servidor |
| **¿Ejecuta código?** | **Sí** (JavaScript en el cliente) | **No** — solo manda una petición HTTP |
| **Dónde ocurre el daño** | En el **cliente** (navegador de la víctima) | En el **servidor** (procesa la acción) |
| **¿El atacante ve la respuesta?** | **Sí**, puede leer datos y adaptarse | **No**, es ciego (SOP lo bloquea) |
| **Alcance** | **Amplio**: robar cookies/datos, modificar la página, hacer cualquier acción | **Limitado**: solo ejecutar **una acción de cambio de estado** predefinida |
| **¿Necesita cookies de la víctima?** | No necesariamente (ejecuta código directo) | **Sí**, depende 100% de que el navegador adjunte la cookie |
| **Defensa principal** | **Output Encoding** + **CSP** + sanitización | **Token Anti-CSRF** + cookie **`SameSite`** |
| **Relación entre ellos** | **Más poderoso**: un XSS puede **hacer todo lo que haría un CSRF y más** | Más acotado; **un token CSRF NO protege contra XSS** |

---

## 5. Un punto clave: XSS "gana" sobre CSRF

Una consecuencia importante de la comparación: **el XSS es estrictamente más poderoso**. Como el XSS **ejecuta código** dentro de la sesión, puede **leer el token anti-CSRF** de la página y usarlo para forjar peticiones válidas — es decir, **un XSS rompe las defensas anti-CSRF**. Por eso se dice que **si tenés un XSS, el CSRF es lo de menos**: el atacante ya puede hacer cualquier cosa.

Al revés **no funciona**: un CSRF **no** te da ejecución de código, así que no puede robar datos ni leer respuestas; solo disparar una acción a ciegas. Son armas de **potencia muy distinta**.

> Esto también explica por qué las defensas **no son intercambiables**: un token anti-CSRF no hace nada contra XSS, y el output encoding/CSP no es, por sí solo, una defensa diseñada para CSRF. Cada ataque necesita **su propia** mitigación.

---

## 6. Ejemplo lado a lado (mismo objetivo, mecánica opuesta)

**Objetivo:** cambiar el email de la cuenta de la víctima en `banco.com`.

- **Con CSRF:** el atacante arma una página con un `<form>` auto-enviado a `banco.com/cambiar-email`. La víctima la abre, su navegador manda el POST **con la cookie**, el servidor cambia el email. El atacante **nunca ve la respuesta**; apostó a que la acción se ejecutara. Si el sitio exige un **token CSRF**, falla (no lo conoce).

- **Con XSS:** el atacante inyecta JS en `banco.com` (ej. en un comentario). Cuando la víctima entra, el código se ejecuta **dentro** del sitio, **lee el token CSRF del DOM**, y hace el `fetch` a `cambiar-email` con el token correcto — **e incluso lee la respuesta** para confirmar. Ninguna defensa anti-CSRF lo detiene, porque el código corre **como si fuera la propia página**.

Mismo objetivo, dos caminos opuestos: uno **fuerza una petición desde afuera** (CSRF), el otro **ejecuta código desde adentro** (XSS).

---

## 7. Conclusión

Aunque XSS y CSRF comparten que usan el **navegador de la víctima** para **atacar su cuenta**, sus mecánicas son **opuestas**. El **XSS** abusa de la **confianza del usuario en el sitio**: **inyecta y ejecuta código** en el navegador, ocurre en el **cliente**, el atacante **ve y controla** todo, y su alcance es **amplísimo** (robo de datos, cualquier acción). El **CSRF** abusa de la **confianza del sitio en el usuario**: **no ejecuta código**, solo **fuerza una petición forjada** que el **servidor** procesa gracias a la cookie que el navegador adjunta solo; el atacante es **ciego** y su alcance se limita a **una acción de cambio de estado**.

La diferencia fundamental, en síntesis: **XSS = ejecutar código en el cliente (confianza usuario→sitio); CSRF = forzar una acción en el servidor (confianza sitio→usuario).** Por eso el XSS es más poderoso (puede incluso vencer las defensas anti-CSRF) y por eso **cada uno exige su propia defensa**: encoding + CSP para XSS, token anti-CSRF + `SameSite` para CSRF.

---

*Fin del Objetivo 3 — Módulo X.*
