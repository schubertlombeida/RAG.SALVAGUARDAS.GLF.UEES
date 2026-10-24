# Guía de entrega y presentación final del proyecto RAG

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Actualización 24 de octubre de 2026

## Qué contiene el paquete

La entrega organiza el proyecto RAG de salvaguardas en un repositorio público y conserva los documentos de las semanas 1 a 5 fuera de cambios. Los seis informes exigidos se publican como Markdown para GitHub y como Word con Arial, títulos 12 en negrita, texto 11 negro, tablas en grises y numeración Página X de Y. El código del portal y del servicio está copiado con manifiesto de procedencia y enlace a la aplicación publicada.

## Correspondencia con la rúbrica

| Requisito | Ubicación | Evidencia o condición |
|---|---|---|
| Repositorio público | README y estructura raíz | URL confirmada por el equipo |
| Planificación | docs/planificacion.md | Problema, alcance, objetivos, cronograma y riesgos |
| Análisis de datos | docs/analisis_datos.md | Conjuntos separados y seis figuras reproducibles |
| Arquitectura | docs/arquitectura.md e integration | Portal, Supabase, E5, BM25, Qwen y contratos |
| Optimización | docs/optimizacion.md, src/optimize.py y cuaderno 04 | Antecedentes separados y rejilla reproducible con validación |
| Ética | docs/consideraciones_eticas.md | Ocho ejes, mitigaciones y estado de mecanismos |
| Manual | docs/manual_usuario.md | Instalación, uso, fuentes y solución de errores |
| Cinco cuadernos | notebooks/01 a 05 | Exploración, preparación, modelado, optimización y evaluación |
| Código modular y pruebas | src, app y tests | Ejecución automática y reporte de resultados |
| Datos y modelos | data y models | Manifiestos y configuración, sin datos privados |
| Interfaz funcional | Portal Vercel y app local | Portal real e interfaz reproducible limitada al RAG |
| Evaluación independiente | evaluation y src/evaluate.py | Requiere preguntas y pasajes revisados |
| Video pitch | Materiales de GUIONES_VIDEOS_20261024 | Guion preparado; grabación y enlace por incorporar |
| Video de preguntas | Materiales de GUIONES_VIDEOS_20261024 | Diez preguntas oficiales recibidas; grabación por incorporar |

La tabla es un control de completitud y no declara como terminados componentes que dependen de evidencia todavía no recibida. Un resultado no ejecutado no se marca aprobado.

## Ruta para integrar las preguntas frecuentes

1. Conservar el archivo FAQ recibido como una versión de fuente local y registrar autoría y fecha.
2. Seleccionar entre 40 y 60 preguntas equilibradas por tema, incluidas entre 10 y 15 no contestables.
3. Congelar PDF, fragmentación e identificadores y obtener la huella del corpus.
4. Pedir a un especialista distinto de quien generó las preguntas que identifique pasajes correctos, página, fuente y razón de la etiqueta.
5. Separar intenciones cercanas entre desarrollo, validación y prueba sin fugas.
6. Ejecutar BM25 y E5 con el mismo corpus, preguntas y top k. Guardar resultados por tema, conteos e intervalos apropiados.
7. Revisar entre 20 y 30 respuestas, abstenciones y tiempos manuales frente a asistidos, incluyendo verificación de citas.
8. Actualizar informes y README con resultados reales, sin sustituir los antecedentes históricos.

Los formatos JSONL y CSV preparados son propios de este paquete. Las dos plantillas Excel de la profesora fueron recibidas y se conservan en la carpeta local INSTRUCCIONES_Y_RUBRICA/PLANTILLAS_METRICAS_PROFESORA, sin confundir el archivo de ejemplo con resultados del equipo.

## Guion del video pitch de cinco minutos

El video debe mostrar el sistema real, resolución mínima de 720p, voz comprensible y un máximo de 8 a 10 diapositivas. El siguiente guion usa ocho y totaliza 300 segundos. La grabación debe corresponder a una versión comprobada del código.

| Tiempo | Diapositiva y objetivo | Contenido o demostración |
|---|---|---|
| 00 a 30 s | 1 Problema y autores | Grupo 10, dispersión normativa y decisión humana |
| 30 a 90 s | 2 Datos | Corpus y versiones separados, fuentes y privacidad |
| 90 a 135 s | 3 Método y optimización | E5 y ruta BM25 Qwen, resultados históricos con alcance |
| 135 a 155 s | 4 Demostración primera consulta | Pregunta concreta, progreso y respuesta con fuentes |
| 155 a 175 s | 5 Demostración y error | Segunda consulta y caso insuficiente o entrada inválida |
| 175 a 195 s | 6 Fuentes y trazabilidad | Abrir una página y contrastar la cita |
| 195 a 240 s | 7 Resultados y límites | Pruebas reales, métricas históricas y evaluación independiente |
| 240 a 285 s | 8 Ética y continuidad | Privacidad, sesgo, responsabilidad y medición siguiente |
| 285 a 300 s | Cierre en diapositiva 8 | Repositorio y portal visibles, conclusión proporcionada |

Los textos completos e intervenciones de cada integrante se encuentran en los guiones separados de GUIONES_VIDEOS_20261024. Durante la grabación se mostrarán las consultas, fuentes y modos de la versión efectivamente publicada. Reemplace cualquier resultado pendiente solo después de medirlo; no presente las métricas históricas como evaluación independiente.

## Video de preguntas de la profesora

Se recibieron las diez preguntas oficiales y se prepararon prompts y guiones separados para ambos videos. Schubert responde las impares y Niko las pares. Cada respuesta debe mostrar evidencia del repositorio o interfaz y corresponder a la versión que se entrega. El pitch utiliza el portal GLF publicado. Las grabaciones se realizarán antes del envío final; sus enlaces se incorporarán al README. Las credenciales de la profesora están preparadas y se remitirán por un canal separado.

## Acceso de evaluación y publicación

El repositorio es https://github.com/schubertlombeida/RAG.SALVAGUARDAS.GLF.UEES y el portal es https://glf-postulaciones.vercel.app/. El acceso de la profesora se comparte por un canal separado con permisos limitados y datos de demostración. No publicar usuario y contraseña, claves de Supabase ni tokens de Hugging Face.

Antes del envío comprobar que el repositorio sea visible sin sesión, los enlaces de ambos videos abran, los documentos se descarguen, los cinco cuadernos correspondan a la versión publicada y el acceso permita entrar al módulo RAG. La publicación del código académico no autoriza cambios de permisos ni de producción del portal.

## Decisiones que se conservan para continuidad

El portal GLF sigue siendo el sistema de aplicación y el RAG una parte acotada de él. No se altera aquí la estructura de formularios, sus validaciones, anexos ni flujos. Las semanas 1 a 5 permanecen intactas. Se mantiene la autoría del Grupo 10, se separan hechos de propuestas y se documentan corpus, modelos y métricas con versiones. El archivo FAQ esperado el 26 de octubre se integrará sin convertir respuestas no revisadas en un gold válido.
