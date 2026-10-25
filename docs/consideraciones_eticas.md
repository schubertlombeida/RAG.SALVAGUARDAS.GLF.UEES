# Consideraciones éticas y responsabilidad del asistente RAG GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Edición 24 de octubre de 2026

## Alcance y conclusión

El asistente recupera evidencia para una revisión ambiental y social humana. Su utilidad potencial depende de que localice disposiciones pertinentes, respete la confidencialidad y permita corregir errores. El funcionamiento de una consulta no prueba que mejore decisiones o beneficie a comunidades. El análisis distingue controles presentes en el código, medidas documentales incorporadas y verificaciones empíricas que requieren especialistas.

Se utiliza el marco de gestión de riesgos de inteligencia artificial de NIST como referencia de organización, no como certificación del sistema. Las categorías de probabilidad y severidad propuestas por el equipo son juicios para priorizar acciones y no frecuencias medidas de incidentes.

## Sesgo de fuentes y representación

El corpus puede privilegiar documentos extensos, español, fuentes oficiales disponibles y términos exactos. Una traducción o guía derivada puede recuperar mejor que una disposición original sin tener la misma autoridad. El peso GLF mejora una preferencia editorial, pero no demuestra corrección jurídica.

Mitigación técnica y documental: 1. Identificar documento, idioma, tipo de fuente y versión. 2. Mantener traducciones y normalizaciones identificadas. 3. Equilibrar preguntas por tema y registrar resultados desagregados. 4. Revisar errores donde una excepción quede fuera del fragmento. La estructura y procedencia están documentadas. Los resultados incluidos no estiman diferencias por tema sobre una muestra independiente.

## Equidad y acceso

El sistema no clasifica personas ni produce decisiones individuales de concesión. La paridad demográfica no es una métrica adecuada para este recuperador y no se calcula sin datos y una pregunta causal pertinente. Sí es relevante que diferentes temas, idiomas y formas de preguntar reciban apoyo comparable.

Mitigación de evaluación y diseño: 1. Incluir reformulaciones y distintos niveles de lenguaje técnico. 2. Comparar Hit@5 y MRR por tema sobre el mismo corpus. 3. Mantener legibles fuente y página en móvil. 4. Ofrecer acceso directo a los originales cuando la IA falla. La interfaz incluye fuentes legibles; no se afirma haber medido accesibilidad integral ni equidad entre poblaciones.

## Privacidad y protección de datos

El repositorio público utiliza manifiestos de documentos oficiales y código. Excluye expedientes, contraseñas, tokens y embeddings privados. El servicio generativo puede recibir una pregunta y su contexto en un proveedor externo: limitar el corpus a normas públicas no impide que el usuario escriba datos personales en la pregunta.

Mitigación técnica y organizativa: 1. No introducir información identificable en consultas de demostración. 2. Mantener secretos en servidor y separar datos de postulaciones de los textos públicos. 3. Definir finalidad, base de legitimación, conservación y responsables antes de tratar datos personales con IA. 4. Revisar condiciones del proveedor, transferencias y procedimientos para derechos e incidentes. Los dos primeros puntos son controles de la entrega y del código; los documentos de gobernanza y su aplicación institucional no se acreditan como aprobados por este trabajo.

La Ley Orgánica de Protección de Datos Personales, su Reglamento y la normativa aplicable de la Superintendencia de Protección de Datos Personales (SPDP) constituyen referencias para la revisión institucional del tratamiento de datos. Esta revisión no declara cumplimiento legal integral. Identificar una ley no sustituye un inventario de datos, una evaluación de riesgos, contratos ni evidencia de ejercicio de derechos.

| Requisito operativo a documentar | Cambio de diseño relacionado | Situación acreditada |
|---|---|---|
| Finalidad y minimización | Corpus público separado de expedientes | Aplicado a este repositorio |
| Seguridad y confidencialidad | Autenticación, claves en servidor y fuentes permitidas | Visible en el código revisado |
| Información a usuarios y límites | Avisos de apoyo documental y revisión de citas | Incluido en interfaz y manual |
| Conservación y derechos | Política y procedimiento institucional | No demostrado mediante este paquete |
| Evaluación del proveedor y transferencias | Identificar ruta de inferencia y datos enviados | Flujo documentado; valoración jurídica fuera del alcance académico |

## Transparencia y explicabilidad

La interfaz muestra texto recuperado, fuente y página. Los puntajes de BM25 y E5 ordenan documentos; no son probabilidades de verdad. Los controles de citas verifican coherencia formal de identificadores, pero no garantizan que cada afirmación se desprenda del pasaje.

Mitigación técnica y de evaluación: 1. Mostrar qué modo se ejecutó. 2. Distinguir búsqueda sin generación de respuesta con IA. 3. Conservar las citas y abrir la página original. 4. Revisar una muestra de afirmaciones y registrar soportadas, no soportadas y ambiguas. Los tres primeros controles forman parte de la implementación. La revisión de afirmaciones constituye el procedimiento de evaluación semántica; sus resultados independientes no forman parte de las mediciones reportadas.

