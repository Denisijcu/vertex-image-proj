---
license: openrail++
pipeline_tag: text-to-image
base_model: stabilityai/stable-diffusion-xl-base-1.0
tags:
  - stable-diffusion-xl
  - sdxl-lightning
  - gguf
  - stable-diffusion.cpp
  - mcp-server
  - vertex-coders
---

# Vertex-Imagen-Core-v1 // Studio HUD & MCP

Desarrollado por **Denis Sanchez Leyva** (**Vertex Coders LLC** - Miami, FL).

Plataforma de generación de imágenes local optimizada para arquitecturas de **6 GB de VRAM** (NVIDIA GTX 1660 Ti), combinando un servidor web **FastAPI (Studio HUD)**, integración nativa con **Model Context Protocol (MCP)** para agentes de IA en **LM Studio**, y el motor C++ de **`stable-diffusion.cpp`** con aceleración de **4 pasos (`SDXL-Lightning`)**.

## Componentes del Proyecto
1. **`vertex_image_studio.py`**: Interfaz web local con HUD oscuro (Glassmorphism) en `http://localhost:8090`.
2. **`vertex_imagen_mcp.py`**: Servidor MCP v2 para automatizar la creación de diseños desde modelos de lenguaje (LLMs).
3. **`vertex-imagen-core-v1-q8_0.gguf`**: Modelo principal en formato GGUF (Q8_0).

---

## Guía Completa: Cómo Usarlo desde LM Studio

Para que tus agentes de IA locales en **LM Studio** puedan generar imágenes bajo demanda mediante *Tool Calling* sin colapsar tu memoria gráfica, sigue este flujo de integración:

### Requisito previo
Asegúrate de tener descargados en tu máquina:
- El motor C++ y sus librerías CUDA en `E:\models\sd-cpp\sd-cli.exe`
- El modelo cuantizado en `E:\models\Denisijcu\vertex-imagen-core-gguf\vertex-imagen-core-v1-q8_0.gguf`
- El codificador auxiliar en `E:\models\sd-cpp\clip_g.safetensors`

### Paso 1: Configurar el Servidor MCP en LM Studio
1. Abre **LM Studio** y carga un modelo con soporte de herramientas (por ejemplo, un LLM de 3B optimizado para herramientas).
2. En el panel derecho, haz clic en el icono de herramientas/programación (**Program**) e ingresa a la configuración de servidores MCP (`mcp.json`).
3. Agrega la siguiente entrada apuntando a tu script de Python:

```json
{
  "mcpServers": {
    "vertex-imagen-core": {
      "command": "python",
      "args": [
        "E:\\models\\sd-cpp\\vertex_imagen_mcp.py"
      ]
    }
  }
}