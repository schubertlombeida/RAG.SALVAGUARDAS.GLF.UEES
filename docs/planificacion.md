# Planificación del asistente RAG de salvaguardas GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Corte documental 23 de octubre de 2026

## Propósito y conclusión

El proyecto desarrolla un asistente de consulta de evidencia normativa para apoyar a los especialistas del Galápagos Life Fund (GLF). El portal ya integra búsqueda documental y una ruta de generación con citas. La entrega académica reúne código, documentación y experimentos anteriores, y prepara una evaluación independiente sobre un corpus común. La utilidad institucional y el cumplimiento de las metas de calidad todavía requieren esa evaluación; una prueba funcional no demuestra impacto social.

Los documentos de las semanas 1 a 5 se preservan como antecedentes entregados. Este informe actualiza la presentación final a partir del código revisado y de la retroalimentación docente, sin reescribir esos antecedentes ni alterar el portal de producción.

## Problema y usuarios

Los requisitos ambientales y sociales están repartidos entre el Manual del Sistema de Gestión Ambiental y Social (SGAS), sus anexos y referencias complementarias. El especialista necesita localizar la disposición aplicable, comprobar su fuente y distinguir una obligación de una recomendación. Una respuesta sin evidencia puede inducir omisiones o requisitos inexistentes.

El usuario principal es el personal técnico que revisa proyectos. Los administradores mantienen corpus, permisos y servicios. Los postulantes son beneficiarios indirectos de una revisión más consistente; el asistente no determina su elegibilidad ni asigna financiamiento. La profesora evalúa reproducibilidad y fundamento técnico mediante el repositorio y un acceso de demostración que se comparte por un canal separado.

## Objetivo y criterios de éxito

El objetivo es recuperar evidencia relevante y producir apoyo documental trazable, manteniendo la decisión en el especialista. Las metas históricas se conservan como objetivos y no como resultados alcanzados de la nueva evaluación.

| Criterio | Definición operativa y meta histórica | Evidencia necesaria |
|---|---|---|
| Cobertura de recuperación | Recall@5 macro de al menos 80 % | Pasajes relevantes anotados por especialista |
| Precisión de recuperación | Precision@5 macro de al menos 80 % | Mismo corpus, preguntas y top k |
| Trazabilidad | Toda respuesta generada con citas comprobables | Verificación de contrato y revisión semántica |
| Tiempo | Reducción mediana de al menos 20 % | Comparación manual y asistida incluyendo lectura de citas |
| Utilidad | Promedio de al menos 4 sobre 5 | Instrumento aplicado a especialistas |
| Latencia | Percentil 95 de hasta 7 segundos | Medición completa con red, recuperación y generación |

Hit@5 mide si aparece al menos un pasaje correcto y no equivale a Recall@5. La existencia de un identificador válido tampoco demuestra que la cita respalde la afirmación.

## Alcance y exclusiones

Se incluyen recuperación lexical BM25, consulta semántica E5, generación con evidencia, tratamiento de insuficiencia documental, fuentes con páginas y una interfaz conectada al portal. El repositorio incorpora una interfaz académica que permite reconstruir la búsqueda con documentos oficiales públicos, además de una copia de la integración real.

Se excluyen aprobación automática, calificación jurídica vinculante, entrenamiento de un modelo de lenguaje con expedientes personales, clasificación demográfica y promesas de generalización no medidas. La fusión BM25 con E5 y el reranking constan como alternativas experimentales históricas; el código revisado no muestra que E5 alimente actualmente la generación de Qwen en el portal.

## Cronograma previsto y situación documentada

| Periodo original | Trabajo previsto | Evidencia disponible al cierre documental |
|---|---|---|
| 19 al 25 de septiembre | Definición, fuentes y objetivos | Documentos de semana 1 y evaluación SMART |
| 26 de septiembre al 2 de octubre | Corpus y baseline lexical | Inventario EDA y decisión técnica |
| 3 al 16 de octubre | Recuperación semántica y RAG | Código E5, BM25, servicio Qwen e integración |
| 17 al 23 de octubre | Piloto y entrega | Análisis ético, portal y preparación de este paquete |
| Incorporación posterior del archivo FAQ | Anotación y evaluación independiente | El equipo prevé recibir el archivo el 26 de octubre |

Estas fechas describen el plan y los materiales existentes. No se deducen horas ejecutadas, entrevistas ni participación individual a partir del nombre de un archivo.

## Equipo y recursos

La autoría confirmada corresponde a Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno. Los documentos iniciales proponían que Niko trabajara corpus, recuperación y evaluación, y Schubert integración web, permisos y flujos. Se conserva esa distribución como planificación histórica; no se presenta como un registro individual de horas o contribuciones confirmadas.

Los recursos son el portal Next.js en Vercel, Supabase para datos y búsqueda vectorial, servicios en Hugging Face, código Python y documentación normativa. El generador utiliza un proveedor de inferencia remoto; el modelo no se entrena dentro de Vercel. La entrega local utiliza un entorno Python aislado y versiones fijadas. Las credenciales y expedientes no forman parte del repositorio público.

## Riesgos de ejecución y respuesta

| Riesgo | Consecuencia | Acción prevista |
|---|---|---|
| Ausencia de gold independiente | Calidad no estimable de forma válida | Preparar anotación y esperar revisión identificada |
| Cambio de corpus o modelo | Resultados no comparables | Registrar huella, versión, fecha y configuración |
| Fuente pública sin licencia de redistribución | Publicación indebida de documentos | Publicar enlaces y script de descarga local |
| Servicio externo no disponible | Consulta sin respuesta | Error comprensible y consulta de fuentes |
| Filtración de expedientes | Afectación a titulares | Corpus público separado, secretos solo en servidor |
| Videos o enlaces incompletos | Entrega académica incompleta | Guion y matriz de cierre con evidencias reales |

## Control de cambios y aceptación

Cada resultado nuevo debe registrar commit, entorno, corpus, preguntas, partición y fecha. Las mejoras se desarrollan con preguntas de desarrollo y validación; el test se congela antes de usarlo. Un cambio de corpus obliga a revisar los pasajes anotados. Se aceptará la evaluación empírica cuando estén disponibles las anotaciones independientes, los conteos por tema y la revisión de respuestas, sin sustituirlos por los resultados históricos.
