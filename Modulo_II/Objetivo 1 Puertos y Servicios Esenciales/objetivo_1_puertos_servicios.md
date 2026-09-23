# Objetivo 1: Puertos y Servicios Esenciales

## Introducción

Los **puertos** permiten identificar los distintos servicios que se ejecutan en un servidor o dispositivo conectado a una red.

Podemos pensar una dirección IP como la dirección de un edificio y los puertos como sus diferentes puertas de entrada. Cada puerta puede estar asociada a un servicio específico, como una página web, transferencia de archivos, correo electrónico o acceso remoto.

A continuación se describen algunos de los puertos más utilizados y los servicios que funcionan habitualmente en ellos.

---

## Puerto 20 – FTP Data

* **Protocolo:** FTP (File Transfer Protocol)
* **Servicio:** Transferencia de archivos.
* **Descripción:** El puerto 20 se utiliza tradicionalmente en **FTP activo para la conexión de datos**, es decir, para transferir los archivos entre el cliente y el servidor.
* **Seguridad:** FTP tradicional no cifra la información transmitida.

---

## Puerto 21 – FTP Control

* **Protocolo:** FTP (File Transfer Protocol)
* **Servicio:** Control de transferencia de archivos.
* **Descripción:** Se utiliza para establecer la **conexión de control FTP**. Por este puerto se envían comandos, credenciales y solicitudes relacionadas con la transferencia de archivos.
* **Seguridad:** Al utilizar FTP tradicional, las credenciales pueden transmitirse sin cifrado.

---

## Puerto 22 – SSH

* **Protocolo:** SSH (Secure Shell)
* **Servicio:** Acceso remoto seguro.
* **Descripción:** Permite conectarse y administrar un servidor de manera remota mediante una conexión **cifrada**.
* **Ejemplo:** Un administrador puede conectarse a un servidor Linux utilizando SSH para ejecutar comandos de forma remota.

---

## Puerto 23 – Telnet

* **Protocolo:** Telnet
* **Servicio:** Acceso remoto.
* **Descripción:** Permite conectarse de forma remota a otro equipo para ejecutar comandos.
* **Seguridad:** A diferencia de SSH, **Telnet no cifra la comunicación**, por lo que actualmente se considera inseguro para su uso a través de redes no confiables.

---

## Puerto 25 – SMTP

* **Protocolo:** SMTP (Simple Mail Transfer Protocol)
* **Servicio:** Envío y transferencia de correo electrónico.
* **Descripción:** Se utiliza principalmente para la **transferencia de correos electrónicos entre servidores de correo**.
* **Ejemplo:** Un servidor de correo puede utilizar SMTP para enviar un mensaje hacia el servidor de correo del destinatario.

---

## Puerto 53 – DNS

* **Protocolo:** DNS (Domain Name System)
* **Servicio:** Resolución de nombres de dominio.
* **Descripción:** Permite traducir nombres de dominio, como `google.com`, a direcciones IP que las computadoras pueden utilizar para comunicarse.
* **Protocolos de transporte:** DNS tradicional puede utilizar tanto **UDP como TCP** en el puerto 53 dependiendo de la operación.

---

## Puerto 80 – HTTP

* **Protocolo:** HTTP (Hypertext Transfer Protocol)
* **Servicio:** Navegación web.
* **Descripción:** Se utiliza para acceder a sitios y aplicaciones web mediante HTTP.
* **Seguridad:** La información transmitida mediante HTTP **no se encuentra cifrada**, por lo que puede ser interceptada si no existen otras protecciones.

Ejemplo:

`http://ejemplo.com`

---

## Puerto 110 – POP3

* **Protocolo:** POP3 (Post Office Protocol Version 3)
* **Servicio:** Recepción de correo electrónico.
* **Descripción:** Permite que un cliente de correo descargue mensajes almacenados en un servidor.
* **Seguridad:** El uso tradicional del puerto 110 no proporciona cifrado por sí mismo. Para POP3 sobre TLS se utiliza habitualmente otro puerto, como el **995**.

---

## Puerto 443 – HTTPS

* **Protocolo:** HTTPS (HTTP sobre TLS)
* **Servicio:** Navegación web segura.
* **Descripción:** Permite acceder a sitios y aplicaciones web utilizando una conexión protegida mediante **TLS**.
* **Seguridad:** La comunicación entre el cliente y el servidor se cifra, proporcionando confidencialidad e integridad y permitiendo autenticar al servidor mediante certificados digitales.

Ejemplo:

`https://ejemplo.com`

---

## Puerto 3306 – MySQL

* **Protocolo/Servicio:** MySQL
* **Servicio:** Base de datos.
* **Descripción:** Es el puerto utilizado por defecto por el sistema de gestión de bases de datos **MySQL** para recibir conexiones de clientes.
* **Ejemplo:** Una aplicación Backend puede conectarse a un servidor MySQL mediante el puerto 3306 para consultar o modificar información almacenada en una base de datos.
* **Seguridad:** Generalmente no debería exponerse directamente a Internet sin controles de acceso adecuados.

---

## Resumen

|   Puerto | Servicio    | Función principal                         |
| -------: | ----------- | ----------------------------------------- |
|   **20** | FTP Data    | Transferencia de datos FTP en modo activo |
|   **21** | FTP Control | Control de conexiones FTP                 |
|   **22** | SSH         | Acceso remoto seguro                      |
|   **23** | Telnet      | Acceso remoto sin cifrado                 |
|   **25** | SMTP        | Transferencia de correo electrónico       |
|   **53** | DNS         | Resolución de nombres de dominio          |
|   **80** | HTTP        | Navegación web sin cifrado                |
|  **110** | POP3        | Recepción/descarga de correo electrónico  |
|  **443** | HTTPS       | Navegación web cifrada mediante TLS       |
| **3306** | MySQL       | Conexiones a bases de datos MySQL         |

---

## Conclusión

Conocer los puertos y los servicios asociados es fundamental para comprender cómo se comunican los sistemas dentro de una red.

También es importante desde el punto de vista de la **seguridad informática**, ya que cada puerto abierto representa un servicio accesible que debe estar correctamente configurado y protegido.

Antes de interactuar o realizar pruebas sobre un servidor, identificar los puertos abiertos permite conocer qué servicios se encuentran disponibles y comprender mejor la superficie de exposición del sistema.
