# Asistente RAG de salvaguardas GLF

![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/Code-MIT-lightgrey)

Grupo 10 · Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno.

## Contenido

1. [Problema](#problema)
2. [Solución](#solución)
3. [Datos](#datos)
4. [Método](#método)
5. [Resultados](#resultados)
6. [Instalación](#instalación)
7. [Interfaz](#interfaz)
8. [Estructura](#estructura)
9. [Documentación](#documentación)
10. [Ética y límites](#ética-y-límites)
11. [Equipo](#equipo)
12. [Licencias](#licencias)
13. [Fuentes y reconocimientos](#fuentes-y-reconocimientos)
14. [Videos de entrega](#videos-de-entrega)

## Problema

Los especialistas del GLF necesitan localizar requisitos repartidos entre manuales y anexos.
Este sistema recupera evidencia y apoya su consulta. No aprueba proyectos, no determina
financiamiento y no reemplaza la interpretación humana.

## Solución

El [portal GLF publicado](https://glf-postulaciones.vercel.app/) es la interfaz real.
Esta entrega incluye una copia trazable de su integración RAG y una demostración Python
reproducible sobre documentos públicos. Las semanas 1 a 5 entregadas no se modifican.

## Datos

Se distinguen los 26 expedientes históricos privados, el corpus normativo de 585 fragmentos
y siete PDF públicos usados por el servicio generativo. No se publican datos de postulantes.
[Fuentes y derechos](data/README.md) y [manifiesto de descarga](data/sources.json).
El recuento reconstruido se guarda en [public_eda.json](results/metrics/public_eda.json).

## Método

- E5-small genera vectores de 384 dimensiones para recuperación semántica.
- La ruta generativa usa BM25 y Qwen con fuentes y páginas. E5 no alimenta esa generación en la integración revisada.
- El servicio en Hugging Face invoca un proveedor remoto; Vercel no ejecuta los pesos de Qwen.
- Los puntajes de recuperación no son probabilidades de verdad.
- Configuración, límites, contratos y modelos: [arquitectura](docs/arquitectura.md).

## Resultados

Los resultados históricos de BM25 reportan Recall@5 de desarrollo de 68.9 % a 83.6 %.
Corresponden a otro corpus y anotación; **no son la validación independiente final ni métricas del portal actual**.
El benchmark anterior de Qwen 7B local no se transfiere al runtime 72B remoto.
Los originales numéricos y sus límites se conservan en [históricos](results/metrics/historical/PROVENANCE.md).

Las pruebas nuevas se registran en [verificacion.json](results/reports/verificacion.json).
El nuevo conjunto FAQ y sus pasajes revisados no se han recibido. La evaluación de calidad
se ejecutará con corpus común y anotación independiente; no se rellenan métricas faltantes con ceros.

## Instalación

Python 3.12, conexión a Internet para preparar fuentes y entorno virtual.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.data_processing
python -m src.train
python -m pytest -q
python -m app.app
```

Abra http://127.0.0.1:8766. La búsqueda local funciona sin claves y se identifica como
recuperación sin generación. Para respuesta con IA, configure en el servidor GLF_RAG_URL y
GLF_RAG_KEY según .env.example. No se cargan archivos .env automáticamente ni se publican claves.

## Interfaz

![Interfaz de consulta](results/figures/ui_desktop.png)

Escriba una pregunta o pulse un ejemplo, seleccione modo y consulte. Abra la fuente y
revise la página. Entrada inválida, corpus ausente y servicio no disponible tienen mensajes
propios. [Manual completo](docs/manual_usuario.md).

## Estructura

```text
docs/           Seis informes exigidos y guía de entrega
notebooks/      Cinco cuadernos ordenados y ejecutables
src/            Preparación, modelos, índice, evaluación y utilidades
app/            Interfaz Flask con ejemplos y progreso
tests/          Validaciones de datos, recuperación, evaluación y contratos
data/           Manifiesto público y carpetas locales excluidas de Git
models/         Configuración JSON del índice y explicación RAG
integration/    Copias trazables del portal y servicio original
evaluation/     Formatos de anotación, abstención, soporte y tiempos
results/        Figuras, métricas históricas y verificaciones nuevas
entregables/    Versiones Word de los informes
```

El requisito genérico de archivos pickle se adapta a un índice RAG con configuración JSON
y pesos de terceros identificados. No se crean modelos vacíos ni se declara fine tuning.

## Documentación

- [Planificación](docs/planificacion.md)
- [Análisis de datos](docs/analisis_datos.md)
- [Arquitectura](docs/arquitectura.md)
- [Optimización](docs/optimizacion.md)
- [Consideraciones éticas](docs/consideraciones_eticas.md)
- [Manual de usuario](docs/manual_usuario.md)
- [Guía de entrega, rúbrica y videos](docs/guia_entrega_y_videos.md)

Versiones editables en Word:

1. [Planificación](entregables/01_Planificacion_RAG_GLF.docx)
2. [Análisis de datos](entregables/02_Analisis_de_datos_RAG_GLF.docx)
3. [Arquitectura](entregables/03_Arquitectura_RAG_GLF.docx)
4. [Optimización](entregables/04_Optimizacion_RAG_GLF.docx)
5. [Consideraciones éticas](entregables/05_Consideraciones_eticas_RAG_GLF.docx)
6. [Manual de usuario](entregables/06_Manual_de_usuario_RAG_GLF.docx)
7. [Guía de entrega y videos](entregables/07_Guia_de_entrega_y_videos_RAG_GLF.docx)

Los Word usan Arial, títulos 12 en negrita, texto 11 negro, tablas grises y gráficos a color. La visualización
Markdown de GitHub usa las fuentes propias de GitHub; el formato solicitado se conserva en Word.

## Ética y límites

Datos privados separados, claves en servidor, decisión humana y fuentes verificables.
Validar citas formales no prueba que todas las afirmaciones estén sustentadas. No se afirma
cumplimiento jurídico integral, impacto social medido ni equidad demográfica de un clasificador
de personas. Las limitaciones y mitigaciones se documentan con su estado real.

## Equipo

Autores: Schubert Lombeida Manjarrez y Niko Dimitri Jiménez Bruno, Grupo 10.
La planificación inicial asignaba corpus y recuperación a Niko e integración web a Schubert.
Es una distribución histórica propuesta, no un registro individual de horas confirmado.

## Licencias

Código del equipo bajo [MIT](LICENSE). Los documentos GLF y pesos de terceros conservan
sus derechos y licencias. No se redistribuye el corpus privado ni se relicencian los PDF.

## Fuentes y reconocimientos

GLF aporta las fuentes normativas oficiales; el equipo académico es responsable de la
implementación y de sus afirmaciones. No se declara aprobación institucional del sistema.
Referencias técnicas: [BM25](https://doi.org/10.1561/1500000019),
[Multilingual E5](https://arxiv.org/abs/2402.05672),
[RAG](https://arxiv.org/abs/2005.11401) y [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework).

## Videos de entrega

El pitch de máximo cinco minutos y el video de preguntas son requisitos distintos.
Sus grabaciones y enlaces todavía no se han aportado. La [guía](docs/guia_entrega_y_videos.md)
contiene el guion de 300 segundos y el procedimiento para incorporar las preguntas oficiales.
Esta versión no se declara entrega académica completamente cerrada mientras falten esas
evidencias y la evaluación independiente.
