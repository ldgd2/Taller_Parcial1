import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private http = inject(HttpClient);
  private config: any;

  async loadConfig() {
    try {
      this.config = await firstValueFrom(
        this.http.get('/assets/config.json')
      );
      console.log('Configuración cargada dinámicamente:', this.config);
    } catch (error) {
      console.error('No se pudo cargar config.json, usando valores por defecto:', error);
      this.config = { apiUrl: 'http://localhost:8000/api/v1' };
    }
  }

  get apiUrl(): string {
    return this.config?.apiUrl || 'http://localhost:8000/api/v1';
  }
}
