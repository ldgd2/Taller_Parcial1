import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { ApiService } from '../../../core/api/api.service';
import { FormsModule } from '@angular/forms';
import { toast } from 'ngx-sonner';
import * as L from 'leaflet';

interface Specialty { id: number; nombre: string; }

@Component({
  selector: 'app-taller-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule, FormsModule],
  template: `
    <div class="min-h-full bg-[#0d0d0d] text-white animate-in fade-in duration-500 pb-20 relative">
      
      <!-- TOP NAVIGATION -->
      <div class="h-24 bg-[#0d0d0d]/90 border-b border-[#222222] px-8 lg:px-12 flex items-center justify-between sticky top-0 z-40 backdrop-blur-xl">
        <div class="flex items-center gap-6">
          <button (click)="goBack()" class="w-12 h-12 border border-zinc-800 flex items-center justify-center hover:bg-[#FF5733] hover:border-[#FF5733] transition-all group">
            <lucide-icon name="arrow-left" class="text-zinc-500 group-hover:text-white" size="18"></lucide-icon>
          </button>
          <div *ngIf="taller">
            <div class="flex items-center gap-4 mb-1">
              <h1 class="text-[28px] font-bold tracking-tight uppercase text-white">{{ taller.nombre }}</h1>
              <span class="px-3 py-1 font-mono text-[10px] font-bold uppercase tracking-[.2em] border border-[#222222] bg-[#111111] text-zinc-400">
                REF : {{ taller.cod }}
              </span>
            </div>
            <p class="font-mono text-[10px] text-[#FF5733] uppercase tracking-[.25em]">Configuración de Infraestructura Operativa</p>
          </div>
        </div>

        <button *ngIf="!loading && taller" (click)="save()" 
                class="bg-[#FF5733] text-white px-10 py-4 font-bold text-[11px] uppercase tracking-widest hover:brightness-110 transition-all shadow-lg shadow-[#FF5733]/20 flex items-center gap-2">
          ACTUALIZAR INSTALACIÓN
        </button>
      </div>

      <!-- LOADING -->
      <div *ngIf="loading" class="p-40 flex flex-col items-center justify-center gap-6">
        <div class="w-12 h-12 border-2 border-[#FF5733] border-t-transparent rounded-full animate-spin"></div>
        <p class="font-mono text-[9px] uppercase tracking-[.4em] text-[#FF5733]">Sincronizando Instalación...</p>
      </div>

      <ng-container *ngIf="!loading && taller">
        <div class="p-8 lg:p-12 max-w-5xl mx-auto space-y-8">
          
          <!-- GENERAL SETTINGS -->
          <section class="bg-[#111111] border border-[#222222] p-10 space-y-8 shadow-xl">
            <h3 class="font-bold text-[11px] uppercase tracking-[.4em] text-white border-l-2 border-[#FF5733] pl-4">Datos Generales y Ubicación</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="space-y-3">
                <label class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">Nombre del Taller</label>
                <input [(ngModel)]="taller.nombre" type="text" class="w-full bg-[#050505] border border-[#222222] p-4 text-sm font-bold tracking-tight outline-none focus:border-[#FF5733] transition-all text-white">
              </div>
              
              <div class="space-y-3">
                <label class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">Estado Operativo</label>
                <select [(ngModel)]="taller.estado" class="w-full bg-[#050505] border border-[#222222] p-4 text-xs font-bold uppercase tracking-widest outline-none focus:border-[#FF5733] cursor-pointer text-white">
                  <option value="ACTIVO">OPERATIVO / EN RUTA (ACTIVO)</option>
                  <option value="INACTIVO">FUERA DE SERVICIO (INACTIVO)</option>
                </select>
              </div>
            </div>
            
            <div class="space-y-3 relative z-10">
              <label class="font-mono text-[10px] uppercase tracking-widest text-zinc-500 flex justify-between">
                <span>Dirección Física Resolucionada</span>
                <span class="text-[#FF5733]">{{ taller.latitud || '?' }}N, {{ taller.longitud || '?' }}W</span>
              </label>
              <div class="relative">
                <input [(ngModel)]="taller.direccion" type="text" class="w-full bg-[#050505] border border-[#222222] p-4 pl-12 text-sm outline-none focus:border-[#FF5733] transition-all text-white shadow-inner">
                <lucide-icon name="map-pin" class="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-600" size="16"></lucide-icon>
              </div>
            </div>

            <!-- MAP CONTAINER -->
            <div class="space-y-2">
              <label class="font-mono text-[10px] uppercase tracking-widest text-zinc-500">
                Selección de Coordenadas (Pin Satelital)
              </label>
              <!-- Leaflet Map Container -->
              <div id="map" class="h-[400px] w-full bg-[#050505] border border-[#222222] relative z-0"></div>
            </div>
          </section>

          <!-- ESPECIALIDADES TAGS SECTION -->
          <section class="bg-[#111111] border border-[#222222] p-10 space-y-8 shadow-xl relative">
            <div class="flex justify-between items-center mb-2">
              <h3 class="font-bold text-[11px] uppercase tracking-[.4em] text-white border-l-2 border-[#00ff9d] pl-4">Especialidades Activas</h3>
              <span class="font-mono text-[10px] text-[#00ff9d]">TAG_SYSTEM_V.2</span>
            </div>

            <!-- TAG CLOUD -->
            <div class="flex flex-wrap gap-3 p-6 bg-[#050505] border border-[#222222] min-h-[140px]">
              <div *ngFor="let esp of taller.especialidades" 
                   class="flex items-center gap-4 bg-[#1a1a1a] border border-zinc-700/50 px-4 py-2 group hover:border-[#FF5733] transition-all">
                <lucide-icon name="tag" size="12" class="text-[#FF5733]"></lucide-icon>
                <span class="text-[11px] font-bold uppercase tracking-widest text-white">{{ esp.nombre }}</span>
                <button (click)="removeSpecialty(esp.id)" class="text-zinc-600 hover:text-red-500 hover:bg-black/20 p-1 rounded transition-colors ml-2">
                  <lucide-icon name="x" size="14"></lucide-icon>
                </button>
              </div>
              
              <div *ngIf="taller.especialidades?.length === 0" class="flex-1 flex items-center justify-center italic text-zinc-600 font-mono text-[10px] uppercase tracking-widest">
                AÑADA ETIQUETAS PARA DEFINIR LAS ESPECIALIDADES
              </div>
            </div>

            <!-- SEARCH / ADD TAG -->
            <div class="relative w-full z-20 mt-6 md:w-1/2">
                <lucide-icon name="plus" class="absolute left-4 top-1/2 -translate-y-1/2 text-[#FF5733]" size="14"></lucide-icon>
                <input 
                    type="text" 
                    [(ngModel)]="searchQuery" 
                    (input)="onSearch()"
                    placeholder="Búsqueda de especialidad..." 
                    class="w-full bg-[#1a1a1a] border border-[#222222] p-4 pl-12 text-xs font-bold uppercase tracking-[.2em] outline-none text-white focus:border-[#FF5733] placeholder:text-zinc-600">
                    
                <div *ngIf="filteredSpecs.length > 0" class="absolute w-full mt-1 bg-[#111111] border border-[#222222] shadow-2xl max-h-[250px] overflow-y-auto">
                    <div *ngFor="let spec of filteredSpecs" 
                         (click)="addSpecialtySearch(spec)"
                         class="p-4 border-b border-[#222222] hover:bg-[#FF5733] hover:text-white cursor-pointer text-xs font-bold uppercase tracking-[.2em] transition-colors flex items-center gap-3">
                         <lucide-icon name="tag" size="12" class="opacity-50"></lucide-icon>
                         {{ spec.nombre }}
                    </div>
                </div>
            </div>
          </section>

        </div>
      </ng-container>
    </div>
  `
})
export class TallerDetailComponent implements OnInit {
  taller: any = null;
  loading = true;
  catalogSpecialties: Specialty[] = [];
  
