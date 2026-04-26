import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ReportesService, StatsResponse } from '../../core/services/reportes.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';
import { LucideAngularModule, TrendingUp, DollarSign, Wrench, FileText, Calendar } from 'lucide-angular';

@Component({
  selector: 'app-reportes',
  standalone: true,
  imports: [CommonModule, FormsModule, BaseChartDirective, LucideAngularModule],
  template: `
    <div class="p-8 min-h-screen bg-[#050505] text-white selection:bg-primary selection:text-white">
      <!-- Header Section -->
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 border-b border-zinc-900 pb-8">
        <div class="space-y-2">
          <div class="flex items-center gap-3 mb-1">
            <div class="w-2 h-2 bg-primary"></div>
            <span class="text-[10px] font-bold uppercase tracking-[.4em] text-zinc-500">Analytics _Kernel v1.0</span>
          </div>
          <h1 class="text-4xl font-bold tracking-tight uppercase">Rendimiento <span class="text-zinc-600 font-normal">Taller</span></h1>
        </div>
        
        <!-- Filter Controls -->
        <div class="flex items-center gap-px bg-zinc-900 border border-zinc-800 p-1 rounded-sm">
          <div class="flex items-center gap-2 px-4 py-2 bg-[#050505] border border-zinc-800">
            <lucide-icon [name]="Calendar" class="w-3.5 h-3.5 text-zinc-600"></lucide-icon>
            <select [(ngModel)]="selectedMonth" (change)="loadData()" 
                    class="bg-transparent border-none focus:ring-0 text-[10px] font-bold uppercase tracking-widest text-zinc-300">
              <option *ngFor="let m of months; let i = index" [value]="i + 1" class="bg-zinc-900">{{ m }}</option>
            </select>
          </div>
          <div class="px-4 py-2 bg-[#050505] border border-zinc-800 border-l-0">
            <select [(ngModel)]="selectedYear" (change)="loadData()" 
                    class="bg-transparent border-none focus:ring-0 text-[10px] font-bold uppercase tracking-widest text-zinc-300">
              <option *ngFor="let y of years" [value]="y" class="bg-zinc-900">{{ y }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Stats Grid (Industrial Cards) -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <!-- Servicos Card -->
        <div class="card-industrial p-8 group">
          <div class="flex justify-between items-start mb-6">
            <lucide-icon [name]="Wrench" class="w-5 h-5 text-zinc-600 group-hover:text-primary transition-colors"></lucide-icon>
            <span class="text-[8px] font-bold uppercase tracking-[.2em] px-2 py-0.5 border border-zinc-800 text-zinc-500">Mtd_Total</span>
          </div>
          <div class="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Servicios Finalizados</div>
          <div class="text-4xl font-black">{{ stats?.resumen?.total_servicios || 0 }}</div>
        </div>

        <!-- Gross Income Card -->
        <div class="card-industrial p-8 group">
          <div class="flex justify-between items-start mb-6">
            <lucide-icon [name]="DollarSign" class="w-5 h-5 text-zinc-600 group-hover:text-emerald-500 transition-colors"></lucide-icon>
            <span class="text-[8px] font-bold uppercase tracking-[.2em] px-2 py-0.5 border border-zinc-800 text-zinc-500">Bruto_USD</span>
          </div>
          <div class="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Ingreso Bruto</div>
          <div class="text-4xl font-black text-white">\${{ stats?.resumen?.ingreso_bruto | number:'1.2-2' }}</div>
        </div>

        <!-- Commission Card -->
        <div class="card-industrial p-8 group border-l-primary/30">
          <div class="flex justify-between items-start mb-6">
            <lucide-icon [name]="TrendingUp" class="w-5 h-5 text-zinc-600 group-hover:text-amber-500 transition-colors"></lucide-icon>
            <span class="text-[8px] font-bold uppercase tracking-[.2em] px-2 py-0.5 border border-amber-900/30 text-amber-500/50">Fee_10%</span>
          </div>
          <div class="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Comisión Plataforma</div>
          <div class="text-4xl font-black text-amber-600">-\${{ stats?.resumen?.comisiones_pagadas | number:'1.2-2' }}</div>
        </div>

        <!-- Net Income Card -->
        <div class="card-industrial p-8 group relative overflow-hidden ring-1 ring-primary/20">
          <div class="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-100 transition-opacity">
             <button (click)="downloadReport()" class="p-2 bg-primary text-white" title="Export PDF">
               <lucide-icon [name]="FileText" class="w-4 h-4"></lucide-icon>
            </button>
          </div>
          <div class="flex justify-between items-start mb-6">
            <lucide-icon [name]="DollarSign" class="w-5 h-5 text-primary"></lucide-icon>
            <span class="text-[8px] font-bold uppercase tracking-[.2em] px-2 py-0.5 bg-primary text-white">Neto_Real</span>
          </div>
          <div class="text-[10px] font-bold uppercase tracking-widest text-zinc-500 mb-1">Ingreso Neto</div>
          <div class="text-4xl font-black text-primary">\${{ stats?.resumen?.ingreso_neto | number:'1.2-2' }}</div>
        </div>
      </div>

      <!-- Visualization Area -->
      <div class="card-industrial p-10">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
          <div>
            <h2 class="text-xs font-bold uppercase tracking-[.3em] text-white mb-2">Monitor de Ingresos Diarios</h2>
            <p class="text-[10px] font-medium text-zinc-600 uppercase tracking-widest">Visualización en tiempo real de flujo de caja</p>
          </div>
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-3">
              <div class="w-3 h-0.5 bg-primary"></div>
              <span class="text-[9px] font-bold uppercase tracking-widest text-zinc-400">Rendimiento Diario</span>
            </div>
          </div>
        </div>
        
        <div class="h-[450px] w-full relative">
          <canvas baseChart
            [data]="lineChartData"
            [options]="lineChartOptions"
            [type]="lineChartType">
          </canvas>
        </div>
      </div>

      <!-- Data Empty State -->
      <div *ngIf="!stats?.grafica?.length" class="mt-8 flex flex-col items-center justify-center p-20 border border-dashed border-zinc-900 bg-zinc-950/50">
        <div class="w-12 h-1 bg-zinc-800 mb-6"></div>
        <p class="text-[10px] font-bold uppercase tracking-[.4em] text-zinc-600">Sistema sin registros para este periodo</p>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; background-color: #050505; }
    canvas { filter: drop-shadow(0 0 10px rgba(255, 87, 51, 0.1)); }
  `]
})
export class WorkshopReportsComponent implements OnInit {
  private reportesService = inject(ReportesService);

