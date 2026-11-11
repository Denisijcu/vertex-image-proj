import os
import time
import uuid
import shutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# ==============================================================================
# CONFIGURACIÓN DE RUTAS (VALIDADO CON CLIP_G Y ESCALA VAE SDXL)
# ==============================================================================
SD_CLI_PATH = Path(r"E:\models\sd-cpp\sd-cli.exe")
if not SD_CLI_PATH.exists() and Path(r"E:\models\sd-cpp\sd.exe").exists():
    SD_CLI_PATH = Path(r"E:\models\sd-cpp\sd.exe")

MODEL_PATH = Path(r"E:\models\Denisijcu\vertex-imagen-core-gguf\vertex-imagen-core-v1-q8_0.gguf")
CLIP_G_PATH = Path(r"E:\models\sd-cpp\clip_g.safetensors")
OUTPUT_DIR = Path(r"E:\models\sd-cpp\outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Copiar tu vertex_wolf.png a la carpeta de galería si aún no está ahí
wolf_test = Path(r"E:\models\sd-cpp\vertex_wolf.png")
if wolf_test.exists() and not (OUTPUT_DIR / "vertex_wolf.png").exists():
    shutil.copy2(wolf_test, OUTPUT_DIR / "vertex_wolf.png")

app = FastAPI(title="Vertex-Imagen-Core-v1 // Studio HUD", version="1.1.0")


# Habilitar CORS estricto para tus orígenes locales de Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8090",
        "http://127.0.0.1:8090",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")




class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=1200)
    negative_prompt: str = Field(default="blurry, low quality, deformed, watermark, text, signature")
    width: int = Field(default=1024, ge=512, le=1024)
    height: int = Field(default=1024, ge=512, le=1024)
    steps: int = Field(default=4, ge=1, le=12)
    cfg_scale: float = Field(default=1.0, ge=0.0, le=5.0)
    seed: int = Field(default=-1)
    clip_on_cpu: bool = Field(default=False)


@app.post("/api/generate")
def generate_image(req: GenerateRequest):
    if not SD_CLI_PATH.exists():
        raise HTTPException(status_code=500, detail=f"No se encontró sd-cli.exe en: {SD_CLI_PATH}")
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=500, detail=f"No se encontró el GGUF en: {MODEL_PATH}")
    if not CLIP_G_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Falta clip_g.safetensors en: {CLIP_G_PATH}")

    final_prompt = req.prompt.strip()
    if "vtxcore style" not in final_prompt.lower():
        final_prompt = f"vtxcore style, {final_prompt}"

    filename = f"vtx_{int(time.time())}_{uuid.uuid4().hex[:6]}.png"
    out_file = OUTPUT_DIR / filename

    # Comando idéntico al que te funcionó en PowerShell
    cmd = [
        str(SD_CLI_PATH),
        "-m", str(MODEL_PATH),
        "--clip_g", str(CLIP_G_PATH),
        "-p", final_prompt,
        "-n", req.negative_prompt,
        "--cfg-scale", str(req.cfg_scale),
        "--steps", str(req.steps),
        "--sampling-method", "euler",
        "-W", str(req.width),
        "-H", str(req.height),
        "-s", str(req.seed),
        "--vae-tiling",
        "--force-sdxl-vae-conv-scale",
        "-v",
        "-o", str(out_file)
    ]

    if req.clip_on_cpu:
        cmd.append("--clip-on-cpu")

    start_t = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SD_CLI_PATH.parent))
    elapsed = round(time.time() - start_t, 2)

    if proc.returncode != 0 or not out_file.exists():
        err_msg = (proc.stderr or proc.stdout)[-800:]
        raise HTTPException(status_code=500, detail=f"Fallo en sd-cli.exe:\n{err_msg}")

    return {
        "status": "ok",
        "image_url": f"/outputs/{filename}",
        "filename": filename,
        "elapsed_seconds": elapsed,
        "prompt_used": final_prompt
    }


