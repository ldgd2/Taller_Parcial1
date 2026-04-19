import { Component, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { ApiService } from '../../../core/api/api.service';
import { toast } from 'ngx-sonner';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';

@Component({
  selector: 'app-emergency-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule, FormsModule],
  template: `
    <div class="min-h-full flex flex-col bg-[#050505] text-white animate-in fade-in duration-500 pb-20 font-sans">
      
      <!-- TOP NAVIGATION BAR -->
      <div class="h-20 bg-[#050505] border-b border-zinc-900 px-8 flex items-center justify-between sticky top-0 z-50 backdrop-blur-xl bg-opacity-80">
        <div class="flex items-center gap-6">
          <button (click)="goBack()" 
                  class="w-10 h-10 border border-zinc-800 flex items-center justify-center hover:bg-zinc-900 transition-all group">
            <lucide-icon name="arrow-left" class="text-zinc-600 group-hover:text-white" size="16"></lucide-icon>
          </button>
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-lg font-bold tracking-tight uppercase">{{ emergency?.descripcion }}</h1>
              <span class="px-2 py-0.5 font-mono text-[8px] font-bold uppercase tracking-[.2em] border border-primary text-primary">
                {{ emergency?.estado_actual }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex gap-4">
           <button *ngIf="emergency?.idTaller === currentWorkshop && emergency?.estado_actual !== 'CANCELADO'"
                   (click)="openFichaModal()"
                   class="border border-zinc-700 text-zinc-300 hover:text-primary hover:border-primary px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all">
             Editar Ficha CU10
           </button>
           <button *ngIf="emergency?.estado_actual === 'ATENDIDO' && !pagoExistente"
                   (click)="showPagoModal = true"
                   class="border border-emerald-700 text-emerald-400 hover:bg-emerald-900/20 px-6 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all">
             Registrar Pago CU05
           </button>
           <div *ngIf="pagoExistente" class="flex items-center gap-2 px-6 py-3 bg-emerald-900/20 border border-emerald-700">
             <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
             <span class="font-mono text-[9px] uppercase text-emerald-400 tracking-widest">PAGO: $ {{ pagoExistente.monto }}</span>
           </div>
           <button *ngIf="emergency?.estado_actual === 'PENDIENTE' || emergency?.estado_actual === 'INICIADA'"
                   (click)="openAssignModal()"
                   [disabled]="emergency?.is_locked && emergency?.locked_by !== currentWorkshop"
                   class="bg-primary text-white px-8 py-3 font-bold text-[9px] uppercase tracking-[.25em] transition-all shadow-[0_10px_20px_rgba(255,87,51,0.2)]">
             {{ emergency?.is_locked ? 'Continuar Asignación' : 'Reclamar Misión' }}
           </button>
        </div>
      </div>

      <!-- LOADING STATE -->
      <div *ngIf="loading" class="flex-1 flex flex-col items-center justify-center gap-6 py-40">
        <div class="w-16 h-16 border-2 border-primary border-t-transparent rounded-full animate-spin shadow-[0_0_15px_rgba(255,87,51,0.3)]"></div>
        <p class="font-mono text-[10px] uppercase tracking-[.4em] text-zinc-600">Sincronizando Telemetría...</p>
      </div>

      <ng-container *ngIf="!loading && emergency">
        <!-- PANORAMIC MAP SECTION -->
        <div class="relative w-full h-[450px] border-b border-zinc-900 overflow-hidden group">
           <div id="emergency-map" class="absolute inset-0 z-0 bg-black"></div>
           
           <!-- DATA HUD OVERLAY -->
           <div class="absolute inset-x-0 bottom-0 p-8 flex justify-between items-end z-10 pointer-events-none">
              <!-- HUD LEFT: ADDRESS -->
              <div class="bg-black/80 backdrop-blur-md border border-zinc-800 p-6 shadow-2xl animate-in slide-in-from-left duration-700 pointer-events-auto">
                 <div class="flex items-center gap-3 mb-3">
                   <lucide-icon name="map-pin" class="text-primary" size="16"></lucide-icon>
                   <span class="font-bold text-xs uppercase tracking-widest text-white">{{ emergency.direccion }}</span>
                 </div>
                 <div class="flex gap-6 items-center">
                    <div class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest">
                       SEC_LAT: {{ emergency.latitud }}
                    </div>
                    <div class="font-mono text-[10px] text-zinc-500 uppercase tracking-widest">
                       SEC_LNG: {{ emergency.longitud }}
                    </div>
                 </div>
              </div>

              <!-- HUD RIGHT: TELEMETRY -->
              <div class="flex gap-px bg-zinc-900 border border-zinc-800 shadow-2xl overflow-hidden animate-in slide-in-from-right duration-700 pointer-events-auto">
                 <div class="bg-black/90 p-5 min-w-[140px] text-center">
                    <div class="text-[8px] text-zinc-500 uppercase mb-2 tracking-[.25em]">Distancia Ruta</div>
                    <div class="font-mono font-bold text-xl text-primary">{{ telemetry.distance || '--.-' }} <span class="text-[10px] text-zinc-600">KM</span></div>
                 </div>
                 <div class="bg-black/90 p-5 min-w-[140px] text-center border-l border-zinc-900">
                    <div class="text-[8px] text-zinc-500 uppercase mb-2 tracking-[.25em]">ETA Estimado</div>
                    <div class="font-mono font-bold text-xl text-emerald-500">{{ telemetry.duration || '--' }} <span class="text-[10px] text-zinc-600">MIN</span></div>
                 </div>
                 <div class="bg-black/90 p-5 flex flex-col items-center justify-center border-l border-zinc-900">
                    <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
                    <span class="text-[8px] font-bold text-zinc-600 uppercase mt-2 tracking-widest">LIVE</span>
                 </div>
              </div>
           </div>

           <!-- HUD TOP: SAT STATUS -->
           <div class="absolute top-6 right-8 bg-black/40 backdrop-blur-sm border border-zinc-800/50 px-4 py-2 flex items-center gap-3 z-10 pointer-events-none">
              <span class="text-[9px] font-mono text-emerald-500/80 tracking-[.3em]">OSRM_SAT_FEED: ACTIVE</span>
              <div class="w-1 h-3 bg-emerald-500/20 rounded-full flex flex-col justify-end">
                 <div class="w-full h-2/3 bg-emerald-500 rounded-full"></div>
              </div>
           </div>
        </div>

        <!-- CONTENT GRID -->
        <div class="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-px bg-zinc-900">
          
          <!-- TECHNICAL DETAILS -->
          <div class="lg:col-span-8 bg-[#050505] p-10 lg:p-14 space-y-20 border-r border-zinc-900">
            
            <!-- IA HEADLINE -->
            <div class="space-y-4">
               <div class="flex items-center gap-3 opacity-50">
                  <lucide-icon name="radio" size="12"></lucide-icon>
                  <span class="font-mono text-[9px] uppercase tracking-[.4em]">Resumen de Inteligencia Operativa</span>
               </div>
               <h2 class="text-3xl font-light italic leading-snug text-zinc-200">
                 "{{ emergency.resumen_ia?.resumen || 'Sin resumen disponible' }}"
               </h2>
            </div>

            <!-- TECHNICAL CARDS -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-12 pt-10 border-t border-zinc-900">
              <div class="space-y-6">
                <h3 class="font-bold text-[10px] uppercase tracking-[.4em] text-primary flex items-center gap-3">
                   <div class="w-1.5 h-1.5 bg-primary"></div> Diagnóstico Probable
                </h3>
                <p class="text-sm text-zinc-400 font-mono leading-relaxed bg-[#0a0a0a] p-6 border border-zinc-900">
                   {{ getFichaField('diagnostico_probable')[0] }}
                </p>
              </div>

              <div class="space-y-6">
                <h3 class="font-bold text-[10px] uppercase tracking-[.4em] text-zinc-400 flex items-center gap-3">
                   <div class="w-1.5 h-1.5 bg-zinc-800"></div> Piezas Comprometidas
                </h3>
                <ul class="space-y-3">
                  <li *ngFor="let item of getFichaField('piezas_necesarias')" class="flex gap-4 items-center bg-zinc-900/50 border border-zinc-900 px-5 py-3 font-mono text-xs text-zinc-500">
                    <span class="text-zinc-800">#</span> {{ item }}
                  </li>
                </ul>
              </div>

              <div class="space-y-6">
                <h3 class="font-bold text-[10px] uppercase tracking-[.4em] text-emerald-500 flex items-center gap-3 font-mono">
                   <div class="w-1.5 h-1.5 bg-emerald-500"></div> Kit de Respuesta (Qué llevar)
                </h3>
                <div class="grid grid-cols-1 gap-2">
                   <div *ngFor="let item of getFichaField('repuestos_sugeridos')" class="bg-emerald-500/5 border-l-2 border-emerald-500/20 px-5 py-4 text-[11px] font-bold uppercase tracking-widest text-emerald-500/80">
                   {{ item }}
                   </div>
                </div>
              </div>

              <div class="space-y-6 bg-zinc-900/10 p-8 border border-zinc-900/50">
                <h3 class="font-bold text-[10px] uppercase tracking-[.4em] text-zinc-500 flex items-center gap-3">
                   <lucide-icon name="shield-alert" size="14"></lucide-icon> Recomendaciones Críticas
                </h3>
                <ul class="space-y-4">
                  <li *ngFor="let item of getFichaField('acciones_inmediatas')" class="font-mono text-[11px] text-zinc-600 italic border-l border-zinc-800 pl-4 py-1">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- SIDEBAR METADATA -->
          <div class="lg:col-span-4 bg-[#080808] p-10 lg:p-14 space-y-12">
             <section class="space-y-6">
                <h3 class="text-[10px] font-bold uppercase tracking-[.4em] text-zinc-600">Datos del Vehículo</h3>
                <div class="bg-zinc-950 border border-zinc-900 p-8 space-y-6">
                   <div>
                      <div class="text-[9px] text-zinc-700 uppercase mb-2 tracking-widest">Marca / Modelo</div>
                      <div class="text-lg font-bold">{{ emergency.vehiculo?.marca }} {{ emergency.vehiculo?.modelo }}</div>
                   </div>
                   <div class="grid grid-cols-2 gap-4">
                      <div>
                         <div class="text-[9px] text-zinc-700 uppercase mb-2 tracking-widest">Matrícula</div>
                         <div class="font-mono font-bold">{{ emergency.vehiculo?.placa }}</div>
                      </div>
                      <div>
                         <div class="text-[9px] text-zinc-700 uppercase mb-2 tracking-widest">Año</div>
                         <div class="font-mono font-bold">{{ emergency.vehiculo?.anio }}</div>
                      </div>
                   </div>
                </div>
             </section>

             <section class="space-y-6">
                <h3 class="text-[10px] font-bold uppercase tracking-[.4em] text-zinc-600">Reporte del Sistema</h3>
                <div class="bg-[#050505] border border-dashed border-zinc-800 p-8 font-mono text-[11px] text-zinc-500 leading-relaxed uppercase tracking-tighter">
                   {{ emergency.texto_adicional || 'NO_ADDITIONAL_TEXT_DETECTED' }}
                </div>
             </section>

              <section *ngIf="emergency.evidencias?.length" class="space-y-6">
                 <h3 class="text-[10px] font-bold uppercase tracking-[.4em] text-zinc-600">Telemetría Visual</h3>
                 <div class="grid grid-cols-2 gap-px bg-zinc-900 border border-zinc-900">
                    <div *ngFor="let img of emergency.evidencias" class="aspect-square bg-[#050505] overflow-hidden group">
                       <img [src]="img.direccion" class="w-full h-full object-cover opacity-50 group-hover:opacity-100 transition-all duration-500 group-hover:scale-110">
                    </div>
                 </div>
              </section>
           </div>

        </div>
      </ng-container>

      <!-- ASSIGNMENT MODAL -->
      <div *ngIf="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 backdrop-blur-sm bg-black/60 animate-in fade-in duration-300">
         <div class="bg-[#0a0a0a] border border-zinc-800 w-full max-w-2xl overflow-hidden animate-in zoom-in-95 duration-300 shadow-3xl">
            <div class="p-8 border-b border-zinc-900 flex justify-between items-center">
               <h2 class="font-bold text-lg uppercase tracking-widest">Asignación Operativa</h2>
               <button (click)="showModal = false" class="text-zinc-600 hover:text-white transition-colors">
                  <lucide-icon name="x" size="20"></lucide-icon>
               </button>
            </div>

            <div class="p-8 space-y-8 max-h-[60vh] overflow-y-auto">
               <div class="grid grid-cols-1 gap-px bg-zinc-900">
                  <div *ngFor="let tech of availableTechs" 
                       (click)="toggleTech(tech.id)"
                       [class.bg-zinc-900]="selectedTechs.includes(tech.id)"
                       class="bg-[#050505] p-6 flex items-center justify-between cursor-pointer group hover:bg-zinc-950 transition-colors">
                     <div class="flex items-center gap-4">
                        <div [class.bg-emerald-500]="selectedTechs.includes(tech.id)"
                             class="w-4 h-4 border border-zinc-800 transition-colors flex items-center justify-center">
                           <lucide-icon *ngIf="selectedTechs.includes(tech.id)" name="chevrons-right" class="text-black" size="8"></lucide-icon>
                        </div>
                        <div>
                           <div class="font-bold text-sm" [class.text-emerald-500]="selectedTechs.includes(tech.id)">{{ tech.nombre }}</div>
                           <div class="text-[9px] uppercase tracking-widest text-zinc-600 mt-1">{{ tech.especialidades?.[0]?.nombre || 'GENERAL' }}</div>
                        </div>
                     </div>
                     <span class="font-mono text-[9px] text-zinc-500">ID#{{ tech.id }}</span>
                  </div>
               </div>
            </div>

            <div class="p-8 border-t border-zinc-900 bg-zinc-950 flex gap-4">
               <button (click)="showModal = false" class="flex-1 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500 hover:text-white">Abortar</button>
               <button (click)="confirmAssignment()" 
                       [disabled]="selectedTechs.length === 0"
                       class="flex-1 bg-primary text-white py-4 font-bold text-[10px] uppercase tracking-widest disabled:opacity-30">
                  Confirmar Misión
               </button>
            </div>
         </div>
      </div>

      <!-- MODAL: REGISTRAR PAGO (CU05) -->
      <div *ngIf="showPagoModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
        <div class="bg-zinc-950 border border-emerald-900 w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-300">
          <div class="p-8 border-b border-zinc-900 flex justify-between items-center">
            <div>
              <h2 class="font-bold text-lg uppercase tracking-widest text-emerald-400">Registrar Pago — CU05</h2>
              <p class="font-mono text-[9px] text-zinc-600 uppercase tracking-widest mt-1">Emergencia {{ emergency?.id }} · Servicio finalizado</p>
            </div>
            <button (click)="showPagoModal = false" class="text-zinc-600 hover:text-white"><lucide-icon name="x" size="20"></lucide-icon></button>
          </div>
          <div class="p-8 space-y-6">
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Monto Total del Servicio (USD)</label>
              <input [(ngModel)]="pagoMonto" type="number" placeholder="0.00"
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-emerald-500 outline-none font-mono text-2xl">
            </div>
            <div class="bg-zinc-900/50 border border-zinc-800 p-4 font-mono text-[10px] text-zinc-500 space-y-1">
              <div class="flex justify-between"><span>Monto del servicio:</span> <span class="text-white">$ {{ pagoMonto || 0 }}</span></div>
              <div class="flex justify-between"><span>Comisión plataforma (10%):</span> <span class="text-primary">$ {{ ((pagoMonto || 0) * 0.10).toFixed(2) }}</span></div>
              <div class="flex justify-between font-bold border-t border-zinc-800 pt-2 mt-2"><span>Neto al taller:</span> <span class="text-emerald-400">$ {{ ((pagoMonto || 0) * 0.90).toFixed(2) }}</span></div>
            </div>
          </div>
          <div class="p-8 bg-zinc-900/30 flex gap-4">
            <button (click)="showPagoModal = false" class="flex-1 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500 hover:text-white">Cancelar</button>
            <button (click)="registrarPago()" [disabled]="!pagoMonto"
                    class="flex-1 bg-emerald-700 hover:bg-emerald-600 text-white py-4 font-bold text-[10px] uppercase tracking-widest disabled:opacity-30">
              Confirmar Pago
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL: EDITAR FICHA TÉCNICA (CU10) -->
      <div *ngIf="showFichaModal" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
        <div class="bg-zinc-950 border border-zinc-800 w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in zoom-in-95 duration-300">
          <div class="p-8 border-b border-zinc-900 flex justify-between items-center">
            <div>
              <h2 class="font-bold text-lg uppercase tracking-widest">Editar Ficha Técnica — CU10</h2>
              <p class="font-mono text-[9px] text-zinc-600 uppercase tracking-widest mt-1">Completa con los datos reales del servicio</p>
            </div>
            <button (click)="showFichaModal = false" class="text-zinc-600 hover:text-white"><lucide-icon name="x" size="20"></lucide-icon></button>
          </div>
          <div class="p-8 space-y-6">
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Resumen del Servicio</label>
              <textarea [(ngModel)]="fichaEdit.resumen" rows="3"
                        class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none resize-none"></textarea>
            </div>
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Diagnóstico Real (separado por comas)</label>
              <input [(ngModel)]="fichaEdit.ficha_tecnica.diagnostico_probable" type="text"
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
            </div>
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Piezas Utilizadas (separado por comas)</label>
              <input [(ngModel)]="fichaEdit.ficha_tecnica.piezas_necesarias" type="text"
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
            </div>
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Repuestos Instalados (separado por comas)</label>
              <input [(ngModel)]="fichaEdit.ficha_tecnica.repuestos_sugeridos" type="text"
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
            </div>
            <div class="space-y-2">
              <label class="font-mono text-[9px] uppercase tracking-[.25em] text-zinc-500">Acciones Realizadas (separado por comas)</label>
              <input [(ngModel)]="fichaEdit.ficha_tecnica.acciones_inmediatas" type="text"
                     class="w-full bg-[#050505] border border-zinc-800 px-4 py-3 text-sm focus:border-primary outline-none">
            </div>
          </div>
          <div class="p-8 bg-zinc-900/30 flex gap-4 sticky bottom-0">
            <button (click)="showFichaModal = false" class="flex-1 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500 hover:text-white">Cancelar</button>
            <button (click)="saveFicha()"
                    class="flex-1 bg-primary text-white py-4 font-bold text-[10px] uppercase tracking-widest">
              Guardar Ficha Real
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    #emergency-map { height: 100%; width: 100%; transition: opacity 0.5s; background: #000; }
    .leaflet-container { background: #000 !important; }
    .leaflet-tile-pane { filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%); }
    .leaflet-routing-container { display: none !important; }
  `]
})
export class EmergencyDetailComponent implements OnInit, OnDestroy {
  emergency: any = null;
  loading = true;
  showModal = false;
  availableTechs: any[] = [];
  selectedTechs: number[] = [];
  loadingTechs = false;
  currentWorkshop = localStorage.getItem('cod_taller') || 'TALLER_01';
  
