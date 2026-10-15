# Reporte técnico de vulnerabilidad

**Laboratorio:** Turnero — Software Seguro  
**Fecha:** 15 de octubre de 2026  
**Identificador:** SEC-TUR-001  
**Hallazgo:** Control de acceso a nivel de objeto insuficiente (IDOR)  
**Clasificación:** CWE-639 / CWE-862 (relacionada)  
**Severidad:** **Alta — CVSS v3.1: 8.8**  
**Estado:** Vulnerabilidad observada en laboratorio; remediación pendiente de verificar  
**Alcance:** API de gestión de turnos, entorno de práctica autorizado

## 1. Resumen ejecutivo

Se identificó una debilidad en la autorización de operaciones sobre turnos médicos. Durante el laboratorio fue posible consultar identificadores de turnos y eliminar registros correspondientes a otro usuario (`xdalvik`) desde una sesión distinta. El riesgo principal es que un usuario autenticado altere o suprima reservas ajenas sin una validación de propiedad del recurso en el servidor.

**Impacto de negocio:** cancelaciones no autorizadas, pérdida de confianza en la agenda y posible exposición de información de citas. Se recomienda validar la titularidad y permisos en cada solicitud, independientemente de lo que permita la interfaz.

## 2. Detalles técnicos

- **Activo:** API REST del Turnero.
- **Superficie:** consulta y eliminación de turnos por identificador.
- **Condición:** sesión autenticada de un usuario distinto del titular.
- **Debilidad:** ausencia o insuficiencia de controles de autorización por objeto (BOLA/IDOR).

**Contexto observado:** se consultó `GET /api/1/appointments/` y, con la pista del ejercicio, se revisaron identificadores entre 90 y 105 hasta encontrar turnos con el campo `user` igual a `xdalvik`. Luego se enviaron solicitudes `DELETE` dirigidas a los identificadores encontrados. No se conservan aquí capturas ni respuestas HTTP completas que permitan atribuir códigos de estado a cada operación.

## 3. Evaluación CVSS

**CVSS v3.1: 8.8 (Alta)**  
**Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`

| Métrica | Valor | Justificación |
|---|---|---|
| AV — Vector de ataque | N (Red) | Explotación mediante API accesible por red. |
| AC — Complejidad | L (Baja) | No se requiere una condición compleja adicional. |
| PR — Privilegios | L (Bajos) | Se utiliza una sesión autenticada estándar. |
| UI — Interacción del usuario | N (Ninguna) | No requiere acción de la víctima. |
| S — Alcance | U (Sin cambios) | Impacto en el mismo componente vulnerable. |
| C — Confidencialidad | H (Alta) | Escenario de posible exposición amplia de datos de citas. |
| I — Integridad | H (Alta) | Eliminación no autorizada de turnos. |
| A — Disponibilidad | H (Alta) | Posibilidad de suprimir reservas y afectar la agenda. |

> **Supuesto del cálculo:** el puntaje 8.8 representa un escenario de acceso a datos sensibles y borrado amplio de turnos. Si la exposición o el alcance real fueran menores, se debe recalcular el score a partir de evidencias.

## 4. Prueba de concepto (PoC) reproducible

**Prerrequisitos:** entorno de laboratorio autorizado, sesión de prueba de un usuario que no sea `xdalvik` y al menos un turno de prueba asignado a `xdalvik`. Ejecutar únicamente sobre datos de laboratorio.

1. **Iniciar sesión.** Autenticarse como el usuario de prueba (en la práctica se utilizó una sesión de `luis`). Registrar la cookie de sesión en el cliente HTTP, sin incluirla en el reporte.
2. **Consultar la API.** Enviar `GET /api/1/appointments/` y revisar la estructura de los registros: `id`, `user`, `user_id`, `clinic`, `date`.
3. **Identificar un turno ajeno.** Inspeccionar los IDs 90 a 105 mediante consultas `GET` hasta encontrar un registro cuyo `user` sea `xdalvik`. Anotar su ID como `ID_OBJETIVO`.
4. **Verificar autorización de lectura.** Con la sesión del otro usuario, consultar el recurso correspondiente a `ID_OBJETIVO`. Registrar la respuesta y comprobar si revela información del titular sin permiso.
5. **Probar la eliminación.** Sobre una copia de datos o un turno recuperable, enviar `DELETE /api/appointments/ID_OBJETIVO` con la misma sesión. **La ruta exacta es ilustrativa y debe validarse** en Network o en la documentación del laboratorio antes de ejecutarla.
6. **Confirmar el resultado.** Repetir la consulta `GET` y verificar si el turno fue eliminado. Si se borra pese a que el usuario de sesión no es titular ni administrador, queda demostrada la falla. Restaurar el turno de prueba.

**Resultado esperado en un sistema seguro:** `403 Forbidden` o `404 Not Found`, sin revelar información y sin eliminar el turno.

**Resultado observado en el ejercicio:** se logró eliminar turnos identificados como pertenecientes a `xdalvik`. No se dispone de las solicitudes y respuestas HTTP originales para una verificación independiente completa.

## 5. Recomendaciones de remediación

- Aplicar autorización del lado del servidor en cada operación `GET`, `DELETE` y demás métodos, comprobando titularidad del turno o un rol administrativo explícito.
- No confiar en los identificadores de la URL, los campos enviados por el cliente ni las restricciones visibles en la interfaz.
- Aplicar el principio de mínimo privilegio y políticas de acceso por recurso; registrar accesos y eliminaciones con identidad, fecha e ID afectado.
- Agregar pruebas automatizadas negativas: un usuario A no debe consultar ni borrar turnos de B; validar respuestas `403/404` y ausencia de efectos en base de datos.
- Evaluar mecanismos de recuperación y auditoría de eliminaciones, así como alertas ante patrones de borrado anómalos.

## 6. Criterios de aceptación y retest

Con dos cuentas de prueba y turnos separados, verificar:

1. El titular puede operar sobre sus propios turnos.
2. Otro usuario recibe una denegación de acceso.
3. Ningún registro ajeno se modifica o elimina.
4. El rol administrador, si existe, solo accede conforme a permisos documentados.
5. Los eventos quedan auditados.

Adjuntar evidencia de las respuestas HTTP y del estado de los datos antes y después de las pruebas.

## 7. Valor para el cliente y limitaciones

El **resumen ejecutivo** permite priorizar el riesgo; los **detalles técnicos y la PoC** ayudan a reproducirlo; **CVSS** comunica la severidad mediante criterios comparables; y las **recomendaciones y criterios de retest** permiten al equipo de desarrollo corregir la falla y a QA verificar su resolución.

Este reporte se basa en el ejercicio ya realizado. **No se ejecutaron nuevas pruebas** ni se dispone de capturas o tráfico HTTP original para adjuntar.

## 8. Referencias

- [OWASP API Security Top 10 — API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [MITRE CWE-639 — Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)
- [FIRST — CVSS v3.1 Specification](https://www.first.org/cvss/v3.1/specification-document)
- [FIRST — CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)
