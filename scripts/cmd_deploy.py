import os
import getpass
import platform
import socket
import urllib.request

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

def panel_print(rich_content, plain_content, border="blue"):
    if HAS_RICH:
        console.print(Panel(rich_content, border_style=border))
    else:
        print("-" * 40)
        print(plain_content)
        print("-" * 40)

def get_public_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"

def add_subparser(parser):
    parser.add_argument("--domain", help="Dominio o IP del servidor")
    parser.add_argument("--port-backend", type=int, default=8000, help="Puerto para el backend")
    parser.add_argument("--port-frontend", type=int, default=80, help="Puerto para el frontend")

def interactive_menu():
    if not HAS_QUESTIONARY:
        print("[!] Questionary no está instalado. Ejecuta 'pip install questionary'")
        return

    panel_print(
        "[bold cyan]MODULO DE DESPLIEGUE (Ubuntu/VPS)[/bold cyan]",
        "MODULO DE DESPLIEGUE (Ubuntu/VPS)"
    )

    public_ip = get_public_ip()
    cprint(f"[dim]IP Detectada automáticamente:[/dim] [bold green]{public_ip}[/bold green]", f"IP Detectada: {public_ip}")

    port_backend = questionary.text("¿En qué puerto quieres correr el BACKEND?", default="8000").ask()
    port_frontend = questionary.text("¿En qué puerto quieres correr el FRONTEND (Nginx)?", default="80").ask()
    domain = questionary.text("¿Dominio o IP para el servidor? (Enter para usar la IP detectada)", default=public_ip).ask()

    execute_logic(domain, int(port_backend), int(port_frontend))

def execute(args):
    execute_logic(args.domain or get_public_ip(), args.port_backend, args.port_frontend)

def execute_logic(domain, port_backend, port_frontend):
    is_windows = platform.system() == "Windows"
    cwd = os.getcwd()
    # En Linux, solemos querer el usuario real si no es root
    user = getpass.getuser() if not is_windows else "ubuntu"
    
    if not os.path.exists("deploy"):
        os.makedirs("deploy")

    # --- Generar Servicio Backend ---
    backend_service = f"""[Unit]
Description=Backend FastAPI - Taller Movil
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={cwd}/backend
Environment="PATH={cwd}/backend/.venv/bin"
EnvironmentFile={cwd}/.env
ExecStart={cwd}/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port {port_backend} --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
"""
    with open("deploy/taller-backend.service", "w") as f:
        f.write(backend_service)
    cprint(f"[green]✔[/green] Generado: [white]deploy/taller-backend.service[/white] (Puerto {port_backend})", f"Generado: deploy/taller-backend.service (Puerto {port_backend})")

    # --- Generar Configuración Nginx ---
    nginx_config = f"""server {{
    listen {port_frontend};
    server_name {domain};

    # Backend API
    location /api/v1/ {{
        proxy_pass http://localhost:{port_backend};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}

    # Frontend Angular
    location / {{
        root {cwd}/frontend/dist/frontend/browser;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}
}}
"""
    with open("deploy/taller-nginx.conf", "w") as f:
        f.write(nginx_config)
    cprint(f"[green]✔[/green] Generado: [white]deploy/taller-nginx.conf[/white] (Puerto {port_frontend})", f"Generado: deploy/taller-nginx.conf (Puerto {port_frontend})")

    # --- Mostrar Instrucciones ---
    instructions = f"""
[bold yellow]INSTRUCCIONES PARA TU VPS (UBUNTU):[/bold yellow]

1. Copia los archivos a sus carpetas correspondientes:
   [cyan]sudo cp {cwd}/deploy/taller-backend.service /etc/systemd/system/[/cyan]
   [cyan]sudo cp {cwd}/deploy/taller-nginx.conf /etc/nginx/sites-available/taller[/cyan]

2. Activa el sitio en Nginx y reinicia:
   [cyan]sudo ln -s /etc/nginx/sites-available/taller /etc/nginx/sites-enabled/[/cyan]
   [cyan]sudo nginx -t && sudo systemctl restart nginx[/cyan]

3. Inicia el servicio del Backend:
   [cyan]sudo systemctl daemon-reload[/cyan]
   [cyan]sudo systemctl enable taller-backend[/cyan]
   [cyan]sudo systemctl start taller-backend[/cyan]

[bold green]Proyecto configurado para responder en: http://{domain}:{port_frontend}[/bold green]
"""
    panel_print(instructions, instructions, border="yellow")
