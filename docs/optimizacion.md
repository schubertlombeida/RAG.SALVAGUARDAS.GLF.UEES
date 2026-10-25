# Optimización y evaluación del asistente RAG GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Edición 24 de octubre de 2026

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

Los archivos posteriores registran un corpus de 585 fragmentos y 38 preguntas de desarrollo, divididas en 27 train y 11 validation. La primera etapa varió k1 y b. La segunda añadió encabezados y una prioridad moderada a fuentes GLF. El archivo optimization_summary.json conserva los resultados, y delimita su uso como resultados de desarrollo con anotación no independiente.

| Configuración reportada | Recall@5 de desarrollo | Estado de la evidencia |
|---|---|---|
| BM25 base k1 1.5 y b 0.75 | 68.9 % | Resultado histórico |
| BM25 ajustado k1 1.0 y b 0.2 | 71.5 % | Resultado histórico |
| BM25 con encabezados y prioridad GLF | 83.6 % | Resultado histórico, no gold independiente |

La mejora histórica de 14.7 puntos porcentuales compara configuraciones sobre ese conjunto de desarrollo. No demuestra mejora sobre nuevas preguntas, E5-small ni la versión publicada de 72B. Su alcance es el conjunto de desarrollo descrito, sin extrapolación a precisión normativa en producción.

## Sensibilidad y dependencia marginal

La documentación histórica describe una rejilla post congelamiento de 320 combinaciones: k1 en 0.6, 0.8, 1.0 y 1.2; b en 0.0, 0.2, 0.4 y 0.75; peso de encabezados en 0.0, 0.15, 0.30 y 0.45; prioridad GLF en 0.0, 0.05, 0.10, 0.15 y 0.20. Los CSV marginales e interacciones se conservan como evidencia recibida. No se dispone aquí de todas las ejecuciones individuales de la rejilla ni se afirma haberla repetido.

![Dependencia marginal](../results/figures/07_historical_partial_dependence.png)

En un recuperador se adapta la dependencia parcial a la media de Recall@5 sobre combinaciones de hiperparámetros. Esta visualización es un análisis de sensibilidad de una métrica, no una explicación causal de atributos de personas ni el PDP de un clasificador supervisado.

![Importancia histórica](../results/figures/08_historical_importance.png)

El rango entre el mayor y menor promedio marginal fue 9.87 puntos para encabezados, 1.80 para prioridad GLF, 1.21 para b y 0.98 para k1. Depende de los rangos explorados y de la muestra; no es una clasificación universal de importancia.

![Interacciones históricas](../results/figures/09_historical_interactions.png)

Las interacciones conservadas relacionan k1 con peso de encabezados y b con prioridad GLF. La región descrita favoreció encabezados cercanos a 0.30. El análisis caracteriza la sensibilidad histórica; no estima rendimiento sobre un conjunto externo de prueba.

## Latencia y comparación justa

Un benchmark anterior reportó 40 consultas exitosas con Qwen 7B local, tres calentamientos excluidos, mediana 1.815 segundos y percentil 95 de 4.617 segundos. Son resultados del entorno local documentado en ese experimento. No miden el portal Vercel, el proveedor DeepInfra ni el arranque en frío de los servicios actuales. La entrega separa las comprobaciones funcionales y la latencia de una consulta de un benchmark.

Para comparar BM25 y E5 se congelará el mismo corpus y top k igual a cinco, y se evaluarán las mismas preguntas. Se registrarán errores, calentamiento y tiempos por etapa. Los ajustes se harán en desarrollo y validación; el test se ejecutará tras fijar la configuración. No se usarán similitudes o distancias como probabilidades de corrección.

## Protocolo de evaluación independiente

El módulo src/evaluate.py calcula Hit@5, Recall@5, Precision@5 y MRR@5 por pregunta y tema. Rechaza preguntas sin aprobación, sin revisor diferente al autor, sin nota de anotación o con una huella de corpus incompatible. Las preguntas no contestables no reciben Recall igual a cero: se excluyen de ese denominador y se evalúan aparte para abstención.

El protocolo define una batería de 40 a 60 preguntas, incluidas 10 a 15 no contestables. Cada pregunta requiere identificación de pasajes y revisión independiente. Los formatos de anotación están en evaluation. Las mediciones incluidas en esta entrega corresponden a desarrollo y comprobación funcional; no se reportan métricas de una batería externa anotada por especialistas.

