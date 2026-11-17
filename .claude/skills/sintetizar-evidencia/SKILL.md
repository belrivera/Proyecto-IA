---
name: sintetizar-evidencia
description: Integra las fichas de lectura en una síntesis de pros y contras con tabla comparativa, puntos de consenso y controversias. Usar cuando se pida "comparar los estudios", "hacer la síntesis", "tabla de pros y contras", "conclusiones" o "redactar el marco teórico".
---

# Sintetizar evidencia

## Entrada
Las fichas de `fichas/`. Si faltan fichas de artículos importantes, avisar y sugerir usar la skill `fichar-articulo` primero. La bibliografía `.md` sirve solo como contexto: no afirmar lo que dice un artículo sin haberlo leído y fichado.

## Salida: `sintesis_pros_contras.md`
1. **Pregunta de investigación** (una línea).
2. **Tabla comparativa**, una fila por efecto:

   | Efecto | Especie / raza | Dirección (beneficio o riesgo) | Magnitud | Edad de esterilización | Fuentes | Fuerza de la evidencia |
   |---|---|---|---|---|---|---|

3. **Ventajas**: texto agrupado por tema, con citas (Autor, año).
4. **Desventajas**: con la misma estructura.
5. **Factores que modifican el balance**: especie, raza, tamaño, sexo, edad al esterilizar y contexto (mascota con dueño, refugio o colonia).
6. **Consensos y controversias**: dónde coinciden las fuentes y dónde no, y por qué (diseño del estudio, población, conflictos de interés).
7. **Vacíos de conocimiento**: lo que la evidencia todavía no responde.
8. **Conclusión** equilibrada, sin tomar partido más allá de lo que muestra la evidencia.
9. **Referencias** en APA, solo las que se citaron.

## Reglas
- Cada afirmación lleva su cita. No generalizar de una raza a todas, ni de perros a gatos.
- Dar más peso a las guías y revisiones sistemáticas que a los estudios individuales, y señalar cuando un solo estudio sostiene una conclusión.
- Escribir en español claro, en un registro apto para un trabajo académico.