@app.get("/api/gallery")
def list_gallery():
    files = sorted(OUTPUT_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)[:16]
    return [{"url": f"/outputs/{f.name}", "name": f.name} for f in files]


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8" />
  <title>Vertex-Imagen-Core-v1 | Studio HUD</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color: #e2e8f0; font-family: 'Segoe UI', system-ui, sans-serif; }
    .glass { background: rgba(15, 23, 42, 0.78); backdrop-filter: blur(14px); border: 1px solid rgba(56, 189, 248, 0.22); }
    .neon-btn { background: linear-gradient(90deg, #0284c7, #06b6d4); box-shadow: 0 0 20px rgba(6, 182, 212, 0.35); }
    .neon-btn:hover { box-shadow: 0 0 28px rgba(6, 182, 212, 0.65); }
  </style>
</head>
<body class="min-h-screen p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    <header class="glass rounded-2xl p-5 flex items-center justify-between">
      <div>
        <div class="flex items-center gap-3">
          <span class="h-3 w-3 rounded-full bg-emerald-400 animate-pulse"></span>
          <h1 class="text-2xl font-bold tracking-wider text-cyan-400">VERTEX-IMAGEN-CORE-V1 // STUDIO HUD</h1>
        </div>
        <p class="text-xs text-slate-400 mt-1">Motor: stable-diffusion.cpp (CUDA + CLIP-G Fix) | Modelo: vertex-imagen-core-v1-q8_0.gguf (4-Steps)</p>
      </div>
      <span class="px-3 py-1 rounded-full text-xs font-mono bg-emerald-950 text-emerald-300 border border-emerald-700">GTX 1660 Ti // ONLINE</span>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <section class="lg:col-span-5 glass rounded-2xl p-6 space-y-4">
        <label class="text-sm font-semibold text-cyan-300">PROMPT DE DISEÑO (Auto-Trigger: vtxcore style)</label>
        <textarea id="prompt" rows="4" class="w-full rounded-xl bg-slate-900/90 border border-slate-700 p-3 text-sm focus:border-cyan-400 focus:outline-none">vtxcore style, aggressive cybernetic wolf emblem, geometric metallic plates, glowing emerald eyes, isolated on solid black background, esports and apparel sublimation vector print, 8k</textarea>

        <div class="space-y-1">
          <span class="text-xs text-slate-400">Presets rápidos de Vertex Coders:</span>
          <div class="flex flex-wrap gap-2">
            <button onclick="setPreset('sublimation')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 border border-slate-700 text-cyan-300">Sublimación / Vector</button>
            <button onclick="setPreset('cover')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 border border-slate-700 text-cyan-300">Portada Sci-Fi / Aethelgard</button>
            <button onclick="setPreset('redteam')" class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 border border-slate-700 text-cyan-300">Ciberseguridad / Red Team</button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 pt-2">
          <div>
            <label class="text-xs text-slate-400">Resolución</label>
            <select id="res" class="w-full mt-1 rounded-lg bg-slate-900 border border-slate-700 p-2 text-sm">
              <option value="1024x1024">1024 x 1024 (Nativa)</option>
              <option value="768x768">768 x 768 (Rápida)</option>
              <option value="512x512">512 x 512 (Borrador)</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-slate-400">Pasos (Lightning)</label>
            <input id="steps" type="number" value="4" min="1" max="12" class="w-full mt-1 rounded-lg bg-slate-900 border border-slate-700 p-2 text-sm" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs text-slate-400">CFG Scale</label>
            <input id="cfg" type="number" step="0.5" value="1.0" class="w-full mt-1 rounded-lg bg-slate-900 border border-slate-700 p-2 text-sm" />
          </div>
          <div>
            <label class="text-xs text-slate-400">Seed (-1 = Aleatorio)</label>
            <input id="seed" type="number" value="-1" class="w-full mt-1 rounded-lg bg-slate-900 border border-slate-700 p-2 text-sm" />
          </div>
        </div>

        <label class="flex items-center gap-2 pt-1 cursor-pointer">
          <input id="clip_cpu" type="checkbox" class="rounded bg-slate-900 border-slate-700 text-cyan-500" />
          <span class="text-xs text-slate-300">Modo Low-VRAM (<code>--clip-on-cpu</code> si tienes LM Studio abierto)</span>
        </label>

        <button id="genBtn" onclick="generate()" class="w-full neon-btn text-slate-950 font-bold py-3 rounded-xl transition flex items-center justify-center gap-2">
          <span>⚡ GENERAR IMAGEN (4 PASOS)</span>
        </button>

        <div id="statusBox" class="hidden text-xs font-mono p-3 rounded-xl bg-slate-950/90 border border-slate-800 text-emerald-400 whitespace-pre-wrap"></div>
      </section>

      <section class="lg:col-span-7 glass rounded-2xl p-6 flex flex-col items-center justify-center min-h-[540px] relative">
        <div id="loader" class="hidden flex-col items-center gap-3">
          <div class="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p class="text-sm font-mono text-cyan-300">Renderizando 1024x1024 en GTX 1660 Ti...</p>
        </div>
        <img id="mainImage" src="/outputs/vertex_wolf.png" class="max-h-[520px] rounded-xl shadow-2xl border border-cyan-500/30" onerror="this.classList.add('hidden')" />
        <a id="downloadBtn" href="/outputs/vertex_wolf.png" download class="mt-3 text-xs font-mono text-cyan-300 hover:underline">⬇ Descargar PNG (1024x1024)</a>
      </section>
    </div>

    <section class="glass rounded-2xl p-5">
      <h2 class="text-sm font-semibold text-cyan-400 mb-3">HISTORIAL LOCAL (E:\\models\\sd-cpp\\outputs) — Clic para ver en grande</h2>
      <div id="gallery" class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-3"></div>
    </section>
  </div>

  <script>
    const presets = {
      sublimation: "vtxcore style, aggressive cybernetic wolf emblem, geometric metallic plates, glowing emerald eyes, isolated on solid black background, esports and apparel sublimation vector print, high contrast, 8k",
      cover: "vtxcore style, dark sci-fi book cover illustration, lone cybernetic architect standing before a massive glowing quantum data monolith in the void, Aethelgard aesthetic, cinematic lighting, masterpiece",
      redteam: "vtxcore style, offensive cybersecurity red team shield emblem, glowing binary matrix firewall, sleek obsidian armor texture, neon red and cyan accents, minimal tech cover art, 8k"
    };

    function setPreset(key) {
      document.getElementById('prompt').value = presets[key];
    }

    function showInViewer(url, name) {
      const img = document.getElementById('mainImage');
      const dl = document.getElementById('downloadBtn');
      img.src = url + '?t=' + Date.now();
      img.classList.remove('hidden');
      dl.href = url;
      dl.textContent = `⬇ Descargar ${name} (1024x1024)`;
    }

    async function loadGallery() {
      const res = await fetch('/api/gallery');
      const items = await res.json();
      const gal = document.getElementById('gallery');
      gal.innerHTML = items.map(i => `
        <button onclick="showInViewer('${i.url}', '${i.name}')" class="block overflow-hidden rounded-lg border border-slate-800 hover:border-cyan-400 transition">
          <img src="${i.url}" class="w-full h-24 object-cover" title="${i.name}" />
        </button>
      `).join('');
    }

    async function generate() {
      const btn = document.getElementById('genBtn');
      const loader = document.getElementById('loader');
      const img = document.getElementById('mainImage');
      const statusBox = document.getElementById('statusBox');
      const [w, h] = document.getElementById('res').value.split('x').map(Number);

      btn.disabled = true;
      btn.classList.add('opacity-50');
      loader.classList.remove('hidden');
      loader.classList.add('flex');
      img.classList.add('hidden');
      statusBox.classList.remove('hidden');
      statusBox.textContent = "[+] Ejecutando sd-cli.exe con --clip_g y --vae-tiling...";

      try {
        const res = await fetch('/api/generate', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            prompt: document.getElementById('prompt').value,
            width: w,
            height: h,
            steps: Number(document.getElementById('steps').value),
            cfg_scale: Number(document.getElementById('cfg').value),
            seed: Number(document.getElementById('seed').value),
            clip_on_cpu: document.getElementById('clip_cpu').checked
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Error al generar');

        showInViewer(data.image_url, data.filename);
        statusBox.textContent = `[+] ¡Completado en ${data.elapsed_seconds}s!\n[+] Guardado en: E:\\models\\sd-cpp\\outputs\\${data.filename}`;
        loadGallery();
      } catch (err) {
        statusBox.textContent = "[!] ERROR: " + err.message;
      } finally {
        loader.classList.add('hidden');
        loader.classList.remove('flex');
        btn.disabled = false;
        btn.classList.remove('opacity-50');
      }
    }

    loadGallery();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("🚀 Vertex-Imagen-Core-v1 Studio HUD activo en http://127.0.0.1:8090")
    uvicorn.run(app, host="127.0.0.1", port=8090)