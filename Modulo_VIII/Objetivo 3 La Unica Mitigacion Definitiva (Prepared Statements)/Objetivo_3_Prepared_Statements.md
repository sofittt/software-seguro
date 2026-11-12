# Objetivo 3 — La Única Mitigación Definitiva (Prepared Statements)

**Módulo VIII · SQL Injection**
**Curso Profesional de Ciberseguridad Web y Ethical Hacking — Software Seguro**
**Autora:** Sofía Lourdes Toledo Criado
**Fecha:** 2026-11-12

---

## 1. Por qué las "listas negras" y escapar comillas fracasan

Antes de ver la solución buena, entendamos por qué las soluciones malas no sirven:

### Lista negra (blacklist) — bloquear palabras como `SELECT`, `UNION`, `OR`
- **Siempre te olvidás una.** El diccionario de SQL es enorme y cada motor tiene sus variantes.
- **Es evadible con mil trucos:** mayúsculas/minúsculas (`SeLeCt`), comentarios en el medio (`SEL/**/ECT`), codificación (URL, hex, Unicode), duplicación (`UNIUNIONON` → al borrar `UNION` queda `UNION`), sinónimos, etc.
- Bloquear por lista negra es **jugar a adivinar todo lo malo**, y eso es imposible.

### Escapar comillas simples (`'` → `\'` o `''`)
- Solo cubre **un** carácter, y mal. Hay bypasses con **comillas dobles**, con valores **numéricos** (donde no hace falta comilla: `id=1 OR 1=1`), con **doble codificación**, o con el truco del **backslash** que rompe el escapado.
- Mezcla **los datos con el escapado manual**, que es frágil y depende de que el programador nunca se equivoque.

> El problema de fondo: **estas técnicas tratan el síntoma (ciertos caracteres) en vez de la causa.** La causa real de la SQL Injection es que **el dato del usuario se mezcla con el código de la consulta**. Si no separás datos de código, siempre va a haber una forma de colar código disfrazado de dato.

---

## 2. La causa raíz de la SQL Injection

Una consulta vulnerable se construye **concatenando** texto del usuario dentro de la sentencia SQL:

```python
# VULNERABLE: el input del usuario se pega como texto dentro del SQL
usuario = request.get("user")   # el atacante manda:  ' OR '1'='1
query = "SELECT * FROM usuarios WHERE nombre = '" + usuario + "'"
db.execute(query)
```

Si el atacante manda `' OR '1'='1`, la consulta final queda:

```sql
SELECT * FROM usuarios WHERE nombre = '' OR '1'='1'
```

La base de datos **no distingue** qué parte era "dato" y qué parte era "instrucción": recibe **un solo string** y lo interpreta **todo como código**. La comilla del atacante **cerró el valor** y el `OR '1'='1'` se convirtió en **lógica ejecutable**. Ahí nació la inyección.

**La inyección existe porque datos y código viajan mezclados en el mismo texto.** Cualquier mitigación que no resuelva ESA mezcla es un parche.

---

## 3. Cómo funciona una Consulta Parametrizada (Prepared Statement) a nivel de arquitectura

Un **prepared statement** (consulta preparada / parametrizada) **separa físicamente el código SQL de los datos**, mandándolos a la base **en dos momentos distintos y por canales distintos**. Este es el mecanismo exacto:

### Paso 1 — Se envía la plantilla con "huecos" (placeholders)
El programador escribe la consulta con **marcadores de posición** (`?` o `:nombre`) donde irían los valores. El valor del usuario **NO** se concatena:

```python
# SEGURO: la consulta tiene un hueco (?), no el dato
query = "SELECT * FROM usuarios WHERE nombre = ?"
```

Esta **plantilla** se manda primero a la base de datos **sola**, sin ningún dato del usuario.

### Paso 2 — La base de datos COMPILA la plantilla primero (aquí está la clave)
La base **recibe la plantilla y la analiza/compila ANTES de ver los datos**:
- La **parsea** (análisis sintáctico): decide cuál es el `SELECT`, el `FROM`, el `WHERE`.
- Arma el **plan de ejecución** (qué tablas, qué índices).
- En ese plan, el `?` queda marcado como **"acá va un VALOR"**, un casillero de datos — **nunca** como un lugar donde pueda aparecer estructura SQL.

En este momento **la estructura de la consulta ya quedó fija e inmutable**. La base ya decidió qué va a hacer. **Todavía no vio ni un solo carácter del usuario.**

### Paso 3 — Se envían los datos por separado, como parámetros
Recién ahora el valor del usuario viaja **por un canal aparte**, atado al placeholder:

```python
db.execute(query, (usuario,))   # 'usuario' viaja como PARÁMETRO, no como código
```

### Paso 4 — La base trata el dato SOLO como valor literal
La base **mete el dato en el casillero** que ya había reservado, y lo trata como un **valor literal puro**: un bloque de texto que **rellena** el hueco. **No lo vuelve a parsear como SQL.** La estructura ya estaba compilada y cerrada en el Paso 2; el dato **llega tarde para cambiarla**.

> **La frase que lo resume:** en un prepared statement, **el código SQL se compila antes de que el dato exista.** Como la estructura ya está fija cuando el dato entra, el dato **no tiene forma de convertirse en estructura**. Puede ser lo que sea — la base lo va a tratar como un valor, no como una orden.

---

## 4. Por qué neutraliza CUALQUIER carácter que envíe el usuario

Volvamos al ataque. El usuario manda otra vez `' OR '1'='1`. Con prepared statement:

