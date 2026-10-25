---
title: GLF E5 inference
sdk: docker
app_port: 7860
---

# Servicio E5 para el portal GLF

Este componente convierte texto en vectores para la búsqueda semántica de evidencia normativa. Utiliza `intfloat/multilingual-e5-small` en CPU, con 384 dimensiones y normalización L2. No genera respuestas ni alimenta la generación Qwen: el portal ofrece ambas rutas por separado.

## Integración documentada

El servicio se identifica en https://huggingface.co/spaces/Schubertlm/glf-e5-inference y su endpoint es `https://schubertlm-glf-e5-inference.hf.space/embed`. El portal solicita el vector desde el servidor y consulta la evidencia en Supabase con los permisos del revisor. La revisión funcional del 24 de octubre de 2026 registró seis pasajes recuperados en una consulta de 1,2 segundos; es una observación individual, no una estimación general de latencia o exactitud.

Consulte [arquitectura](../../docs/arquitectura.md) y [evidencia de ejecución](../../results/live_v0762/) para el flujo, versiones y alcance de las comprobaciones. La documentación académica de esta carpeta se actualiza sobre la instantánea identificada en `../source_manifest.json`; los archivos de código mantienen su huella de origen.

## Contrato del servicio

- `GET /health` devuelve el estado y el nombre del modelo.
- `POST /embed` recibe `inputs`, una lista de uno a ocho textos, y `kind`, con valor `query` o `passage`.
- Las consultas admiten hasta 1500 caracteres y los pasajes hasta 12000. Se rechaza texto vacío. El modelo tiene además su límite de tokens; el límite de caracteres no elimina el posible truncamiento.
- Se añade el prefijo `query:` o `passage:` antes de codificar.
- La respuesta contiene `model` y `embeddings`.

## Configuración y acceso

La carpeta contiene Dockerfile y dependencias para un Docker Space de Hugging Face. Configure `GLF_E5_API_KEY` como secreto con al menos 32 caracteres y el mismo valor como variable del servidor de Vercel. `GLF_E5_ENDPOINT` identifica `/embed`. La API exige autenticación Bearer; ninguna clave se entrega al navegador ni se incluye en Git.

La modalidad protegida del Space permite acceder a su aplicación manteniendo privado el repositorio del servicio. La autenticación propia de esta API es distinta de la autenticación de un Space privado de Hugging Face. El cliente documentado utiliza la clave del servicio y no incorpora una segunda credencial de acceso privado de Hugging Face.

## Corpus y límites operativos

El corpus y los expedientes no se almacenan en esta carpeta. Los pasajes se conservan con nombre de documento, versión y localizador en el sistema documental; no se deben mezclar vectores de modelos diferentes. La ruta de pasajes utiliza lotes de hasta ocho entradas. La autorización y revisión de fuentes corresponden al flujo administrativo del corpus.

La carga inicial descarga el modelo y un reinicio del servicio puede aumentar el tiempo de espera. La configuración fija el nombre del modelo, sin fijar una revisión inmutable de sus pesos. Para reproducir una ejecución se registra la revisión resuelta, la versión del corpus y la configuración. El servicio de vectores no incorpora por sí solo una cuota persistente por cuenta ni constituye una auditoría integral del uso institucional.

Una consulta vacía, un fallo del servicio o un resultado sin evidencia no acreditan cumplimiento ambiental o social. La interpretación corresponde al especialista.
