import os
import time
import uuid
import subprocess
from pathlib import Path

# Soporte híbrido para el SDK de MCP v2 (MCPServer) y v1 (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("Vertex-Imagen-Core")
except ImportError:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("Vertex-Imagen-Core")

# ==============================================================================
# RUTAS OFICIALES EN TU DISCO E:
# ==============================================================================
SD_CLI_PATH = Path(r"E:\models\sd-cpp\sd-cli.exe")
if not SD_CLI_PATH.exists() and Path(r"E:\models\sd-cpp\sd.exe").exists():
    SD_CLI_PATH = Path(r"E:\models\sd-cpp\sd.exe")

MODEL_PATH = Path(r"E:\models\Denisijcu\vertex-imagen-core-gguf\vertex-imagen-core-v1-q8_0.gguf")
CLIP_G_PATH = Path(r"E:\models\sd-cpp\clip_g.safetensors")
OUTPUT_DIR = Path(r"E:\models\sd-cpp\outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@mcp.tool()
def generate_vertex_image(
    prompt: str,
    preset: str = "custom",
    width: int = 1024,
    height: int = 1024,
    steps: int = 4,
    seed: int = -1,
    open_image: bool = True
) -> str:
    """
    Genera una imagen de alta resolución usando el motor local Vertex-Imagen-Core-v1 (GGUF Q8_0).
    Úsala siempre que el usuario pida dibujar, diseñar, ilustrar o generar un emblema, portada o gráfico.

    Args:
        prompt: Descripción detallada en inglés del diseño a generar.
        preset: Estilo adicional ('sublimation', 'cover', 'redteam' o 'custom').
        width: Ancho en píxeles (por defecto 1024, usar 768 para mayor velocidad).
        height: Alto en píxeles (por defecto 1024, usar 768 para mayor velocidad).
        steps: Pasos de inferencia SDXL-Lightning (por defecto 4).
        seed: Semilla de generación (-1 para aleatoria).
        open_image: Si es True, abre la imagen automáticamente en Windows al terminar.
    """
    if not SD_CLI_PATH.exists():
        return f"[ERROR] No se encontró el binario en: {SD_CLI_PATH}"
    if not MODEL_PATH.exists():
        return f"[ERROR] No se encontró el modelo GGUF en: {MODEL_PATH}"

    # Sanitización de límites para proteger los 6 GB de VRAM de la GTX 1660 Ti
    width = max(512, min(1024, (width // 64) * 64))
    height = max(512, min(1024, (height // 64) * 64))
    steps = max(1, min(8, steps))

    # Inyección de estilo según preset
    style_addons = {
        "sublimation": "isolated on pure pitch black background, esports and apparel sublimation vector print, high contrast, 8k",
        "cover": "dark sci-fi book cover illustration, Aethelgard aesthetic, cinematic lighting, masterpiece, 8k",
        "redteam": "offensive cybersecurity red team aesthetic, sleek obsidian armor texture, neon cyan and crimson accents, 8k",
        "custom": "high contrast, sharp focus, 8k"
    }
    addon = style_addons.get(preset.lower(), style_addons["custom"])

    clean_prompt = prompt.strip()
    if "vtxcore style" not in clean_prompt.lower():
        clean_prompt = f"vtxcore style, {clean_prompt}"
    final_prompt = f"{clean_prompt}, {addon}"

    filename = f"vtx_mcp_{int(time.time())}_{uuid.uuid4().hex[:6]}.png"
    out_file = OUTPUT_DIR / filename

    # Construcción segura de subproceso (sin shell=True para prevenir Command Injection)
    cmd = [
        str(SD_CLI_PATH),
        "-m", str(MODEL_PATH),
        "-p", final_prompt,
        "-n", "white background, light background, white border, frame, cropped, blurry, low quality, deformed hands, extra swords, asymmetrical, watermark, text",
        "--cfg-scale", "1.0",
        "--steps", str(steps),
        "--sampling-method", "euler",
        "-W", str(width),
        "-H", str(height),
        "-s", str(seed),
        "--vae-tiling",
        "--clip-on-cpu",  # Crítico cuando LM Studio ya ocupa parte de la VRAM
        "--force-sdxl-vae-conv-scale",
        "-o", str(out_file)
    ]

    # Añadir clip_g externo automáticamente si existe en la carpeta
    if CLIP_G_PATH.exists():
        cmd.extend(["--clip_g", str(CLIP_G_PATH)])

    start_t = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SD_CLI_PATH.parent))
    elapsed = round(time.time() - start_t, 2)

    if proc.returncode != 0 or not out_file.exists():
        err_tail = (proc.stderr or proc.stdout)[-600:]
        return f"[ERROR] Falló sd-cli.exe ({proc.returncode}):\n{err_tail}"

    # Abrir automáticamente el PNG en Windows si open_image=True
    if open_image and os.name == "nt":
        try:
            os.startfile(str(out_file))
        except Exception:
            pass

    return (
        f"[OK] Imagen generada exitosamente en {elapsed}s.\n"
        f"- Archivo local: {out_file}\n"
        f"- URL en Studio HUD: http://127.0.0.1:8090/outputs/{filename}\n"
        f"- Resolución: {width}x{height} ({steps} pasos)\n"
        f"- Prompt aplicado: {final_prompt}"
    )


@mcp.tool()
def list_generated_images(limit: int = 10) -> str:
    """
    Lista las últimas imágenes generadas por Vertex-Imagen-Core en el disco E:.
    """
    limit = max(1, min(30, limit))
    files = sorted(OUTPUT_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)[:limit]
    if not files:
        return "No hay imágenes generadas todavía en E:\\models\\sd-cpp\\outputs."

    lines = ["Últimas imágenes generadas en E:\\models\\sd-cpp\\outputs:"]
    for f in files:
        size_mb = round(f.stat().st_size / (1024 * 1024), 2)
        lines.append(f"- {f.name} ({size_mb} MB) -> {f}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()