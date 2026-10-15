# Objetivo 1: Estandarización de Vulnerabilidades (CVE y CWE)

**Curso:** Software Seguro  
**Tema:** Identificación y clasificación de vulnerabilidades  
**Fecha:** 15/10/2026

## 1. ¿Qué es CVE?

**CVE (Common Vulnerabilities and Exposures)** es un programa internacional que identifica y registra vulnerabilidades de seguridad conocidas y divulgadas públicamente. Cada vulnerabilidad recibe un identificador único, como `CVE-2021-44228`, que permite a investigadores, fabricantes y equipos de seguridad referirse al mismo problema sin confusiones.

El identificador CVE no representa por sí mismo el nivel de gravedad de una vulnerabilidad: para evaluar su severidad suelen utilizarse métricas complementarias, como CVSS.

**Ejemplo:** `CVE-2021-44228` identifica la vulnerabilidad conocida como *Log4Shell*, que afecta a determinadas versiones de Apache Log4j.

## 2. ¿Qué es CWE?

**CWE (Common Weakness Enumeration)** es un catálogo mantenido por MITRE que clasifica debilidades comunes de seguridad en el diseño, la arquitectura, el código y la implementación de software y hardware. Estas debilidades pueden dar origen a vulnerabilidades concretas.

**Ejemplos:**
- `CWE-89`: neutralización incorrecta de elementos especiales utilizados en comandos SQL (*SQL Injection*).
- `CWE-79`: neutralización incorrecta de entradas durante la generación de páginas web (*Cross-Site Scripting*, XSS).

CWE ayuda a identificar causas raíz y prevenir errores similares durante el desarrollo.

## 3. Diferencias entre CVE y CWE

| Aspecto | CVE | CWE |
|---|---|---|
| ¿Qué identifica? | Una vulnerabilidad específica | Una clase de debilidad de seguridad |
| Enfoque | Identificación y seguimiento de casos concretos | Clasificación, prevención y corrección de causas raíz |
| Formato | `CVE-AAAA-NNNN...` | `CWE-Número` |
| Ejemplo | `CVE-2021-44228` (Log4Shell) | `CWE-89` (inyección SQL) |
| Uso principal | Gestión de vulnerabilidades, parches y alertas | Desarrollo seguro, auditoría y análisis de debilidades |

**Diferencia fundamental:** CVE responde **«¿qué vulnerabilidad concreta se descubrió?»**, mientras que CWE responde **«¿qué tipo de debilidad permitió que existiera?»**. Una vulnerabilidad registrada como CVE puede relacionarse con una o varias categorías CWE.

## 4. ¿Quién asigna los CVE? Autoridades CNA

Las **CNA (CVE Numbering Authorities)** son organizaciones autorizadas por el programa CVE para asignar identificadores CVE y publicar los registros correspondientes, siempre dentro de su ámbito de responsabilidad.

Pueden ser fabricantes de software y hardware, proyectos de código abierto, equipos de respuesta a incidentes (CERT/CSIRT), organizaciones de investigación y entidades que coordinan la divulgación de vulnerabilidades. No cualquier persona u organización puede asignar un identificador CVE de manera independiente.

Las CNA trabajan conforme a las reglas del programa CVE para evitar duplicaciones y facilitar la publicación coordinada de información.

**Listado oficial de CNA:** https://www.cve.org/ProgramOrganization/CNAs

## 5. ¿Dónde se consultan públicamente?

- **CVE Program:** https://www.cve.org/ — consulta de identificadores y registros oficiales de vulnerabilidades.
- **NVD (National Vulnerability Database):** https://nvd.nist.gov/vuln/search — base pública del NIST que complementa registros CVE con análisis y métricas, cuando están disponibles.
- **CWE (MITRE):** https://cwe.mitre.org/ — catálogo de debilidades, descripciones, ejemplos y recomendaciones de mitigación.

## 6. Herramientas automatizadas de detección

**Nessus (Tenable):** escáner de vulnerabilidades que analiza sistemas, servicios y software para detectar problemas conocidos. Sus resultados pueden asociarse con identificadores CVE y servir para priorizar actualizaciones y correcciones.

**Greenbone/OpenVAS:** solución de análisis de vulnerabilidades que ejecuta pruebas de seguridad sobre equipos y servicios. Permite identificar hallazgos relacionados con vulnerabilidades conocidas y consultar referencias CVE.

**Importante:** estas herramientas detectan indicios de exposición a vulnerabilidades conocidas, pero sus hallazgos deben validarse: puede haber falsos positivos o vulnerabilidades que no sean detectadas.

## 7. Conclusión

CVE y CWE son estándares complementarios fundamentales para la seguridad informática. **CVE permite identificar y gestionar vulnerabilidades específicas**, mientras que **CWE permite comprender y prevenir las debilidades que las originan**. Las CNA hacen posible la asignación coordinada de identificadores, y los escáneres automatizados facilitan la detección y el seguimiento de vulnerabilidades en entornos reales.

## 8. Fuentes consultadas

1. CVE Program — https://www.cve.org/
2. CVE Program, CNA Operational Rules — https://www.cve.org/ResourcesSupport/AllResources/CNARules
3. CVE Program, CVE Numbering Authorities — https://www.cve.org/ProgramOrganization/CNAs
4. MITRE, CWE Frequently Asked Questions — https://cwe.mitre.org/about/faq.html
5. MITRE, catálogo CWE — https://cwe.mitre.org/
6. NIST, National Vulnerability Database — https://nvd.nist.gov/
7. Tenable Nessus — https://www.tenable.com/products/nessus
8. Greenbone — https://www.greenbone.net/
