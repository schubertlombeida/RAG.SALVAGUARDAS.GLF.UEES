# Servicio de recuperación BM25 y generación Qwen

La copia contiene el adaptador `glf-grounded-v3.1` documentado el 30 de octubre de 2026. El origen del núcleo se conserva en `UPSTREAM.json`; la procedencia de cada archivo y del registro de despliegue está en `../source_manifest.json`.

El Space de Hugging Face coordina la recuperación en CPU. Qwen2.5-72B-Instruct se invoca mediante un proveedor remoto; la configuración registrada utiliza `Qwen/Qwen2.5-72B-Instruct:featherless-ai`. Los valores por defecto del núcleo histórico no equivalen a las variables configuradas en el despliegue. Las claves se mantienen exclusivamente en el servidor.

El modo breve conserva un máximo de 700 tokens y una orientación de 200 palabras. El ampliado utiliza 1000 tokens, una orientación de 300 palabras y un objeto JSON de hasta cuatro párrafos con referencias elegidas entre los pasajes recuperados. El servicio valida texto, terminación e identificadores antes de presentar la respuesta. Los contextos admiten 12000 y 18000 caracteres; no son recuentos exactos de tokens.

La generación acumula los eventos del proveedor sin publicar texto parcial. Transporte y corrección comparten dos intentos y 50 segundos. Se rechazan salidas vacías, truncadas, mal formadas o con citas desconocidas. No se agregan referencias que el modelo no haya elegido. La pregunta conserva su valor original; la normalización de espacios antes de puntuación se aplica solo al prompt.

Los controles formales no demuestran que cada afirmación esté respaldada semánticamente. La revisión de fuentes continúa a cargo del especialista. E5 es una ruta separada y no alimenta esta generación.

## Ejecución de pruebas

Desde esta carpeta, con las dependencias académicas instaladas:

```text
python -m unittest discover -p 'test_*.py' -q
python -m public_demo.smoke_test
```

La comprobación del 30 de octubre ejecutó 49 pruebas unitarias y la prueba de integración sin inferencia de pago. Los proveedores se sustituyen por respuestas sintéticas identificadas en las pruebas. La aplicación de demostración académica se ejecuta desde la raíz del repositorio; no deben mezclarse sus módulos `src` con los de este servicio.
