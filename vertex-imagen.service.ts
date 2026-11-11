import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface ImagenGenerateRequest {
  prompt: string;
  negative_prompt?: string;
  width: number;
  height: number;
  steps: number;
  cfg_scale: number;
  seed: number;
  clip_on_cpu: boolean;
}

export interface ImagenGenerateResponse {
  status: string;
  image_url: string;
  filename: string;
  elapsed_seconds: number;
  prompt_used: string;
}

export interface GalleryItem {
  url: string;
  name: string;
}

@Injectable({
  providedIn: 'root',
})
export class VertexImagenService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://127.0.0.1:8090';

  generateImage(payload: ImagenGenerateRequest): Observable<ImagenGenerateResponse> {
    return this.http.post<ImagenGenerateResponse>(`${this.baseUrl}/api/generate`, payload).pipe(
      map((res) => ({
        ...res,
        image_url: `${this.baseUrl}${res.image_url}?t=${Date.now()}`,
      }))
    );
  }

  getGallery(): Observable<GalleryItem[]> {
    return this.http.get<GalleryItem[]>(`${this.baseUrl}/api/gallery`).pipe(
      map((items) =>
        items.map((item) => ({
          ...item,
          url: `${this.baseUrl}${item.url}`,
        }))
      )
    );
  }
}