import { Injectable, inject } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { ConfigService } from '../config/config.service';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: WebSocket | null = null;
  private messageSubject = new Subject<any>();
  private retryCount = 0;
  private readonly maxRetries = 3;
  private clientId: string | null = null;
  private configService = inject(ConfigService);

  constructor() { }

  connect(clientId: string): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.clientId = clientId;
    const wsUrl = this.configService.apiUrl.replace('http', 'ws') + '/ws/' + clientId;
    
    console.log(`📡 Attempting WebSocket connection to: ${wsUrl}`);
    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log('WebSocket connected ✅');
      this.retryCount = 0;
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.messageSubject.next(data);
      } catch (e) {
        console.error('Error parsing socket message:', e);
      }
    };

    this.socket.onclose = (event) => {
      console.warn(`WebSocket closed. Code: ${event.code}, Reason: ${event.reason}`);
      
      if (this.clientId && this.retryCount < this.maxRetries) {
        this.retryCount++;
        const delay = Math.pow(2, this.retryCount) * 2000; // 4s, 8s, 16s...
        console.log(`🔄 Reconnecting in ${delay/1000}s... (Attempt ${this.retryCount}/${this.maxRetries})`);
        setTimeout(() => {
          if (this.clientId) this.connect(this.clientId);
        }, delay);
      } else {
        console.error('❌ Max reconnection retries reached or manual disconnect.');
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error details:', error);
    };
  }

  disconnect(): void {
    this.clientId = null;
    if (this.socket) {
      this.socket.onclose = null; // Prevent auto-reconnect
      this.socket.close();
      this.socket = null;
      console.log('WebSocket manually disconnected 🔌');
    }
  }

  getMessages(): Observable<any> {
    return this.messageSubject.asObservable();
  }
}
