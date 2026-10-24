# Arquitectura e integración del asistente RAG GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Corte documental 23 de octubre de 2026

## Sistema entregado y límites

La solución combina un portal web, almacenamiento y recuperación en Supabase y dos rutas de inferencia documental. El portal es la interfaz funcional del proyecto y está publicado en https://glf-postulaciones.vercel.app/. Este repositorio académico copia los componentes RAG necesarios para explicar la integración y conserva su procedencia. No es una réplica de todos los módulos administrativos del sistema de subvenciones.

La referencia del portal revisada es el commit 382526ecd7b3d8cc250bbe8770e346ee79a83528, versión 0.7.59. El manifiesto integration/source_manifest.json relaciona cada copia con su ruta y SHA256. La copia no incluye secretos, bases de datos, expedientes ni archivos de entorno reales. Los archivos de integración se conservan como instantánea de evidencia; la ejecución autónoma documentada corresponde a app/app.py.

## Flujo real de la consulta

1. El usuario autenticado entra al asistente del portal y escribe su pregunta o prepara una consulta desde la revisión de un riesgo.
2. El servidor valida texto, permisos y configuración. Las claves no se entregan al navegador.
3. La ruta semántica solicita el vector de la consulta a E5 y busca fragmentos del corpus habilitado en Supabase.
4. La ruta de respuesta envía la consulta al servicio RAG en Hugging Face. Este servicio reconstruye su corpus público, recupera con BM25 y entrega los pasajes al generador Qwen.
5. El servicio comprueba las citas y devuelve una respuesta o abstención. El portal valida de nuevo el contrato de fuentes y páginas.
6. El especialista consulta el documento y decide si la evidencia es pertinente. Un resultado del asistente no modifica por sí solo una aprobación, una categoría de riesgo ni una propuesta.

El contexto de revisión puede separar retrieval_query, orientada al riesgo concreto, de la pregunta de generación. El adaptador conserva hasta tres pasajes específicos y una referencia procedimental cuando la consulta lo necesita. Esa selección no constituye un juicio automático sobre el proyecto.

![Arquitectura y separación de rutas](../results/figures/10_architecture.png)

## Servicios de Hugging Face y evidencia actual

El Space E5 es https://huggingface.co/spaces/Schubertlm/glf-e5-inference y su API de vectores es https://schubertlm-glf-e5-inference.hf.space/embed. La interfaz de Hugging Face mostró estado Running y modalidad protected en la revisión del 23 de octubre. Esa modalidad mantiene privado el repositorio del Space y permite acceder a su URL de aplicación; la API exige además su propia clave. No se publican esas claves.

El servidor E5, copiado en integration/e5-inference, carga SentenceTransformer en CPU. Recibe de uno a ocho textos por solicitud, añade query: o passage: y genera vectores normalizados. Limita la consulta a 1500 caracteres y el pasaje a 12000. El modelo admite una longitud máxima de tokens que puede truncar textos largos; el límite de caracteres no demuestra que no haya truncamiento. Fijar la revisión de los pesos y comprobar tokens son medidas de reproducibilidad pendientes, no cambios aplicados al servicio.

El Space generativo es https://huggingface.co/spaces/Schubertlm/glf-rag-bm25-qwen y la consulta usa https://schubertlm-glf-rag-bm25-qwen.hf.space/api/ask. También apareció Running. Una consulta pública sobre PGAS devolvió HTTP 200, respuesta generada, cinco pasajes y dos fuentes; pasó el contrato de citas. El tiempo total informado por el servicio fue 7.331 segundos para esa única consulta. Es una comprobación funcional, no un benchmark ni una evaluación de exactitud semántica.

Las lecturas de salud en esta última prueba encontraron un error de certificado desde el cliente Python. No se desactivó la verificación TLS. Una lectura anterior de healthz sí confirmó siete documentos y 271 fragmentos; la consulta autenticada posterior funcionó. El registro services_check.json conserva tanto los errores como la respuesta correcta. No se realizó una nueva inferencia E5 ni se midió su calidad porque no se configuró su clave en el entorno académico.

El README original de inference conserva notas antiguas de trabajo pendiente. Se mantiene íntegro como evidencia de procedencia, pero no se interpreta como estado actual del despliegue. Este informe diferencia esas notas, el código copiado y las comprobaciones actuales. El portal GLF no se modificó.

## Modelos y funciones

| Componente | Implementación revisada | Entrada y salida |
|---|---|---|
| Representación semántica | intfloat/multilingual-e5-small | Texto query o passage hacia vector de 384 dimensiones |
| Recuperación lexical | BM25-heading-authority-v2 | Consulta hacia hasta cinco pasajes con fuente y página |
| Generación configurada | Qwen/Qwen2.5-72B-Instruct:deepinfra | Contexto y pregunta hacia texto breve con identificadores de cita |
| Validación de evidencia | Contrato Python y Zod del portal | Respuesta remota hacia resultado aceptado o error/abstención |
| Datos y permisos | Supabase | Corpus y expedientes separados con controles de acceso |

