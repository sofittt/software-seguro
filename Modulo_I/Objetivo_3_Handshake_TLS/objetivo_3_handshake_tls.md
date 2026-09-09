# Objetivo 3 – Profundización Técnica: TLS Handshake

## ¿Qué es el TLS Handshake?

Cuando ingresamos a una página que utiliza **HTTPS**, el navegador y el servidor
no comienzan a intercambiar información inmediatamente.

Antes realizan un proceso llamado **TLS Handshake**, que significa "apretón de manos".

Podemos imaginarlo como una presentación entre el navegador y el servidor.
Ambos se ponen de acuerdo sobre cómo van a comunicarse de manera segura antes
de comenzar a intercambiar información.

---

## ¿Cómo funciona?

De forma simplificada, el proceso ocurre de la siguiente manera:

1. **El navegador se conecta al servidor**

   Cuando escribimos una dirección que comienza con `https://`, el navegador
   le indica al servidor que quiere establecer una conexión segura.

2. **El servidor se identifica**

   El servidor responde y envía su **certificado digital**.

   Este certificado funciona de forma parecida a un documento de identidad
   del sitio web.

3. **El navegador verifica el certificado**

   El navegador revisa que el certificado sea válido, que corresponda al
   dominio que estamos visitando y que haya sido emitido o respaldado por
   una entidad de confianza.

   Por ejemplo, si ingresamos a:

   `https://app.softwareseguro.com.ar`

   el navegador verifica que el certificado corresponda a ese sitio.

4. **Se establece una clave segura**

   Una vez que el navegador confía en el servidor, ambos realizan un
   intercambio criptográfico para generar claves que solamente ellos
   podrán utilizar durante esa conexión.

5. **Se crea el canal seguro**

   Cuando el proceso termina, navegador y servidor ya tienen las claves
   necesarias para proteger la información.

   A partir de ese momento comienza el intercambio de las peticiones y
   respuestas HTTP de manera protegida.

Podemos representarlo de forma sencilla así:

Usuario
   |
   v
Navegador
   |
   | ---- Quiero conectarme de forma segura ---->
   |
   | <---- Servidor + Certificado digital -------
   |
   | ---- Verificación del certificado ----------
   |
   | <---- Acuerdo de claves ------------------->
   |
   | ===== CONEXIÓN SEGURA ESTABLECIDA =========
   |
   | ---- Petición HTTP protegida --------------->
   |
Servidor

---

## ¿Qué función cumplen los certificados digitales?

El **certificado digital** sirve principalmente para comprobar la identidad
del servidor.

Podemos compararlo con un documento de identidad.

Cuando entramos a una página HTTPS, el servidor presenta su certificado y
el navegador comprueba que sea válido y que corresponda al sitio al que
queremos ingresar.

Esto ayuda a evitar que un atacante pueda hacerse pasar fácilmente por el
servidor verdadero.

---

## ¿Por qué se utilizan dos tipos de cifrado?

TLS utiliza mecanismos de criptografía **asimétrica** y **simétrica** porque
cada uno tiene una función diferente.

### Cifrado asimétrico

Utiliza claves diferentes pero relacionadas: una **clave pública** y una
**clave privada**.

En TLS se utiliza durante el inicio de la conexión para ayudar a autenticar
al servidor y establecer de manera segura las claves que se utilizarán en
la comunicación.

El problema es que este tipo de criptografía requiere más procesamiento.

### Cifrado simétrico

Una vez establecida la conexión segura, se utilizan **claves de sesión**
para proteger la información que viaja entre el navegador y el servidor.

Este método es mucho más rápido y eficiente para proteger grandes
cantidades de información.

Por ejemplo:

- Datos de formularios.
- Usuarios y contraseñas.
- Cookies.
- Tokens.
- Peticiones a una API.
- Respuestas del servidor.

---

## ¿Por qué se combinan?

La idea puede resumirse de esta manera:

**Primero se establece la confianza y las claves de forma segura**
            ↓
**Se generan las claves de sesión**
            ↓
**Se utiliza cifrado simétrico para proteger la comunicación**

De esta manera, TLS aprovecha lo mejor de ambos mecanismos.

La criptografía asimétrica ayuda a establecer una conexión segura entre
dos equipos que inicialmente no compartían un secreto, mientras que la
criptografía simétrica permite proteger la comunicación posterior de
forma rápida y eficiente.

---

## Conclusión

El **TLS Handshake** es el proceso que realizan el navegador y el servidor
antes de comenzar a intercambiar información mediante HTTPS.

Durante este proceso, el servidor demuestra su identidad utilizando un
certificado digital y ambas partes establecen las claves necesarias para
proteger la conexión.

Una vez terminado el handshake, comienza la comunicación HTTP protegida
por TLS.

Por eso podemos resumirlo como:

**HTTP + TLS = HTTPS**

HTTPS permite proteger la información mientras viaja entre el navegador
y el servidor. Sin embargo, no significa que el sitio sea completamente
seguro, ya que todavía podría tener vulnerabilidades como SQL Injection,
XSS u otros problemas en su código.