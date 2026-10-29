# Objetivo 2: Ingeniería Inversa a JSON Web Tokens (JWT)

## 1. Objetivo
Interceptar un JWT válido en una aplicación web de laboratorio, decodificar su estructura e identificar el algoritmo de firma y los datos contenidos en el Payload.

## 2. Entorno y metodología
- **Plataforma:** PortSwigger Web Security Academy (laboratorio de autenticación JWT).
- **Fecha de observación:** 29/10/2026.
- **Navegador:** Firefox, herramientas de desarrollador.
- **Solicitud observada:** `GET /` sobre el dominio temporal del laboratorio, respuesta HTTP `200`.
- **Ubicación del token:** cabecera HTTP `Cookie`, bajo el nombre `session`.
- **Procedimiento:** se inició sesión con una cuenta de prueba, se inspeccionó una solicitud posterior en la pestaña **Network**, y se identificó una cookie `session` con tres segmentos separados por puntos. Se decodificaron localmente los dos primeros segmentos mediante Base64URL, sin necesidad de la clave secreta.

> **Protección de evidencia:** se omite el JWT completo y su firma en este documento porque un token de sesión vigente puede actuar como credencial de acceso.

## 3. Estructura técnica
Un JWT firmado (JWS en formato compacto) suele presentar esta estructura:

```text
BASE64URL(Header).BASE64URL(Payload).BASE64URL(Signature)
```

- **Header:** describe el algoritmo criptográfico y otros metadatos.
- **Payload:** contiene declaraciones (*claims*) sobre el emisor, el sujeto y la validez del token.
- **Signature:** permite verificar la integridad y autenticidad del contenido cuando el servidor aplica correctamente la validación.

La codificación Base64URL **no cifra** los datos. Cualquier persona que posea el token puede leer el Header y el Payload.

## 4. Resultados reales de la decodificación

### Header

```json
{
  "kid": "0dc46b96-c1b2-4c7a-9f8c-bd9fff50c00a",
  "alg": "HS256"
}
```

- `alg: HS256`: algoritmo HMAC-SHA256, que utiliza una clave secreta compartida para generar y verificar la firma.
- `kid`: identificador de clave, utilizado para seleccionar la clave correspondiente. **No es la clave secreta.**

### Payload

```json
{
  "iss": "portswigger",
  "exp": 1793314108,
  "sub": "wiener"
}
```

| Claim | Valor observado | Interpretación |
|---|---|---|
| `iss` | `portswigger` | Emisor del token |
| `exp` | `1793314108` | Vencimiento expresado como tiempo Unix (segundos) |
| `sub` | `wiener` | Sujeto o usuario al que corresponde el token |

**Datos expuestos en texto legible:** el identificador de usuario `wiener`, el emisor y el vencimiento. **No se observaron** contraseñas, direcciones de correo electrónico ni un claim explícito de rol o privilegios. La identidad de usuario es información de autenticación que puede resultar útil para un atacante, aunque su mera presencia no demuestra una vulnerabilidad.

## 5. Interpretación de seguridad
El token está **firmado con HS256**, no cifrado. Por tanto, sus claims pueden decodificarse sin conocer la clave del servidor. Sin embargo, leer el contenido **no equivale a falsificarlo**: para producir una firma válida de HS256 se necesita la clave secreta, y el servidor debe comprobarla correctamente.

La exposición de un JWT completo sí puede ser peligrosa porque, si funciona como token portador y continúa vigente, un tercero podría reutilizarlo. Por esa razón, las evidencias del informe omiten el valor completo de la cookie y la firma.

## 6. Medidas recomendadas
1. Validar siempre la firma, el algoritmo permitido y los claims relevantes (`exp`, `iss`, `aud` cuando corresponda).
2. No incluir contraseñas, secretos ni datos personales innecesarios en el Payload.
3. Proteger las cookies de sesión con `Secure`, `HttpOnly` y una política `SameSite` adecuada al caso.
4. Utilizar HTTPS y limitar la duración de los tokens.
5. Evitar registrar o publicar JWT completos en capturas, tickets y repositorios.

## 7. Conclusión
Se interceptó y decodificó satisfactoriamente un JWT de sesión en un laboratorio autorizado de PortSwigger. Se identificó el algoritmo **HS256** en el Header y los claims **`iss`, `exp` y `sub`** en el Payload. El token revela el nombre del usuario de prueba, pero no incluye roles explícitos ni secretos. La práctica demuestra que la firma protege la integridad del token, **no la confidencialidad** de sus datos.

## 8. Referencias
- RFC 7519 — JSON Web Token (JWT): https://www.rfc-editor.org/rfc/rfc7519
- RFC 7515 — JSON Web Signature (JWS): https://www.rfc-editor.org/rfc/rfc7515
- PortSwigger Web Security Academy — JWT authentication: https://portswigger.net/web-security/jwt
- OWASP JSON Web Token Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