## Impacto social y ambiental

Una búsqueda más rápida podría reducir trabajo repetitivo y apoyar revisiones consistentes. También puede omitir un criterio, producir una exigencia inexistente o generar dependencia excesiva. En un caso de manglar, por ejemplo, recuperar una definición no basta para establecer si una actividad está excluida: deben revisarse disposición, condiciones y excepciones en el documento completo.

Mitigación de proceso: 1. Registrar el riesgo o pregunta y el fundamento normativo. 2. Pedir al especialista que contraste la disposición y su contexto. 3. Separar sugerencias del asistente de decisiones formales. 4. Medir tiempo con comprobación de citas y utilidad percibida, sin inferir impacto comunitario. El diseño mantiene la decisión humana. No se han medido efectos sociales ni huella energética de los servicios.

## Responsabilidad y seguimiento

El equipo académico responde por describir y probar su implementación. La autoridad técnica institucional mantiene la interpretación y decisión del expediente. La asignación inicial de tareas entre los dos autores es un plan histórico, no prueba de horas ni de revisión especializada independiente.

| Mecanismo | Responsable funcional | Evidencia y estado |
|---|---|---|
| Versionado y manifiestos | Equipo técnico | Commit y huellas incluidos |
| Revisión normativa | Especialista de dominio | Interpretación de respuestas y anotación de evidencia independiente |
| Detección de errores técnicos | Equipo técnico | Pruebas automáticas y errores controlados |
| Registro y corrección de resultados | Administración y especialista | Flujo del portal descrito; no se audita todo su uso institucional |
| Incidentes y derechos | Responsable institucional del tratamiento | Procedimiento formal no acreditado aquí |
| Reevaluación por cambio de corpus o modelo | Equipo técnico y especialista | Protocolo de reevaluación por versión |

Mitigación organizativa: 1. Reportar el identificador de consulta y la fuente sin copiar datos sensibles. 2. Clasificar el error como recuperación, generación, fuente o acceso. 3. Corregir con desarrollo y validación. 4. Reevaluar antes de aplicar cambios a decisiones reales. Un responsable de cierre y una fecha deben acompañar cada incidente institucional.

## Uso indebido y seguridad

Un usuario puede intentar extraer datos, insertar instrucciones en documentos o pedir una conclusión fuera de evidencia. La consulta pública puede ser abusada para generar costos. Las cuotas en memoria y la autenticación ayudan, pero no son un sistema completo de prevención de abuso.

Mitigación técnica: 1. Mantener listas de fuentes autorizadas y no ejecutar instrucciones del texto recuperado. 2. Validar longitud y estructura de solicitudes y respuestas. 3. Aplicar tiempos de espera, cuotas y errores sin secretos. 4. Revisar pruebas adversarias y controles de gasto externos. Se verifican contratos y validaciones; no se presenta esto como una auditoría de penetración ni como resistencia probada a toda inyección de instrucciones.

## Límites y reflexión sobre el diseño

Sí cambiaríamos el diseño respecto de una propuesta que mezclara corpus y tratara toda cita como prueba de exactitud. Congelaríamos un corpus común antes de comparar métodos, haríamos explícita la autoridad de cada fuente y exigiríamos anotación independiente. Mantendríamos la abstención visible y la decisión humana. No incorporaríamos un clasificador que obtiene alta exactitud prediciendo siempre la clase mayoritaria.

El principal límite es empírico: las mediciones históricas y las pruebas funcionales no sustituyen una batería independiente. La estimación de calidad normativa exige pasajes verificables y revisión por un especialista distinto de quien generó las preguntas. Los valores no estimados se identifican como tales, sin asignarles cero ni inferir éxito.

## Referencias

1. NIST. AI Risk Management Framework. https://www.nist.gov/itl/ai-risk-management-framework
2. SPDP. Marco normativo de protección de datos personales. https://www.spdp.gob.ec/marco-normativo/
3. SPDP. Normativa y obligaciones aplicables. https://www.spdp.gob.ec/docs/proteccion-de-datos-personales/general/normativa/
4. SPDP. Comunicación oficial sobre protección de datos e IA. https://www.spdp.gob.ec/prensa/
5. Lewis y colaboradores. Retrieval Augmented Generation for Knowledge Intensive NLP Tasks. https://arxiv.org/abs/2005.11401
6. Wang y colaboradores. Multilingual E5 Text Embeddings. https://arxiv.org/abs/2402.05672
7. Robertson y Zaragoza. The Probabilistic Relevance Framework BM25 and Beyond. https://doi.org/10.1561/1500000019
8. GLF. Manual SGAS y anexos oficiales. Véase data/sources.json para los enlaces individuales y las huellas de las fuentes descargadas.
