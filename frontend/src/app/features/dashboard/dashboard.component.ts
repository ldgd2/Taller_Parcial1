import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

// UI
import { EmergencyCardComponent } from '../../shared/ui/emergency-card/emergency-card.component';
import { ApiService } from '../../core/api/api.service';
import { LucideAngularModule } from 'lucide-angular';
import { toast } from 'ngx-sonner';
import { SocketService } from '../../core/services/socket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    FormsModule,
    LucideAngularModule,
    EmergencyCardComponent
  ],
  template: `
    <div class="p-8 lg:p-12 flex flex-col gap-12 max-w-[1800px] mx-auto animate-in fade-in duration-700">
      
      <!-- FIELDWORK OS HEADER -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-8 border-b border-zinc-900 pb-8">
        <div>
          <h1 class="text-4xl font-bold tracking-tight mb-3 uppercase">Tablero de Control</h1>
          <div class="flex items-center gap-4">
            <p class="font-mono text-[10px] uppercase tracking-[.3em] text-zinc-500">
              Vigilancia de emergencias en tiempo real
            </p>
            <div class="h-px w-24 bg-zinc-800"></div>
            <span class="font-mono text-[10px] text-primary animate-pulse tracking-widest font-bold">LIVE_FEED</span>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex items-center bg-[#050505] border border-zinc-800 p-1">
          <button (click)="filter = 'all'" 
                  [class]="filter === 'all' ? 'bg-zinc-900 text-white' : 'text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white">
            Todas
          </button>
          <button (click)="filter = 'PENDIENTE'" 
                  [class]="filter === 'PENDIENTE' ? 'bg-zinc-900 text-white' : 'text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white">
            Pendientes
          </button>
          <button (click)="filter = 'BLOQUEADO'" 
                  [class]="filter === 'BLOQUEADO' ? 'bg-zinc-900 text-white' : 'text-zinc-600'" 
                  class="px-5 py-2 font-bold text-[9px] uppercase tracking-[.2em] transition-all hover:text-white">
            En Análisis
          </button>
        </div>
      </div>

      <!-- STATS GRID -->
      <div class="grid grid-cols-1 md:grid-cols-4 bg-zinc-900 gap-px border border-zinc-800 shadow-2xl">
        <div class="bg-[#050505] p-8 flex flex-col justify-between hover:bg-zinc-950 transition-colors">
          <span class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500 mb-6 flex items-center gap-2">
            <div class="w-1.5 h-1.5 bg-zinc-600"></div> Total Incidencias
          </span>
          <span class="font-mono text-4xl font-bold tracking-tighter">{{ stats.total }}</span>
        </div>
        <div class="bg-[#050505] p-8 flex flex-col justify-between border-l border-zinc-900">
          <span class="font-mono text-[9px] uppercase tracking-[.25em] text-red-500 mb-6 flex items-center gap-2">
            <div class="w-1.5 h-1.5 bg-red-500 animate-pulse"></div> Nivel Crítico
          </span>
          <span class="font-mono text-4xl font-bold tracking-tighter text-red-500">{{ stats.critical }}</span>
        </div>
        <div class="bg-[#050505] p-8 flex flex-col justify-between border-l border-zinc-900">
          <span class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500 mb-6 flex items-center gap-2">
            <div class="w-1.5 h-1.5 bg-emerald-500"></div> Disponibles
          </span>
          <span class="font-mono text-4xl font-bold tracking-tighter">{{ stats.pending }}</span>
        </div>
        <div class="bg-[#050505] p-8 flex flex-col justify-between border-l border-zinc-900">
          <span class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500 mb-6 flex items-center gap-2">
            <div class="w-1.5 h-1.5 bg-primary"></div> Eficiencia Red
          </span>
          <span class="font-mono text-4xl font-bold tracking-tighter text-primary">99.8%</span>
        </div>
      </div>

      <!-- MAIN EMERGENCY LISTING -->
      <div>
        <div class="flex items-center justify-between mb-8">
          <h2 class="font-bold text-xs tracking-[.4em] uppercase text-zinc-600">
            Monitor de Incidencias Geográficas
          </h2>
          <div class="flex gap-1">
             <div class="w-8 h-1 bg-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]"></div>
             <div class="w-8 h-1 bg-emerald-500/40"></div>
             <div class="w-8 h-1 bg-emerald-500/60"></div>
          </div>
        </div>

        <div *ngIf="loading" class="p-20 flex flex-col items-center justify-center gap-4">
           <div class="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
           <p class="font-mono text-[9px] uppercase tracking-widest text-zinc-600">Sincronizando feed sismológico...</p>
        </div>

        <div *ngIf="!loading && filteredEmergencies.length === 0" 
             class="border border-zinc-900 bg-zinc-950/30 p-24 text-center flex flex-col items-center shadow-inner">
          <lucide-icon name="alert-triangle" size="32" class="text-zinc-800 mb-6"></lucide-icon>
          <h3 class="font-bold text-lg mb-2 uppercase tracking-widest">Sin Incidencias Disponibles</h3>
          <p class="text-zinc-500 text-xs font-mono uppercase tracking-tight max-w-xs">El sector está limpio o fuera de rango operativo.</p>
        </div>

        <div *ngIf="!loading && filteredEmergencies.length > 0" 
             class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-px bg-zinc-900 border border-zinc-800 shadow-2xl">
          <app-emergency-card 
            *ngFor="let emg of filteredEmergencies" 
            [data]="mapToCardFormat(emg)"
            (onAssign)="handleClaim($event)">
          </app-emergency-card>
        </div>
      </div>
    </div>
  `,
  styles: []
})
export class DashboardComponent implements OnInit, OnDestroy {
  emergencies: any[] = [];
  filter: 'all' | 'PENDIENTE' | 'BLOQUEADO' = 'all';
  loading = true;
  private socketSub?: Subscription;