  // Workshop Coords (Dynamic)
  private workshopCoords: [number, number] = [-16.5, -68.15];
  
  telemetry = {
    distance: '',
    duration: ''
  };

  // CU05 — Pago
  showPagoModal = false;
  pagoMonto: number | null = null;
  pagoExistente: any = null;

  // CU10 — Ficha técnica editable
  showFichaModal = false;
  fichaEdit = {
    resumen: '',
    ficha_tecnica: {
      diagnostico_probable: '',
      piezas_necesarias: '',
      repuestos_sugeridos: '',
      acciones_inmediatas: ''
    }
  };

  private map: L.Map | null = null;
  private routeLayer: L.GeoJSON | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.loadDetail();
  }

  ngOnDestroy() {
    if (this.map) {
      this.map.remove();
    }
  }

  loadDetail() {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) return;
    
    this.loading = true;
    
    // 1. Cargar detalle de emergencia
    this.api.get<any>(`/gestion-emergencia/${id}`).subscribe({
      next: (res) => {
        this.emergency = res;
        this.cargarPago(); // CU05 — Cargar pago si ya existe
        
        // 2. Cargar coordenadas del taller para el HUD/Mapa
        this.api.get<any>(`/talleres/${this.currentWorkshop}`).subscribe({
           next: (tlr) => {
              if (tlr.latitud && tlr.longitud) {
                this.workshopCoords = [tlr.latitud, tlr.longitud];
              }
              this.loading = false;
              setTimeout(() => {
                this.initMap();
                this.calculateRoute();
              }, 300);
           },
           error: () => {
              // Si falla usamos default, pero no bloqueamos la vista
              this.loading = false;
              setTimeout(() => { this.initMap(); this.calculateRoute(); }, 300);
           }
        });
      },
      error: () => {
        this.loading = false;
        toast.error('Error al sincronizar con el satélite');
      }
    });
  }

  private initMap() {
    if (!this.emergency || !this.emergency.latitud) return;

    if (this.map) this.map.remove();

    try {
      this.map = L.map('emergency-map', {
        zoomControl: false,
        attributionControl: false
      }).setView([this.emergency.latitud, this.emergency.longitud], 13);

      L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(this.map);

      // Emergency Icon
      const emgIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #FF5733; width: 14px; height: 14px; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 20px #FF5733;"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      // Workshop Icon
      const tlrIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #3b82f6; width: 14px; height: 14px; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 20px #3b82f6;"></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });

      L.marker([this.emergency.latitud, this.emergency.longitud], { icon: emgIcon }).addTo(this.map);
      L.marker(this.workshopCoords, { icon: tlrIcon }).addTo(this.map);

      // Fit bounds to show both
      const bounds = L.latLngBounds([this.workshopCoords, [this.emergency.latitud, this.emergency.longitud]]);
      this.map.fitBounds(bounds, { padding: [100, 100] });

    } catch (e) {
      console.error("Map initialization failed", e);
    }
  }

  private calculateRoute() {
    if (!this.emergency || !this.map) return;

    const start = `${this.workshopCoords[1]},${this.workshopCoords[0]}`;
    const end = `${this.emergency.longitud},${this.emergency.latitud}`;
    const url = `https://router.project-osrm.org/route/v1/driving/${start};${end}?overview=full&geometries=geojson`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.code === 'Ok' && data.routes.length > 0) {
          const route = data.routes[0];
          
          // Draw Route
          if (this.routeLayer) this.map?.removeLayer(this.routeLayer);
          this.routeLayer = L.geoJSON(route.geometry, {
            style: { color: '#FF5733', weight: 4, opacity: 0.8 }
          }).addTo(this.map!);

          // Update Telemetry
          this.telemetry.distance = (route.distance / 1000).toFixed(1);
          this.telemetry.duration = Math.ceil(route.duration / 60).toString();
        }
      })
      .catch(err => console.error("OSRM Route failure", err));
  }

  getFichaField(key: string): string[] {
    const field = this.emergency?.resumen_ia?.ficha_tecnica?.[key];
    if (Array.isArray(field)) return field;
    if (typeof field === 'string') return [field];
    return ['SIN_DATA_DETECTED'];
  }

  openAssignModal() {
    if (!this.emergency.is_locked) {
      this.api.post(`/gestion-emergencia/${this.emergency.id}/analizar`, {}).subscribe({
        next: () => { this.loadTechs(); this.showModal = true; },
        error: () => toast.error('Fallo en el protocolo de bloqueo')
      });
    } else {
      this.loadTechs();
      this.showModal = true;
    }
  }

  loadTechs() {
    this.loadingTechs = true;
    this.api.get<any[]>(`/tecnicos/taller/${this.currentWorkshop}`).subscribe({
      next: (res) => { this.availableTechs = res; this.loadingTechs = false; },
      error: () => { this.loadingTechs = false; toast.error('Error al cargar personal'); }
    });
  }

  toggleTech(id: number) {
    if (this.selectedTechs.includes(id)) {
      this.selectedTechs = this.selectedTechs.filter(i => i !== id);
    } else {
      this.selectedTechs.push(id);
    }
  }

  confirmAssignment() {
    this.api.post(`/gestion-emergencia/${this.emergency.id}/asignar`, {
      tecnicos_ids: this.selectedTechs
    }).subscribe({
      next: () => {
        toast.success('Protocolo de Asignación Completado');
        this.showModal = false;
        this.router.navigate(['/app/trabajos']);
      },
      error: () => toast.error('Fallo en la confirmación de misión')
    });
  }

  goBack() { this.router.navigate(['/app/dashboard']); }

  // ─── CU10: Ficha Técnica ─────────────────────────────────────────
  openFichaModal() {
    const ficha = this.emergency?.resumen_ia?.ficha_tecnica || {};
    this.fichaEdit = {
      resumen: this.emergency?.resumen_ia?.resumen || '',
      ficha_tecnica: {
        diagnostico_probable: Array.isArray(ficha.diagnostico_probable) ? ficha.diagnostico_probable.join(', ') : (ficha.diagnostico_probable || ''),
        piezas_necesarias: Array.isArray(ficha.piezas_necesarias) ? ficha.piezas_necesarias.join(', ') : (ficha.piezas_necesarias || ''),
        repuestos_sugeridos: Array.isArray(ficha.repuestos_sugeridos) ? ficha.repuestos_sugeridos.join(', ') : (ficha.repuestos_sugeridos || ''),
        acciones_inmediatas: Array.isArray(ficha.acciones_inmediatas) ? ficha.acciones_inmediatas.join(', ') : (ficha.acciones_inmediatas || '')
      }
    };
    this.showFichaModal = true;
  }

  saveFicha() {
    const payload = {
      resumen: this.fichaEdit.resumen,
      ficha_tecnica: {
        diagnostico_probable: this.fichaEdit.ficha_tecnica.diagnostico_probable.split(',').map((s: string) => s.trim()).filter(Boolean),
        piezas_necesarias: this.fichaEdit.ficha_tecnica.piezas_necesarias.split(',').map((s: string) => s.trim()).filter(Boolean),
        repuestos_sugeridos: this.fichaEdit.ficha_tecnica.repuestos_sugeridos.split(',').map((s: string) => s.trim()).filter(Boolean),
        acciones_inmediatas: this.fichaEdit.ficha_tecnica.acciones_inmediatas.split(',').map((s: string) => s.trim()).filter(Boolean),
      }
    };
    this.api.patch(`/talleres/${this.emergency.id}/ficha-tecnica`, payload).subscribe({
      next: () => {
        toast.success('Ficha técnica actualizada');
        this.showFichaModal = false;
        this.loadDetail();
      },
      error: () => toast.error('Error al actualizar ficha técnica')
    });
  }

  // ─── CU05: Gestionar Tipo de Pago ────────────────────────────────
  cargarPago() {
    this.api.get<any>(`/pagos/${this.emergency.id}`).subscribe({
      next: (res) => { this.pagoExistente = res; },
      error: () => { this.pagoExistente = null; }
    });
  }

  registrarPago() {
    if (!this.pagoMonto || this.pagoMonto <= 0) {
      toast.error('Ingresa un monto válido');
      return;
    }
    this.api.post(`/pagos/${this.emergency.id}`, { monto: this.pagoMonto }).subscribe({
      next: (res) => {
        toast.success(`Pago de $${this.pagoMonto} registrado correctamente`);
        this.pagoExistente = res;
        this.pagoMonto = null;
        this.showPagoModal = false;
      },
      error: (err) => toast.error('Error al registrar pago', { description: err.error?.detail })
    });
  }
}
