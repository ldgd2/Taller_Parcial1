import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { EmergencyCardComponent } from '../../shared/ui/emergency-card/emergency-card.component';
import { ApiService } from '../../core/api/api.service';
import { LucideAngularModule } from 'lucide-angular';

@Component({
  selector: 'app-trabajos',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule, EmergencyCardComponent],
  template: `
    <div class="p-8 lg:p-12 flex flex-col gap-12 max-w-[1800px] mx-auto animate-in fade-in duration-700">
      
      <!-- HEADER -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-zinc-900 pb-6">
        <div>
          <h1 class="text-4xl font-bold tracking-tight mb-3 uppercase">Trabajos Operativos</h1>
          <p class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-500">
            Seguimiento de misiones y operaciones finalizadas
          </p>
        </div>
        
        <div class="flex items-center bg-[#050505] border border-zinc-800 p-1">
          <button (click)="tab = 'active'" 
                  [class]="tab === 'active' ? 'bg-zinc-900 text-white' : 'text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white flex items-center gap-2">
            <div *ngIf="tab === 'active'" class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
            EN CURSO
          </button>
          <button (click)="tab = 'done'" 
                  [class]="tab === 'done' ? 'bg-zinc-900 text-white' : 'text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white flex items-center gap-2">
            <div *ngIf="tab === 'done'" class="w-1.5 h-1.5 bg-zinc-500 rounded-full"></div>
            FINALIZADOS
          </button>
        </div>
      </div>

      <!-- GRID -->
      <div *ngIf="loading" class="p-20 flex flex-col items-center justify-center gap-4">
           <div class="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
           <p class="font-mono text-[9px] uppercase tracking-widest text-zinc-600">Sincronizando bitácora operativa...</p>
      </div>

      <div *ngIf="!loading && filteredItems.length === 0" 
             class="border border-zinc-900 bg-zinc-950/30 p-24 text-center flex flex-col items-center shadow-inner">
          <lucide-icon [name]="tab === 'active' ? 'clipboard-list' : 'history'" size="32" class="text-zinc-800 mb-6"></lucide-icon>
          <h3 class="font-bold text-lg mb-2 uppercase tracking-widest">
            {{ tab === 'active' ? 'Sin trabajos asignados' : 'Vacío Histórico' }}
          </h3>
          <p class="text-zinc-500 text-xs font-mono uppercase tracking-tight max-w-sm">
            {{ tab === 'active' ? 'No tienes misiones activas en este momento. Revisa tu tablero central.' : 'No tienes operaciones finalizadas en el registro de este terminal.' }}
          </p>
      </div>

      <div *ngIf="!loading && filteredItems.length > 0" 
             class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-px bg-zinc-900 border border-zinc-800 shadow-2xl">
          <app-emergency-card 
            *ngFor="let emg of filteredItems" 
            [data]="mapToCardFormat(emg)">
          </app-emergency-card>
      </div>
    </div>
  `
})
export class TrabajosComponent implements OnInit {
  items: any[] = [];
  loading = true;
  tab: 'active' | 'done' = 'active';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    // API call for assigned emergencies
    this.api.get<any[]>('/gestion-emergencia/asignadas').subscribe({
      next: (res) => {
        this.items = res;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  get filteredItems() {
    return this.items.filter(emg => {
        const isDone = ['ATENDIDO', 'CANCELADO'].includes(emg.estado_actual);
        return this.tab === 'active' ? !isDone : isDone;
    });
  }

  mapToCardFormat(emg: any) {
    const vehiculo = emg.vehiculo || {};
    const isDone = ['ATENDIDO', 'CANCELADO'].includes(emg.estado_actual);
    
    return {
      id: `EMG-${emg.id}`,
      title: emg.descripcion,
      summary: emg.resumen_ia?.resumen,
      status: isDone ? emg.estado_actual : 'in_progress',
      priority: emg.idPrioridad,
      location: emg.direccion,
      timeElapsed: isDone ? 'COMPLETADO' : 'ACTIVO',
      vehicle: `${vehiculo.marca || 'N/A'} ${vehiculo.modelo || 'MOD_0'} [${emg.placaVehiculo}]`,
      client: vehiculo.idCliente
    };
  }
}
