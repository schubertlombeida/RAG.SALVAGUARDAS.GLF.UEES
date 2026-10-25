# Protocolo de evaluación del asistente RAG

## Datos y separación

Las preguntas frecuentes orientan el conjunto, pero una respuesta FAQ no sustituye un pasaje correcto anotado. Complete annotation_template.jsonl con IDs del corpus, tema, autor, especialista independiente, fecha, nota y aprobación explícita. Use intent_group para agrupar reformulaciones antes de asignar development, validation o test. Congele el archivo del corpus y su SHA-256. El hash de un archivo académico y la huella canónica que emite el servicio son formatos distintos; no se intercambian ni permiten comparar dos corpus diferentes.

Se proponen 40 a 60 preguntas, 10 a 15 no contestables. Las mediciones de esta entrega corresponden a desarrollo y funcionamiento. No se reportan métricas de una batería independiente ni se utilizan los casos sintéticos de pruebas como estimaciones de calidad GLF.

## Selección y comparación de recuperación

Ejecute desde la raíz, con el mismo data/processed/chunks.jsonl. Configure GLF_E5_ENDPOINT y GLF_E5_API_KEY únicamente en el servidor para E5 y hybrid. BM25 y optimización local no requieren inferencia externa.

```text
python -m src.optimize --development evaluation/gold_development.jsonl --validation evaluation/gold_validation.jsonl --output results/metrics/optimization_reviewed
python -m src.evaluate --labels evaluation/gold_test.jsonl --method bm25
python -m src.evaluate --labels evaluation/gold_test.jsonl --method bm25-heading --configuration results/metrics/optimization_reviewed/optimization.json
python -m src.evaluate --labels evaluation/gold_test.jsonl --method e5
python -m src.evaluate --labels evaluation/gold_test.jsonl --method hybrid
```

La selección usa validación; test se abre una vez fijados parámetros y criterios. El optimizador rechaza fugas explícitas de IDs, preguntas y grupos. La revisión humana debe detectar reformulaciones no marcadas. RRF utiliza 20 candidatos de cada recuperador y constante 60. No se suma coseno a puntajes BM25. Registre Hit@5, Recall@5, Precision@5 y MRR@5 por tema, con conteos. Una pregunta no contestable se evalúa aparte. Conserve cada versión de reportes antes de repetir una ejecución; no compare corpus ni métodos con preparaciones diferentes.

## Calidad de respuesta y utilidad

Revise entre 20 y 30 respuestas de configuraciones congeladas. Cada registro de runs debe contener configuration, query_id, corpus_sha256 y generated (booleano), junto con la respuesta, fuentes, versión y tiempos conservados como evidencia. No comparta claves ni preguntas privadas. Cada registro de reviews debe identificar configuration, query_id, reviewer, review_date, review_status igual a approved, claims_total, claims_supported, answer_adequate, review_note y, cuando se midan, manual_seconds y assisted_seconds. Los CSV vacíos de esta carpeta muestran las columnas; conviértalos a JSONL conservando números y booleanos reales antes de ejecutar.

El especialista anota cada afirmación y comprueba la cita y sus condiciones. En abstenciones, claims_total y claims_supported son cero. Alternar el orden manual/asistido reduce aprendizaje; ambos tiempos deben incluir comprobar fuentes. No confundir un fallo técnico con insuficiencia documental: regístrelo por separado y no elimine casos fallidos silenciosamente.

```text
python -m src.answer_evaluation --labels evaluation/gold_test.jsonl --runs evaluation/answer_runs.jsonl --reviews evaluation/answer_reviews.jsonl --corpus data/processed/chunks.jsonl --output results/metrics/answers_reviewed.json
```

El informe distingue ejecuciones sin revisión, adecuación, soporte de afirmaciones, abstención correcta e incorrecta, y ahorro mediano por pares. Un conjunto sin casos no produce una proporción cero ficticia. El cambio se decide por evidencia y costo/latencia medidos, no por una respuesta aislada más larga.

## Producción y alcance

Producción mantiene BM25 y E5 como rutas separadas. Qwen conserva el proveedor, hardware y cuotas. glf-grounded-v1 añade modos de hasta 700 o 1500 tokens y máximo dos intentos de inferencia; un texto truncado nunca se presenta como respuesta completa. La sintaxis de citas se valida automáticamente; su significado requiere revisión humana. Los ensayos de interfaz y contratos prueban funcionamiento, no precisión normativa.
