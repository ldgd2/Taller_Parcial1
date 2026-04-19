import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { ApiService } from '../../core/api/api.service';
import { toast } from 'ngx-sonner';

interface TallerCard {
  cod: string;
  nombre: string;
  direccion: string;
  estado: string;
  trabajos_activos?: number; // mock or future use
}

@Component({
  selector: 'app-talleres',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, RouterModule, FormsModule],
  template: `
    <div class="h-full bg-[#0d0d0d] text-white p-8 lg:p-12 animate-in fade-in duration-700 relative">
      
      <!-- PAGE HEADER -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12 border-b border-zinc-800/60 pb-8">
        <div>
          <h1 class="text-[32px] font-bold tracking-tight mb-2 text-white">Mis Talleres</h1>
          <p class="font-mono text-[10px] uppercase tracking-[.25em] text-zinc-500">
            Gestión de instalaciones y unidades móviles
          </p>
        </div>

        <button (click)="openCreateModal()" class="bg-[#FF5733] text-white px-8 py-3 font-bold text-[11px] uppercase tracking-widest hover:brightness-110 transition-all shadow-lg shadow-[#FF5733]/20 flex items-center gap-2">
          + REGISTRAR TALLER
        </button>
      </div>

      <!-- LOADING -->
      <div *ngIf="loading" class="py-20 text-center">
         <div class="w-10 h-10 border-2 border-[#FF5733] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
         <p class="font-mono text-[9px] uppercase tracking-widest text-[#FF5733]">Sincronizando red de talleres...</p>
      </div>

      <!-- TALLERES GRID -->
      <div *ngIf="!loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <div *ngFor="let t of talleres" class="group border border-[#222222] bg-[#111111] p-8 flex flex-col transition-all hover:border-zinc-700 shadow-xl opacity-90 hover:opacity-100">
          
          <!-- Card Top -->
          <div class="flex justify-between items-center mb-8">
            <span class="bg-zinc-800/50 px-3 py-1 text-xs font-mono font-bold text-zinc-400 tracking-widest">{{ t.cod || 'T-XX' }}</span>
            <span [class]="getStatusClass(t.estado)" class="px-2 py-1 text-[9px] font-bold tracking-[.15em] uppercase border">
              {{ t.estado === 'ACTIVO' ? 'OPERATIVO' : t.estado }}
            </span>
          </div>

          <!-- Card Body -->
          <div class="flex-1 flex flex-col justify-start">
             <lucide-icon name="factory" size="32" class="text-zinc-700/60 mb-4" strokeWidth="1.5"></lucide-icon>
             
             <h3 class="text-xl font-bold tracking-tight mb-6 mt-2 text-white group-hover:text-white transition-colors">{{ t.nombre }}</h3>
             
             <div class="space-y-4">
                <div class="flex items-center gap-3 text-zinc-400">
                  <lucide-icon name="map-pin" size="14"></lucide-icon>
                  <span class="text-xs font-medium tracking-wide">{{ t.direccion || 'Ubicación no especificada' }}</span>
                </div>
                <div class="flex items-center gap-3 text-zinc-400">
                  <lucide-icon name="settings" size="14"></lucide-icon>
                  <span class="text-xs font-medium tracking-wide">{{ t.trabajos_activos || 0 }} Trabajos en curso</span>
                </div>
             </div>
          </div>

          <!-- Card Footer -->
          <div class="mt-8 pt-6 border-t border-[#222222]">
            <button [routerLink]="['/app/taller', t.cod]"
                    class="w-full py-3 border border-zinc-800 font-bold text-[10px] uppercase tracking-[.25em] text-white hover:bg-[#FF5733] hover:text-white hover:border-[#FF5733] transition-all">
              ADMINISTRAR
            </button>
          </div>
        </div>

        <!-- EMPTY STATE -->
        <div *ngIf="talleres.length === 0" class="col-span-full border border-dashed border-zinc-800 p-20 text-center">
           <lucide-icon name="info" size="32" class="text-zinc-600 mx-auto mb-4"></lucide-icon>
           <p class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">No hay talleres registrados en su red.</p>
        </div>
      </div>

      <!-- CREATE MODAL OVERLAY -->
      <div *ngIf="showModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-[#111111] border border-[#333333] p-8 w-full max-w-lg shadow-2xl relative">
          <button (click)="closeCreateModal()" class="absolute top-4 right-4 text-zinc-500 hover:text-white">
            <lucide-icon name="x" size="20"></lucide-icon>
          </button>
          
          <h2 class="text-2xl font-bold mb-2 uppercase text-white">Registrar Taller</h2>
          <p class="text-[10px] font-mono text-zinc-500 uppercase tracking-widest border-b border-zinc-800 pb-4 mb-6">Detalles de Nueva Instalación Operativa</p>

          <div class="space-y-6">
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-widest text-zinc-400">Nombre del Taller / Unidad</label>
              <input type="text" [(ngModel)]="newTaller.nombre" class="w-full bg-[#050505] border border-zinc-800 p-4 text-sm font-bold text-white focus:border-[#FF5733] outline-none">
            </div>
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-widest text-zinc-400">Dirección Base / Cobertura</label>
              <input type="text" [(ngModel)]="newTaller.direccion" class="w-full bg-[#050505] border border-zinc-800 p-4 text-sm font-bold text-white focus:border-[#FF5733] outline-none">
            </div>
            
            <button (click)="submitCreate()" [disabled]="creating" class="w-full bg-[#FF5733] text-white py-4 font-bold text-[11px] uppercase tracking-widest hover:brightness-110 flex items-center justify-center gap-2 mt-8 disabled:opacity-50">
               <lucide-icon *ngIf="creating" name="loader-2" size="14" class="animate-spin"></lucide-icon>
               CONFIRMAR REGISTRO
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; min-height: 100vh; background-color: #0d0d0d; }
  `]
})
export class TalleresComponent implements OnInit {
  talleres: TallerCard[] = [];
  loading = true;

  showModal = false;
  creating = false;
  newTaller = { nombre: '', direccion: '' };

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.api.get<TallerCard[]>('/talleres/mis-talleres').subscribe({
      next: (res) => {
        this.talleres = res;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        toast.error('Fallo en la sincronización de red');
      }
    });
  }

  openCreateModal() {
    this.newTaller = { nombre: '', direccion: '' };
    this.showModal = true;
  }
  
  closeCreateModal() {
    this.showModal = false;
  }

  submitCreate() {
    if (!this.newTaller.nombre || !this.newTaller.direccion) {
      toast.warning('Complete todos los campos requeridos');
      return;
    }
    this.creating = true;
    this.api.post<{cod: string}>('/talleres/', this.newTaller).subscribe({
      next: () => {
        toast.success('Taller registrado correctamente');
        this.creating = false;
        this.closeCreateModal();
        this.load();
      },
      error: () => {
        toast.error('Error al registrar taller');
        this.creating = false;
      }
    });
  }

  getStatusClass(estado: string) {
    switch (estado) {
      case 'ACTIVO': return 'bg-[#00ff9d]/10 text-[#00ff9d] border-[#00ff9d]/40';
      case 'INACTIVO': return 'bg-red-500/10 text-red-500 border-red-500/40';
      default: return 'bg-zinc-800 text-zinc-400 border-zinc-700';
    }
  }
}
