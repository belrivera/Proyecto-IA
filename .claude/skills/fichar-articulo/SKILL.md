---
name: fichar-articulo
description: Lee un PDF de la carpeta articulos/ y crea una ficha de lectura estructurada en fichas/. Usar cuando se pida "fichar", "resumir", "analizar" o "leer" un artículo, o "hacer fichas" de los artículos descargados.
---

# Fichar artículo

Para cada PDF que se pida (o para todos los de `articulos/` que todavía no tengan ficha), crear `fichas/<mismo_nombre>.md` con esta plantilla:

```markdown
# <Título>

**Cita APA:** ...
**Tipo de estudio:** revisión sistemática / cohorte retrospectiva / caso-control / experimental / guía / opinión
**Especie y población:** (especie, razas, n, país, fuente de datos)
**Postura respecto a la esterilización:** A favor / En contra / Mixta / Neutral

## Pregunta u objetivo
## Método (2-4 líneas)
## Resultados principales
- Dato concreto con su cifra (riesgo relativo, %, odds ratio, IC 95 %) — p. X
## Ventajas que documenta
## Desventajas o riesgos que documenta
## Limitaciones
(las que reconocen los autores y las que se detectan al leer: sesgo de selección, n pequeño, una sola raza, etc.)
## Nivel de evidencia
Alto / Medio / Bajo, con una línea de justificación.
## Citas textuales útiles
> "..." (p. X)
```

## Reglas
- Todo dato debe salir **del PDF**, con su número de página. Si algo no aparece en el artículo, escribir "no informado".
- Las citas textuales van en el idioma original; el resto de la ficha, en español.
- Distinguir asociación de causalidad: los estudios observacionales muestran asociaciones, no prueban causas.
- Para PDF largos (más de 10 páginas), leerlos por partes con el parámetro `pages`.
