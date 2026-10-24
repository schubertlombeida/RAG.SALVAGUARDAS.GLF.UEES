# Artefactos del recuperador

`python -m src.train` genera `index_config.json` con la huella exacta del corpus.
En RAG, entrenar se adapta a construir el índice; no se ajusta E5 ni Qwen con expedientes del GLF.
No se crean best_model.pkl ni model_v1.pkl vacíos: los pesos de terceros y sus versiones se describen
en arquitectura.md. La configuración es JSON auditable, evitando deserialización pickle no confiable.
Los embeddings privados no se publican.