En una muestra de 20 a 30 respuestas se revisará cada afirmación y su cita. Se contarán abstenciones correctas sobre preguntas no contestables y abstenciones erróneas sobre preguntas contestables. Para proporciones binarias se reportarán conteos e intervalo Wilson al 95 %. Este intervalo no se aplica sin más a un Recall macro de pasajes. El tiempo manual y asistido se comparará por pares, alternando orden e incluyendo la comprobación de fuentes.

## Reproducción de la evaluación

Los comandos siguientes ejecutan la evaluación sobre una versión local del corpus y un archivo de anotaciones aprobado. El modo E5 requiere GLF_E5_ENDPOINT y GLF_E5_API_KEY configurados en el servidor. La validación de las anotaciones ocurre antes de solicitar inferencia. Estos comandos documentan el procedimiento; no constituyen resultados de una ejecución independiente.

```text
python -m src.evaluate --labels evaluation/gold_test.jsonl --method bm25
python -m src.evaluate --labels evaluation/gold_test.jsonl --method e5
```

Los reportes se escriben por método para evitar sobrescribir el resultado comparador. Las plantillas no son datos de prueba completos; deben llenarse con las fuentes, páginas, identificadores y revisión independiente reales.

## Mejoras de interfaz y pruebas funcionales

La actualización del 24 de octubre incorpora orientación por tarea, ejemplos editables, límites de entrada, avance real por etapas, modelo ejecutado, reloj, cancelación de espera, referencias numeradas, exportación con fuentes e historial temporal. Los fallos de conexión, cuota, configuración, formato y citas tienen mensajes distintos. La interfaz no transforma similitud en confianza ni presenta una abstención como aprobación del proyecto.

La actualización de calidad supera 33 pruebas de la aplicación académica, 187 pruebas TypeScript y 81 de base de datos y funciones del portal, y 25 pruebas Python del servicio más su smoke test. Se verificaron resultados, error, cancelación, historial y adaptación móvil en navegador, y ambas rutas publicadas con consultas reales. Los archivos results/reports/ux_verificacion_20261024.json y quality_verificacion_20261024.json delimitan la evidencia de cada revisión. Estas pruebas verifican contratos y comportamiento del software; no sustituyen la revisión independiente de respuestas.

## Optimización reproducible de esta entrega

src/optimize.py implementa una rejilla de doce combinaciones: k1 en 0.8, 1.2 y 1.5; b en 0.2 y 0.75; peso de encabezados en 0.0 y 0.3. Exige desarrollo y validación con anotaciones aprobadas, rechaza preguntas o grupos de intención compartidos y no recibe test. Selecciona por Recall@5 de validación, desempata con MRR@5 y después con menor peso de encabezados. Conserva todas las ejecuciones por pregunta y genera gráficas a color de sensibilidad, importancia marginal e interacción. Sus pruebas usan datos sintéticos identificados como tales; no son nuevos resultados GLF.

src/evaluate.py permite evaluar BM25, BM25 ajustado, E5 y fusión RRF sobre los mismos registros y metadatos. RRF significa Reciprocal Rank Fusion, fusión mediante el inverso del rango; evita sumar puntajes de escalas distintas. La fusión está disponible para el experimento académico y no se activa en el portal hasta demostrar una ventaja con anotaciones revisadas.

src/answer_evaluation.py resume revisión humana de afirmaciones y utilidad, abstenciones con denominadores separados e intervalos Wilson del 95 %, y tiempos manuales y asistidos pareados. No usa Qwen como juez de sus propias respuestas. La fracción de afirmaciones sustentadas no recibe un intervalo binomial que ignore la correlación dentro de cada respuesta.

El protocolo ejecutable, campos y comandos están en evaluation/README.md. La referencia anterior del portal se conserva en results/baseline_v0761. Una consulta de ejemplo permite observar el cambio de formato, pero no cuantificar una mejora general. Una comparación general requiere preguntas anotadas y revisión independiente de pasajes; una consulta aislada no permite estimar esa mejora.

## Aporte a la rúbrica

La implementación aporta evidencia verificable a funcionamiento, usabilidad, código, documentación, optimización, evaluación y ética: modos de respuesta acotados, contratos y errores probados, trazabilidad del contexto y experimentos reproducibles con separación de particiones. El puntaje académico no se anticipa. El alcance empírico se limita a las mediciones documentadas y a las versiones identificadas.

## Decisión técnica

La solución utiliza búsqueda interpretable y validación de fuentes. El clasificador exploratorio no se despliega porque su exactitud balanceada no evidencia discriminación útil. Los resultados históricos fundamentan el diseño y sus límites; las pruebas actuales verifican contratos e interacción. La generalización a preguntas nuevas requiere el protocolo independiente descrito en este informe.