# Guía de revisión del proyecto RAG de salvaguardas GLF

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno · Edición 24 de octubre de 2026

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

La versión documentada del portal es 0.7.62 y el servicio RAG corresponde al adaptador 1.7. Las 33 pruebas académicas verifican comportamiento del código. Al incluir portal, base de datos y servicio, el registro de comprobación contiene 326 pruebas. Estos conteos no representan preguntas evaluadas por especialistas ni estimaciones de exactitud normativa.

Las consultas reales registran respuestas, fuentes, tiempos y límites observados. Una referencia técnicamente válida no demuestra por sí sola respaldo semántico. La evaluación independiente se define en evaluation/README.md; las métricas publicadas corresponden a desarrollo y funcionamiento, sin atribuirles generalización externa.

## Presentación audiovisual

El pitch organiza la presentación en siete bloques y ocho pantallas. Su duración máxima es cinco minutos y la demostración utiliza el portal GLF real.

| Intervalo | Contenido |
|---|---|
| 00:00 a 00:30 | Problema y equipo |
| 00:30 a 01:30 | Datos y metodología |
| 01:30 a 02:15 | Desarrollo y optimización |
| 02:15 a 03:15 | Interfaz, casos de uso y manejo de errores |
| 03:15 a 04:00 | Evaluación y resultados |
| 04:00 a 04:45 | Consideraciones éticas |
| 04:45 a 05:00 | Cierre y acceso al proyecto |

El video técnico responde las diez preguntas oficiales en orden. Schubert Lombeida Manjarrez responde las impares y Niko Dimitri Jiménez Bruno las pares. Cada respuesta dura como máximo dos minutos y mantiene al expositor visible en cámara. La pregunta 9 desarrolla la opción C, correspondiente a texto y modelos de lenguaje.

La sección audiovisual del índice utiliza un catálogo de enlaces. Admite archivos MP4 del repositorio y enlaces a una plataforma de reproducción. Una grabación editada identifica los recortes de espera y no transforma la duración del montaje en una medición de latencia.

## Reproducción y trazabilidad

README.md contiene los comandos de instalación y ejecución. Los cuadernos se ordenan desde exploración hasta evaluación. data/sources.json identifica los PDF oficiales; integration/source_manifest.json relaciona los componentes copiados con su origen y huella. Los registros históricos se conservan sin alterar sus resultados.

Los formatos de evaluación exigen pregunta, pasajes correctos, revisor independiente, versión de corpus y partición. Las preguntas frecuentes son un insumo de muestreo y no sustituyen la anotación de evidencia. El protocolo separa desarrollo, validación y prueba, y distingue recuperación, respaldo de afirmaciones y abstención.

## Enlaces de consulta

Repositorio: https://github.com/schubertlombeida/RAG.SALVAGUARDAS.GLF.UEES

Asistente del portal: https://glf-postulaciones.vercel.app/internal/evidence

El portal conserva sus controles de acceso. La revisión del material académico se realiza sobre fuentes públicas, código y evidencia documentada.
