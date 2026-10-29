# Objetivo 3: Peligros del Directory Listing

## 1. Introducción

El **Directory Listing** (listado de directorios) es una funcionalidad de algunos servidores web, como Apache y Nginx, que permite mostrar en el navegador el contenido de una carpeta del servidor. Si se habilita sin necesidad, puede exponer nombres de archivos, rutas y documentos que no estaban destinados a ser descubiertos públicamente.

## 2. ¿Qué sucede técnicamente?

Cuando un usuario solicita una URL que corresponde a un directorio, por ejemplo `https://ejemplo.com/archivos/`, el servidor busca un archivo de índice configurado, como `index.html` o `index.php`.

- **Si existe un índice**, normalmente entrega ese archivo como respuesta.
- **Si no existe y el listado está habilitado**, genera una página HTML con los nombres de archivos y subdirectorios que el proceso del servidor puede enumerar en esa ubicación. Habitualmente incluye enlaces navegables y, según la configuración, fechas de modificación y tamaños.
- **Si no existe un índice y el listado está deshabilitado**, normalmente responde con un error como `403 Forbidden`, en lugar de mostrar el contenido de la carpeta.

El listado por sí solo no implica que el atacante pueda modificar archivos ni acceder a archivos protegidos por controles de autorización. Sin embargo, **facilita descubrir recursos** que podrían estar expuestos por una mala configuración adicional.

### Ejemplo ilustrativo (ficticio)

```text
Index of /archivos/

Name                  Last modified       Size
../
backup_2026.zip       2026-09-01          12 MB
config.old            2026-08-15           3 KB
reporte_clientes.csv  2026-09-20         480 KB
imagenes/             2026-09-22             -
```

Si los archivos de ese directorio son públicos y no cuentan con controles adicionales, una persona podría descargarlos simplemente haciendo clic en los enlaces.

## 3. ¿Qué información sensible podría exponerse?

| Tipo de archivo | Ejemplos | Riesgo potencial |
|---|---|---|
| Copias de seguridad | `.zip`, `.tar.gz`, `.sql`, `.bak` | Exposición de bases de datos, código y datos personales |
| Archivos de configuración | `.env`, `.ini`, `.conf`, `config.old` | Divulgación de credenciales, claves o detalles internos, si el servidor permite su descarga |
| Registros | `.log`, archivos de depuración | Revelación de rutas, errores, identificadores o datos sensibles |
| Documentos internos | `.pdf`, `.xlsx`, `.csv` | Exposición de información comercial, financiera o de clientes |
| Código fuente y versiones antiguas | `.php.bak`, `.old`, `.git/` | Revelación de lógica de negocio o secretos incluidos por error |
| Listados de usuarios o exportaciones | `usuarios.csv`, `export.json` | Exposición de información personal |

**Importante:** que un nombre de archivo aparezca listado no garantiza que su contenido sea accesible; el impacto depende de los permisos, las reglas de acceso y el contenido real.

## 4. Riesgos de seguridad

1. **Pérdida de confidencialidad:** si los archivos listados pueden descargarse, podrían exponerse datos privados.
2. **Reconocimiento de la infraestructura:** nombres de carpetas y archivos pueden revelar tecnologías, estructura del proyecto y versiones antiguas.
3. **Facilitación de ataques posteriores:** un respaldo o archivo de configuración accesible podría proporcionar información útil para otros ataques.
4. **Exposición de información histórica:** archivos olvidados pueden permanecer disponibles aun cuando ya no se usan.

El riesgo puede variar desde **informativo o bajo**, cuando solo se listan recursos públicos, hasta **alto o crítico**, si realmente se exponen credenciales o grandes volúmenes de datos sensibles. No corresponde asignar una puntuación CVSS concreta sin conocer el impacto comprobado.

## 5. ¿Cómo se mitiga?

### Apache HTTP Server

Deshabilitar la opción `Indexes` en la configuración del directorio correspondiente:

```apache
<Directory "/var/www/html">
    Options -Indexes
    Require all granted
</Directory>
```

En entornos que permiten `.htaccess`, también puede configurarse `Options -Indexes` allí. La configuración efectiva depende de los permisos de sobrescritura (`AllowOverride`) y de otras directivas existentes.

### Nginx

Mantener deshabilitada la generación automática de índices:

```nginx
server {
    location / {
        autoindex off;
        index index.html index.php;
    }
}
```

En Nginx, `autoindex` está desactivado por defecto, salvo que se habilite explícitamente en una configuración aplicable.

### Controles complementarios

- Guardar respaldos, secretos, registros y archivos internos **fuera del directorio público** (*document root*).
- Aplicar autorización y permisos mínimos a recursos que no deben ser públicos.
- Evitar publicar archivos temporales, copias antiguas y exportaciones con información sensible.
- Revisar la configuración tras despliegues y cambios de infraestructura.
- Verificar en entornos propios o autorizados que los directorios sin índice no muestran listados ni permiten descargar archivos privados.

**Desactivar Directory Listing no sustituye el control de acceso.** Aunque se oculte el listado, un archivo podría seguir siendo descargable si alguien conoce su URL exacta.

## 6. Conclusión

El Directory Listing es una configuración que puede facilitar la exposición de información al mostrar automáticamente el contenido de directorios sin archivos de índice. Su peligrosidad depende de los archivos disponibles y de si estos pueden consultarse sin autorización. La mitigación principal consiste en deshabilitar el listado automático, mantener los archivos sensibles fuera de las rutas públicas y aplicar controles de acceso adecuados.

## 7. Referencias técnicas

- Apache HTTP Server — `mod_autoindex`: https://httpd.apache.org/docs/2.4/mod/mod_autoindex.html
- Apache HTTP Server — `Options`: https://httpd.apache.org/docs/2.4/mod/core.html#options
- Nginx — `ngx_http_autoindex_module`: https://nginx.org/en/docs/http/ngx_http_autoindex_module.html
- OWASP — Web Security Testing Guide: https://owasp.org/www-project-web-security-testing-guide/

---

**Modalidad del trabajo:** explicación técnica e investigación conceptual. Los nombres de archivos y el dominio del ejemplo son ficticios; no se realizaron pruebas sobre sistemas de terceros.
