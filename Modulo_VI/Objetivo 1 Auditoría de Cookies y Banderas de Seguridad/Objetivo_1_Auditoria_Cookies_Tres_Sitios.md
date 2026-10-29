# Objetivo 1: Auditoría de Cookies y Banderas de Seguridad

**Módulo:** Seguridad de aplicaciones web  
**Fecha de observación:** 29 de octubre de 2026  
**Herramienta:** Firefox Developer Tools → Storage → Cookies  
**Modalidad:** inspección pasiva de tres sitios web públicos, sin modificar peticiones ni intentar explotación.

## 1. Objetivo

Examinar las banderas `HttpOnly` y `Secure` de las cookies visibles en tres sitios públicos y explicar su relevancia para la protección de sesiones. La evaluación se limita a las cookies presentes durante las visitas capturadas; no constituye una auditoría exhaustiva ni prueba de vulnerabilidad.

## 2. Fundamentos técnicos

### Bandera `HttpOnly`

Cuando una cookie tiene `HttpOnly`, los scripts ejecutados en la página no pueden leerla mediante `document.cookie`. Esto reduce la posibilidad de que un ataque de *Cross-Site Scripting* (XSS) robe directamente el valor de esa cookie. **No impide por sí sola un XSS**, ni evita que el navegador envíe la cookie automáticamente en solicitudes HTTP correspondientes.

### Bandera `Secure`

Cuando una cookie tiene `Secure`, el navegador restringe su envío a conexiones seguras HTTPS (con excepciones locales definidas por navegadores). Si una **cookie de sesión** carece de `Secure`, podría enviarse por una conexión HTTP no cifrada si el sitio o una ruta permiten esa comunicación. Esto expone el identificador de sesión a interceptación en redes inseguras y podría facilitar un secuestro de sesión. El riesgo efectivo depende de la configuración del sitio, sus redirecciones, HSTS y la posibilidad real de acceder por HTTP.

### Consideración sobre `SameSite`

`SameSite` controla en qué contextos entre sitios se envía una cookie y puede contribuir a reducir algunos escenarios de CSRF. No reemplaza `HttpOnly` ni `Secure`.

**Importante:** una cookie que vence al cerrar el navegador no es necesariamente una cookie de autenticación. Tampoco la ausencia de `HttpOnly` en cookies de preferencias o analítica constituye automáticamente una vulnerabilidad.

## 3. Metodología

1. Acceder a cada sitio mediante HTTPS con Firefox.
2. Abrir las herramientas de desarrollo (`F12`).
3. Ingresar a **Storage → Cookies** y seleccionar el dominio.
4. Registrar los nombres de cookies y los valores booleanos de `HttpOnly` y `Secure`, sin copiar los valores secretos de las cookies.
5. Distinguir cookies potencialmente relacionadas con sesión de cookies técnicas o de preferencias y evitar inferir vulnerabilidades sin confirmar su finalidad.

## 4. Resultados observados

### 4.1 Wikipedia

**URL visitada:** `https://en.wikipedia.org/wiki/Soda_Stereo`  
**Contexto:** navegación pública sin inicio de sesión visible.

| Cookie (nombre visible en captura) | HttpOnly | Secure | Observación |
|---|---|---|---|
| `enwikimwuser-s...` | No | No | Expira como `Session` en Firefox; finalidad exacta no confirmada. |
| `GeoIP` | No | Sí | Asociada a información geográfica. |
| `NetworkProbeLi...` | No | Sí | Cookie técnica; nombre truncado. |
| `WMF-DP` | Sí | Sí | Ambas banderas activas. |
| `WMF-Last-Acce...` | Sí | Sí | Ambas banderas activas. |
| `WMF-Last-Access` | Sí | Sí | Ambas banderas activas. |
| `WMF-Uniq` | Sí | Sí | Ambas banderas activas. |

**Interpretación:** se observó al menos una cookie sin `HttpOnly` ni `Secure`. No se comprobó que fuese un token de autenticación, por lo que no es correcto concluir que se expuso una sesión autenticada.

### 4.2 Mercado Libre Argentina

**URL visitada:** `https://www.mercadolibre.com.ar`  
**Contexto:** visita al sitio; el estado de autenticación no se verificó independientemente.

