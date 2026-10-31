# Herramientas de evaluación del asistente RAG

## Evidencia de esta entrega

Los resultados numéricos de desarrollo se conservan en `results/metrics/historical`, con su procedencia. `docs/optimizacion.md` explica las métricas, la sensibilidad y el alcance de las comparaciones. Los registros funcionales se encuentran en `results/reports`; las pruebas sintéticas de `tests` verifican el comportamiento del código y no se cuentan como consultas reales.

## Formatos y controles

Las plantillas de esta carpeta describen los datos que aceptan las utilidades de evaluación. No constituyen resultados adicionales. Cada anotación identifica pregunta, tema, pasajes relevantes, autor, revisor, nota, estado, partición y SHA-256 del corpus. El validador exige que autor y revisor sean distintos y rechaza registros sin aprobar; esto es un contrato del software, no una afirmación de revisión externa de la entrega. Los grupos de intención permiten mantener reformulaciones en la misma partición.

La huella del archivo JSONL académico y la huella canónica del servicio tienen formatos diferentes. No se intercambian ni se usan para comparar corpus distintos. Las preguntas no contestables se separan de los denominadores de recuperación.

## Métricas implementadas

- Hit@5: existencia de al menos un pasaje relevante entre los cinco primeros.
- Recall@5: proporción de los pasajes relevantes recuperados.
- Precision@5: proporción de pasajes relevantes entre los recuperados.
- MRR@5: inverso de la posición del primer pasaje relevante dentro de los cinco primeros.
- Revisión de respuestas: conteos de afirmaciones sustentadas, adecuación y abstención.
- Tiempo: comparación pareada cuando se proporcionan mediciones manuales y asistidas.

`src/optimize.py` selecciona parámetros con desarrollo y validación, sin recibir test. `src/evaluate.py` permite BM25, BM25 ajustado, E5 y fusión RRF sobre registros compatibles. `src/answer_evaluation.py` resume las revisiones suministradas y conserva valores no estimados sin inventar porcentajes.

## Reproducción del software

```text
python -m pytest -q
```

El cuaderno `05_evaluacion.ipynb` verifica las fórmulas con ejemplos sintéticos identificados y utiliza etiquetas adicionales solo cuando se proporcionan. Los argumentos de las utilidades se consultan mediante `python -m src.evaluate --help`, `python -m src.optimize --help` y `python -m src.answer_evaluation --help`.

## Servicio documentado

La política glf-grounded-v3.1 conserva BM25 para generación y E5 como ruta separada. Qwen2.5-72B se invoca mediante el proveedor remoto registrado Featherless AI. Los límites de salida son 700 tokens en modo breve y 1000 en ampliado, con dos intentos totales y un presupuesto compartido de 50 segundos. El modo ampliado valida contenido estructurado antes de mostrar la prosa. Las pruebas verifican errores, integridad y referencias; los puntajes de recuperación no son probabilidades de verdad.
