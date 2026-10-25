# Integración del portal y servicios de inferencia

Portal: https://glf-postulaciones.vercel.app/
Repositorio de origen: https://github.com/soulkernel/Prototipo.Postulacion.Salvaguardas
Commit de la instantánea: a5a7e5a3ec8703990c2f62ce559536ac0a1eba94, versión 0.7.62.

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
Su README documenta la integración y sus límites operativos. El manifiesto distingue
la huella del documento académico actualizado de su huella de origen; el código
conserva la instantánea original. Consulte `../docs/arquitectura.md` para el flujo completo.

- E5: https://huggingface.co/spaces/Schubertlm/glf-e5-inference
- BM25 y Qwen: https://huggingface.co/spaces/Schubertlm/glf-rag-bm25-qwen

Las comprobaciones del 24 de octubre están en `results/reports/ux_verificacion_20261024.json` y `results/reports/quality_verificacion_20261024.json`; `services_check.json` conserva la revisión anterior. El progreso se transmite por `/api/rag/query` en el portal y `/api/ask-stream` en el servicio; `/api/ask` sigue disponible.
Una consulta funcional no acredita calidad en preguntas independientes.