| Cookie (nombre visible en captura) | HttpOnly | Secure | Observación |
|---|---|---|---|
| `_csrf` | Sí | Sí | Nombre compatible con mecanismo CSRF; función no verificada. |
| `_d2id` | No | Sí | Identificador técnico o de dispositivo. |
| `_hjSession...` (dos entradas) | No | Sí | Probables cookies de analítica. |
| `cp` | Sí | Sí | Ambas banderas activas. |
| `ftid` | Sí | Sí | Ambas banderas activas. |
| `g_state` | No | No | Carece de ambas banderas; no se determinó si contiene datos sensibles. |
| `nsa_rotok` | Sí | Sí | Posible token relacionado con seguridad; sin confirmación funcional. |
| `NSESSION...` | Sí | Sí | Nombre compatible con sesión; ambas banderas activas. |
| `ssid` | Sí | Sí | Nombre compatible con identificador de sesión; ambas banderas activas. |

**Interpretación:** algunas cookies potencialmente sensibles presentan ambas protecciones. La cookie `g_state` no tiene `HttpOnly` ni `Secure`, pero no se acreditó que sea una cookie de autenticación. En la captura también se observan otras cookies de preferencias y seguimiento que no se clasifican como sesiones por su nombre únicamente.

### 4.3 GitHub

**URL visitada:** `https://github.com`  
**Contexto:** navegación pública; la interfaz muestra la opción «Sign in».

| Cookie (nombre visible en captura) | HttpOnly | Secure | SameSite |
|---|---|---|---|
| `_gh_sess` | Sí | Sí | Lax |
| `_octo` | No | Sí | Lax |
| `cpu_bucket` | No | Sí | Lax |
| `logged_in` | Sí | Sí | Lax |
| `preferred...` | No | Sí | Lax |
| `tz` | No | Sí | Lax |

**Interpretación:** todas las cookies mostradas tienen `Secure`. Las cookies `_gh_sess` y `logged_in` también tienen `HttpOnly`. La falta de `HttpOnly` en cookies de preferencias no demuestra una falla de seguridad.

## 5. Comparación

| Sitio | Observación principal | ¿Vulnerabilidad de sesión confirmada? |
|---|---|---|
| Wikipedia | Una cookie visible sin `HttpOnly` y `Secure`; uso de autenticación no confirmado. | No |
| Mercado Libre | Cookies posiblemente sensibles con ambas banderas; `g_state` sin ellas. | No |
| GitHub | Todas las cookies observadas con `Secure`; `_gh_sess` con ambas banderas. | No |

## 6. Riesgos y recomendaciones

- Aplicar `Secure` a todas las cookies que contengan identificadores de sesión o datos sensibles y servir el sitio exclusivamente por HTTPS.
- Aplicar `HttpOnly` a las cookies de autenticación que no necesiten acceso desde JavaScript.
- Configurar `SameSite` apropiadamente y emplear protecciones CSRF cuando corresponda.
- Evaluar HSTS para reducir riesgos de navegación HTTP, sin considerarlo sustituto de `Secure`.
- Evitar almacenar información confidencial directamente en cookies legibles por JavaScript.
- Revisar el propósito de cada cookie antes de calificar la ausencia de una bandera como vulnerabilidad.

## 7. Conclusión

La inspección pasiva de Wikipedia, Mercado Libre Argentina y GitHub permitió observar distintas configuraciones de cookies. Se identificaron cookies sin alguna bandera, pero **no se demostró que una cookie de autenticación sensible estuviera expuesta**. GitHub mostró `Secure` habilitado en todas las cookies visibles, mientras que Mercado Libre y Wikipedia incluyeron cookies con configuraciones diferentes según su aparente función.

`HttpOnly` protege el valor de una cookie frente a lecturas directas desde JavaScript; `Secure` evita su transmisión habitual por HTTP sin cifrar. En una cookie de sesión, la ausencia de `Secure` puede aumentar el riesgo de interceptación y secuestro de sesión cuando existe una vía HTTP utilizable.

## 8. Evidencia y limitaciones

Las observaciones proceden de tres capturas de pantalla del panel **Storage → Cookies** de Firefox aportadas para este ejercicio el 29/10/2026. Los nombres truncados se mantienen como aparecen en pantalla. No se inspeccionaron respuestas `Set-Cookie` completas, ni se verificó el funcionamiento interno de cada cookie. El resultado refleja únicamente el estado visible en el momento de la captura. **No deben publicarse los valores de las cookies en un repositorio o informe**, ya que podrían incluir identificadores sensibles.

## 9. Referencias

- MDN Web Docs, *Set-Cookie*: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
- OWASP, *Session Management Cheat Sheet*: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- OWASP, *Secure Cookie Attribute*: https://owasp.org/www-community/controls/SecureCookieAttribute
