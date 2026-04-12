import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

// UI
import { CardComponent } from '../../shared/ui/card/card.component';
import { ButtonComponent } from '../../shared/ui/button/button.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent],
  template: `
    <div class="dashboard-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="font-bold text-primary">Taller Móvil</h2>
        </div>
        <nav class="sidebar-nav">
          <a class="nav-item active">Panel Principal</a>
          <a class="nav-item">Mis Vehículos</a>
          <a class="nav-item">Emergencias</a>
          <a class="nav-item">Configuración</a>
        </nav>
        <div class="sidebar-footer">
          <app-button variant="ghost" [fullWidth]="true" (clicked)="logout()">
            Cerrar Sesión
          </app-button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Headerbar -->
        <header class="headerbar">
          <div class="welcome-text">
            <h3>Bienvenido, {{ nombreUsuario }}</h3>
            <span class="badge role-badge">{{ rolUsuario | uppercase }}</span>
          </div>
          <div class="actions">
            <!-- Avatar mockup -->
            <div class="avatar">{{ nombreUsuario.charAt(0) }}</div>
          </div>
        </header>

        <!-- Content Area -->
        <div class="content-body">
          <div class="stats-grid mb-4">
            <app-card>
              <h4 class="text-muted font-size-sm">Solicitudes Activas</h4>
              <h2>2</h2>
            </app-card>
            <app-card>
              <h4 class="text-muted font-size-sm">Vehículos Registrados</h4>
              <h2>1</h2>
            </app-card>
            <app-card>
              <h4 class="text-muted font-size-sm">Estado</h4>
              <h2 class="text-success">Disponible</h2>
            </app-card>
          </div>

          <app-card title="Visión General" subtitle="Actividad reciente en el sistema">
            <div class="empty-state text-center p-6 text-muted">
              <i class="las la-car-crash" style="font-size: 3rem; margin-bottom: 1rem;"></i>
              <p>No tienes emergencias recientes.</p>
              <div class="mt-4" *ngIf="rolUsuario === 'cliente'">
                <app-button variant="primary">Reportar Nueva Emergencia</app-button>
              </div>
            </div>
          </app-card>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .dashboard-layout {
      display: flex;
      min-height: 100vh;
      background-color: var(--bg-body);
    }
    
    /* SIDEBAR */
    .sidebar {
      width: 260px;
      background-color: var(--bg-surface);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
    }
    .sidebar-header {
      padding: var(--space-5) var(--space-6);
      border-bottom: 1px solid var(--border-color);
      h2 { margin: 0; font-size: var(--font-size-xl); color: var(--color-primary); }
    }
    .sidebar-nav {
      flex: 1;
      padding: var(--space-4) 0;
      display: flex;
      flex-direction: column;
    }
    .nav-item {
      padding: var(--space-3) var(--space-6);
      color: var(--color-text-muted);
      cursor: pointer;
      font-weight: 500;
      transition: background var(--transition-fast), color var(--transition-fast);
      
      &:hover {
        background-color: var(--bg-surface-hover);
        color: var(--color-primary);
      }
      &.active {
        color: var(--color-primary);
        background-color: var(--color-primary-light);
        border-right: 3px solid var(--color-primary);
      }
    }
    .sidebar-footer {
      padding: var(--space-4);
      border-top: 1px solid var(--border-color);
    }

    /* MAIN CONTENT */
    .main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .headerbar {
      height: 70px;
      background-color: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 var(--space-8);
      
      .welcome-text { display: flex; align-items: center; gap: var(--space-3); }
      h3 { margin: 0; font-size: var(--font-size-lg); }
    }
    
    .role-badge {
      background-color: var(--color-primary-light);
      color: var(--color-primary);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-size: var(--font-size-xs);
      font-weight: 600;
    }
    
    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background-color: var(--color-secondary);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
    }

    .content-body {
      padding: var(--space-8);
      flex: 1;
      overflow-y: auto;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: var(--space-6);
      
      h2 { margin-top: var(--space-2); font-size: var(--font-size-2xl); }
    }
    
    .text-success { color: var(--color-success); }
  `]
})
export class DashboardComponent implements OnInit {
  nombreUsuario = 'Usuario';
  rolUsuario = 'Desconocido';

  constructor(private router: Router) {}

  ngOnInit() {
    this.nombreUsuario = localStorage.getItem('nombre') || 'Usuario Guest';
    this.rolUsuario = localStorage.getItem('rol') || 'cliente';
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/']);
  }
}
