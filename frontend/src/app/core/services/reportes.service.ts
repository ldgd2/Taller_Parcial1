import { Injectable, inject } from '@angular/core';
import { ApiService } from '../api/api.service';
import { ConfigService } from '../config/config.service';
import { Observable } from 'rxjs';
import { HttpParams } from '@angular/common/http';

export interface StatsResumen {
  total_servicios: number;
  ingreso_bruto: number;
  comisiones_pagadas: number;
  ingreso_neto: number;
  mes: number;
  anio: number;
}

export interface StatsGrafica {
  fecha: string;
  monto: number;
}

export interface StatsResponse {
  resumen: StatsResumen;
  grafica: StatsGrafica[];
}

@Injectable({
  providedIn: 'root'
})
export class ReportesService {
  private api = inject(ApiService);
  private configService = inject(ConfigService);

  getStats(mes: number, anio: number): Observable<StatsResponse> {
    const params = new HttpParams()
      .set('mes', mes.toString())
      .set('anio', anio.toString());
    return this.api.get<StatsResponse>('/reportes/stats', params);
  }

  downloadPdf(mes: number, anio: number): void {
    const token = localStorage.getItem('access_token');
    const url = `${this.configService.apiUrl}/reportes/pdf?mes=${mes}&anio=${anio}`;

    fetch(url, {
      method: 'GET',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
      .then(res => {
        if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
        return res.blob();
      })
      .then(blob => {
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `reporte_${mes}_${anio}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
      })
      .catch(err => console.error('❌ Error descargando reporte PDF:', err));
  }
}
