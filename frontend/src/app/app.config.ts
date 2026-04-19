import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { 
  LucideAngularModule, 
  Home, Menu, User, Settings, AlertTriangle, Hammer, Users, 
  History, ClipboardList, LogOut, ArrowLeft, Clock, MapPin, 
  Wrench, ShieldAlert, Send, Sun, Moon, ChevronsLeft, ChevronsRight,
  LayoutDashboard, Briefcase, Factory, Eye, Globe, Plus, Bell,
  ArrowRight, Camera, Mail, KeyRound, Loader2, CheckSquare, Check, Image as ImageIcon, Tag, X, Radio, Video, Info
} from 'lucide-angular';

import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    importProvidersFrom(
      LucideAngularModule.pick({ 
        Home, Menu, User, Settings, AlertTriangle, Hammer, Users, 
        History, ClipboardList, LogOut, ArrowLeft, Clock, MapPin, 
        Wrench, ShieldAlert, Send, Sun, Moon, ChevronsLeft, ChevronsRight,
        LayoutDashboard, Briefcase, Factory, Eye, Globe, Plus, Bell,
        ArrowRight, Camera, Mail, KeyRound, Loader2, CheckSquare, Check, Image: ImageIcon, Tag, X, Radio, Video, Info
      })
    )
  ]
};
