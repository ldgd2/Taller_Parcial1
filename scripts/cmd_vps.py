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
    
    port_back = questionary.text("Puerto para el servicio BACKEND:", default="8000").ask()
    port_front = questionary.text("Puerto para el servicio FRONTEND (Nginx):", default="80").ask()
    
    cwd = os.getcwd()
    user = getpass.getuser()
    
    if not os.path.exists("deploy"):
        os.makedirs("deploy")

    # --- BACKEND SERVICE ---
    backend_svc = f"""[Unit]
Description=Servicio Taller Backend (Auto-Restart)
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={cwd}/backend
Environment="PATH={cwd}/backend/.venv/bin"
EnvironmentFile={cwd}/.env
ExecStart={cwd}/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port {port_back} --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-backend.service", "w") as f:
        f.write(backend_svc)

    # --- FRONTEND NGINX ---
    nginx_conf = f"""server {{
    listen {port_front};
    server_name {public_ip};

    location /api/v1/ {{
        proxy_pass http://localhost:{port_back};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}

    location / {{
        root {cwd}/frontend/dist/frontend/browser;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}
}}
"""
    with open("deploy/taller-nginx.conf", "w") as f:
        f.write(nginx_conf)

    cprint("\n[bold green]✔ Archivos de servicio generados en ./deploy/[/bold green]", "Archivos generados en ./deploy/")
    
    if platform.system() != "Windows":
        install = questionary.confirm("¿Deseas intentar instalar los servicios automáticamente en este sistema Linux?").ask()
        if install:
            os.system(f"sudo cp {cwd}/deploy/taller-backend.service /etc/systemd/system/")
            os.system(f"sudo cp {cwd}/deploy/taller-nginx.conf /etc/nginx/sites-available/taller")
            os.system("sudo ln -sf /etc/nginx/sites-available/taller /etc/nginx/sites-enabled/")
            os.system("sudo systemctl daemon-reload")
            os.system("sudo systemctl enable taller-backend")
            os.system("sudo systemctl restart taller-backend")
            os.system("sudo systemctl restart nginx")
            cprint("[bold green]🚀 Servicios instalados y levantados con éxito.[/bold green]", "Servicios instalados.")
    else:
        cprint("[yellow]⚠ Estás en Windows.[/yellow] Copia los archivos de ./deploy/ a tu VPS y ejecútalos con systemctl.", "Copia los archivos a tu VPS.")

def check_services():
    if platform.system() == "Windows":
        cprint("[red]Esta opción solo funciona en Linux/VPS.[/red]", "Solo Linux.")
        return
    
    os.system("clear")
    cprint("[bold cyan]ESTADO DE SERVICIOS[/bold cyan]", "ESTADO DE SERVICIOS")
    os.system("systemctl status taller-backend --no-pager")
    os.system("systemctl status nginx --no-pager")
    input("\nPresiona Enter para continuar...")

def restart_services():
    if platform.system() == "Windows":
        cprint("[red]Esta opción solo funciona en Linux/VPS.[/red]", "Solo Linux.")
        return
    
    cprint("[yellow]Reiniciando servicios...[/yellow]", "Reiniciando...")
    os.system("sudo systemctl restart taller-backend")
    os.system("sudo systemctl restart nginx")
    cprint("[bold green]✔ Reiniciado.[/bold green]", "Reiniciado.")
    time.sleep(2)
