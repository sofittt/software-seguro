# Objetivo 2: Análisis de la Tríada CIA

## Introducción

La **tríada CIA** es un modelo básico de seguridad de la información. Sus siglas provienen del inglés *Confidentiality, Integrity, Availability* y representan tres propiedades que debemos proteger: **confidencialidad, integridad y disponibilidad**. Aunque se analizan por separado, un mismo incidente puede afectar a más de una.

## 1. Confidencialidad

**¿Qué significa?** Que la información solo pueda ser consultada por personas o sistemas autorizados. No alcanza con que los datos estén guardados: también hay que evitar que alguien acceda a información que no le corresponde.

**Ejemplo de vulnerabilidad web: IDOR (Insecure Direct Object Reference).**

Supongamos que una aplicación permite ver una factura mediante la URL `https://ejemplo.com/facturas/1001`. Si un usuario autenticado cambia el identificador a `1002` y puede ver la factura de otra persona porque el servidor no verifica que le pertenezca, existe una falla de control de acceso.

- **Pilar afectado principalmente:** confidencialidad.
- **Por qué:** se divulga información privada a alguien que no tiene permiso para verla.
- **Medida preventiva:** comprobar la autorización del usuario para cada recurso solicitado, del lado del servidor.

## 2. Integridad

**¿Qué significa?** Que los datos se mantengan correctos y completos, y que solo se modifiquen mediante acciones autorizadas. El objetivo es poder confiar en que la información no fue alterada indebidamente.

**Ejemplo de vulnerabilidad web: modificación no autorizada de parámetros (parameter tampering).**

Imaginemos una tienda en línea que recibe desde el navegador un precio como `precio=15000`. Si el servidor acepta sin validación un valor modificado, por ejemplo `precio=100`, un atacante podría alterar el importe de una compra.

- **Pilar afectado principalmente:** integridad.
- **Por qué:** se modifica un dato relevante de la transacción sin autorización.
- **Medida preventiva:** calcular y validar los precios en el servidor, sin confiar en los valores enviados por el cliente.

## 3. Disponibilidad

**¿Qué significa?** Que los sistemas y la información estén accesibles para los usuarios autorizados cuando los necesiten. Un servicio puede mantener los datos privados y correctos, pero si nadie puede usarlo, sigue existiendo un problema de seguridad.

**Ejemplo de ataque web: denegación de servicio distribuida (DDoS).**

Un sitio de turnos recibe una cantidad masiva de solicitudes desde múltiples equipos. El servidor o su infraestructura se saturan y los usuarios legítimos ya no pueden ingresar ni reservar turnos.

- **Pilar afectado principalmente:** disponibilidad.
- **Por qué:** el servicio deja de responder o se vuelve inutilizable.
- **Medida preventiva:** aplicar limitación de solicitudes (*rate limiting*), protección anti-DDoS y mecanismos de escalado y monitoreo.

## Comparación de los tres pilares

| Pilar | Pregunta clave | Vulnerabilidad o ataque de ejemplo | Consecuencia principal |
|---|---|---|---|
| **Confidencialidad** | ¿Quién puede ver los datos? | IDOR con lectura de facturas ajenas | Exposición de información privada |
| **Integridad** | ¿Quién puede modificar los datos? | Manipulación del precio enviado al servidor | Alteración no autorizada de información |
| **Disponibilidad** | ¿Se puede acceder al servicio cuando se necesita? | DDoS contra un sitio web | Interrupción del servicio |

## Conclusión

La tríada CIA permite identificar **qué aspecto de la seguridad está en riesgo**. Un IDOR que expone datos afecta principalmente la confidencialidad; una modificación indebida de precios compromete la integridad; y un DDoS que impide usar un sitio perjudica la disponibilidad. Para desarrollar aplicaciones seguras es necesario proteger los tres pilares, porque ninguno reemplaza a los demás.

## Referencias de consulta

- NIST Computer Security Resource Center — Glosario: https://csrc.nist.gov/glossary
- OWASP — Insecure Direct Object Reference Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html
- OWASP — Web Security Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
