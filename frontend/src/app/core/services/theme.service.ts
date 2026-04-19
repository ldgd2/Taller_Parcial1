import { Injectable, Renderer2, RendererFactory2 } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  isDark = true;

  constructor() {
    this.applyTheme();
  }

  toggleTheme() {
    // Permanent Dark Mode for FIELDWORK _OS
    this.isDark = true;
    this.applyTheme();
  }

  private applyTheme() {
    // Force dark class to be present
    document.documentElement.classList.add("dark");
    localStorage.setItem('theme', 'dark');
  }
}
