# Guía de revisión del proyecto RAG de salvaguardas GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Edición 30 de octubre de 2026

## Acceso y recorrido de lectura

La entrega reúne la implementación RAG, seis informes temáticos, cinco cuadernos y evidencia de evaluación. El punto de entrada es index.html, que permite leer los informes, descargarlos y acceder a su fuente en GitHub. El menú ofrece dos áreas: Documentación y Portal GLF.

En Documentación se recomienda comenzar por el manual de usuario, continuar con arquitectura y revisar los informes de datos, optimización, ética y planificación según el criterio de evaluación. Los documentos Word y PDF conservan Arial 11, títulos Arial 12 en negrita, texto negro, tablas grises y numeración de páginas. Las figuras se mantienen a color.

Portal GLF abre el asistente publicado. La profesora utiliza la cuenta facilitada por el equipo mediante el portal de la universidad. El índice y el repositorio no solicitan ni contienen contraseñas. La aplicación académica local permite reproducir la recuperación sobre fuentes públicas sin acceder a expedientes privados.

## Documentos y criterios de evaluación

| Criterio | Documento o recurso | Contenido |
|---|---|---|
| Problema y planificación | docs/planificacion.md | Usuarios, objetivos, alcance, etapas y riesgos |
| Análisis de datos | docs/analisis_datos.md | Fuentes, conjuntos separados y seis figuras |
| Diseño técnico | docs/arquitectura.md e integration | Portal, servicios, modelos y flujos de consulta |
| Optimización | docs/optimizacion.md y cuaderno 04 | Comparación histórica, sensibilidad y protocolo reproducible |
| Ética | docs/consideraciones_eticas.md | Sesgos, privacidad, explicabilidad y responsabilidad |
| Uso de la aplicación | docs/manual_usuario.md | Modos, etapas, fuentes, exportación y errores |
| Código y pruebas | src, app, tests y .github/workflows/ci.yml | Ejecución local y comprobaciones automáticas |
| Evaluación | evaluation y results | Formatos, resultados con alcance y registros de consultas |
| Presentación audiovisual | Catálogo de videos del índice | Pitch y respuestas técnicas |

## Cómo interpretar la evidencia

El corpus público reconstruido contiene siete documentos, 98 páginas y 271 fragmentos. Los experimentos históricos de recuperación utilizaron otro corpus de 585 fragmentos. Sus resultados se presentan con la configuración y el contexto de desarrollo que les corresponden.

La copia de componentes del portal conserva el commit de la versión 0.7.62; el servicio incorpora la política glf-grounded-v3.1 documentada el 30 de octubre. En esa fecha se ejecutaron 33 pruebas académicas, 49 pruebas del servicio y su prueba de integración. Los registros anteriores conservan sus fechas y alcance. Estos conteos corresponden a la verificación funcional del código.

Las consultas reales registran respuestas, fuentes, tiempos y límites observados. Una referencia técnicamente válida no demuestra por sí sola respaldo semántico. Las métricas publicadas corresponden a desarrollo y funcionamiento y se interpretan dentro de sus corpus y condiciones.

## Presentación audiovisual

El pitch exportado dura 4 minutos y 4 segundos, dentro del máximo de cinco minutos. Presenta problema, datos, metodología, demostración del portal, resultados, ética y cierre. El video técnico dura 12 minutos y 17 segundos. Las duraciones corresponden a los archivos revisados, no a tiempos de inferencia.

| Video | Propósito | Duración revisada |
|---|---|---|
| Pitch | Presentación del problema, solución y demostración | 4 min 4 s |
| Diez respuestas técnicas | Decisiones, evidencia, errores y límites | 12 min 17 s |

El video técnico responde las diez preguntas oficiales en orden. Schubert Lombeida Manjarrez responde las impares y Niko Dimitri Jiménez Bruno las pares. Cada respuesta dura como máximo dos minutos y mantiene al expositor visible en cámara. La pregunta 9 desarrolla la opción C, correspondiente a texto y modelos de lenguaje.

La sección audiovisual del índice utiliza un catálogo de enlaces. Admite archivos MP4 del repositorio y enlaces a una plataforma de reproducción. Una grabación editada identifica los recortes de espera y no transforma la duración del montaje en una medición de latencia.

## Reproducción y trazabilidad

README.md contiene los comandos de instalación y ejecución. Los cuadernos se ordenan desde exploración hasta evaluación. data/sources.json identifica los PDF oficiales; integration/source_manifest.json relaciona los componentes copiados con su origen y huella. Los registros históricos se conservan sin alterar sus resultados.

Las utilidades de evaluación distinguen recuperación, respaldo de afirmaciones y abstención. Sus formatos identifican pregunta, pasajes, versión de corpus y partición. Las pruebas sintéticas demuestran el comportamiento de esas funciones y se separan de las métricas de desarrollo publicadas.

