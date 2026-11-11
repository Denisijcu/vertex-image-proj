import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  VertexImagenService,
  ImagenGenerateRequest,
  GalleryItem,
} from '../../services/vertex-imagen.service';

@Component({
  selector: 'app-vertex-imagen-hud',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="p-6 bg-slate-950 text-slate-100 rounded-2xl border border-cyan-500/20 shadow-2xl space-y-6">
      <!-- Top Telemetry Bar -->
      <div class="flex flex-wrap items-center justify-between gap-4 bg-slate-900/80 backdrop-blur-md p-4 rounded-xl border border-cyan-500/30">
        <div class="flex items-center gap-3">
          <span
            class="h-3 w-3 rounded-full"
            [class]="isGenerating() ? 'bg-amber-400 animate-ping' : 'bg-emerald-400 animate-pulse'"
          ></span>
          <div>
            <h2 class="text-lg font-bold tracking-wider text-cyan-400 font-mono">
              VERTEX-IMAGEN-CORE-V1 // BENTO HUD
            </h2>
            <p class="text-xs text-slate-400 font-mono">
              Engine: stable-diffusion.cpp (Q8_0) | Endpoint: 127.0.0.1:8090
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 text-xs font-mono">
          <span class="px-3 py-1 rounded-lg bg-violet-950/80 text-violet-300 border border-violet-700/60">
            SDXL-Lightning 4-Step
          </span>
          <span class="px-3 py-1 rounded-lg bg-emerald-950/80 text-emerald-300 border border-emerald-700/60">
            GTX 1660 Ti (6GB VRAM)
          </span>
        </div>
      </div>

      <!-- Main Bento Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left Panel: Controls -->
        <div class="lg:col-span-5 bg-slate-900/60 backdrop-blur-md p-5 rounded-xl border border-slate-800 space-y-4">
          <div>
            <label class="text-xs font-mono uppercase tracking-wider text-cyan-300">
              Prompt Vectorial / Escena (Trigger: vtxcore style)
            </label>
            <textarea
              [ngModel]="prompt()"
              (ngModelChange)="prompt.set($event)"
              rows="4"
              class="w-full mt-1.5 rounded-xl bg-slate-950/90 border border-slate-700 p-3 text-sm text-slate-100 focus:border-cyan-400 focus:outline-none"
            ></textarea>
          </div>

          <!-- Presets -->
          <div class="space-y-1.5">
            <span class="text-xs text-slate-400 font-mono">Presets Tácticos:</span>
            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                (click)="applyPreset('sublimation')"
                class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950 border border-cyan-500/30 text-cyan-300 transition"
              >
                Sublimación / Wolf
              </button>
              <button
                type="button"
                (click)="applyPreset('cover')"
                class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-violet-950 border border-violet-500/30 text-violet-300 transition"
              >
                Sci-Fi / Aethelgard
              </button>
              <button
                type="button"
                (click)="applyPreset('redteam')"
                class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-emerald-950 border border-emerald-500/30 text-emerald-300 transition"
              >
                Red Team / Forensic
              </button>
            </div>
          </div>

          <!-- Parameters -->
          <div class="grid grid-cols-2 gap-3 pt-1">
            <div>
              <label class="text-xs text-slate-400 font-mono">Resolución</label>
              <select
                [ngModel]="resolution()"
                (ngModelChange)="resolution.set($event)"
                class="w-full mt-1 rounded-lg bg-slate-950 border border-slate-700 p-2 text-sm text-slate-200"
              >
                <option value="1024x1024">1024 x 1024 (Nativa SDXL)</option>
                <option value="768x768">768 x 768 (Rápida)</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-slate-400 font-mono">Pasos (Lightning)</label>
              <input
                type="number"
                [ngModel]="steps()"
                (ngModelChange)="steps.set($event)"
                min="1"
                max="8"
                class="w-full mt-1 rounded-lg bg-slate-950 border border-slate-700 p-2 text-sm text-slate-200"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-400 font-mono">CFG Scale</label>
              <input
                type="number"
                step="0.5"
                [ngModel]="cfgScale()"
                (ngModelChange)="cfgScale.set($event)"
                class="w-full mt-1 rounded-lg bg-slate-950 border border-slate-700 p-2 text-sm text-slate-200"
              />
            </div>
            <div>
              <label class="text-xs text-slate-400 font-mono">Seed (-1 = Random)</label>
              <input
                type="number"
                [ngModel]="seed()"
                (ngModelChange)="seed.set($event)"
                class="w-full mt-1 rounded-lg bg-slate-950 border border-slate-700 p-2 text-sm text-slate-200"
              />
            </div>
          </div>

          <label class="flex items-center gap-2.5 pt-1 cursor-pointer">
            <input
              type="checkbox"
              [ngModel]="clipOnCpu()"
              (ngModelChange)="clipOnCpu.set($event)"
              class="rounded bg-slate-950 border-slate-700 text-cyan-500"
            />
            <span class="text-xs text-slate-300 font-mono">
              Low-VRAM Mode (--clip-on-cpu activo junto a LM Studio)
            </span>
          </label>

          <button
            type="button"
            (click)="triggerGeneration()"
            [disabled]="isGenerating()"
            class="w-full py-3 rounded-xl font-bold text-slate-950 bg-gradient-to-r from-cyan-400 to-emerald-400 hover:from-cyan-300 hover:to-emerald-300 disabled:opacity-50 transition shadow-lg shadow-cyan-500/20 font-mono"
          >
            @if (isGenerating()) {
              <span>RENDERIZANDO EN GTX 1660 Ti...</span>
            } @else {
              <span>⚡ DISPARAR MOTOR VISUAL (4 PASOS)</span>
            }
          </button>

          @if (statusMessage()) {
            <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 whitespace-pre-wrap">
              {{ statusMessage() }}
            </div>
          }
        </div>

        <!-- Right Panel: Active Viewport -->
        <div class="lg:col-span-7 bg-slate-900/60 backdrop-blur-md p-5 rounded-xl border border-slate-800 flex flex-col items-center justify-center min-h-[500px]">
          @if (isGenerating()) {
            <div class="flex flex-col items-center gap-3">
              <div class="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-xs font-mono text-cyan-300">
                Procesando tensores Q8_0 ({{ resolution() }})...
              </p>
            </div>
          } @else if (activeImageUrl()) {
            <img
              [src]="activeImageUrl()"
              [alt]="activeFilename()"
              class="max-h-[480px] rounded-xl border border-cyan-500/30 shadow-2xl object-contain"
            />
            <div class="mt-3 flex items-center gap-4 text-xs font-mono text-slate-400">
              <span>Archivo: {{ activeFilename() }}</span>
              <a
                [href]="activeImageUrl()"
                target="_blank"
                class="text-cyan-400 hover:underline"
              >
                Abrir original 1024x1024 ↗
              </a>
            </div>
          } @else {
            <p class="text-sm font-mono text-slate-500">
              Selecciona una imagen del historial o dispara una nueva generación.
            </p>
          }
        </div>
      </div>

      <!-- Bottom Gallery Strip -->
      <div class="bg-slate-900/60 backdrop-blur-md p-4 rounded-xl border border-slate-800">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-xs font-mono uppercase tracking-wider text-cyan-400">
            Vault Local (E:\models\sd-cpp\outputs) — {{ gallery().length }} archivos
          </h3>
          <button
            type="button"
            (click)="refreshGallery()"
            class="text-xs font-mono text-slate-400 hover:text-cyan-300"
          >
            ↻ Refrescar
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-3">
          @for (item of gallery(); track item.name) {
            <button
              type="button"
              (click)="selectFromGallery(item)"
              class="group relative overflow-hidden rounded-lg border border-slate-800 hover:border-cyan-400 transition"
            >
              <img
                [src]="item.url"
                [alt]="item.name"
                class="w-full h-24 object-cover group-hover:scale-105 transition"
              />
            </button>
          }
        </div>
      </div>
    </div>
  `,
})
export class VertexImagenHudComponent implements OnInit {
  private readonly imagenService = inject(VertexImagenService);

  // Signals de estado reactivo
  prompt = signal<string>(
    'vtxcore style, aggressive cybernetic wolf emblem, geometric metallic plates, glowing emerald eyes, isolated on solid black background, esports and apparel sublimation vector print, 8k'
  );
  resolution = signal<string>('1024x1024');
  steps = signal<number>(4);
  cfgScale = signal<number>(1.0);
  seed = signal<number>(-1);
  clipOnCpu = signal<boolean>(true);

  isGenerating = signal<boolean>(false);
  statusMessage = signal<string>('');
  activeImageUrl = signal<string>('');
  activeFilename = signal<string>('');
  gallery = signal<GalleryItem[]>([]);

  dimensions = computed(() => {
    const [w, h] = this.resolution().split('x').map(Number);
    return { width: w || 1024, height: h || 1024 };
  });

  private readonly presets: Record<string, string> = {
    sublimation:
      'vtxcore style, aggressive cybernetic wolf emblem, geometric metallic plates, glowing emerald eyes, isolated on solid black background, esports and apparel sublimation vector print, high contrast, 8k',
    cover:
      'vtxcore style, dark sci-fi book cover illustration, lone cybernetic architect standing before a massive glowing quantum data monolith in the void, Aethelgard aesthetic, cinematic lighting, masterpiece',
    redteam:
      'vtxcore style, offensive cybersecurity red team shield emblem, glowing binary matrix firewall, sleek obsidian armor texture, neon red and cyan accents, minimal tech cover art, 8k',
  };

  ngOnInit(): void {
    this.refreshGallery();
  }

  applyPreset(key: string): void {
    if (this.presets[key]) {
      this.prompt.set(this.presets[key]);
    }
  }

  refreshGallery(): void {
    this.imagenService.getGallery().subscribe({
      next: (items) => {
        this.gallery.set(items);
        if (!this.activeImageUrl() && items.length > 0) {
          this.activeImageUrl.set(items[0].url);
          this.activeFilename.set(items[0].name);
        }
      },
      error: () =>
        this.statusMessage.set(
          '[!] Verifica que vertex_image_studio.py esté corriendo en el puerto 8090.'
        ),
    });
  }

  selectFromGallery(item: GalleryItem): void {
    this.activeImageUrl.set(item.url);
    this.activeFilename.set(item.name);
  }

  triggerGeneration(): void {
    this.isGenerating.set(true);
    this.statusMessage.set('[+] Ejecutando sd-cli.exe con CUDA y --vae-tiling...');

    const { width, height } = this.dimensions();
    const payload: ImagenGenerateRequest = {
      prompt: this.prompt(),
      negative_prompt:
        'white background, light background, white border, frame, cropped, blurry, low quality, deformed, watermark, text',
      width,
      height,
      steps: this.steps(),
      cfg_scale: this.cfgScale(),
      seed: this.seed(),
      clip_on_cpu: this.clipOnCpu(),
    };

    this.imagenService.generateImage(payload).subscribe({
      next: (res) => {
        this.activeImageUrl.set(res.image_url);
        this.activeFilename.set(res.filename);
        this.statusMessage.set(
          `[+] Renderizado en ${res.elapsed_seconds}s | Archivo: ${res.filename}`
        );
        this.isGenerating.set(false);
        this.refreshGallery();
      },
      error: (err) => {
        const msg = err?.error?.detail || err.message || 'Fallo de conexión con 127.0.0.1:8090';
        this.statusMessage.set(`[!] ERROR: ${msg}`);
        this.isGenerating.set(false);
      },
    });
  }
}