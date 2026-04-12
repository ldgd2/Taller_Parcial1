import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ButtonComponent } from '../../shared/ui/button/button.component';
import { CardComponent } from '../../shared/ui/card/card.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, ButtonComponent, CardComponent],
  template: `
    <div class="landing-container">
      <header class="top-nav">
        <div class="logo font-bold">Taller Móvil AI</div>
        <div class="actions">
          <app-button variant="ghost" (clicked)="irALogin()">Iniciar Sesión</app-button>
          <app-button variant="primary" (clicked)="irARegistro()">Registrarse</app-button>
        </div>
      </header>

      <main class="hero">
        <div class="hero-content">
          <h1 class="hero-title">Atención de Emergencias Vehiculares en Tiempo Real</h1>
          <p class="hero-subtitle text-muted">
            Conecta al instante con los mejores talleres más cercanos a tu ubicación mediante inteligencia artificial multimodal.
          </p>
          <div class="hero-actions flex gap-4 justify-center mt-4">
            <app-button variant="primary" (clicked)="irALogin()">Solicitar Asistencia Ahora</app-button>
            <app-button variant="secondary" (clicked)="irALogin()">Soy un Taller</app-button>
          </div>
        </div>

        <div class="features mt-4">
          <app-card title="Rapidez" [interactive]="true">
            <p class="text-muted">Asignación automática basada en tu ubicación GPS.</p>
          </app-card>
          <app-card title="Precisión IA" [interactive]="true">
            <p class="text-muted">Envío de audio e imágenes para pre-diagnóstico.</p>
          </app-card>
          <app-card title="Confianza" [interactive]="true">
            <p class="text-muted">Trazabilidad completa y técnicos certificados.</p>
          </app-card>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .landing-container {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-color: var(--bg-body);
    }
    .top-nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--space-4) var(--space-8);
      background-color: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
    }
    .logo {
      font-size: var(--font-size-xl);
      color: var(--color-primary);
    }
    .hero {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: var(--space-12) var(--space-4);
      text-align: center;
    }
    .hero-content {
      max-width: 800px;
    }
    .hero-title {
      font-size: 3rem;
      color: var(--color-secondary);
      margin-bottom: var(--space-4);
    }
    .hero-subtitle {
      font-size: var(--font-size-lg);
      margin-bottom: var(--space-6);
    }
    .features {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: var(--space-6);
      width: 100%;
      max-width: 1000px;
      margin-top: 4rem;
    }
  `]
})
export class HomeComponent {
  constructor(private router: Router) {}

  irALogin() {
    this.router.navigate(['/auth/login']);
  }
  
  irARegistro() {
    // Por ahora redirige a login también
    this.router.navigate(['/auth/login']);
  }
}
