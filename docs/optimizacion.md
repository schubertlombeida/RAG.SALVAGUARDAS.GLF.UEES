# Optimización y evaluación del asistente RAG GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Corte documental 23 de octubre de 2026

## Qué se optimizó y qué puede concluirse

El proyecto contiene dos líneas de experimentación: un clasificador exploratorio de relevancia de pares consulta y pasaje, presentado en la semana 4, y una optimización posterior del recuperador BM25. Se describen separadamente porque tienen objetivos, datos y métricas distintos. Los archivos históricos se preservan en results/metrics/historical con su procedencia y no se presentan como nuevas mediciones ni como validación independiente del portal.

## Experimento supervisado de la semana 4

El reporte utilizó 50 pares propuestos por IA a partir de los cinco primeros resultados BM25 para diez consultas. Tras excluir tres pares inciertos y uno duplicado entre particiones, quedaron 28 pares de entrenamiento, nueve de validación y nueve de prueba. Los datos se separaron por consulta. No hubo validación humana independiente y el conjunto de prueba tenía ocho positivos y un negativo.

La representación TF IDF de unigramas y bigramas se ajustó solo con entrenamiento y produjo 24001 características al concatenar consulta, documento, interacción y coseno. Se compararon descenso de gradiente sin regularización, regularización L2 y parada temprana. Estos experimentos no entrenaron E5 ni Qwen.

| Configuración histórica | Pérdida de validación | Exactitud balanceada de validación | Lectura |
|---|---|---|---|
| Base de 200 épocas | 0.8662 | 50 % | Referencia exploratoria |
| L2 con alfa 0.01 | 0.6801 | 50 % | Menor pérdida sin mejora de discriminación |
| Parada temprana restaurando época 2 | 0.6235 | 50 % | Mejor pérdida de validación, mismo problema de clase |

En prueba, todas las variantes predijeron la clase positiva. La exactitud de 88.9 % se explica por el desbalance de ocho positivos entre nueve casos; la exactitud balanceada fue 50 % y F1 macro 0.4706. El resultado no justifica desplegar ese clasificador. No se vuelve a elegir una configuración mirando el test.

## Optimización histórica de BM25

Los archivos posteriores registran un corpus de 585 fragmentos y 38 preguntas de desarrollo, divididas en 27 train y 11 validation. La primera etapa varió k1 y b. La segunda añadió encabezados y una prioridad moderada a fuentes GLF. El archivo optimization_summary.json conserva los resultados, mientras que la anotación que los sustenta no cumple todavía la independencia y trazabilidad solicitadas para la nueva evaluación.

| Configuración reportada | Recall@5 de desarrollo | Estado de la evidencia |
|---|---|---|
| BM25 base k1 1.5 y b 0.75 | 68.9 % | Resultado histórico |
| BM25 ajustado k1 1.0 y b 0.2 | 71.5 % | Resultado histórico |
| BM25 con encabezados y prioridad GLF | 83.6 % | Resultado histórico, no gold independiente |

La mejora histórica de 14.7 puntos porcentuales compara configuraciones sobre ese conjunto de desarrollo. No demuestra mejora sobre nuevas preguntas, E5-small ni la versión publicada de 72B. Tampoco permite afirmar que se cumple la meta académica final.

## Sensibilidad y dependencia marginal

La documentación histórica describe una rejilla post congelamiento de 320 combinaciones: k1 en 0.6, 0.8, 1.0 y 1.2; b en 0.0, 0.2, 0.4 y 0.75; peso de encabezados en 0.0, 0.15, 0.30 y 0.45; prioridad GLF en 0.0, 0.05, 0.10, 0.15 y 0.20. Los CSV marginales e interacciones se conservan como evidencia recibida. No se dispone aquí de todas las ejecuciones individuales de la rejilla ni se afirma haberla repetido.

![Dependencia marginal](../results/figures/07_historical_partial_dependence.png)

