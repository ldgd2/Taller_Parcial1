import os
import platform
import getpass
import socket
import urllib.request
import subprocess
import time
import sys

HAS_RICH = False
HAS_QUESTIONARY = False
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    pass

def cprint(rich_msg, plain_msg):
    if HAS_RICH:
        console.print(rich_msg)
    else:
        print(plain_msg)

def get_public_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        return "localhost"

def interactive_menu():
    if not HAS_QUESTIONARY:
        print("[!] Questionary no está instalado.")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    cprint("[bold magenta]🛰  GESTIÓN DE SERVICIOS VPS (AUTO-RESTART)[/bold magenta]", "GESTIÓN DE SERVICIOS VPS (AUTO-RESTART)")
    
    choice = questionary.select(
        "¿Qué acción deseas realizar en el VPS?",
        choices=[
            "1. Crear Servicios Systemd (Backend/Frontend)",
            "2. Verificar Estado de Servicios (Solo Linux)",
            "3. Reiniciar Todos los Servicios (Solo Linux)",
            "4. Eliminar Servicios Systemd (Solo Linux)",
            "5. Ver Logs en Tiempo Real (Backend)",
            "6. Ver Logs en Tiempo Real (Frontend)",
            "7. Editar IP y Puertos (.env + Sync)",
            "8. Volver al Menú Principal"
        ]
    ).ask()

    if choice is None:
        return
    
    if "Crear" in choice:
        setup_vps_services()
    elif "Verificar" in choice:
        check_services()
    elif "Reiniciar" in choice:
        restart_services()
    elif "Eliminar" in choice:
        delete_services()
    elif "Logs" in choice and "Backend" in choice:
        view_logs("backend")
    elif "Logs" in choice and "Frontend" in choice:
        view_logs("frontend")
    elif "Editar" in choice:
        edit_network_config()

def edit_network_config():
    public_ip = get_public_ip()
    cprint(f"[dim]IP Detectada:[/dim] [bold green]{public_ip}[/bold green]", f"IP: {public_ip}")
    
    port_back = questionary.text("Nuevo puerto para BACKEND:", default="8000").ask()
    
    update_env_file(public_ip, port_back)
    sync_env_to_angular(public_ip, port_back)
    
    cprint("[bold green]✔ Configuración de red actualizada y sincronizada.[/bold green]", "Configuración actualizada.")
    time.sleep(2)

def setup_vps_services():
    public_ip = get_public_ip()
    cprint(f"[dim]IP Detectada:[/dim] [bold green]{public_ip}[/bold green]", f"IP: {public_ip}")
    
    port_back = questionary.text("Puerto para el servicio BACKEND (FastAPI):", default="8000").ask()
    port_front = questionary.text("Puerto para el servicio FRONTEND (Angular DEV):", default="4200").ask()
    
    # 1. Actualizar .env con los nuevos valores
    update_env_file(public_ip, port_back)
    
    # 2. Sincronizar con Angular environment.ts
    sync_env_to_angular(public_ip, port_back)

    cwd = os.getcwd()
    user = getpass.getuser()
    python_exe = sys.executable
    
    if not os.path.exists("deploy"):
        os.makedirs("deploy")
    
    # ... rest of the service generation ...
    backend_svc = f"""[Unit]
Description=Servicio Taller Backend (Dev Mode)
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/backend
EnvironmentFile={cwd}/.env
ExecStart={python_exe} -m uvicorn main:app --host 0.0.0.0 --port {port_back}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-backend.service", "w") as f:
        f.write(backend_svc)

    frontend_svc = f"""[Unit]
