import subprocess
from pathlib import Path
from safetensors.torch import load_file, save_file
from huggingface_hub import hf_hub_download

# 1. Descargar solo el text_encoder_2 oficial en FP16 (~1.39 GB)
print("[+] Descargando pesos limpios de CLIP-G (text_encoder_2)...")
te2_path = hf_hub_download(
    repo_id="stabilityai/stable-diffusion-xl-base-1.0",
    filename="text_encoder_2/model.fp16.safetensors"
)

# 2. Convertir a formato nativo con el prefijo exacto que pide stable-diffusion.cpp
print("[+] Mapeando llaves a conditioner.embedders.1.transformer...")
te2_sd = load_file(te2_path)
fixed_te2 = {}
for k, v in te2_sd.items():
    if k.startswith("text_model."):
        fixed_te2[f"conditioner.embedders.1.transformer.{k}"] = v.half()
    else:
        fixed_te2[f"conditioner.embedders.1.transformer.text_model.{k}"] = v.half()

out_te2 = Path(r"E:\models\sd-cpp\clip_g_fix.safetensors")
save_file(fixed_te2, str(out_te2))
print(f"[+] CLIP-G reparado guardado en: {out_te2}")