import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule],
  template: `
    <div class="min-h-screen bg-[#0a0a0a] text-white selection:bg-[#FF5733] selection:text-white font-sans overflow-x-hidden">
      
      <!-- TOP NAVIGATION -->
      <nav class="border-b border-[#222222] bg-[#0a0a0a]/90 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-[1600px] mx-auto px-6 h-20 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2.5 h-2.5 bg-[#FF5733]"></div>
            <span class="font-mono text-xs font-bold tracking-widest uppercase text-white">FIELDWORK <span class="text-zinc-600">_OS</span></span>
          </div>
          <div class="flex items-center gap-4">
            <button (click)="irALogin()" class="bg-white text-black px-6 py-2.5 font-bold text-[9px] tracking-widest uppercase hover:bg-zinc-200 transition-colors">
              ACCESO AL SISTEMA
            </button>
            <button class="w-10 h-10 border border-[#222222] flex items-center justify-center text-zinc-400 hover:text-white hover:border-white transition-all">
              <lucide-icon name="sun" size="16"></lucide-icon>
            </button>
          </div>
        </div>
      </nav>

      <!-- HERO SECTION -->
      <main class="relative px-6 py-24 lg:py-32 max-w-[1600px] mx-auto">
         <!-- BG glow decorative -->
         <div class="absolute top-0 left-1/4 w-[500px] h-[500px] bg-[#FF5733]/5 blur-[120px] rounded-full pointer-events-none"></div>

         <div class="max-w-4xl relative z-10">
           <div class="inline-flex items-center gap-3 px-3 py-1.5 border border-[#222222] bg-[#111111] mb-8">
             <div class="w-1.5 h-1.5 bg-[#FF5733]"></div>
             <span class="font-mono text-[9px] font-bold uppercase tracking-[.25em] text-zinc-300">SISTEMA DE DESPACHO ACTIVO</span>
           </div>
           
           <h1 class="text-5xl md:text-6xl lg:text-[80px] font-extrabold tracking-tighter uppercase leading-[0.95] mb-8 text-white">
             LA EMERGENCIA NO<br/>ESPERA. TU TALLER<br/>TAMPOCO.
           </h1>
           
           <p class="text-zinc-400 text-base md:text-lg lg:text-xl max-w-2xl leading-relaxed mb-12">
             FieldWork es el entorno de alta precisión para gestores de talleres mecánicos. Recibe incidencias en tiempo real, evalúa la criticidad y asigna técnicos antes de que el motor se enfríe.
           </p>
           
           <div class="flex flex-col sm:flex-row gap-4">
             <button (click)="irALogin()" class="bg-[#FF5733] text-white px-8 py-4 font-bold text-[11px] uppercase tracking-[.2em] shadow-lg shadow-[#FF5733]/20 hover:brightness-110 transition-all flex items-center justify-center gap-3">
               INICIAR SESIÓN <lucide-icon name="arrow-right" size="14"></lucide-icon>
             </button>
             <button class="bg-transparent border border-[#333333] text-white px-8 py-4 font-bold text-[11px] uppercase tracking-[.2em] hover:bg-[#111111] transition-all flex items-center justify-center">
               VER DOCUMENTACIÓN
             </button>
           </div>
         </div>
      </main>

      <!-- PROCESS SECTION -->
      <section class="border-t border-b border-[#222222] bg-[#0a0a0a]">
        <div class="max-w-[1600px] mx-auto px-6 py-32">
          <div class="mb-20">
            <span class="font-mono text-[10px] uppercase tracking-[.25em] text-[#FF5733] font-bold block mb-4">EL PROCESO</span>
            <h2 class="text-4xl md:text-5xl font-extrabold tracking-tight uppercase text-white">DEL CAMPO AL TALLER EN SEGUNDOS.</h2>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-0 border border-[#222222]">
            <!-- Step 1 -->
            <div class="p-10 md:p-14 border-b md:border-b-0 md:border-r border-[#222222] bg-[#0d0d0d] hover:bg-[#111111] transition-colors">
               <div class="w-12 h-12 border border-[#333333] flex items-center justify-center mb-8">
                 <lucide-icon name="camera" size="18" class="text-[#FF5733]"></lucide-icon>
               </div>
               <h3 class="text-xl font-bold mb-4 tracking-tight">1. Captura del Problema</h3>
               <p class="text-zinc-500 text-sm leading-relaxed">
                 El cliente registra la emergencia mediante una simple foto y descripción. El sistema extrae los metadatos y ubica la incidencia en tiempo real.
               </p>
            </div>
            <!-- Step 2 -->
            <div class="p-10 md:p-14 border-b md:border-b-0 md:border-r border-[#222222] bg-[#0c0c0c] hover:bg-[#111111] transition-colors">
               <div class="w-12 h-12 border border-[#333333] flex items-center justify-center mb-8">
                 <lucide-icon name="alert-triangle" size="18" class="text-[#FF5733]"></lucide-icon>
               </div>
               <h3 class="text-xl font-bold mb-4 tracking-tight">2. Evaluación de Prioridad</h3>
               <p class="text-zinc-500 text-sm leading-relaxed">
                 FieldWork cataloga automáticamente el nivel de urgencia, desde una revisión rutinaria hasta una falla catastrófica (Código Rojo).
               </p>
            </div>
            <!-- Step 3 -->
            <div class="p-10 md:p-14 bg-[#0a0a0a] hover:bg-[#111111] transition-colors">
               <div class="w-12 h-12 border border-[#333333] flex items-center justify-center mb-8">
                 <lucide-icon name="check-square" size="18" class="text-[#FF5733]"></lucide-icon>
               </div>
               <h3 class="text-xl font-bold mb-4 tracking-tight">3. Asignación Directa</h3>
               <p class="text-zinc-500 text-sm leading-relaxed">
                 El gestor de taller toma la emergencia desde el tablero. Todo el contexto técnico se envía inmediatamente a la tableta del mecánico encargado.
               </p>
            </div>
          </div>
        </div>
      </section>

      <!-- TRANSFORMATION SECTION -->
      <section class="max-w-[1600px] mx-auto px-6 py-32 grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
        <div>
          <span class="font-mono text-[10px] uppercase tracking-[.25em] text-[#FF5733] font-bold block mb-4">TRANSFORMACIÓN</span>
          <h2 class="text-4xl md:text-5xl font-extrabold tracking-tight uppercase leading-tight mb-8 text-white">DE CAOS AL CONTROL MILIMÉTRICO.</h2>
          <p class="text-zinc-400 text-lg leading-relaxed mb-12">
             Olvida las notas escritas a mano, los mensajes de voz incomprensibles y las fotos borrosas. FieldWork estructura el desastre en un expediente técnico inmutable.
          </p>
          
          <ul class="space-y-6">
            <li class="flex items-center gap-4 text-zinc-300">
               <lucide-icon name="check" size="18" class="text-[#FF5733]"></lucide-icon>
               <span class="font-medium tracking-wide">Estandarización de partes afectadas</span>
            </li>
            <li class="flex items-center gap-4 text-zinc-300">
               <lucide-icon name="check" size="18" class="text-[#FF5733]"></lucide-icon>
               <span class="font-medium tracking-wide">Registro de tiempo hasta resolución</span>
            </li>
            <li class="flex items-center gap-4 text-zinc-300">
               <lucide-icon name="check" size="18" class="text-[#FF5733]"></lucide-icon>
               <span class="font-medium tracking-wide">Exportación a formatos de aseguradoras</span>
            </li>
          </ul>
        </div>
        
        <!-- VISUAL CUES: ANTES vs DESPUES -->
        <div class="border border-[#222222] bg-[#0c0c0c] flex flex-col md:flex-row">
           <!-- ANTES -->
           <div class="flex-1 p-8 border-b md:border-b-0 md:border-r border-[#222222] relative overflow-hidden bg-[#0d0d0d] min-h-[350px]">
              <span class="absolute top-4 left-4 bg-red-950/50 text-red-500 border border-red-900/50 px-2 py-0.5 text-[8px] font-bold uppercase tracking-widest font-mono">ANTES</span>
              
              <!-- Messy Mockups -->
              <div class="mt-12 opacity-40 rotate-[15deg] translate-y-10 translate-x-4">
                 <div class="bg-[#1a1512] border border-[#ff8c00]/20 w-48 h-32 p-4 rounded-sm shadow-xl absolute z-10 -left-10">
                    <div class="w-full h-2 bg-[#ff8c00]/20 mb-3 rounded-full"></div>
                    <div class="w-3/4 h-2 bg-[#ff8c00]/20 mb-3 rounded-full"></div>
                    <div class="w-1/2 h-2 bg-[#ff8c00]/20 rounded-full"></div>
                 </div>
                 <div class="bg-[#151515] border border-[#666] w-32 h-44 rounded-sm shadow-2xl relative z-20 left-16 top-10 flex items-center justify-center">
                    <lucide-icon name="image" class="text-zinc-700" size="32"></lucide-icon>
                 </div>
              </div>
           </div>
           
           <!-- DESPUES -->
           <div class="flex-1 p-8 relative min-h-[350px] bg-[#0a0a0a]">
              <span class="absolute top-4 left-4 bg-[#FF5733]/10 text-[#FF5733] border border-[#FF5733]/20 px-2 py-0.5 text-[8px] font-bold uppercase tracking-widest font-mono">DESPUÉS</span>
              
              <!-- Clean Mockup -->
              <div class="mt-12 bg-[#111111] border border-[#333333] w-full max-w-[240px] shadow-2xl mx-auto rounded-sm p-4 flex flex-col gap-4">
                 <div class="flex justify-between items-center border-b border-[#222222] pb-3">
                    <div class="w-16 h-2 bg-zinc-400 rounded-full"></div>
                    <div class="w-8 h-2 bg-[#FF5733] rounded-sm"></div>
                 </div>
                 <div class="flex gap-4">
                    <div class="w-12 h-16 bg-[#1a1a1a] rounded-sm border border-[#222222]"></div>
                    <div class="flex-1 space-y-2 pt-1">
                       <div class="w-full h-2 bg-zinc-700/50 rounded-full"></div>
                       <div class="w-2/3 h-2 bg-zinc-700/50 rounded-full"></div>
                    </div>
                 </div>
                 <div class="border-t border-[#222222] pt-4 mt-2 grid grid-cols-2 gap-2">
                    <div class="h-1.5 bg-[#222222] rounded-full"></div>
                    <div class="h-1.5 bg-[#222222] rounded-full"></div>
                 </div>
              </div>
           </div>
        </div>
      </section>

      <!-- PRE-FOOTER / CTA -->
      <footer class="border-t border-[#222222] py-16 px-6 flex flex-col items-center justify-center bg-[#050505]">
         <div class="w-3 h-3 bg-[#FF5733] mb-6"></div>
         <h2 class="text-zinc-500 font-mono text-[10px] tracking-[.3em] uppercase mb-4 text-center">Protocolo Operacional Preparado</h2>
         <p class="text-zinc-700 text-xs mb-8 text-center uppercase tracking-widest">_OS_ONLINE / SYSTEMS_NOMINAL</p>
         <button (click)="irALogin()" class="text-zinc-400 border-b border-[#FF5733] pb-1 hover:text-[#FF5733] transition-colors text-[10px] uppercase tracking-[.2em] font-bold">ACCEDER A TERMINAL -></button>
      </footer>
    </div>
  `
})
export class HomeComponent {
  constructor(private router: Router) {}

  irALogin() {
    this.router.navigate(['/auth/login']);
  }
}
