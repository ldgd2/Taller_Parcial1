import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

// UI
import { CardComponent } from '../../../shared/ui/card/card.component';
import { InputComponent } from '../../../shared/ui/input/input.component';
import { ButtonComponent } from '../../../shared/ui/button/button.component';
import { SelectComponent, SelectOption } from '../../../shared/ui/select/select.component';
import { ApiService } from '../../../core/api/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, CardComponent, InputComponent, ButtonComponent, SelectComponent],
  template: `
    <div class="auth-layout">
      <div class="auth-left">
        <!-- Decoración / Imagen Branding -->
        <div class="brand">
          <h1>Taller Móvil</h1>
          <p>Tu asistente vehicular con inteligencia artificial.</p>
        </div>
      </div>
      
      <div class="auth-right">
        <app-card class="login-card" [noPadding]="false">
          <div class="login-header">
            <h2>Bienvenido de nuevo</h2>
            <p class="text-muted">Ingresa tus credenciales para continuar</p>
          </div>

          <form (ngSubmit)="onLogin()" #loginForm="ngForm" class="login-form">
            
            <app-select
              label="Tipo de Usuario"
              [options]="rolesOptions"
              [(ngModel)]="formData.rol"
              name="rol"
              [required]="true">
            </app-select>

            <app-input
              label="Correo Electrónico"
              type="email"
              placeholder="Ej: cliente@demo.com"
              [(ngModel)]="formData.correo"
              name="correo"
              [required]="true"
              icon="las la-envelope">
            </app-input>

            <app-input
              label="Contraseña"
              type="password"
              placeholder="********"
              [(ngModel)]="formData.contrasena"
              name="contrasena"
              [required]="true"
              icon="las la-lock">
            </app-input>

            <div class="error-panel" *ngIf="errorMessage">
              {{ errorMessage }}
            </div>

            <div class="actions mt-4">
              <app-button 
                type="submit" 
                variant="primary" 
                [fullWidth]="true" 
                [loading]="loading">
                Ingresar al Sistema
              </app-button>
            </div>
            
            <div class="footer-links text-center mt-4">
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
      background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--space-8);
      
      @media (max-width: 768px) {
        display: none;
      }
    }
    .brand h1 { font-size: 3rem; margin-bottom: var(--space-2); }
    .brand p { font-size: 1.25rem; opacity: 0.8; }
    
    .auth-right {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: var(--space-6);
    }
    .login-card {
      width: 100%;
      max-width: 440px;
    }
    .login-header {
      margin-bottom: var(--space-6);
      text-align: center;
      
      h2 { color: var(--color-text-main); font-size: 1.5rem; }
    }
    .error-panel {
      padding: var(--space-2);
      border-radius: var(--radius-sm);
      background-color: var(--color-danger-light);
      color: var(--color-danger);
      font-size: var(--font-size-sm);
      margin-bottom: var(--space-4);
      text-align: center;
    }
    .font-size-sm { font-size: var(--font-size-sm); }
  `]
})
export class LoginComponent {
  rolesOptions: SelectOption[] = [
    { label: 'Soy Cliente', value: 'cliente' },
    { label: 'Soy Técnico / Taller', value: 'tecnico' }
  ];

  formData = {
    correo: '',
    contrasena: '',
    rol: 'cliente'
  };

  loading = false;
  errorMessage = '';

  constructor(private api: ApiService, private router: Router) {}

  onLogin() {
    if (!this.formData.correo || !this.formData.contrasena) {
      this.errorMessage = 'Por favor completa todos los campos.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.api.post<any>('/auth/login', this.formData).subscribe({
      next: (res) => {
        this.loading = false;
        // Guardar token
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('rol', res.rol);
        localStorage.setItem('nombre', res.nombre);
        
        // Simular redirección según rol
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'Error al iniciar sesión. Verifica tus credenciales.';
      }
    });
  }
}
