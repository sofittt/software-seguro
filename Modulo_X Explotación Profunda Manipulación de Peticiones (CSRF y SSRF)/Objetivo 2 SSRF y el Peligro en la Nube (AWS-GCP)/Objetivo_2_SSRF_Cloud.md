# Objetivo 2 — SSRF y el Peligro en la Nube (AWS/GCP)

**Módulo X · Manipulación de Peticiones (CSRF y SSRF)**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. ¿Qué es un SSRF?

**SSRF (Server-Side Request Forgery / Falsificación de Petición del Lado del Servidor)** es una vulnerabilidad donde el atacante logra que **el servidor haga peticiones HTTP a una dirección que el atacante elige**. En vez de que el servidor hable con los destinos previstos, el atacante lo **usa como "proxy"** para alcanzar lugares a los que él **no podría llegar directamente**.

La diferencia clave con el CSRF: en CSRF el que hace la petición forjada es el **navegador de la víctima**; en SSRF el que la hace es **el servidor**. Y eso es mucho más peligroso, porque **el servidor suele estar dentro de la red interna**, con acceso a recursos privados que desde internet están bloqueados.

### ¿Dónde aparece?
En cualquier funcionalidad donde la app **toma una URL del usuario y la va a buscar**: un campo "importar imagen desde URL", un conversor de documentos, un generador de PDFs desde una web, un webhook, un "probar esta URL". Si el servidor pide esa URL **sin validar a dónde apunta**, el atacante le pasa una dirección **interna** en vez de una pública.

---

## 2. El escenario: SSRF en una app alojada en AWS → `169.254.169.254`

La app tiene un campo tipo "cargá tu avatar desde una URL". Normalmente el usuario pone `https://misitio.com/foto.jpg` y el servidor la descarga. El atacante, en cambio, pone:

```
http://169.254.169.254/latest/meta-data/
```

Y fuerza al servidor a hacerle un `GET` **a esa dirección mágica**. ¿Qué es y por qué es catastrófico?

### 2.1 Qué es `169.254.169.254` — el "Metadata Service"
`169.254.169.254` es una **dirección IP especial (link-local)** que en los proveedores de nube (**AWS, GCP, Azure, etc.**) apunta al **Instance Metadata Service (IMDS)**: un servicio interno **al que solo puede acceder la propia máquina virtual desde adentro**. Sirve para que la instancia consulte datos sobre sí misma: su nombre, su región, su configuración y —lo crítico— **sus credenciales de acceso temporales**.

Desde internet **no se puede llegar** a esa IP. Pero el **servidor vulnerable SÍ puede**, porque está **dentro** de la nube. El SSRF le presta al atacante ese acceso privilegiado: **el servidor consulta el metadata por él.**

### 2.2 La información que el atacante quiere extraer
El premio gordo está en la ruta de las **credenciales del rol IAM** asociado a la instancia:

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

Eso devuelve el **nombre del rol** (ej. `mi-rol-app`). Pidiendo después:

```
http://169.254.169.254/latest/meta-data/iam/security-credentials/mi-rol-app
```

El servicio devuelve, **en texto plano (JSON)**, las **credenciales temporales de AWS** de la instancia:

```json
{
  "AccessKeyId": "ASIA....",
  "SecretAccessKey": "xxxxxxxx....",
  "Token": "FQoGZXIvYXdz....",
  "Expiration": "2026-11-12T20:00:00Z"
}
```

Estas son las **llaves del reino**: `AccessKeyId` + `SecretAccessKey` + `Token` de sesión. Con ellas el atacante puede **autenticarse ante la API de AWS haciéndose pasar por el servidor**, con **todos los permisos que tenga el rol IAM** de esa instancia.

