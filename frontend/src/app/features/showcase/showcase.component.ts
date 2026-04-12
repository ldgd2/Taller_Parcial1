import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// Importando los "Legos" UI
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { InputComponent } from '../../shared/ui/input/input.component';
import { SelectComponent, SelectOption } from '../../shared/ui/select/select.component';
import { CardComponent } from '../../shared/ui/card/card.component';
import { ApiService } from '../../core/api/api.service';

@Component({
  selector: 'app-showcase',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonComponent, InputComponent, SelectComponent, CardComponent],
  template: `
    <div class="showcase-container p-6">
      <div class="header">
        <h1 class="title">Taller Móvil - Plataforma Administrativa</h1>
        <p class="subtitle text-muted">Sistema de Diseño & Componentes UI (Showcase)</p>
      </div>

      <div class="grid">
        <!-- Ejemplos de Inputs -->
        <app-card title="Controles de Texto (Inputs)">
          <app-input
            label="Nombre Completo"
            placeholder="Ingrese su nombre"
            type="text"
            icon="las la-user">
          </app-input>
          
          <app-input
            label="Correo Electrónico"
            placeholder="ejemplo@correo.com"
            type="email"
            icon="las la-envelope">
          </app-input>

          <app-input
            label="Contraseña"
            placeholder="********"
            type="password"
            icon="las la-lock">
          </app-input>

          <app-input
            label="Campo con Error"
            placeholder="Intenta con otro valor"
            [error]="'Este campo es obligatorio'"
            icon="las la-times-circle">
          </app-input>
        </app-card>

        <!-- Ejemplos de Selects & Botones -->
        <app-card title="Módulo de Selección y Acciones">
          
          <app-select
            label="Disponibilidad de Taller"
            [options]="disponibilidadOptions"
            [(ngModel)]="estadoTaller">
          </app-select>

          <div class="flex-col gap-4 mt-4">
            <h4 class="font-medium text-muted">Botones Primarios / Secundarios</h4>
            <div class="flex gap-2 items-center flex-wrap">
              <app-button variant="primary" (clicked)="testAction('Primary')">Guardar Cambios</app-button>
              <app-button variant="secondary" (clicked)="testAction('Secondary')">Cancelar</app-button>
              <app-button variant="danger" (clicked)="testAction('Danger')">Eliminar Registro</app-button>
              <app-button variant="ghost" (clicked)="testAction('Ghost')">Ver Perfil</app-button>
            </div>

            <h4 class="font-medium text-muted mt-4">Estados (Full width & Loading)</h4>
            <div class="flex gap-2">
              <app-button variant="primary" [fullWidth]="true">Finalizar Asignación</app-button>
            </div>
            <div class="flex gap-2 mt-2">
              <app-button variant="primary" [loading]="true">Procesando</app-button>
              <app-button variant="secondary" [disabled]="true">Aceptado</app-button>
            </div>
          </div>
        </app-card>

        <!-- Conexión a Backend Mockup -->
        <app-card title="Prueba de API (Core Services)">
          <p class="text-muted mb-4">Esta caja prueba el flujo arquitectónico desde el ApiService hacia el backend.</p>
          <div class="flex items-center justify-between">
            <span class="font-bold">Estado actual simulado:</span>
            <span class="badge" [class.success]="apiStatus">{{ apiResponseText }}</span>
          </div>
          <div class="mt-4">
            <app-button variant="secondary" [fullWidth]="true" [loading]="loadingApi" (clicked)="testConnection()">
              Probar Conexión con Backend
            </app-button>
          </div>
        </app-card>
      </div>
    </div>
  `,
  styles: [`
    .showcase-container {
      max-width: 1200px;
      margin: 0 auto;
    }
    .header { margin-bottom: var(--space-8); text-align: center; }
    .title { font-size: var(--font-size-3xl); color: var(--color-primary-hover); }
    .subtitle { font-size: var(--font-size-lg); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: var(--space-6);
    }
    .badge {
      padding: 4px 12px;
      border-radius: var(--radius-full);
      font-size: var(--font-size-xs);
      font-weight: 600;
      background-color: var(--color-danger-light);
      color: var(--color-danger);
    }
    .badge.success {
      background-color: var(--color-success-light);
      color: var(--color-success);
    }
  `]
})
export class ShowcaseComponent {
  // Valores para los compontes visuales
  estadoTaller = 'ACTIVO';
  disponibilidadOptions: SelectOption[] = [
    { label: 'Taller Activo (Disponible)', value: 'ACTIVO' },
    { label: 'Taller Inactivo (Aforo Lleno)', value: 'INACTIVO' }
  ];

  // Variables para la simulación de API
  loadingApi = false;
  apiStatus = false;
  apiResponseText = 'Sin Conexión';

  constructor(private apiService: ApiService) {}

  testAction(type: string) {
    alert(`Has clickeado el botón: ${type}`);
  }

  testConnection() {
    this.loadingApi = true;
    
    // Llamada real al backend en Healthcheck "/" (ver main.py del backend)
    this.apiService.get<{status: string, message: string}>('/').subscribe({
      next: (res) => {
        this.loadingApi = false;
        this.apiStatus = true;
        this.apiResponseText = res.message; // 'API funcionando correctamente'
      },
      error: (err) => {
        this.loadingApi = false;
        this.apiStatus = false;
        this.apiResponseText = 'Fallo al conectar. ¿Está iniciado FastAPI?';
        console.error(err);
      }
    });
  }
}
