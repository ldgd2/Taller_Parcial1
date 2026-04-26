import os
import platform
import getpass
import socket
import urllib.request
import subprocess
import time

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
            "4. Volver al Menú Principal"
        ]
    ).ask()

    if "Crear" in choice:
        setup_vps_services()
    elif "Verificar" in choice:
        check_services()
    elif "Reiniciar" in choice:
        restart_services()

def setup_vps_services():
    public_ip = get_public_ip()
    cprint(f"[dim]IP Detectada:[/dim] [bold green]{public_ip}[/bold green]", f"IP: {public_ip}")
    
    port_back = questionary.text("Puerto para el servicio BACKEND (FastAPI):", default="8000").ask()
    port_front = questionary.text("Puerto para el servicio FRONTEND (Angular DEV):", default="4200").ask()
    
    cwd = os.getcwd()
    user = getpass.getuser()
    
    if not os.path.exists("deploy"):
        os.makedirs("deploy")

    # --- BACKEND SERVICE (Uvicorn) ---
    backend_svc = f"""[Unit]
Description=Servicio Taller Backend (Dev Mode)
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/backend
Environment="PATH={cwd}/backend/.venv/bin"
EnvironmentFile={cwd}/.env
ExecStart={cwd}/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port {port_back}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-backend.service", "w") as f:
        f.write(backend_svc)

    # --- FRONTEND SERVICE (Angular Dev Server) ---
    # Usamos npm start pasándole host y puerto para que sea accesible externamente
    frontend_svc = f"""[Unit]
Description=Servicio Taller Frontend (Angular Dev)
After=network.target

[Service]
User={user}
WorkingDirectory={cwd}/frontend
ExecStart=/usr/bin/npm start -- --host 0.0.0.0 --port {port_front} --disable-host-check
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-frontend.service", "w") as f:
        f.write(frontend_svc)

    cprint("\n[bold green]✔ Servicios GENERADOS (SIN NGINX) en ./deploy/[/bold green]", "Servicios generados (SIN NGINX).")
    
    if platform.system() != "Windows":
        install = questionary.confirm("¿Deseas instalar y activar estos servicios de ejecución ahora mismo?").ask()
        if install:
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
