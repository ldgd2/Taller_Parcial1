import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';

export interface EmergencyCardData {
  id: string;
  title: string;
  summary?: string;
  status: 'pending' | 'assigned' | 'in_progress';
  priority: number;
  location: string;
  timeElapsed: string;
  vehicle: string;
  client?: string;
  hasUnreadMessages?: boolean;
}

@Component({
  selector: 'app-emergency-card',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule],
  template: `
    <div [routerLink]="['/app/emergency', data.id.replace('EMG-', '')]"
         class="group flex flex-col transition-all duration-300 cursor-pointer overflow-hidden shadow-sm border border-t-4 relative"
         [ngClass]="getCardClasses()">
      
      <!-- Indicador de Chat (Puntito) -->
      <div *ngIf="data.hasUnreadMessages" 
           class="absolute top-2 left-2 z-20 flex items-center gap-1.5 bg-blue-600 px-2 py-0.5 rounded-full shadow-lg border border-blue-400">
        <div class="w-2 h-2 bg-white rounded-full animate-ping"></div>
        <span class="text-[8px] font-bold text-white uppercase tracking-tighter">Mensaje Nuevo</span>
      </div>

      <!-- Efecto de alarma pulsante para criticidad extrema -->
      <div *ngIf="data.priority >= 4" class="absolute inset-0 bg-red-500/5 animate-pulse pointer-events-none"></div>
      
      <div class="p-6 flex-1 flex flex-col gap-4 relative z-10">
        <!-- Cabecera -->
        <div class="flex justify-between items-start gap-4">
          <div class="flex flex-col">
            <span class="font-mono text-[10px] font-bold uppercase tracking-widest opacity-60" [ngClass]="getTextColor()">{{ data.id }}</span>
            <h3 class="font-bold text-sm leading-tight text-white group-hover:text-white transition-colors line-clamp-2 mt-1 uppercase tracking-tight">
              {{ data.title }}
            </h3>
          </div>
          
          <!-- INDICADOR DE PRIORIDAD SUPERIOR DERECHO -->
          <div class="font-mono text-[9px] uppercase font-bold tracking-widest border px-2 py-1 flex-shrink-0 text-center"
               [ngClass]="getBadgeClasses()">
            {{ getPriorityLabel() }}
          </div>
        </div>

        <!-- Resumen de IA -->
        <p *ngIf="data.summary" class="text-[11px] text-zinc-400 italic line-clamp-2 leading-relaxed bg-[#050505]/50 p-3 border-l-2 shadow-inner"
           [ngClass]="getSummaryBorder()">
          "{{ data.summary }}"
        </p>

        <!-- Grilla de Información -->
        <div class="grid grid-cols-1 gap-3 mt-2">
          <div class="flex items-center gap-2 text-[11px] text-zinc-300">
            <lucide-icon name="map-pin" size="12" class="shrink-0 opacity-60" [ngClass]="getTextColor()"></lucide-icon>
            <span class="truncate font-medium">{{ data.location }}</span>
          </div>
          <div class="flex items-center gap-2 text-[11px] font-bold text-white">
            <lucide-icon name="wrench" size="12" class="shrink-0 opacity-80" [ngClass]="getTextColor()"></lucide-icon>
            <span class="truncate uppercase tracking-wider">{{ data.vehicle }}</span>
          </div>
        </div>
      </div>

      <!-- Pie de página / Acciones -->
      <div class="px-6 py-4 border-t flex items-center justify-between relative z-10 transition-colors"
           [ngClass]="getFooterClasses()">
         <span class="font-mono text-[9px] uppercase tracking-[.2em] font-bold opacity-60" [ngClass]="getTextColor()">
           ESTADO: {{ data.status === 'pending' ? 'PENDIENTE' : data.status }}
         </span>
         <button (click)="$event.stopPropagation(); onAssign.emit(data.id)"
                 class="font-mono text-[10px] uppercase tracking-widest font-bold hover:text-white hover:underline transition-all"
                 [ngClass]="getTextColor()">
           INGRESO INMEDIATO >
         </button>
      </div>
    </div>
  `
})
export class EmergencyCardComponent {
  @Input() data!: EmergencyCardData;
  @Output() onAssign = new EventEmitter<string>();

  getCardClasses() {
    switch (true) {
      case this.data.priority <= 1: 
        return 'border-zinc-800 border-t-emerald-500 bg-[#0a0a0a] hover:border-emerald-500/50';
      case this.data.priority === 2: 
        return 'border-zinc-800 border-t-amber-500 bg-[#0a0a0a] hover:border-amber-500/50';
      case this.data.priority === 3: 
        return 'border-zinc-800 border-t-orange-500 bg-orange-950/10 hover:border-orange-500/50';
      default: 
        return 'border-red-900 border-t-red-500 bg-red-950/20 hover:border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.1)]';
    }
  }

  getTextColor() {
    switch (true) {
      case this.data.priority <= 1: return 'text-emerald-500';
      case this.data.priority === 2: return 'text-amber-500';
      case this.data.priority === 3: return 'text-orange-500';
      default: return 'text-red-500';
    }
  }

  getBadgeClasses() {
    switch (true) {
      case this.data.priority <= 1: return 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10';
      case this.data.priority === 2: return 'border-amber-500/30 text-amber-500 bg-amber-500/10';
      case this.data.priority === 3: return 'border-orange-500/30 text-orange-500 bg-orange-500/10';
      default: return 'border-red-500 text-white bg-red-600 animate-pulse';
    }
  }

  getSummaryBorder() {
    switch (true) {
      case this.data.priority <= 1: return 'border-emerald-500/50';
      case this.data.priority === 2: return 'border-amber-500/50';
      case this.data.priority === 3: return 'border-orange-500/50';
      default: return 'border-red-500/80';
    }
  }

  getFooterClasses() {
    switch (true) {
      case this.data.priority <= 1: return 'border-zinc-900 bg-emerald-950/10 group-hover:bg-emerald-950/20';
      case this.data.priority === 2: return 'border-zinc-900 bg-amber-950/10 group-hover:bg-amber-950/20';
      case this.data.priority === 3: return 'border-orange-900/30 bg-orange-950/20 group-hover:bg-orange-950/30';
      default: return 'border-red-900 bg-red-950/40 group-hover:bg-red-900/50';
    }
  }

  getPriorityLabel() {
    switch (true) {
      case this.data.priority <= 1: return 'LVL 1 - TRANQUI';
      case this.data.priority === 2: return 'LVL 2 - LEVE';
      case this.data.priority === 3: return 'LVL 3 - URGENTE';
      default: return 'LVL 4 - EXTREMA';
    }
  }
}
