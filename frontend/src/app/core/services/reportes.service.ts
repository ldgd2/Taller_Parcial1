import { Injectable, inject } from '@angular/core';
import { ApiService } from '../api/api.service';
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

  getStats(mes: number, anio: number): Observable<StatsResponse> {
    const params = new HttpParams()
      .set('mes', mes.toString())
      .set('anio', anio.toString());
    return this.api.get<StatsResponse>('/reportes/stats', params);
  }

  downloadPdf(mes: number, anio: number): void {
    const url = `http://localhost:8000/api/v1/reportes/pdf?mes=${mes}&anio=${anio}`;
    window.open(url, '_blank');
  }
}
