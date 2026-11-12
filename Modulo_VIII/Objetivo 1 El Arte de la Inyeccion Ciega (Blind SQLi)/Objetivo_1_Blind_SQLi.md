# Objetivo 1 — El Arte de la Inyección Ciega (Blind SQLi)

**Módulo VIII · SQL Injection**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. ¿Qué es una inyección "ciega" (Blind SQLi)?

En una SQL Injection **clásica** (in-band), el atacante ve el resultado **directamente en la pantalla**: la base devuelve los datos, o te tira un **error amigable** ("Error de SQL cerca de…") que te cuenta qué pasó. Ahí el ataque es cómodo: preguntás y la página te responde con los datos.

Pero muchas aplicaciones **no muestran nada útil**: no devuelven datos, no muestran errores, solo una pantalla genérica ("Cargando…", "Operación completada", o siempre la misma respuesta). **La inyección existe igual** (el servidor sí procesa tu SQL), pero estás **a ciegas**: no ves el resultado.

Ahí entra la **Blind SQL Injection**. La idea es genial: si no puedo **ver** la respuesta, le hago a la base **preguntas de SÍ o NO**, y deduzco la respuesta mirando **cómo se comporta** la aplicación. No leo los datos; los **adivino preguntando**, un bit a la vez. Hay dos formas de leer ese "sí/no": por **contenido** (boolean-based) y por **tiempo** (time-based).

---

## 2. Boolean-Based Blind (basada en verdadero/falso)

### La idea
El atacante inyecta una **condición** y observa si la **respuesta de la página cambia** según esa condición sea **verdadera o falsa**. No importa qué datos muestre: importa que la página se vea **distinta** en los dos casos.

### Cómo funciona
Se mandan dos peticiones y se comparan:

```sql
-- Condición SIEMPRE verdadera
... AND 1=1     → la página responde "normal"  (ej. muestra el producto)

-- Condición SIEMPRE falsa
... AND 1=2     → la página responde "distinto" (ej. producto vacío / "no encontrado")
```

Si con `1=1` la página se ve de una forma y con `1=2` se ve de otra, **la base está evaluando mi condición** → hay inyección, y tengo mi canal de "sí/no":

- **Respuesta tipo A** (igual que `1=1`) = la condición fue **VERDADERA**.
- **Respuesta tipo B** (igual que `1=2`) = la condición fue **FALSA**.

La "diferencia" puede ser cualquier señal observable: que aparezca o no un producto, un texto, un cambio en la **longitud** de la respuesta, un `200` vs un `302`, etc. El atacante no necesita ver datos: **le alcanza con distinguir dos estados**.

### Ventaja / desventaja
- ✅ **Rápida**: la respuesta es inmediata.
- ❌ Necesita que **exista una diferencia visible** entre verdadero y falso. Si la página se ve **exactamente igual** pase lo que pase, boolean-based no sirve → hay que ir a **time-based**.

---

## 3. Time-Based Blind (basada en tiempo)

### La idea
Cuando la página responde **siempre igual** (mismo texto, misma longitud, siempre "Cargando…"), el atacante ya no puede mirar el **contenido**. Entonces usa otra señal que la base **no puede ocultar: el TIEMPO**. Le ordena a la base: *"si mi condición es verdadera, **esperá** unos segundos antes de responder"*. Después mide **cuánto tardó**.

### Cómo funciona
Se usa una función de **retardo** del motor (`SLEEP()` en MySQL, `pg_sleep()` en PostgreSQL, `WAITFOR DELAY` en SQL Server) **condicionada**:

```sql
-- MySQL: "si la condición es verdadera, dormí 5 segundos"
... AND IF( (condición), SLEEP(5), 0)
```

Y se cronometra:

- La respuesta **tarda ~5 segundos** → la condición fue **VERDADERA** (la base ejecutó el `SLEEP`).
- La respuesta **vuelve al instante** (~0 s) → la condición fue **FALSA** (no durmió).

El reloj se convierte en el canal de información: **tiempo largo = SÍ, tiempo corto = NO.** No hace falta ver absolutamente nada en pantalla.

### Ventaja / desventaja
- ✅ Funciona **aunque la página no cambie nunca** (es el último recurso, el más universal).
- ❌ **Lenta**: cada pregunta cuesta varios segundos, y el "ruido" de la red puede confundir (por eso se usan retardos claros, de 5 s, y a veces se repite la medición).

---

## 4. La diferencia técnica, en una línea

| | **Boolean-Based** | **Time-Based** |
|---|---|---|
| **Qué mira el atacante** | El **contenido** de la respuesta (cambia o no) | El **tiempo** de la respuesta (tarda o no) |
| **Señal de "verdadero"** | La página se ve distinta (tipo A) | La respuesta se demora (ej. 5 s) |
| **Cuándo se usa** | Cuando hay **alguna** diferencia visible entre V y F | Cuando la página responde **siempre igual** |
| **Velocidad** | Rápida | Lenta |
| **Depende de** | Que la salida cambie | Que la base ejecute un `SLEEP` |

> En el fondo **las dos hacen lo mismo**: convierten la base en una máquina de responder **SÍ/NO**. Solo cambia **cómo leen** ese sí/no — una por lo que **ve**, otra por lo que **tarda**.