### 2.3 Por qué es catastrófico
Si el rol tiene permisos amplios (algo tristemente común), con esas credenciales el atacante puede, **desde su propia máquina**:
- **Leer todos los buckets S3** (bases de datos de clientes, backups, archivos privados).
- **Crear, borrar o modificar instancias** EC2.
- **Leer secretos** de Secrets Manager / Parameter Store (contraseñas de bases, claves de API).
- **Pivotar** por toda la infraestructura cloud.
- En el peor caso, **tomar control total de la cuenta de AWS**.

Todo esto **sin haber comprometido el servidor en sí**: le bastó con que el servidor hiciera **un GET a una IP interna** y le devolviera las credenciales. Por eso un SSRF en la nube suele ser **crítico**: convierte un simple "cargar imagen desde URL" en un **compromiso total de la infraestructura**.

### Otros objetivos internos del mismo SSRF
Además del metadata, el atacante puede usar el SSRF para:
- **Escanear la red interna** (`http://10.0.0.5:8080`, `http://localhost:6379`…) buscando servicios privados (bases de datos, paneles de admin, Redis sin auth).
- Alcanzar **otros endpoints internos** que confían en que "solo la red interna puede llamarlos".

### 🔍 Cómo verlo en el software
1. En un campo que reciba una **URL** (avatar, importar, webhook, conversor), en **Burp Repeater** cambiás la URL legítima por `http://169.254.169.254/latest/meta-data/`.
2. Mirás la **respuesta**.
   - **Señal que confirma el SSRF (grave):** el servidor **devuelve el contenido del metadata** (el listado de rutas, o peor, el JSON con `AccessKeyId`/`SecretAccessKey`). También es señal un comportamiento distinto al pasar IPs internas (`127.0.0.1`, `10.0.0.1`) vs. externas.
   - **Señal de que está protegido:** la petición es **rechazada/bloqueada** (la app valida el destino con lista blanca, o la instancia usa **IMDSv2**, que exige un token PUT previo y frena los SSRF simples de solo-GET).

---

## 3. Cómo se defiende (breve)

- **IMDSv2 (AWS):** la versión moderna del metadata service **exige un token** obtenido con un `PUT` previo (con cabeceras especiales) antes de dar datos. Como el SSRF clásico solo hace `GET`, **IMDSv2 lo frena**. Hay que forzar su uso (deshabilitar IMDSv1).
- **Lista blanca de destinos:** la app solo debe permitir URLs hacia dominios **explícitamente autorizados**, nunca hacia IPs internas/link-local (`169.254.169.254`, `127.0.0.1`, rangos privados `10.x`, `172.16.x`, `192.168.x`).
- **Mínimo privilegio en el rol IAM:** si el rol de la instancia tiene **solo** los permisos que necesita, aunque roben las credenciales el daño es acotado.
- **Segmentación de red / firewall de salida:** bloquear que el servidor pueda iniciar conexiones a destinos que no necesita.

---

## 4. Conclusión

Un **SSRF** permite al atacante **forzar al servidor a hacer peticiones a destinos que él elige**, usándolo como proxy hacia la **red interna** — un lugar inalcanzable desde afuera. En **AWS** (y GCP/Azure), el objetivo estrella es la dirección mágica **`169.254.169.254`**, el **Instance Metadata Service**: accesible solo desde la propia instancia, expone en la ruta `/latest/meta-data/iam/security-credentials/` las **credenciales temporales del rol IAM** (`AccessKeyId`, `SecretAccessKey` y `Token`) **en texto plano**.

Con esas credenciales, el atacante se autentica ante AWS **haciéndose pasar por el servidor**, heredando todos los permisos de su rol: leer buckets S3, acceder a secretos, crear o destruir instancias y, potencialmente, **comprometer toda la cuenta cloud** — sin haber hackeado el servidor en sí, solo haciéndolo pedir una URL interna. Por eso el SSRF en la nube es **catastrófico**, y la defensa pasa por **IMDSv2**, **listas blancas de destino** y el **mínimo privilegio** en los roles IAM.

---

*Fin del Objetivo 2 — Módulo X.*
