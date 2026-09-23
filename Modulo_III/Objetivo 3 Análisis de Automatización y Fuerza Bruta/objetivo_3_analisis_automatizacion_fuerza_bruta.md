# Objetivo 3: Análisis de Automatización y Fuerza Bruta

## Introducción

En un formulario de inicio de sesión, un atacante puede intentar
descubrir las credenciales de un usuario realizando múltiples intentos
de autenticación de manera automatizada.

Dos técnicas conocidas para realizar este tipo de ataques son el
**ataque de Fuerza Bruta** y el **ataque de Diccionario**.

Aunque ambos tienen como objetivo encontrar una contraseña válida
mediante diferentes intentos, la principal diferencia se encuentra en la
forma en la que se generan o seleccionan las contraseñas que se van a
probar.

------------------------------------------------------------------------

## Ataque de Fuerza Bruta

Un ataque de **Fuerza Bruta** consiste en probar de manera sistemática
diferentes combinaciones de caracteres hasta encontrar la contraseña
correcta.

En este caso, el atacante no necesariamente parte de una lista de
contraseñas conocidas, sino que puede generar combinaciones utilizando
letras, números y símbolos.

Por ejemplo, si una contraseña estuviera formada únicamente por cuatro
números, se podrían probar combinaciones como:

``` text
0000
0001
0002
0003
...
9999
```

El proceso continúa intentando diferentes combinaciones hasta encontrar
una contraseña válida o hasta recorrer todas las combinaciones
definidas.

La principal desventaja de este método es la cantidad de intentos que
puede llegar a necesitar. A medida que aumenta la longitud de la
contraseña y la cantidad de caracteres posibles, el número de
combinaciones crece considerablemente.

Por este motivo, una contraseña larga y difícil de predecir hace que un
ataque de Fuerza Bruta sea mucho menos práctico.

------------------------------------------------------------------------

## Ataque de Diccionario

Un ataque de **Diccionario** funciona de una manera diferente.

En lugar de generar todas las combinaciones posibles, utiliza una lista
previamente preparada de palabras y contraseñas que tienen una mayor
probabilidad de haber sido utilizadas por una persona.

Por ejemplo, un diccionario podría contener valores como:

``` text
password
admin
admin123
qwerty
argentina
bienvenido
password123
```

El sistema automatizado prueba cada una de estas contraseñas contra el
formulario de login hasta encontrar una coincidencia o llegar al final
de la lista.

Este tipo de ataque aprovecha principalmente el hecho de que muchas
personas utilizan contraseñas comunes, palabras conocidas o
combinaciones fáciles de recordar.

Por este motivo, puede necesitar muchos menos intentos que un ataque de
Fuerza Bruta si la contraseña utilizada por el usuario se encuentra
dentro del diccionario.

------------------------------------------------------------------------

## Diferencia entre Fuerza Bruta y Diccionario

La diferencia fundamental entre ambos ataques se encuentra en **cómo se
obtienen las contraseñas que se van a probar**.

  -----------------------------------------------------------------------
  Fuerza Bruta                        Diccionario
  ----------------------------------- -----------------------------------
  Genera diferentes combinaciones de  Utiliza una lista previamente
  caracteres.                         preparada.

  Puede intentar recorrer todas las   Solo prueba las contraseñas
  combinaciones definidas.            incluidas en el diccionario.

  Generalmente puede requerir una     Puede ser más rápido si la
  gran cantidad de intentos.          contraseña utilizada es común.

  No depende de que la contraseña sea Depende de que la contraseña o una
  una palabra conocida.               variante esté incluida en la lista.
  -----------------------------------------------------------------------

De manera simplificada:

### Fuerza Bruta

``` text
Generar combinaciones
        ↓
Probar contraseña
        ↓
¿Es correcta?
   ↓          ↓
  Sí          No
   ↓           ↓
Acceso     Probar otra
```

### Diccionario

``` text
Lista de contraseñas
        ↓
Seleccionar una
        ↓
Probar contraseña
        ↓
¿Es correcta?
   ↓          ↓
  Sí          No
   ↓           ↓
Acceso     Probar siguiente
```