En un recuperador se adapta la dependencia parcial a la media de Recall@5 sobre combinaciones de hiperparámetros. Esta visualización es un análisis de sensibilidad de una métrica, no una explicación causal de atributos de personas ni el PDP de un clasificador supervisado.

![Importancia histórica](../results/figures/08_historical_importance.png)

El rango entre el mayor y menor promedio marginal fue 9.87 puntos para encabezados, 1.80 para prioridad GLF, 1.21 para b y 0.98 para k1. Depende de los rangos explorados y de la muestra; no es una clasificación universal de importancia.

![Interacciones históricas](../results/figures/09_historical_interactions.png)

Las interacciones conservadas relacionan k1 con peso de encabezados y b con prioridad GLF. La región descrita favoreció encabezados cercanos a 0.30. El análisis se reporta sin usarlo para afirmar calidad en el test independiente pendiente.

## Latencia y comparación justa

Un benchmark anterior reportó 40 consultas exitosas con Qwen 7B local, tres calentamientos excluidos, mediana 1.815 segundos y percentil 95 de 4.617 segundos. Son resultados del entorno local documentado en ese experimento. No miden el portal Vercel, el proveedor DeepInfra ni el arranque en frío de los servicios actuales. La entrega separa las comprobaciones funcionales y la latencia de una consulta de un benchmark.

Para comparar BM25 y E5 se congelará el mismo corpus y top k igual a cinco, y se evaluarán las mismas preguntas. Se registrarán errores, calentamiento y tiempos por etapa. Los ajustes se harán en desarrollo y validación; el test se ejecutará tras fijar la configuración. No se usarán similitudes o distancias como probabilidades de corrección.

## Evaluación independiente preparada

El módulo src/evaluate.py calcula Hit@5, Recall@5, Precision@5 y MRR@5 por pregunta y tema. Rechaza preguntas sin aprobación, sin revisor diferente al autor, sin nota de anotación o con una huella de corpus incompatible. Las preguntas no contestables no reciben Recall igual a cero: se excluyen de ese denominador y se evalúan aparte para abstención.

Se propone una batería de 40 a 60 preguntas, incluidas 10 a 15 no contestables. Las respuestas frecuentes pueden iniciar esa batería, pero requieren identificar pasajes y revisión independiente. El equipo informó que espera el archivo FAQ el 26 de octubre. Los formatos de anotación están en evaluation y no incluyen respuestas inventadas.

En una muestra de 20 a 30 respuestas se revisará cada afirmación y su cita. Se contarán abstenciones correctas sobre preguntas no contestables y abstenciones erróneas sobre preguntas contestables. Para proporciones binarias se reportarán conteos e intervalo Wilson al 95 %. Este intervalo no se aplica sin más a un Recall macro de pasajes. El tiempo manual y asistido se comparará por pares, alternando orden e incluyendo la comprobación de fuentes.

## Ejecución posterior con anotaciones revisadas

Los comandos siguientes utilizan la misma versión local del corpus. Se ejecutarán cuando exista un archivo de anotaciones aprobado; no se ejecutaron con preguntas independientes en esta entrega. El modo E5 requiere GLF_E5_ENDPOINT y GLF_E5_API_KEY configurados en el servidor. La validación del gold ocurre antes de solicitar inferencia.

```text
python -m src.evaluate --labels evaluation/gold_test.jsonl --method bm25
python -m src.evaluate --labels evaluation/gold_test.jsonl --method e5
```

Los reportes se escriben por método para evitar sobrescribir el resultado comparador. Las plantillas no son datos de prueba completos; deben llenarse con las fuentes, páginas, identificadores y revisión independiente reales.

## Decisión técnica

Se mantiene la búsqueda interpretable y la validación de fuentes, y se descarta presentar el clasificador exploratorio como solución terminada. El resultado final de calidad se calculará con el corpus y la batería independientes. Hasta entonces, los valores históricos orientan el diseño y el análisis de limitaciones, sin sustituir esa medición.