  constructor(
    private api: ApiService, 
    private router: Router,
    private socketService: SocketService
  ) {}

  ngOnInit() {
    this.refreshData();
    
    // Connect to WebSocket for real-time updates
    const workshopId = localStorage.getItem('cod_taller') || 'anonymous';
    this.socketService.connect(workshopId);
    
    this.socketSub = this.socketService.getMessages().subscribe(msg => {
      if (msg.type === 'db_update' && (msg.table === 'emergencia' || msg.table === 'pago')) {
        console.log('Real-time update received:', msg);
        this.refreshData();
        toast.info(`Cambio detectado en ${msg.table}: Actualizando tablero...`);
      }
    });
  }

  ngOnDestroy() {
    if (this.socketSub) this.socketSub.unsubscribe();
  }

  refreshData() {
    // API endpoint corrected for management-admin
    this.api.get<any[]>('/gestion-emergencia/disponibles').subscribe({
      next: (res) => {
        this.emergencies = res;
        this.loading = false;
      },
      error: (e) => {
        console.error('Error loading emergencies', e);
        this.loading = false;
      }
    });
  }

  get filteredEmergencies() {
    return this.emergencies.filter(emg => {
      if (this.filter === 'all') return true;
      if (this.filter === 'BLOQUEADO') return emg.is_locked;
      return emg.estado_actual === this.filter && !emg.is_locked;
    });
  }

  get stats() {
    return {
      total: this.emergencies.length,
      critical: this.emergencies.filter(e => e.idPrioridad >= 4).length,
      pending: this.emergencies.filter(e => e.estado_actual === 'PENDIENTE' && !e.is_locked).length
    };
  }

  mapToCardFormat(emg: any) {
    const vehiculo = emg.vehiculo || {};
    return {
      id: `EMG-${emg.id}`,
      title: emg.descripcion,
      summary: emg.resumen_ia?.resumen,
      status: (emg.is_locked ? 'assigned' : 'pending') as 'assigned' | 'pending',
      priority: emg.idPrioridad,
      location: emg.direccion,
      timeElapsed: 'REC_V_01',
      vehicle: `${vehiculo.marca || 'N/A'} ${vehiculo.modelo || 'MOD_0'} [${emg.placaVehiculo}]`,
      client: vehiculo.idCliente
    };
  }

  handleClaim(id: string) {
    const rawId = id.replace('EMG-', '');
    // Navigate to detail for full analysis
    this.router.navigate(['/app/emergency', rawId]);
  }
}
