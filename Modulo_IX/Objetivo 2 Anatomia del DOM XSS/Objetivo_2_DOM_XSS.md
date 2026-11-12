# Objetivo 2 — Anatomía del DOM XSS

**Módulo IX · Cross-Site Scripting (XSS)**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. Un repaso rápido: los tres tipos de XSS

- **XSS Reflejado:** el payload viaja en la petición (ej. un parámetro de URL), el **servidor lo refleja** en el HTML de la respuesta y el navegador lo ejecuta. **El servidor procesa el payload.**
- **XSS Almacenado:** el payload se **guarda en la base** (un comentario, un ticket) y se ejecuta cada vez que alguien ve esa sección. **El servidor procesa y guarda el payload.**
- **XSS Basado en DOM (DOM-Based):** la vulnerabilidad ocurre **100% en el navegador**. El **servidor nunca ve ni procesa el payload**. El problema está en un JavaScript inseguro que **ya vive en la página** y que toma un dato controlable por el atacante y lo inyecta en el DOM.

Esa última frase es la clave de por qué el DOM XSS es tan difícil de detectar para WAF e IPS.

---

## 2. Por qué el DOM XSS es invisible para WAF e IPS

Un **WAF** (firewall de aplicaciones) y un **IPS** (sistema de prevención de intrusiones) funcionan **inspeccionando el tráfico de red** que entra y sale del **servidor**: miran las peticiones HTTP que llegan y las respuestas que salen, buscando payloads sospechosos (`<script>`, `onerror`, etc.). **Solo pueden ver lo que pasa por el cable.**

El problema es que, en el DOM XSS, **el payload malicioso nunca viaja al servidor.** Y el motivo técnico central es **cómo el navegador maneja el fragmento `#` de la URL.**

### 2.1 El fragmento `#` NUNCA se envía al servidor
En una URL, todo lo que viene **después del `#`** se llama **fragmento** (o *hash*). Y hay una regla fundamental del protocolo HTTP:

> **El navegador NUNCA envía al servidor la parte que está después del `#`.**

El `#` fue diseñado originalmente para apuntar a una sección **dentro** de la misma página (un ancla), algo que resuelve el navegador localmente. Por eso, cuando pedís:

```
https://sitio.com/perfil#<img src=1 onerror=alert(1)>
```

El navegador **solo le pide al servidor** `https://sitio.com/perfil`. **Todo el payload (`#<img...>`) se queda en el navegador y jamás sale a la red.**

### 2.2 Conclusión: el WAF/IPS no tiene nada que inspeccionar
Como el payload vive en el `#` y el `#` no se transmite:

- El **WAF** mira la petición que llega al servidor y ve solo `GET /perfil` → **limpio, nada sospechoso**.
- El **servidor** responde un HTML **seguro y limpio** (nunca tocó el payload) → **la respuesta también pasa el control**.
- El **IPS** inspecciona el tráfico de red y **no ve el payload en ningún momento**, porque nunca cruzó la red.

El ataque ocurre **enteramente del lado del cliente**, en un lugar donde las defensas perimetrales **no tienen visibilidad**. Es como un robo que sucede **dentro de tu casa**: la cámara de la puerta (el WAF) no graba nada porque el ladrón nunca cruzó la puerta — ya estaba adentro (el JavaScript vulnerable de la propia página).

---

## 3. Cómo ocurre: Source y Sink

El DOM XSS nace de un JavaScript inseguro **que ya existe en la página**. Se explica con dos conceptos:

- **Source (fuente):** de dónde saca el dato el JavaScript. Es una entrada **controlable por el atacante**: `location.hash`, `location.search`, `document.URL`, `document.referrer`, etc. En nuestro caso, **`location.hash`** (lo que está después del `#`).
- **Sink (sumidero):** dónde el JavaScript **vuelca** ese dato de forma peligrosa. Es una función/propiedad que **convierte texto en HTML o código ejecutable**: `innerHTML`, `document.write()`, `eval()`, `insertAdjacentHTML()`, etc.

**El XSS ocurre cuando un dato va de un Source controlable a un Sink peligroso sin sanitizar en el medio.**

### Ejemplo concreto (el del escenario)

El sitio tiene este JavaScript, pensado para saludar al usuario:

```javascript
// Código vulnerable que YA está en la página
document.getElementById("saludo").innerHTML = "Hola " + window.location.hash.substring(1);
//                                   ▲ SINK                      ▲ SOURCE
```

Lee `location.hash` (**Source**, controlado por el atacante) y lo mete directo en `innerHTML` (**Sink**, que interpreta HTML). No hay sanitización en el medio. Entonces el atacante manda a la víctima este enlace:

```
https://sitio.com/perfil#<img src=1 onerror=alert(1)>
```

**Qué pasa, paso a paso:**
1. La víctima hace clic. El navegador pide al servidor **solo** `https://sitio.com/perfil` (el `#...` se queda local).
2. El servidor devuelve un HTML **limpio y seguro** (nunca vio el payload). ✅ WAF, IPS y servidor: todos contentos.
3. **Ya en el navegador**, el JavaScript local se ejecuta: toma el valor del hash (`<img src=1 onerror=alert(1)>`, el **Source**) y lo inyecta en la página con `innerHTML` (el **Sink**).
4. El navegador renderiza ese `<img>` con un `src` inválido → **falla la carga → se dispara `onerror` → se ejecuta el JavaScript**. 💥 XSS, sin que ninguna defensa perimetral se enterara.

### 🔍 Cómo verlo en el software
1. Abrís **DevTools → Sources** y buscás usos de **Sinks** peligrosos (`innerHTML`, `document.write`, `eval`) que reciban un **Source** controlable (`location.hash`, `location.search`, `document.URL`).
2. Probás un enlace con el payload en el `#`: `.../perfil#<img src=1 onerror=alert(1)>`.
   - **Señal que confirma el DOM XSS:** salta el `alert` **aunque en la pestaña Network la petición al servidor NO lleve el payload** (viaja solo `GET /perfil`) y la respuesta del servidor venga limpia. Eso prueba que la ejecución fue 100% en el cliente — invisible para el WAF.

---

## 4. Conclusión

El **DOM-Based XSS** es invisible para WAF e IPS porque esas defensas inspeccionan el **tráfico de red hacia y desde el servidor**, y en este ataque **el payload nunca viaja al servidor**. La razón técnica es el **fragmento `#` de la URL**: por diseño del protocolo, **el navegador nunca envía al servidor lo que está después del `#`**, así que un payload colocado ahí (`#<img src=1 onerror=alert(1)>`) se queda **enteramente en el cliente**. El servidor solo recibe `GET /perfil`, responde un HTML limpio, y tanto el WAF como el IPS ven tráfico impecable.

El daño ocurre después, **dentro del navegador**, cuando un JavaScript inseguro que ya vivía en la página toma ese dato de una **Source** controlable (`location.hash`) y lo vuelca sin sanitizar en un **Sink** peligroso (`innerHTML`), ejecutando el código. Por eso el DOM XSS **no se defiende en el perímetro**: se defiende **en el código del cliente**, usando APIs seguras (`textContent` en vez de `innerHTML`), sanitización (DOMPurify) y CSP (Objetivo 3). Lo que no cruza la red, la red no lo puede proteger.

---

*Fin del Objetivo 2 — Módulo IX.*
