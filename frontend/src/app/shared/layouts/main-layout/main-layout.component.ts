import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { ThemeService } from '../../../core/services/theme.service';
import { ApiService } from '../../../core/api/api.service';
import { toast } from 'ngx-sonner';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule],
  template: `
    <div class="flex h-screen bg-[#050505] text-white transition-all duration-300 overflow-hidden font-sans selection:bg-primary selection:text-white">
      
      <!-- SIDEBAR (FIELDWORK _OS STYLE) -->
      <aside [class.w-72]="!isCollapsed" [class.w-20]="isCollapsed"
             class="bg-[#050505] border-r border-zinc-800 flex flex-col transition-all duration-300 relative z-20">
        
        <!-- Brand Section -->
        <div class="h-20 p-6 flex items-center gap-3 border-b border-zinc-900 overflow-hidden">
          <div class="min-w-[12px] w-3 h-3 bg-primary shrink-0"></div>
          <h2 *ngIf="!isCollapsed" class="font-bold tracking-[.25em] text-xs uppercase animate-in fade-in slide-in-from-left-4">
            Fieldwork <span class="text-zinc-500 font-normal">_OS</span>
          </h2>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-3 flex flex-col gap-1 overflow-y-auto overflow-x-hidden pt-8">
          <ng-container *ngFor="let item of navItems">
            <a [routerLink]="item.path" 
               routerLinkActive="bg-zinc-900 border-l border-primary"
               class="flex items-center gap-4 px-5 py-4 transition-all hover:bg-zinc-900/50 group relative">
              <lucide-icon [name]="item.icon" size="16" class="shrink-0 text-zinc-500 group-hover:text-white transition-colors"></lucide-icon>
              <span *ngIf="!isCollapsed" class="font-bold text-[10px] uppercase tracking-[.2em] animate-in fade-in duration-500">
                {{ item.label }}
              </span>
            </a>
          </ng-container>
        </nav>

        <!-- Footer Actions -->
        <div class="p-6 border-t border-zinc-900 flex flex-col gap-6">
          
          <!-- Public Portal -->
          <a href="#" class="flex items-center gap-4 text-zinc-500 hover:text-white transition-all group">
            <lucide-icon name="globe" size="14"></lucide-icon>
            <span *ngIf="!isCollapsed" class="font-bold text-[10px] uppercase tracking-[.15em]">Portal Público</span>
          </a>

          <!-- Logout -->
          <button (click)="logout()" 
                  class="flex items-center gap-4 text-zinc-500 hover:text-red-500 transition-all pt-4 border-t border-zinc-900 mt-2 group">
            <lucide-icon name="log-out" size="14"></lucide-icon>
            <span *ngIf="!isCollapsed" class="font-bold text-[10px] uppercase tracking-[.15em]">Salir</span>
          </button>

          <!-- Collapse Toggle (Small at bottom right) -->
          <button (click)="isCollapsed = !isCollapsed" 
                  class="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-zinc-900 border border-zinc-800 rounded-full flex items-center justify-center hover:bg-primary transition-colors z-30">
            <lucide-icon [name]="isCollapsed ? 'chevrons-right' : 'chevrons-left'" size="10"></lucide-icon>
          </button>
        </div>
      </aside>

      <!-- MAIN CONTENT AREA -->
      <main class="flex-1 flex flex-col min-w-0 h-full relative">
        
        <!-- Top Status Bar -->
        <header class="h-20 border-b border-zinc-900 flex items-center justify-between px-8 bg-[#050505]">
          <div class="flex items-center gap-4">
            <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
            <span class="font-bold text-[10px] uppercase tracking-[.25em] text-zinc-600">Conexión Segura Establecida</span>
          </div>

          <div class="flex items-center gap-8">
            <lucide-icon name="bell" size="16" class="text-zinc-600 hover:text-white cursor-pointer"></lucide-icon>
            <div class="flex items-center gap-4 border-l border-zinc-800 pl-8">
              <div class="text-right">
                <div class="font-bold text-xs">{{ operadorNombre }}</div>
                <div class="font-bold text-[10px] uppercase tracking-widest text-zinc-600">{{ operadorTaller }}</div>
              </div>
              <div class="w-10 h-10 bg-zinc-900 border border-zinc-800 flex items-center justify-center text-xs font-bold">
                {{ operadorInicial }}
              </div>
            </div>
          </div>
        </header>

        <!-- Scrollable Content -->
        <div class="flex-1 overflow-y-auto bg-[#0a0a0a]">
          <router-outlet></router-outlet>
        </div>
      </main>

    </div>
  `,
  styles: [`
    :host { display: block; height: 100vh; }
  `]
})
export class MainLayoutComponent implements OnInit {
  isCollapsed = false;
  operadorNombre = localStorage.getItem('user_name') || 'Operador';
  operadorTaller = localStorage.getItem('nombre_taller') || 'Taller OS';
  operadorInicial = (this.operadorNombre).substring(0, 2).toUpperCase();
  
  navItems = [
    { label: 'Tablero', icon: 'layout-dashboard', path: '/app/dashboard' },
    { label: 'Reportes', icon: 'trending-up', path: '/app/reportes' },
    { label: 'Mis Trabajos', icon: 'briefcase', path: '/app/trabajos' },
    { label: 'Técnicos', icon: 'users', path: '/app/tecnicos' },
    { label: 'Mis Talleres', icon: 'factory', path: '/app/talleres' },
  ];

  constructor(
    public themeService: ThemeService,
    private router: Router,
    private api: ApiService
  ) {}

  ngOnInit() {}

  logout() {
    // CU02 — Llamar al endpoint de cierre de sesión en el backend
    this.api.post('/auth/logout', {}).subscribe({
      next: () => {
        localStorage.clear();
        this.router.navigate(['/auth/login']);
      },
      error: () => {
        // Incluso si falla el endpoint, cerramos sesión localmente
        localStorage.clear();
        this.router.navigate(['/auth/login']);
      }
    });
  }
}
