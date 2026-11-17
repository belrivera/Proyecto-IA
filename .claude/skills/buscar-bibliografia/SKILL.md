---
name: buscar-bibliografia
description: Busca y verifica referencias científicas sobre un tema y las agrega en formato APA a un archivo de bibliografía. Usar cuando se pida "buscar bibliografía", "agregar referencias", "buscar estudios/papers sobre X" o "agregar la guía de...".
---

# Buscar bibliografía

Objetivo: encontrar fuentes académicas **reales y verificadas** sobre el tema pedido y agregarlas a la bibliografía del proyecto.

## Reglas
- **Nunca inventar referencias.** Cada referencia nueva tiene que estar confirmada con una búsqueda (Europe PMC, PubMed, la web de la editorial o la DOI). Si no se puede confirmar un dato (volumen, páginas, autores), se omite y se avisa.
- Preferir revisiones sistemáticas, metaanálisis, guías de sociedades (WSAVA, AAHA, AVMA, etc.) y estudios de cohorte grandes antes que estudios pequeños o artículos de divulgación.
- Si el tema es controvertido, buscar fuentes de **ambos lados**.
- No enviar datos personales del usuario a servicios externos.

## Pasos
1. Aclarar el tema y el subtema (por ejemplo, "esterilización → incontinencia urinaria"). Si el pedido es ambiguo, interpretar el sentido más probable y decirlo (por ejemplo, "WASABA" se interpreta como WSAVA).
2. Buscar con la API de Europe PMC, que es gratuita y no requiere clave:
   `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<términos>&format=json&resultType=core&pageSize=25`
   Para verificar una DOI concreta, usar `query=DOI:<doi>`. Completar la búsqueda con WebSearch para encontrar guías y documentos que no estén indexados.
3. Para cada fuente, registrar: autores, año, título, revista, volumen(número), páginas, DOI y si es de acceso abierto (campo `isOpenAccess` de Europe PMC).
4. Formatear en **APA 7**, con una anotación de una o dos líneas en español que diga qué aporta y si va a favor, en contra o tiene una postura mixta.
5. Agregar las referencias a la sección temática que corresponda del archivo de bibliografía (por defecto, `bibliografia_esterilizacion_animales.md`), sin duplicar las que ya están. Si existe una fe de erratas o una crítica publicada, mencionarla.
6. Responder con la lista de lo que se agregó y las fuentes (URLs) que se consultaron.
