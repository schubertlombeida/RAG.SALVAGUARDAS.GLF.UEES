# Manual del asistente documental de salvaguardas GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Corte documental 23 de octubre de 2026

## Para qué sirve

Este manual explica cómo consultar evidencia normativa mediante el portal GLF y cómo reproducir la interfaz académica del Grupo 10. El asistente ayuda a localizar disposiciones y muestra sus fuentes. El usuario debe leer los pasajes y comprobar su pertinencia; el sistema no concede financiamiento, no determina elegibilidad y no reemplaza al especialista.

## Acceso al portal publicado

1. Abra https://glf-postulaciones.vercel.app/ con el acceso de evaluación habilitado por el equipo.
2. Inicie sesión y entre al módulo del asistente RAG o al espacio de revisión permitido por su rol.
3. Abra la consulta de corpus y escriba una pregunta concreta sobre el requisito, riesgo o medida que necesita revisar.
4. Ejecute la consulta y espere la indicación de progreso. No repita clics mientras esté procesando.
5. Revise la respuesta, los pasajes y la página original. Mantenga separada la evidencia encontrada de la decisión técnica.

La cuenta y contraseña para la profesora se comparten fuera del repositorio público. Este manual no publica credenciales ni instruye usar una cuenta administrativa personal. La disponibilidad del módulo depende de los permisos asignados a esa cuenta.

## Instalar la demostración reproducible

Abra una terminal en la raíz del repositorio. Utilice Python 3.12 y cree un entorno virtual antes de instalar dependencias.

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m src.data_processing
python -m src.train
python -m app.app
```

En Linux o macOS active el entorno con source .venv/bin/activate. Abra http://127.0.0.1:8766. La preparación inicial requiere Internet para descargar los PDF oficiales. Si una URL cambia, el proceso falla de forma visible y debe actualizarse el manifiesto y la versión del corpus.

## Hacer una consulta en la demostración

![Pantalla de consulta](../results/figures/ui_desktop.png)

La pantalla presenta la caja de pregunta, el modo de consulta, el botón Consultar y ejemplos. Escriba entre 3 y 600 caracteres. Un ejemplo rellena la caja para que pueda leerlo o modificarlo antes de consultar. El botón muestra progreso y se bloquea durante la operación.

El modo Búsqueda local de pasajes funciona sin claves y utiliza BM25. Devuelve texto recuperado para revisión y lo identifica explícitamente como búsqueda sin generación. El modo Respuesta con IA del servicio del portal necesita que el equipo configure GLF_RAG_URL y GLF_RAG_KEY en el servidor. No escriba claves en el navegador ni las agregue a un cuaderno.

## Interpretar la evidencia

![Resultados y fuentes](../results/figures/ui_results.png)

Cada resultado incluye documento, página e identificador de pasaje. Abra la fuente original para comprobar contexto, excepciones y vigencia. El puntaje de recuperación, cuando se consulte por API, ordena pasajes y no indica certeza. El tiempo mostrado corresponde a esa consulta, no a una evaluación estadística del sistema.

Si el servicio se abstiene, significa que no pudo producir una respuesta con evidencia suficiente bajo sus controles. No interprete esa abstención como inexistencia del requisito. Consulte el documento original o al especialista. Si aparecen pasajes en una abstención, son material de apoyo y no citas de una afirmación generada.

## Consultas recomendadas

Puede preguntar qué actividades figuran en la lista de exclusión, qué es un PGAS o cómo se describen las categorías ambientales y sociales. Es preferible una pregunta concreta a copiar un expediente completo. Para un riesgo específico, describa la actividad y el aspecto que quiere contrastar sin incluir nombres personales, cédulas ni datos reservados.

Una pregunta sobre la aprobación de un proyecto particular o información que no está en las fuentes debe remitirse a la revisión humana. La recuperación de una definición no basta para concluir que una actividad está permitida o excluida.

## Errores frecuentes

| Mensaje o síntoma | Qué hacer |
|---|---|
| Texto demasiado corto o largo | Escriba una consulta entre 3 y 600 caracteres |
| Corpus no preparado | Ejecute python -m src.data_processing y vuelva a abrir la aplicación |
| Servicio RAG sin configurar | Utilice búsqueda local o solicite configuración al equipo |
| Servicio remoto sin evidencia válida | Espere y consulte las fuentes; no tome la falta de respuesta como una decisión |
| Cuota o límite temporal | Espere el plazo indicado y evite repetir solicitudes |
| Cita que no respalda la afirmación | Registre pregunta, pasaje y discrepancia para revisión técnica |
| Fuente cambia o no abre | Revise el enlace oficial y regenere el corpus con una versión nueva |

## Preguntas frecuentes y soporte

¿La búsqueda local es el mismo generador del portal? No. Es una reproducción autónoma de recuperación sobre fuentes públicas; la generación remota requiere configuración. La integración original del portal y del servicio se conserva en integration para inspección.

¿Se ha medido ya la calidad con el nuevo archivo FAQ? No. Se preparó el procedimiento y se calcularán las métricas después de recibir preguntas y pasajes revisados independientemente. Los resultados históricos están identificados por separado.

¿Puedo subir expedientes al repositorio para probar? No utilice datos privados en esta entrega pública. Los datos reales permanecen en el sistema autorizado y sus permisos.

Para reportar un problema de la demostración utilice la sección Issues del repositorio académico, sin incluir credenciales ni datos personales. Indique versión, modo, síntoma y fuente pública. La consulta normativa sustantiva corresponde al especialista del GLF; el equipo académico atiende la reproducción del software.
