# Objetivo 1 - Mapeo de Arquitectura Lógica

## Aplicación seleccionada

Para representar el flujo de información se tomó como ejemplo el proceso de inicio de sesión de Easy Resolve.

## Flujo de información

1. El usuario ingresa su correo electrónico y contraseña en el formulario de login.

2. El Frontend captura los datos ingresados.

3. El Frontend realiza una petición hacia el Backend.

4. La comunicación entre el navegador y el servidor se realiza mediante HTTPS.

5. HTTPS utiliza TLS para cifrar la información durante su transmisión, evitando que las credenciales puedan ser leídas fácilmente si el tráfico es interceptado.

6. El Backend recibe la petición y realiza las validaciones correspondientes.

7. El Backend consulta la Base de Datos para verificar la existencia del usuario y validar sus credenciales.

8. La Base de Datos devuelve el resultado de la consulta al Backend.

9. El Backend procesa el resultado y genera una respuesta.

10. La respuesta vuelve al Frontend utilizando nuevamente una conexión HTTPS.

11. El Frontend informa al usuario si el inicio de sesión fue exitoso o si ocurrió un error.

## Diagrama de arquitectura

Usuario  
↓  
Frontend  
↓  
**HTTPS / TLS**  
↓  
Backend  
↓  
Base de Datos  
↓  
Backend  
↓  
**HTTPS / TLS**  
↓  
Frontend  
↓  
Usuario

## Protección HTTPS

La protección HTTPS se encuentra en la comunicación entre el Frontend y el Backend.

HTTPS permite proteger los datos mientras viajan por la red mediante TLS, proporcionando principalmente:

- Confidencialidad: los datos viajan cifrados.
- Integridad: permite detectar modificaciones durante la transmisión.
- Autenticación: permite verificar la identidad del servidor mediante certificados digitales.

Es importante aclarar que HTTPS no protege automáticamente la comunicación interna entre el Backend y la Base de Datos. Esa conexión debe contar con sus propios mecanismos de seguridad y cifrado.