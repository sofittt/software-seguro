# Objetivo 1 — El Arte de la Evasión de Filtros (WAF Bypass)

**Módulo IX · Cross-Site Scripting (XSS)**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. El escenario

Un desarrollador inexperto quiere frenar los ataques XSS en los comentarios. Su "solución": un filtro que **elimina automáticamente las etiquetas `<script>` y `</script>`** del texto que mandan los usuarios. Cree que, sin la etiqueta `<script>`, ya no se puede ejecutar JavaScript.

**Está equivocado.** Esa defensa es prácticamente inútil. Veamos por qué.

---

## 2. Por qué esta defensa es inútil (técnicamente)

### 2.1 `<script>` NO es la única forma de ejecutar JavaScript
El error conceptual de raíz: el desarrollador cree que "XSS = `<script>`". Pero el navegador ejecuta JavaScript de **muchísimas** maneras además de esa etiqueta. Existen **decenas de atributos de eventos HTML** (`onerror`, `onload`, `onmouseover`, `onfocus`, `onclick`, `onanimationstart`…) que ejecutan código **sin ninguna etiqueta `<script>`**. También hay protocolos como `javascript:` y etiquetas como `<svg>`, `<img>`, `<iframe>`, `<body>` que corren código solas. Bloquear solo `<script>` es **tapar una puerta y dejar veinte ventanas abiertas**.

### 2.2 Es una lista negra (blacklist), y las listas negras siempre se evaden
Filtrar `<script>` es el ejemplo clásico de **lista negra**: intentar bloquear "lo malo conocido". Ya lo vimos con SQLi — es un modelo condenado al fracaso, porque **el atacante solo necesita UNA forma que no esté en la lista**, y hay cientos.

### 2.3 El filtro es un simple "borrar texto" → se reconstruye solo
Si el filtro **elimina** la cadena `<script>` **una sola vez y sin recursión**, el atacante la parte en dos para que, **después del borrado**, se vuelva a armar sola:

```html
<scr<script>ipt>alert(1)</script>
```

El filtro ve el `<script>` del medio, lo borra… y las dos mitades que quedaban (`<scr` + `ipt>`) **se pegan y reconstruyen** un `<script>` válido. La "limpieza" **crea** la etiqueta que quería destruir.

### 2.4 Es sensible a mayúsculas, espacios y codificación
HTML **no distingue mayúsculas** en las etiquetas. Si el filtro busca exactamente `<script>` (minúsculas), basta con `<ScRiPt>`, o meter un salto de línea / tabulación / atributo en el medio (`<script\n>`, `<script >`), o usar **entidades HTML** y codificaciones que el navegador decodifica **después** de que el filtro ya pasó. El filtro mira el texto crudo; el navegador interpreta algo distinto.

> **La causa raíz:** el filtro ataca el **síntoma** (una etiqueta puntual) en vez de la **causa** (que el input del usuario termina interpretándose como HTML/JS ejecutable). La defensa correcta no es "borrar `<script>`", es **codificar la salida** para que NADA del input se interprete como código (ver Objetivo 3).

---

## 3. Payloads que ejecutan código SIN usar `<script>`

Acá van varios vectores, todos sin una sola etiqueta `<script>`. (Uso `alert(1)` como prueba de concepto inofensiva; un atacante real pondría robo de cookies, etc.)

### Payload 1 — `<img>` con el evento `onerror`
```html
<img src=x onerror="alert(1)">
```
**Cómo funciona:** se crea una imagen apuntando a `x`, una ruta que **no existe**. La imagen **falla al cargar**, y ese fallo **dispara el evento `onerror`**, que ejecuta el JavaScript. No hay `<script>` por ningún lado, y es uno de los payloads más confiables que existen.

### Payload 2 — `<svg>` con el evento `onload`
```html
<svg onload="alert(1)">
```
**Cómo funciona:** la etiqueta `<svg>` (gráfico vectorial) soporta el evento `onload`, que se ejecuta **apenas el elemento termina de renderizarse** — sin necesidad de que falle nada. Se dispara solo, automáticamente, al cargar la página. Tampoco usa `<script>`.

### Payload 3 (bonus) — Otros vectores igual de válidos
```html
<!-- Entrada de texto que se autoenfoca y ejecuta al recibir foco -->
<input autofocus onfocus="alert(1)">

<!-- El cuerpo entero dispara onload -->
<body onload="alert(1)">

<!-- Enlace con el protocolo javascript: -->
<a href="javascript:alert(1)">clickeame</a>

<!-- iframe con el protocolo javascript: -->
<iframe src="javascript:alert(1)"></iframe>

<!-- Evento que se dispara al pasar el mouse -->
<div onmouseover="alert(1)">pasá el mouse</div>
```

Todos ejecutan JavaScript y **ninguno** contiene la etiqueta `<script>`. Esto demuestra lo inútil que es el filtro: hay un **universo de vectores** fuera de lo que bloquea.

### 🔍 Cómo verlo en el software
1. En el campo de comentario (o en **Burp Repeater**) mandás una **sonda** para ver cómo se refleja: `zzz"'<b>test</b>`.
2. Mirás el **código fuente** de la respuesta (Ctrl+U o la pestaña Response).
   - **Señal de vulnerabilidad:** tu `<b>` aparece como **etiqueta real** (el texto sale en negrita), no como texto escapado `&lt;b&gt;`. Eso significa que el input se interpreta como HTML → probás `<img src=x onerror=alert(1)>` y **salta el alert**, confirmando el XSS pese al filtro de `<script>`.
   - **Señal de que está protegido:** tu payload aparece **escapado** (`&lt;img...`) y no se ejecuta → hay output encoding (Objetivo 3).

---

## 4. Conclusión

Filtrar únicamente la etiqueta `<script>` es una defensa **inútil** por tres razones: (1) `<script>` **no es la única forma** de ejecutar JavaScript — hay decenas de eventos HTML (`onerror`, `onload`, `onmouseover`…) y protocolos (`javascript:`) que corren código sin ella; (2) es una **lista negra**, y al atacante le basta una forma no contemplada; y (3) un filtro que solo **borra texto** se **evade trivialmente** reconstruyendo la etiqueta (`<scr<script>ipt>`), con mayúsculas (`<ScRiPt>`) o con codificaciones.

Lo demostré con payloads reales sin `<script>`: `<img src=x onerror=alert(1)>` (dispara al fallar la carga) y `<svg onload=alert(1)>` (dispara al renderizar), más varios vectores extra. La conclusión es la de siempre: contra XSS no se "bloquean palabras", se **codifica la salida** (Output Encoding) y se refuerza con **CSP** (Objetivo 3). Atacar el síntoma nunca alcanza; hay que cerrar la causa.

---

*Fin del Objetivo 1 — Módulo IX.*
