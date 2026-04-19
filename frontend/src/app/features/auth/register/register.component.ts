import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

// UI
import { CardComponent } from '../../../shared/ui/card/card.component';
import { InputComponent } from '../../../shared/ui/input/input.component';
import { ButtonComponent } from '../../../shared/ui/button/button.component';
import { ApiService } from '../../../core/api/api.service';

import { MapPickerComponent } from '../../../shared/ui/map-picker/map-picker.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule, 
    RouterModule, 
    CardComponent, 
    InputComponent, 
    ButtonComponent,
    MapPickerComponent
  ],
  template: `
    <div class="auth-layout">
      <div class="auth-left">
        <div class="brand">
          <h1>Taller Móvil</h1>
          <p>Gestiona tus talleres con precisión GPS y control total.</p>
        </div>
      </div>
      
      <div class="auth-right">
        <app-card class="register-card" [noPadding]="false">
          <div class="register-header">
            <h2>Crear Cuenta de Administrador</h2>
            <p class="text-muted">Configura tu perfil y tu primer taller</p>
          </div>

          <form (ngSubmit)="onRegister()" #registerForm="ngForm" class="register-form">
            
            <div class="form-section-title">Información Personal</div>
            <div class="row">
              <div class="col">
                <app-input
                  label="Nombre"
                  [(ngModel)]="formData.nombre"
                  name="nombre"
                  [required]="true"
                  placeholder="Ej: Juan">
                </app-input>
              </div>
              <div class="col">
                <app-input
                  label="Apellido"
                  [(ngModel)]="formData.apellido"
                  name="apellido"
                  [required]="true"
                  placeholder="Ej: Pérez">
                </app-input>
              </div>
            </div>

            <app-input
              label="Correo Electrónico"
              type="email"
              [(ngModel)]="formData.correo"
              name="correo"
              [required]="true"
              placeholder="admin@ejemplo.com"
              icon="las la-envelope">
            </app-input>

            <app-input
              label="Contraseña"
              type="password"
              [(ngModel)]="formData.contrasena"
              name="contrasena"
              [required]="true"
              placeholder="********"
              icon="las la-lock">
            </app-input>

            <div class="form-section-title mt-4">Ubicación del Taller</div>
            <p class="text-muted font-size-sm mb-2">Haz clic en el mapa para ubicar tu taller precisamente.</p>
            
            <app-map-picker (locationSelected)="onLocationSelected($event)"></app-map-picker>

            <app-input
              label="Nombre del Taller"
              [(ngModel)]="formData.nombre_taller"
              name="nombre_taller"
              [required]="true"
              placeholder="Ej: Taller Central"
              icon="las la-tools">
            </app-input>

            <app-input
              label="Dirección (Se autocompletará desde el mapa)"
              [(ngModel)]="formData.direccion_taller"
              name="direccion_taller"
              [required]="true"
              placeholder="Calle Principal #123"
              icon="las la-map-marker">
            </app-input>

            <div class="error-panel" *ngIf="errorMessage">
              {{ errorMessage }}
            </div>

            <div class="success-panel" *ngIf="successMessage">
              {{ successMessage }}
            </div>

            <div class="actions mt-6">
              <app-button 
                type="submit" 
                variant="primary" 
                [fullWidth]="true" 
                [loading]="loading">
                ¡Registrarme Ahora!
              </app-button>
            </div>
            
            <div class="footer-links text-center mt-4">
              <p class="text-muted font-size-sm">¿Ya tienes cuenta? <a routerLink="/auth/login">Inicia Sesión</a></p>
              <a routerLink="/" class="text-muted font-size-sm">← Volver al Inicio</a>
            </div>
          </form>
        </app-card>
      </div>
    </div>
  `,
  styles: [`
    .auth-layout {
      display: flex;
      min-height: 100vh;
      background-color: var(--bg-body);
    }
    .auth-left {
      flex: 1;
      background: linear-gradient(135deg, var(--color-secondary), var(--color-primary));
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--space-8);
      
      @media (max-width: 992px) {
        display: none;
      }
    }
    .brand h1 { font-size: 3rem; margin-bottom: var(--space-2); }
    .brand p { font-size: 1.25rem; opacity: 0.8; max-width: 400px; }
    
    .auth-right {
      flex: 1.2;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--space-6);
      overflow-y: auto;
    }
    .register-card {
      width: 100%;
      max-width: 600px;
    }
    .register-header {
      margin-bottom: var(--space-6);
      text-align: center;
      h2 { color: var(--color-text-main); font-size: 1.5rem; }
    }
    .form-section-title {
      font-weight: 700;
      font-size: var(--font-size-sm);
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--color-primary);
      margin-bottom: var(--space-3);
      border-bottom: 1px solid var(--border-color);
      padding-bottom: var(--space-1);
    }
    .row { display: flex; gap: var(--space-4); }
    .col { flex: 1; }
    .mb-2 { margin-bottom: 0.5rem; }
    .error-panel {
      padding: var(--space-2);
      border-radius: var(--radius-sm);
      background-color: var(--color-danger-light);
      color: var(--color-danger);
      font-size: var(--font-size-sm);
      margin-top: var(--space-4);
      text-align: center;
    }
    .success-panel {
      padding: var(--space-2);
      border-radius: var(--radius-sm);
      background-color: var(--color-success-light);
      color: var(--color-success);
      font-size: var(--font-size-sm);
      margin-top: var(--space-4);
      text-align: center;
    }
    .font-size-sm { font-size: var(--font-size-sm); }
  `]
})
export class RegisterComponent {
  formData = {
    nombre: '',
    apellido: '',
    correo: '',
    contrasena: '',
    nombre_taller: '',
    direccion_taller: '',
    latitud_taller: null as number | null,
    longitud_taller: null as number | null
  };

  loading = false;
  errorMessage = '';
  successMessage = '';

  constructor(private api: ApiService, private router: Router) {}

  onLocationSelected(loc: {lat: number, lng: number, address: string}) {
    this.formData.latitud_taller = loc.lat;
    this.formData.longitud_taller = loc.lng;
    this.formData.direccion_taller = loc.address;
  }

  onRegister() {
    if (this.isFormInvalid()) {
      this.errorMessage = 'Por favor completa todos los campos requeridos y ubica tu taller en el mapa.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    // El botón manda a registrar directamente
    this.api.post<any>('/auth/register', this.formData).subscribe({
      next: (res) => {
        this.loading = false;
        this.successMessage = '¡Registro exitoso! Iniciando sesión...';
        
        // Login automático o redirección directa para fluidez
        setTimeout(() => {
          this.router.navigate(['/auth/login'], { queryParams: { registered: true, email: this.formData.correo } });
        }, 1000);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'Error al registrarse. Intenta con otro correo.';
      }
    });
  }

  private isFormInvalid(): boolean {
    return !this.formData.nombre || !this.formData.apellido || 
           !this.formData.correo || !this.formData.contrasena ||
           !this.formData.nombre_taller || !this.formData.direccion_taller;
  }
}
