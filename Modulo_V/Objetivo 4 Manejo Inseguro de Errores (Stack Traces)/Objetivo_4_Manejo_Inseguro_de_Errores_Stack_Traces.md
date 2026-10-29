# Objetivo 4: Manejo Inseguro de Errores (Stack Traces)

## 1. Introducción

El manejo de errores es un control importante en la seguridad de las aplicaciones web. Cuando ocurre una excepción, el servidor debe registrar la información técnica necesaria para diagnosticarla sin revelar detalles internos a quienes utilizan la aplicación. Una respuesta excesivamente detallada puede facilitar la recopilación de información para ataques posteriores.

## 2. Mensaje de error genérico frente a Stack Trace

### Mensaje de error genérico

Es una respuesta destinada al usuario final que informa que una operación no pudo completarse, sin exponer información interna del sistema.

**Ejemplo:**

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "No fue posible procesar la solicitud.",
  "requestId": "abc123"
}
```

El identificador `requestId` permite al equipo técnico localizar el incidente en registros internos, sin mostrar detalles de implementación. No debe contener secretos ni datos personales.

### Stack Trace (traza de pila)

Es una secuencia de llamadas a funciones o métodos que muestra cómo llegó el programa al punto donde se produjo una excepción. Resulta útil para desarrolladores, pero puede revelar información sensible si se entrega íntegra en una respuesta pública.

**Ejemplo ficticio de una exposición insegura:**

```text
HTTP/1.1 500 Internal Server Error

DatabaseConnectionError: connection failed
  at DatabaseClient.connect (/srv/app/src/db/client.js:42:15)
  at UserRepository.findById (/srv/app/src/repositories/users.js:87:9)
  at getUserProfile (/srv/app/src/controllers/profile.js:21:12)
Node.js v20.x
```

En este ejemplo se revelan nombres de componentes, rutas del servidor, líneas de código y una referencia a la tecnología utilizada. Es un ejemplo ilustrativo, no un hallazgo real.

## 3. Diferencias principales

| Aspecto | Mensaje genérico | Stack Trace expuesto |
|---|---|---|
| Destinatario | Usuario final | Personal de desarrollo/operaciones |
| Información mostrada | Descripción breve y referencia del incidente | Funciones, archivos, líneas, excepciones y contexto técnico |
| Utilidad para diagnóstico | Permite correlación mediante un ID | Aporta contexto técnico detallado |
| Riesgo de divulgación | Bajo, si está bien diseñado | Mayor, según los datos revelados |
| Uso recomendado en producción | Sí | No en respuestas accesibles al público |

## 4. ¿Por qué un Stack Trace facilita la explotación?

Una traza detallada puede reducir el esfuerzo de reconocimiento de un atacante porque:

1. **Revela tecnologías y componentes:** frameworks, librerías o motores de base de datos que permiten orientar la búsqueda de vulnerabilidades conocidas.
2. **Expone la estructura interna:** rutas absolutas, nombres de módulos, controladores y funciones que ayudan a comprender la arquitectura de la aplicación.
3. **Describe flujos de ejecución:** muestra qué componentes procesan una operación y dónde falla, lo que puede facilitar la identificación de superficies de ataque.
4. **Puede filtrar información sensible:** en implementaciones especialmente inseguras, los mensajes de excepción o los datos adjuntos pueden contener consultas SQL, nombres de tablas, rutas privadas, identificadores, tokens o credenciales.
5. **Ofrece retroalimentación técnica:** los errores detallados pueden ayudar a interpretar el comportamiento de la aplicación ante entradas inesperadas, incluso cuando no prueban por sí solos una vulnerabilidad explotable.

**Importante:** un Stack Trace no concede automáticamente acceso al sistema ni demuestra que exista una vulnerabilidad explotable. Su gravedad depende de la información expuesta y de si esta permite un impacto real sobre la confidencialidad, integridad o disponibilidad.

## 5. Riesgos y clasificación

La exposición de trazas puede constituir una **divulgación de información por mensajes de error**, relacionada con **CWE-209: Generation of Error Message Containing Sensitive Information**. Si además se muestran datos secretos, el impacto puede ser mayor.

No existe un puntaje CVSS universal para todas las trazas expuestas: debe calcularse según el escenario y el impacto demostrado. Una traza que únicamente muestra nombres de funciones no tiene necesariamente la misma criticidad que otra que revela credenciales válidas.

## 6. Medidas de mitigación

- **Desactivar el modo debug en producción** y evitar páginas de error de desarrollo accesibles al público.
- **Implementar un manejador global de excepciones** que devuelva mensajes genéricos y códigos HTTP adecuados.
- **Registrar las trazas completas solo en sistemas internos de observabilidad**, con acceso restringido y retención definida.
- **No incluir secretos en excepciones o logs:** redactar contraseñas, tokens, datos personales y cadenas de conexión.
- **Usar identificadores de correlación** para asociar el error público con el registro técnico interno.
- **Validar el comportamiento ante errores** durante las pruebas y el despliegue, verificando que no se filtren detalles de implementación.
- **Aplicar controles de acceso y monitoreo** a registros, herramientas de diagnóstico y plataformas de seguimiento de errores.

### Ejemplo de respuesta segura

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "message": "Ocurrió un error inesperado. Intentá nuevamente más tarde.",
  "requestId": "req-7f92"
}
```

El servidor conserva la traza técnica en un registro interno vinculado a `req-7f92`, sin devolverla al navegador.

## 7. Conclusión

La diferencia esencial entre un mensaje genérico y un Stack Trace es la **cantidad y sensibilidad de la información expuesta**. El primero informa del fallo sin revelar cómo funciona internamente la aplicación; el segundo puede mostrar detalles valiosos para el diagnóstico, pero también para el reconocimiento de un atacante. En producción, la práctica recomendada es separar la información pública de los registros técnicos internos y proteger ambos adecuadamente.

## 8. Referencias

- MITRE, **CWE-209 — Generation of Error Message Containing Sensitive Information**: https://cwe.mitre.org/data/definitions/209.html
- OWASP, **Error Handling Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html
- OWASP Web Security Testing Guide, **Testing for Improper Error Handling**: https://owasp.org/www-project-web-security-testing-guide/

---

**Modalidad:** investigación teórica. Los ejemplos son ficticios y no implican pruebas sobre sistemas reales.
