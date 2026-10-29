# Objetivo 4: Análisis del Ataque de Algoritmo "None" en JWT

**Curso:** Software Seguro  
**Tipo de actividad:** Investigación y análisis técnico  
**Fecha:** 29 de octubre de 2026

## 1. Introducción

JSON Web Token (JWT) es un formato compacto para transportar afirmaciones (*claims*) entre partes. Un JWT firmado (JWS) suele emplearse en autenticación y autorización para que un backend pueda verificar que los datos del token no fueron modificados por un tercero.

La vulnerabilidad del algoritmo `none` aparece cuando una aplicación que **debería exigir tokens firmados** acepta como válidos JWT sin firma criptográfica. Esto puede permitir suplantar identidades o elevar privilegios sin conocer la clave secreta ni la clave privada del emisor.

## 2. Estructura de un JWT

Un JWT compacto firmado normalmente tiene tres segmentos separados por puntos:

```text
BASE64URL(header).BASE64URL(payload).BASE64URL(signature)
```

- **Header:** indica el tipo de token y el algoritmo, por ejemplo `HS256`.
- **Payload:** contiene afirmaciones como `sub` (identidad), `role`, `iss`, `aud` o `exp`.
- **Signature:** protege la integridad del header y del payload mediante un mecanismo criptográfico.

Ejemplo conceptual de encabezado y contenido:

```json
{"alg":"HS256","typ":"JWT"}
```

```json
{"sub":"usuario123","role":"user","exp":1893456000}
```

La codificación Base64URL **no es cifrado**: el contenido del header y del payload puede decodificarse. La seguridad de un JWT firmado depende de la verificación correcta de su firma y de sus afirmaciones.

## 3. ¿Qué significa `alg: none`?

La especificación RFC 7519 contempla los llamados *Unsecured JWTs*, que indican `"alg":"none"` y tienen una firma vacía. Existen para casos específicos donde la integridad se protege por otro mecanismo externo. No deben aceptarse como credenciales de autenticación en una aplicación que requiere una firma.

Ejemplo conceptual de un JWT sin firma:

```text
BASE64URL({"alg":"none","typ":"JWT"}).BASE64URL({"sub":"usuario123","role":"user"}).
```

El **punto final permanece** porque representa el tercer segmento, vacío. Este ejemplo es esquemático y no es un token listo para utilizar.

## 4. Funcionamiento técnico del ataque

1. Una aplicación legítima emite JWT firmados, por ejemplo con `HS256` o `RS256`.
2. Un atacante que posee un JWT puede leer y modificar localmente su header y payload porque están codificados, no cifrados.
3. El atacante cambia el algoritmo declarado a `none` y deja vacío el segmento de firma.
4. En un backend vulnerable, el validador **confía en el algoritmo indicado por el propio token no confiable** y acepta la ausencia de firma.
5. Si además la aplicación toma las afirmaciones del token como identidad o permisos, puede tratar al atacante como otro usuario o administrador.

### ¿Por qué no necesita la clave secreta?

Con `HS256`, el servidor debería comprobar un HMAC calculado con una clave secreta. Con `RS256`, debería comprobar una firma usando la clave pública correspondiente al emisor. En cambio, al aceptar indebidamente `none`, **se omite la comprobación criptográfica**: el backend deja de exigir prueba de que el emisor legítimo creó el token. El atacante solo necesita construir texto codificado con afirmaciones falsas.

Por ejemplo, si un sistema vulnerable autoriza según `role`, cambiar `"role":"user"` por `"role":"admin"` podría permitir una escalada de privilegios. El efecto exacto depende de qué afirmaciones use el servidor y de si existen controles de autorización adicionales.

**Importante:** que una biblioteca conozca el algoritmo `none` no implica por sí solo que la aplicación sea vulnerable. La falla existe cuando el verificador lo acepta en un contexto que exige autenticación criptográfica.

## 5. Impacto sobre la seguridad

| Pilar o control | Posible consecuencia |
| --- | --- |
| Autenticación | Suplantación de usuarios mediante identidades inventadas en el token. |
| Autorización | Escalada de privilegios si el backend confía en claims modificados. |
| Confidencialidad | Acceso a información de otras cuentas, si no hay controles adicionales. |
| Integridad | Modificación de recursos en nombre de otros usuarios, según los permisos concedidos. |

La gravedad puede ser **alta o crítica** en una aplicación donde el JWT sea la principal prueba de identidad. No corresponde asignar un CVSS exacto sin conocer un sistema concreto y su impacto comprobado.

## 6. Causa raíz y clasificación

La causa principal es una **verificación insuficiente de la autenticidad del token**: se permite que datos controlados por el cliente determinen si la firma debe verificarse. Puede relacionarse con **CWE-347 (Improper Verification of Cryptographic Signature)** y **CWE-345 (Insufficient Verification of Data Authenticity)**, según el caso.

No se trata de descubrir la clave del servidor, sino de evitar que el servidor la utilice para validar el token.

## 7. Mitigaciones recomendadas

1. **Rechazar `alg: none`** para cualquier token usado como credencial de autenticación o autorización.
2. **Configurar una lista explícita de algoritmos permitidos** del lado del servidor (por ejemplo, solo `RS256` si ese es el algoritmo elegido). No decidir la política de seguridad basándose únicamente en el header recibido.
3. **Verificar siempre la firma** con la clave correcta y una biblioteca JWT actualizada, usando su función de verificación y no solo la de decodificación.
4. **Validar las afirmaciones** pertinentes: emisor (`iss`), audiencia (`aud`), vencimiento (`exp`), inicio de validez (`nbf`) y otras exigidas por el sistema.
5. **Aplicar autorización del lado del servidor** para cada recurso y operación; no confiar ciegamente en un campo `role` enviado por el cliente.
6. **Incluir pruebas automatizadas negativas** que confirmen que el backend rechaza tokens sin firma, con firmas inválidas o algoritmos no permitidos.

### Comportamiento esperado de una implementación segura

```text
JWT recibido
  -> ¿Algoritmo incluido en la lista permitida? NO -> Rechazar
  -> ¿Firma criptográfica válida? NO -> Rechazar
  -> ¿Claims obligatorios válidos? NO -> Rechazar
  -> ¿Usuario autorizado para la operación? NO -> Denegar
  -> Continuar con la solicitud
```

## 8. Conclusión

El ataque de algoritmo `none` demuestra que **no basta con recibir un JWT bien formado**. Si un backend acepta un token sin firma como prueba de identidad, el atacante puede fabricar afirmaciones arbitrarias sin conocer ninguna clave criptográfica. La defensa consiste en exigir algoritmos seguros preconfigurados, verificar firmas y claims, y mantener controles de autorización independientes.

Este informe es una investigación conceptual; **no se realizaron pruebas ni se confirmó una vulnerabilidad en una aplicación real**.

## 9. Referencias

- IETF, **RFC 7519 — JSON Web Token (JWT)**, secciones 6 y 7.2: https://www.rfc-editor.org/rfc/rfc7519.html
- OWASP, **JSON Web Token Cheat Sheet — Unsecured JWTs**: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html
- OWASP, **Web Security Testing Guide — Testing JSON Web Tokens**: https://owasp.org/www-project-web-security-testing-guide/
- PortSwigger, **JWT none algorithm supported**: https://portswigger.net/kb/issues/00200901_jwt-none-algorithm-supported
- PortSwigger, **JWT attacks**: https://portswigger.net/web-security/jwt