E5 transforma textos en vectores; no redacta respuestas. La tarjeta del modelo describe prefijos query y passage, normalización y límite de tokens. El código servidor verifica identidad del modelo, 384 valores finitos y norma no nula, y normaliza el vector. La comparación semántica utiliza similitud vectorial; esa puntuación no es una probabilidad de que una norma aplique.

En la configuración documentada de despliegue, Qwen se invoca a través del router de inferencia de Hugging Face y un proveedor remoto. Hugging Face aloja la aplicación Flask; no debe afirmarse que el modelo de 72 mil millones de parámetros se ejecuta en la CPU del Space. HF_TOKEN permite la inferencia y DEMO_ACCESS_CODE protege la API. El identificador 72B corresponde al runtime de integración, mientras que el archivo upstream conserva por defecto un modelo 7B; la documentación y los benchmarks deben declarar cuál se ejecutó realmente.

## Detalle de recuperación y generación

El recuperador histórico normaliza acentos, tokeniza y calcula BM25 para cuerpo y encabezados. La configuración congelada combina cuerpo con k1 igual a 0.8 y b igual a 0.2, encabezados con k1 igual a 1.2 y b igual a 0.3, peso 0.30 de encabezados y 0.15 de prioridad GLF. Es una prioridad editorial limitada, no una medida de certeza. Una priorización puede recuperar fuentes aun con coincidencia escasa; la abstención debe medirse de extremo a extremo.

El generador upstream usa hasta cuatro pasajes del conjunto recuperado, temperatura cero y una respuesta corta con CHUNK_ID entre corchetes. Si detecta insuficiencia o citas ajenas al contexto, el servicio se abstiene. El adaptador del portal permite un reintento por cita inválida dentro de un presupuesto total de tiempo, sin inventar ni agregar una cita automáticamente.

E5 y Qwen son rutas independientes en la integración revisada. El documento de arquitectura propuesto en una semana anterior incluía fusión y reranker, pero no se presenta esa propuesta como una característica ya desplegada. Los resultados del corpus normativo de 585 fragmentos tampoco se transfieren al corpus público de siete PDF.

## Contratos y controles técnicos

El servidor E5 recibe JSON con inputs y kind. Debe responder model y embeddings. La solicitud usa HTTPS, rechaza redirecciones y permite un reintento ante fallos transitorios de transporte o estados 502, 503 y 504, con espera máxima de 25 segundos por intento. No se cambia de modelo silenciosamente ante un error.

La consulta Qwen acepta entre 3 y 600 caracteres. El contrato exige generated, answer, sources, results y tiempos. Cada fuente debe ser HTTPS del dominio oficial, tener página positiva y corresponder al pasaje devuelto. Las referencias no pueden duplicarse. Una abstención mantiene sources vacío; los resultados pueden mostrarse como material para revisión, sin atribuirles una afirmación generada.

El portal establece un tiempo máximo de 55 segundos para la respuesta remota. El adaptador limita su presupuesto de generación y reintento a 43 segundos. El servicio aplica límites temporales por dirección IP y una cuota global diaria en memoria. Estos controles reducen abuso, pero se reinician con el proceso y no equivalen a un límite persistente de gasto. El presupuesto del proveedor debe administrarse por separado.

## Reproducción y versiones

La interfaz académica Flask funciona en 127.0.0.1:8766. Sin credenciales ejecuta una búsqueda BM25 local y la identifica como recuperación, sin simular generación. Si se configuran GLF_RAG_URL y GLF_RAG_KEY en el servidor, puede usar el servicio autenticado del portal. El modo remoto nunca incorpora la clave al HTML.

requirements.txt fija las dependencias académicas; environment_lock.txt captura las versiones efectivamente instaladas. El código del portal conserva su package.json y lockfile en integration/portal/web. El servicio original conserva runtime.py, Dockerfile, requirements y UPSTREAM.json. Construir el índice en src/train.py no entrena un LLM: genera una configuración JSON con la huella de los datos.

## Interpretabilidad y límites operativos

La evidencia observable es el pasaje, la fuente, la página, el identificador y el tiempo. No se muestra un porcentaje de confianza fabricado a partir del puntaje de BM25 o del coseno de E5. La verificación de formato previene citas inexistentes, pero no detecta todas las contradicciones, omisiones o interpretaciones erróneas. La revisión independiente de afirmaciones es necesaria para medir ese problema.

Fuentes técnicas: Robertson y Zaragoza, BM25 and Beyond, https://doi.org/10.1561/1500000019; Wang y colaboradores, Multilingual E5 Text Embeddings, https://arxiv.org/abs/2402.05672; tarjeta E5, https://huggingface.co/intfloat/multilingual-e5-small; Lewis y colaboradores, Retrieval Augmented Generation, https://arxiv.org/abs/2005.11401.