  // Search state
  searchQuery: string = '';
  filteredSpecs: Specialty[] = [];

  // Map state
  map: L.Map | null = null;
  marker: L.Marker | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.loadAll();
  }

  loadAll() {
    const cod = this.route.snapshot.paramMap.get('cod');
    if (!cod) return;

    this.api.get<any>(`/talleres/${cod}`).subscribe({
      next: (res) => {
        this.taller = res;
        this.loading = false;
        
        // Timeout ensures DOM has rendered *ngIf container
        setTimeout(() => this.initMap(), 100);
      },
      error: () => toast.error('Error al cargar instalación')
    });

    this.api.get<Specialty[]>('/catalogos/especialidades').subscribe({
      next: (res) => this.catalogSpecialties = res,
      error: () => console.error('Error al cargar catálogo')
    });
  }

  initMap() {
    if (this.map) return;
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    let initialLat = -12.0464; // Default to Lima, Peru
    let initialLng = -77.0428; 
    let hasCoords = false;

    if (this.taller.latitud && this.taller.longitud && this.taller.latitud !== 'NO' && this.taller.latitud !== '?') {
        const pLat = parseFloat(this.taller.latitud);
        const pLng = parseFloat(this.taller.longitud);
        if (!isNaN(pLat) && !isNaN(pLng)) {
            initialLat = pLat;
            initialLng = pLng;
            hasCoords = true;
        }
    }

    this.map = L.map('map').setView([initialLat, initialLng], hasCoords ? 15 : 10);

    // Dark Map Base Layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(this.map);

    // Custom pure CSS Marker (no broken png links)
    const customIcon = L.divIcon({
        className: 'custom-pin',
        html: '<div style="background-color: #FF5733; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px rgba(255,87,51,0.8);"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    if (hasCoords) {
        this.marker = L.marker([initialLat, initialLng], { icon: customIcon }).addTo(this.map);
    }

    // Map Click Interaction
    this.map.on('click', (e: L.LeafletMouseEvent) => {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        this.taller.latitud = lat.toFixed(6);
        this.taller.longitud = lng.toFixed(6);

        if (this.marker) {
            this.marker.setLatLng([lat, lng]);
        } else {
            this.marker = L.marker([lat, lng], { icon: customIcon }).addTo(this.map!);
        }

        this.reverseGeocode(lat, lng);
    });
  }

  reverseGeocode(lat: number, lng: number) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
      .then(res => res.json())
      .then(data => {
        if (data && data.display_name) {
          this.taller.direccion = data.display_name;
          toast.info('Dirección inferida desde coordenadas satelitales');
        }
      })
      .catch(err => console.error('Error in reverse geocoding', err));
  }

  onSearch() {
    if (!this.searchQuery) {
       this.filteredSpecs = [];
       return;
    }
    const q = this.searchQuery.toLowerCase();
    
    // Exclude specialities already active
    const addedIds = this.taller.especialidades.map((s:any) => s.id);
    
    this.filteredSpecs = this.catalogSpecialties.filter(s => 
       s.nombre.toLowerCase().includes(q) && !addedIds.includes(s.id)
    );
  }

  addSpecialtySearch(spec: Specialty) {
    this.taller.especialidades.push(spec);
    this.searchQuery = '';
    this.filteredSpecs = [];
    toast.success('Tag vinculado dinámicamente');
  }

  removeSpecialty(id: number) {
    this.taller.especialidades = this.taller.especialidades.filter((s: any) => s.id !== id);
    toast.info('Tag removido de la infraestructura');
  }

  save() {
    const cod = this.taller.cod;
    
    let parsedLat = null;
    let parsedLng = null;
    
    if (this.taller.latitud && this.taller.latitud !== 'NO' && this.taller.latitud !== '?') {
        parsedLat = parseFloat(this.taller.latitud);
    }
    if (this.taller.longitud && this.taller.longitud !== 'NO' && this.taller.longitud !== '?') {
        parsedLng = parseFloat(this.taller.longitud);
    }
    
    const updateData = {
      nombre: this.taller.nombre,
      direccion: this.taller.direccion,
      latitud: parsedLat,
      longitud: parsedLng,
      estado: this.taller.estado,
      especialidades: this.taller.especialidades.map((s: any) => s.id)
    };

    console.log("Enviando actualizacion...", updateData);

    this.api.put(`/talleres/${cod}`, updateData).subscribe({
      next: () => toast.success('Instalación actualizada correctamente'),
      error: () => toast.error('Error critico al sincronizar cambios')
    });
  }

  goBack() { this.router.navigate(['/app/talleres']); }
}