- La consulta `SELECT * FROM usuarios WHERE nombre = ?` **ya fue compilada**: la base sabe que busca un usuario cuyo `nombre` sea **igual a un valor**.
- El dato `' OR '1'='1` entra **al casillero** como **un valor literal completo**.
- La base busca, literalmente, **un usuario que se llame `' OR '1'='1`** (con las comillas, los espacios y todo incluido como parte del nombre).
- Como **nadie se llama así**, no devuelve nada. **La inyección no ocurre: el payload se busca como texto, no se ejecuta como código.**

Esto funciona **sin importar qué mande el atacante** —comillas, `UNION`, `--`, punto y coma, caracteres Unicode raros, lo que sea— porque:

1. **Datos y código nunca se mezclan.** Viajan separados, por canales distintos.
2. **La estructura SQL se decide ANTES de ver el dato.** El dato llega cuando la consulta ya está compilada; es físicamente imposible que modifique la estructura.
3. **El dato siempre se interpreta como valor literal**, jamás como instrucción. No hay carácter "mágico" que lo convierta en código, porque la fase de "entender SQL" ya terminó.

No es que la base "filtre" o "escape" los caracteres peligrosos: es que **ya no hay un lugar donde esos caracteres puedan significar algo**. Por eso es la mitigación **definitiva** — ataca la causa raíz (la mezcla datos/código), no el síntoma (los caracteres).

### Comparación visual

```
❌ CONCATENACIÓN (vulnerable)
   [ SQL + dato del usuario ] ──► todo junto ──► la base parsea TODO como código
                                                 (el dato puede volverse instrucción)

✅ PREPARED STATEMENT (seguro)
   Paso 1: [ SQL con ? ] ──► la base COMPILA la estructura (sin el dato)
   Paso 2: [ dato ]      ──► entra al casillero ya reservado, como VALOR literal
                            (la estructura ya está cerrada: el dato no la puede tocar)
```

---

## 5. Ejemplos en varios lenguajes

**Python (sqlite3 / psycopg2 / mysql-connector):**
```python
cursor.execute("SELECT * FROM usuarios WHERE nombre = %s AND clave = %s", (user, passwd))
```

**Java (JDBC):**
```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM usuarios WHERE nombre = ?");
ps.setString(1, user);   // el dato entra como parámetro tipado
ResultSet rs = ps.executeQuery();
```

**PHP (PDO):**
```php
$stmt = $pdo->prepare("SELECT * FROM usuarios WHERE nombre = :user");
$stmt->execute(['user' => $user]);
```

**C# / .NET (ADO.NET):**
```csharp
var cmd = new SqlCommand("SELECT * FROM Usuarios WHERE Nombre = @nombre", conn);
cmd.Parameters.AddWithValue("@nombre", user);   // parámetro, nunca concatenación
```

**C# / .NET (Entity Framework — lo que usamos en Farmacia Tienda):**
```csharp
// LINQ genera consultas parametrizadas AUTOMÁTICAMENTE
var u = db.Usuarios.Where(x => x.Nombre == user).ToList();
// Incluso con SQL crudo, los valores van como parámetros:
db.Usuarios.FromSqlRaw("SELECT * FROM Usuarios WHERE Nombre = {0}", user);
```

> En todos los casos la regla es la misma: **el valor del usuario va como parámetro (`?`, `%s`, `@nombre`), nunca pegado con `+` o interpolación dentro del string de la consulta.**

### 🔍 Cómo verlo en el software

1. Buscás en el código consultas construidas con **concatenación o interpolación** de input del usuario (`"... WHERE x = '" + valor + "'"`, `f"... {valor}"`, `$"... {valor}"`). Esas son las vulnerables.
2. Probás el endpoint en **Burp Repeater** mandando `'`, `' OR '1'='1`, `1 UNION SELECT ...` en el parámetro.
   - **Señal de que está MAL (concatenación):** aparece un **error 500 de SQL**, un cambio booleano (más/menos resultados con `1=1` vs `1=2`), o un retardo con `SLEEP()`.
   - **Señal de que está BIEN (prepared statement):** el payload **se busca como texto literal** → `0 resultados` o "usuario no encontrado", **sin error de SQL y sin cambiar la lógica**, mande lo que mande el atacante.

---

## 6. Aclaración importante: qué protege y qué no

El prepared statement protege **los VALORES** de la consulta (lo que va en un `WHERE`, un `INSERT`, etc.). **No** se pueden parametrizar **nombres de tabla, columnas o palabras clave** (`ORDER BY <columna>`, por ejemplo), porque esos **son estructura, no datos**. Para esos casos la defensa es una **lista blanca** (aceptar solo un conjunto fijo y conocido de nombres válidos), nunca concatenar input del usuario ahí.

Y como siempre: **defensa en profundidad.** Prepared statements como mitigación principal e innegociable, más validación de entrada, principio de **mínimo privilegio** en el usuario de la base (que la cuenta de la app no pueda hacer `DROP`), y manejo de errores que no filtre trazas SQL.

---

## 7. Conclusión

Las listas negras y el escapado de comillas fracasan porque atacan el **síntoma** (ciertos caracteres) y son siempre evadibles: el atacante encuentra una codificación, un sinónimo o un contexto numérico que las esquiva. La **consulta parametrizada (prepared statement)** es la **única mitigación definitiva** porque ataca la **causa raíz**: separa físicamente el **código SQL** de los **datos**, enviándolos por canales distintos y en momentos distintos.

La clave arquitectónica es que **la base de datos compila la estructura de la consulta ANTES de ver el dato del usuario**. Cuando el dato finalmente llega, entra como **valor literal** en un casillero ya reservado, y la estructura ya está cerrada e inmutable. Por eso **no importa qué caracteres envíe el atacante** —comillas, `UNION`, `--`, lo que sea—: el dato se busca como texto, jamás se ejecuta como código. La inyección no se "filtra": simplemente **ya no tiene dónde ocurrir.**

---

*Fin del Objetivo 3 — Módulo VIII.*