------------------------------------------------------------------------

# Mecanismos de defensa

Existen diferentes mecanismos que un desarrollador puede implementar
para reducir la efectividad de este tipo de automatizaciones.

## 1. Rate Limiting

Una de las principales medidas es implementar **Rate Limiting**, es
decir, limitar la cantidad de intentos de autenticación permitidos
durante un determinado período de tiempo.

Por ejemplo, una aplicación podría detectar que se realizaron varios
intentos fallidos consecutivos y aplicar temporalmente una demora o una
restricción para nuevos intentos.

``` text
Intentos de login
       ↓
Varios intentos fallidos
       ↓
Se supera el límite configurado
       ↓
Restricción o demora temporal
```

Esto dificulta los ataques automatizados porque evita que se puedan
realizar grandes cantidades de intentos en muy poco tiempo.

El mecanismo debe implementarse cuidadosamente para evitar que un
atacante pueda utilizarlo para bloquear intencionalmente la cuenta de
otro usuario.

------------------------------------------------------------------------

## 2. Autenticación Multifactor (MFA)

Otra medida importante es utilizar **autenticación multifactor (MFA)**.

Con este mecanismo, conocer solamente el usuario y la contraseña no
necesariamente es suficiente para ingresar a una cuenta.

Después de ingresar correctamente la contraseña, el sistema puede
solicitar un segundo factor de autenticación, por ejemplo:

-   Un código generado por una aplicación de autenticación.
-   Una llave de seguridad.
-   Un código de un solo uso.

Esto agrega una capa adicional de seguridad frente al compromiso de una
contraseña.

------------------------------------------------------------------------

## 3. Contraseñas seguras

También es importante fomentar el uso de contraseñas **largas, únicas y
difíciles de predecir**.

Una contraseña simple como:

``` text
hola123
```

podría encontrarse fácilmente dentro de un diccionario de contraseñas
comunes.

En cambio, una contraseña larga y única aumenta considerablemente la
dificultad de los ataques basados en adivinación.

También se puede evitar que los usuarios seleccionen contraseñas
conocidas por haber aparecido previamente en filtraciones de datos.

------------------------------------------------------------------------

## 4. CAPTCHA y detección de automatización

Otra protección posible es utilizar un **CAPTCHA** o un desafío similar
cuando el sistema detecta una cantidad anormal de intentos.

No necesariamente debe mostrarse en cada inicio de sesión. Puede
activarse únicamente cuando se detecta un comportamiento sospechoso.

Esto permite agregar una dificultad adicional a los sistemas
automatizados sin afectar constantemente a los usuarios legítimos.

------------------------------------------------------------------------

## 5. Monitoreo de intentos de autenticación

La aplicación también puede registrar y analizar los intentos de inicio
de sesión.

Por ejemplo, podría detectar:

-   Muchos intentos fallidos en poco tiempo.
-   Una cantidad anormal de intentos sobre una misma cuenta.
-   Intentos repetitivos desde un mismo origen.
-   Patrones de autenticación poco habituales.

Estos eventos pueden generar alertas o activar medidas adicionales de
protección.

------------------------------------------------------------------------

## Conclusión

Los ataques de **Fuerza Bruta** y **Diccionario** buscan descubrir
credenciales mediante múltiples intentos de autenticación, pero utilizan
estrategias diferentes.

La **Fuerza Bruta** genera y prueba diferentes combinaciones posibles,
mientras que el **ataque de Diccionario** utiliza una lista previamente
preparada de contraseñas consideradas probables.

Un ataque de diccionario puede ser más eficiente cuando los usuarios
utilizan contraseñas comunes o predecibles, mientras que la Fuerza Bruta
intenta explorar un espacio de combinaciones mucho más amplio.

Para reducir el riesgo de estos ataques, los desarrolladores pueden
implementar diferentes mecanismos de seguridad, como **Rate Limiting,
autenticación multifactor, CAPTCHA, monitoreo de intentos sospechosos y
políticas de contraseñas seguras**.

La utilización de varias de estas medidas en conjunto permite reducir
considerablemente la efectividad de los ataques automatizados contra
formularios de autenticación.