Description=Servicio Taller Frontend (Angular Dev)
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/frontend
ExecStartPre={python_exe} {cwd}/scripts/sync_env.py
ExecStart=/usr/bin/npm start -- --host 0.0.0.0 --port {port_front} --disable-host-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-frontend.service", "w") as f:
        f.write(frontend_svc)

    cprint("\n[bold green]✔ Servicios GENERADOS e .env Sincronizado.[/bold green]", "Servicios generados.")
    
    if platform.system() != "Windows":
        install = questionary.confirm("¿Deseas instalar y activar estos servicios de ejecución ahora mismo?").ask()
        if install:
            os.system("sudo systemctl stop taller-backend taller-frontend 2>/dev/null")
            os.system("sudo systemctl disable taller-backend taller-frontend 2>/dev/null")
            os.system(f"sudo cp {cwd}/deploy/taller-backend.service /etc/systemd/system/")
            os.system(f"sudo cp {cwd}/deploy/taller-frontend.service /etc/systemd/system/")
            os.system("sudo systemctl daemon-reload")
            os.system("sudo systemctl enable taller-backend taller-frontend")
            os.system("sudo systemctl restart taller-backend taller-frontend")
            cprint("[bold green]🚀 Servicios levantados en modo DEV.[/bold green]", "Servicios levantados.")
            cprint(f"[bold cyan]Backend:[/bold cyan] http://{public_ip}:{port_back}", f"Backend: {public_ip}:{port_back}")
            cprint(f"[bold cyan]Frontend:[/bold cyan] http://{public_ip}:{port_front}", f"Frontend: {public_ip}:{port_front}")
    else:
        cprint("[yellow]⚠ Instrucciones:[/yellow] Copia los archivos de ./deploy/ a /etc/systemd/system/ en tu Ubuntu.", "Copia los archivos a /etc/systemd/system/.")

def update_env_file(ip, port):
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()
    
    # Filtrar lineas antiguas
    lines = [l for l in lines if not l.startswith("APP_HOST=") and not l.startswith("APP_PORT_BACKEND=")]
    lines.append(f"APP_HOST={ip}\n")
    lines.append(f"APP_PORT_BACKEND={port}\n")
    
    with open(".env", "w") as f:
        f.writelines(lines)
    cprint("[green]✔ Archivo .env actualizado con la IP y Puerto.[/green]", ".env actualizado.")

def sync_env_to_angular(ip, port):
    config_path = "frontend/src/assets/config.json"
    import json
    config = {
        "apiUrl": f"http://{ip}:{port}/api/v1"
    }
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    cprint(f"[green]✔ Assets/config.json sincronizado con Backend en {ip}:{port}[/green]", "Config.json sincronizado.")

def check_services():
    if platform.system() == "Windows":
        cprint("[red]Esta opción solo funciona en Linux/VPS.[/red]", "Solo Linux.")
        return
    
    os.system("clear")
    cprint("[bold cyan]ESTADO DE LOS DAEMONS DE EJECUCIÓN[/bold cyan]", "ESTADO DE SERVICIOS")
    os.system("systemctl status taller-backend --no-pager")
    print("-" * 30)
    os.system("systemctl status taller-frontend --no-pager")
    input("\nPresiona Enter para continuar...")

def restart_services():
    if platform.system() == "Windows":
        cprint("[red]Esta opción solo funciona en Linux/VPS.[/red]", "Solo Linux.")
        return
    
    cprint("[yellow]Reiniciando servicios de ejecución...[/yellow]", "Reiniciando...")
    os.system("sudo systemctl restart taller-backend taller-frontend")
    cprint("[bold green]✔ Servicios reiniciados.[/bold green]", "Reiniciado.")
    time.sleep(2)

def delete_services():
    if platform.system() == "Windows":
        cprint("[red]Esta opción solo funciona en Linux/VPS.[/red]", "Solo Linux.")
        return
    
    confirm = questionary.confirm("¿Estás seguro de detener y eliminar los servicios taller-backend y taller-frontend?").ask() if HAS_QUESTIONARY else True
    if not confirm:
        return
        
    cprint("[yellow]Deteniendo y eliminando servicios...[/yellow]", "Eliminando...")
    os.system("sudo systemctl stop taller-backend taller-frontend 2>/dev/null")
    os.system("sudo systemctl disable taller-backend taller-frontend 2>/dev/null")
    os.system("sudo rm -f /etc/systemd/system/taller-backend.service")
    os.system("sudo rm -f /etc/systemd/system/taller-frontend.service")
    os.system("sudo systemctl daemon-reload")
    cprint("[bold green]✔ Servicios eliminados correctamente del sistema.[/bold green]", "Servicios eliminados.")
    time.sleep(2)

def view_logs(target):
    if platform.system() == "Windows":
        cprint("[red]Esta opción solo funciona en Linux/VPS.[/red]", "Solo Linux.")
        return
    
    cprint(f"[bold cyan]Mostrando logs en TIEMPO REAL de taller-{target} (Presiona Ctrl+C para salir)[/bold cyan]", f"Logs de {target}")
    try:
        os.system(f"sudo journalctl -u taller-{target}.service -f -n 100")
    except KeyboardInterrupt:
        pass
    print()
