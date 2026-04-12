import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card" [class.interactive]="interactive">
      <!-- Opcional Header -->
      <div class="card-header" *ngIf="title || subtitle">
        <h3 class="card-title" *ngIf="title">{{ title }}</h3>
        <p class="card-subtitle" *ngIf="subtitle">{{ subtitle }}</p>
      </div>
      
      <!-- Content (ng-content) -->
      <div class="card-body" [class.no-padding]="noPadding">
        <ng-content></ng-content>
      </div>
      
      <!-- Opcional Footer -->
      <div class="card-footer" *ngIf="hasFooter">
        <ng-content select="[card-footer]"></ng-content>
      </div>
    </div>
  `,
  styleUrls: ['./card.component.scss']
})
export class CardComponent {
  @Input() title?: string;
  @Input() subtitle?: string;
  @Input() noPadding: boolean = false;
  @Input() hasFooter: boolean = false;
  @Input() interactive: boolean = false;
}
