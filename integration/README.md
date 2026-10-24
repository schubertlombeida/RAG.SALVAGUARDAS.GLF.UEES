# Integración del portal y servicios de inferencia

Portal: https://glf-postulaciones.vercel.app/
Repositorio de origen: https://github.com/soulkernel/Prototipo.Postulacion.Salvaguardas
Commit de la instantánea: 382526ecd7b3d8cc250bbe8770e346ee79a83528, versión 0.7.59.

`source_manifest.json` permite verificar cada archivo copiado. `portal/web` contiene la
selección de componentes, contratos y rutas API que intervienen en RAG, no todo el sistema.
`rag-service` conserva el servicio y el adaptador real con su licencia y UPSTREAM.json.
El servicio se ejecuta desde su propia carpeta, con su propio `src`, para no confundirlo
con los módulos académicos. La interfaz reproducible principal se ejecuta desde la raíz
con `python -m app.app`; las instantáneas de integración no se incluyen en pytest raíz.

La existencia de un endpoint en código no prueba su configuración desplegada; el informe
de arquitectura distingue valores por defecto y el modelo configurado que documenta el runtime.
No se incluyen claves, bases de datos ni datos de postulantes. La licencia MIT de la raíz
cubre código del equipo y no cambia derechos de documentos GLF ni licencias de dependencias.

`e5-inference` contiene el servidor FastAPI real de E5, Dockerfile y dependencias.
Su README es una instantánea original con anotaciones históricas; consulte
`docs/arquitectura.md` para el estado observado y los límites de la verificación.

- E5: https://huggingface.co/spaces/Schubertlm/glf-e5-inference
- BM25 y Qwen: https://huggingface.co/spaces/Schubertlm/glf-rag-bm25-qwen

Las comprobaciones nuevas están en `results/reports/services_check.json`.
Una consulta funcional no acredita calidad en preguntas independientes.