  readonly Wrench = Wrench;
  readonly DollarSign = DollarSign;
  readonly TrendingUp = TrendingUp;
  readonly FileText = FileText;
  readonly Calendar = Calendar;

  months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  years = [2024, 2025, 2026];
  
  selectedMonth = new Date().getMonth() + 1;
  selectedYear = new Date().getFullYear();
  
  stats?: StatsResponse;

  // Chart Properties
  public lineChartData: ChartConfiguration['data'] = {
    datasets: [
      {
        data: [],
        label: 'Ingresos Diarios',
        backgroundColor: 'rgba(255, 87, 51, 0.05)',
        borderColor: '#FF5733',
        pointBackgroundColor: '#FF5733',
        pointBorderColor: '#050505',
        pointHoverBackgroundColor: '#050505',
        pointHoverBorderColor: '#FF5733',
        pointRadius: 4,
        borderWidth: 3,
        fill: 'origin',
        tension: 0.4
      }
    ],
    labels: []
  };

  public lineChartOptions: ChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0a0a0a',
        titleFont: { size: 12, weight: 'bold' },
        bodyFont: { size: 12 },
        padding: 16,
        cornerRadius: 4,
        displayColors: false,
        borderColor: '#27272a',
        borderWidth: 1,
        callbacks: {
          label: (ctx) => ` INGRESO: $${(ctx.parsed.y ?? 0).toLocaleString()}`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: '#18181b' },
        ticks: { color: '#52525b', font: { size: 9, weight: 'bold' }, callback: (v) => `$${v}` }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#52525b', font: { size: 9, weight: 'bold' } }
      }
    }
  };
  
  public lineChartType: ChartType = 'line';

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.reportesService.getStats(this.selectedMonth, this.selectedYear).subscribe(res => {
      this.stats = res;
      this.updateChart(res.grafica);
    });
  }

  updateChart(grafica: any[]) {
    this.lineChartData.labels = grafica.map(g => {
      const d = new Date(g.fecha);
      return `${d.getDate()}/${d.getMonth() + 1}`;
    });
    this.lineChartData.datasets[0].data = grafica.map(g => g.monto);
  }

  downloadReport() {
    this.reportesService.downloadPdf(this.selectedMonth, this.selectedYear);
  }
}