---

## 5. Cómo se extrae el nombre de la base LETRA POR LETRA (pantalla "Cargando…")

Esta es la parte más linda. La aplicación solo muestra "Cargando…", así que usamos **time-based** (o boolean si hubiera alguna diferencia). La estrategia se llama **búsqueda binaria carácter por carácter**, y combina tres funciones SQL:

- `DATABASE()` → devuelve el nombre de la base actual (el dato que queremos robar).
- `SUBSTRING(texto, posición, 1)` → saca **un solo carácter** de ese nombre, en la posición que yo diga.
- `ASCII(carácter)` → convierte ese carácter en su **número ASCII** (ej. `a` = 97, `b` = 98, `s` = 115).

Como la base solo me contesta SÍ/NO, no le puedo preguntar "¿cuál es la letra?". Le pregunto por su **número ASCII** con **comparaciones de mayor/menor**, igual que el juego de "adiviná el número":

### El proceso, posición 1 (la primera letra)

```sql
-- ¿El ASCII de la 1ª letra es mayor que 109 (la mitad del rango)?
... AND IF( ASCII(SUBSTRING(DATABASE(),1,1)) > 109, SLEEP(5), 0)
```

- **Tardó 5 s (SÍ)** → la letra está en la mitad alta (ASCII > 109). Siguiente pregunta: `> 115`.
- **No tardó (NO)** → está en la mitad baja (ASCII ≤ 109). Siguiente pregunta: `> 103`.

Y así voy **partiendo el rango a la mitad** cada vez (búsqueda binaria):

```
¿> 109?  SÍ   → rango 110..122
¿> 115?  SÍ   → rango 116..122
¿> 118?  NO   → rango 116..118
¿> 117?  NO   → rango 116..117
¿= 116?  SÍ   → ¡es 116 = 't' !   ← primera letra encontrada
```

Con **comparaciones** (`>`, `<`) encuentro cualquier letra en **unos 7 intentos** (porque el rango de letras y números imprimibles entra en 2⁷). Mucho más rápido que probar las 26 letras una por una.

### Siguiente posición

Repito todo cambiando la **posición** en `SUBSTRING`:

```sql
... ASCII(SUBSTRING(DATABASE(), 2, 1)) > ?   -- 2ª letra
... ASCII(SUBSTRING(DATABASE(), 3, 1)) > ?   -- 3ª letra
```

Letra por letra, posición por posición, voy reconstruyendo el nombre completo: `t` → `i` → `e` → `n` → `d` → `a` = **`tienda`**. Para saber cuándo terminar, pregunto por el **largo** (`LENGTH(DATABASE())`) o detecto que la posición siguiente devuelve ASCII 0 (no hay más caracteres).

### Por qué se automatiza (SQLmap)
Hacer esto a mano son **cientos de peticiones cronometradas**. Por eso se usa **SQLmap**, que automatiza toda la búsqueda binaria, mide los tiempos, descarta el ruido de red y reconstruye solito no solo el nombre de la base, sino tablas, columnas y datos enteros.

### 🔍 Cómo verlo en el software

1. En **Burp Repeater**, en un parámetro sospechoso, mandás primero `... AND 1=1` y luego `... AND 1=2`.
   - **Señal boolean-based:** las dos respuestas se ven **distintas** (contenido o longitud) → hay inyección ciega booleana.
2. Si se ven **iguales**, probás un retardo: `... AND SLEEP(5)` (o `IF(1=1, SLEEP(5), 0)`) y mirás la **columna de tiempo** de Burp.
   - **Señal time-based:** con la condición verdadera la respuesta tarda **~5 s**, y con la falsa vuelve **al instante** → hay inyección ciega basada en tiempo. Después confirmás con `sqlmap`.
   - **Si NO es vulnerable:** el tiempo **no cambia** mande lo que mande (típico de prepared statements, Objetivo 3).

---

## 6. Conclusión

La **Blind SQL Injection** demuestra que no hace falta ver los datos para robarlos: alcanza con convertir a la base en una **máquina de responder SÍ/NO** y hacerle miles de preguntas. La diferencia técnica entre las dos variantes es **qué señal lee el atacante**: la **Boolean-Based** mira si el **contenido** de la respuesta cambia entre una condición verdadera (`1=1`) y una falsa (`1=2`); la **Time-Based** mira si la respuesta **tarda** (con un `SLEEP` condicionado), y es el recurso cuando la página responde siempre igual.

Para extraer el nombre de la base detrás de una pantalla de "Cargando…", el atacante combina `DATABASE()`, `SUBSTRING()` y `ASCII()` para preguntar, carácter por carácter y con **búsqueda binaria** (mayor/menor), el código ASCII de cada letra — reconstruyendo el nombre completo sin ver jamás un solo dato en pantalla. Herramientas como **SQLmap** automatizan este proceso tedioso. Y la moraleja de siempre: la única defensa de verdad son las **consultas parametrizadas** (ver Objetivo 3), que cortan la inyección de raíz sin importar qué mande el atacante.

---

*Fin del Objetivo 1 — Módulo VIII.*
