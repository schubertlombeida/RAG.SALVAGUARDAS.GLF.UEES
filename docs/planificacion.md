# Planificación del asistente RAG de salvaguardas GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Edición 30 de octubre de 2026

## Propósito y conclusión

El proyecto implementa un asistente de consulta de evidencia normativa para especialistas del Galápagos Life Fund (GLF). Integra búsqueda documental, generación con citas y acceso a las fuentes originales. La entrega reúne el código reproducible, los experimentos de desarrollo, las comprobaciones funcionales y las herramientas de evaluación. Los resultados reportados describen ese alcance; no cuantifican impacto institucional.

El informe presenta el problema, los objetivos, la organización del trabajo, los recursos y los controles de la solución. Los antecedentes de las semanas 1 a 5 se conservan en sus versiones entregadas.

## Problema y usuarios

Los requisitos ambientales y sociales están repartidos entre el Manual del Sistema de Gestión Ambiental y Social (SGAS), sus anexos y referencias complementarias. El especialista necesita localizar la disposición aplicable, comprobar su fuente y distinguir una obligación de una recomendación. Una respuesta sin evidencia puede inducir omisiones o requisitos inexistentes.

El usuario principal es el personal técnico que revisa proyectos. Los administradores mantienen corpus, permisos y servicios. Los postulantes son beneficiarios indirectos de una revisión más consistente; el asistente no determina su elegibilidad ni asigna financiamiento. La profesora evalúa reproducibilidad y fundamento técnico mediante el repositorio y un acceso de demostración que se comparte por un canal separado.

## Objetivo y criterios de éxito

El objetivo es recuperar evidencia relevante y producir apoyo documental trazable, manteniendo la decisión en el especialista. Las metas históricas se conservan como objetivos y no como resultados alcanzados de la evaluación reportada.

| Criterio | Definición operativa y meta histórica | Evidencia necesaria |
|---|---|---|
| Cobertura de recuperación | Recall@5 macro de al menos 80 % | Pasajes relevantes identificados para las consultas de desarrollo |
| Precisión de recuperación | Precision@5 macro de al menos 80 % | Mismo corpus, preguntas y top k |
| Trazabilidad | Toda respuesta generada con citas comprobables | Verificación de contrato y revisión semántica |
| Tiempo | Reducción mediana de al menos 20 % | Comparación manual y asistida incluyendo lectura de citas |
| Utilidad | Promedio de al menos 4 sobre 5 | Instrumento de utilidad percibida, con escala de 1 a 5 |
| Latencia | Percentil 95 de hasta 7 segundos | Medición completa con red, recuperación y generación |

Hit@5 mide si aparece al menos un pasaje correcto y no equivale a Recall@5. La existencia de un identificador válido tampoco demuestra que la cita respalde la afirmación.

## Alcance y exclusiones

Se incluyen recuperación lexical BM25, consulta semántica E5, generación con evidencia, tratamiento de insuficiencia documental, fuentes con páginas y una interfaz conectada al portal. El repositorio incorpora una interfaz académica que permite reconstruir la búsqueda con documentos oficiales públicos, además de una copia de la integración real.

Se excluyen aprobación automática, calificación jurídica vinculante, entrenamiento de un modelo de lenguaje con expedientes personales, clasificación demográfica y promesas de generalización no medidas. La fusión BM25 con E5 está disponible como comparación experimental en el núcleo académico. La generación del portal utiliza BM25 y Qwen; la búsqueda E5 opera por separado.

## Organización del trabajo

| Periodo | Etapa | Productos documentados |
|---|---|---|
| 19 al 25 de septiembre | Definición, fuentes y objetivos | Documentos de semana 1 y evaluación SMART |
| 26 de septiembre al 2 de octubre | Corpus y baseline lexical | Inventario EDA y decisión técnica |
| 3 al 16 de octubre | Recuperación semántica y RAG | Código E5, BM25, servicio Qwen e integración |
| 17 al 23 de octubre | Piloto y entrega | Análisis ético, portal y preparación de este paquete |

El cronograma conserva las etapas del plan. La consolidación efectiva de la entrega se documenta por hitos: publicación del repositorio académico el 25 de octubre; reparación del servicio Qwen registrada el 30 de octubre; revisión del paquete y de las exportaciones audiovisuales el 30 de octubre. El periodo final se extendió para incorporar pruebas, documentación y demostraciones. Los informes semanales permanecen en sus versiones entregadas.

## Equipo y recursos

El Grupo 10 está integrado por Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno. La planificación distribuye corpus, recuperación y evaluación en el frente de datos, e integración web, permisos y flujos en el frente de aplicación. La autoría de la entrega es conjunta.

Los recursos son el portal Next.js en Vercel, Supabase para datos y búsqueda vectorial, servicios en Hugging Face, código Python y documentación normativa. El generador utiliza un proveedor de inferencia remoto; el modelo no se entrena dentro de Vercel. La entrega local utiliza un entorno Python aislado y versiones fijadas. Las credenciales y expedientes no forman parte del repositorio público.

## Riesgos de ejecución y respuesta

| Riesgo | Consecuencia | Control definido |
|---|---|---|
| Etiquetas de desarrollo propuestas por IA | Estimación optimista del desempeño | Identificar su origen y limitar la conclusión al experimento documentado |
| Cambio de corpus o modelo | Resultados no comparables | Registrar huella, versión, fecha y configuración |
| Fuente pública sin licencia de redistribución | Publicación indebida de documentos | Publicar enlaces y script de descarga local |
| Servicio externo no disponible | Consulta sin respuesta | Error comprensible y consulta de fuentes |
| Filtración de expedientes | Afectación a titulares | Corpus público separado, secretos solo en servidor |

## Control de cambios y aceptación

Cada resultado registra versión, entorno, corpus, preguntas, partición y fecha. Los parámetros se seleccionan con desarrollo y validación; el conjunto de prueba se reserva para la evaluación de la configuración fijada. Un cambio de corpus exige revisar los pasajes anotados. Las mediciones históricas se presentan con sus etiquetas de desarrollo. La revisión funcional comprueba contratos, integridad, errores e interacción; no se presenta como una medida de exactitud normativa.
