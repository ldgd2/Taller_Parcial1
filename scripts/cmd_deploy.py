import os
import getpass
import platform

HAS_RICH = False
try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    HAS_RICH = True
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

def do_status(rich_msg, plain_msg, action_lambda):
    if HAS_RICH:
        with console.status(f"[cyan]{rich_msg}[/cyan]", spinner="dots"):
            return action_lambda()
    else:
        print(plain_msg)
        return action_lambda()

def add_subparser(parser):
    parser.add_argument("--domain", default="localhost", help="Dominio para Nginx (ej: api.taller.com)")
    parser.add_argument("--email", default="admin@taller.com", help="Email para supervisor admin del servidor")
    
def execute(args):
    """
    Genera y opcionalmente instala los archivos systemd `.service` 
    y configuraciones Nginx para despliegue en distribuciones Linux (VPS).
    """
    is_windows = platform.system() == "Windows"
    
    panel_print(
        "[bold blue]Preparando Archivos de Despliegue para Produccion Linux...[/bold blue]",
        "Preparando Archivos de Despliegue para Produccion Linux..."
    )
    
    def generate_files():
        cwd = os.getcwd()
        user = getpass.getuser() if not is_windows else "tu_usuario_linux"
        
        backend_service_content = f"""[Unit]
Description=Gunicorn/Uvicorn Daemon para Backend de Taller Movil
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={cwd}/backend
Environment="PATH={cwd}/backend/.venv/bin"
EnvironmentFile={cwd}/backend/.env
ExecStart={cwd}/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
"""

        if not os.path.exists("deploy"):
            os.makedirs("deploy")
            
        with open("deploy/taller-backend.service", "w") as f:
            f.write(backend_service_content)
            
        cprint("[green] -> Generado:[/green] [white]deploy/taller-backend.service[/white]", " -> Generado: deploy/taller-backend.service")
        
        nginx_config = f"""server {{
    listen 80;
    server_name {args.domain};

    location /api/v1/ {{
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}

    location / {{
        root {cwd}/frontend/dist/frontend/browser;
        index index.html;
        try_files $uri $uri/ /index.html;
    }}
}}
"""
        with open("deploy/nginx-taller.conf", "w") as f:
            f.write(nginx_config)
        cprint("[green] -> Generado:[/green] [white]deploy/nginx-taller.conf[/white]", " -> Generado: deploy/nginx-taller.conf")

    do_status("Calculando directorios y generando scripts...", "Calculando directorios y generando scripts...", generate_files)

    if is_windows:
        msg_rich = (
            "[bold yellow]Estas en Windows.[/bold yellow] Copia estos archivos alojados en '/deploy' a tu servidor Linux y metelos en:\n\n"
            "  [dim]Backend:[/dim] [cyan]/etc/systemd/system/taller-backend.service[/cyan]\n"
            "  [dim]Frontend Nginx:[/dim] [cyan]/etc/nginx/sites-available/taller[/cyan]\n\n"
            "Luego en tu servidor ejecuta:\n"
            "  [bold]sudo systemctl daemon-reload[/bold]\n"
            "  [bold]sudo systemctl start taller-backend[/bold]\n"
            "  [bold]sudo systemctl enable taller-backend[/bold]"
        )
        msg_plain = (
            "Estas en Windows. Copia estos archivos alojados en '/deploy' a tu servidor Linux:\n"
            "  Backend: /etc/systemd/system/taller-backend.service\n"
            "  Frontend Nginx: /etc/nginx/sites-available/taller\n\n"
            "Luego en tu servidor ejecuta:\n"
            "  sudo systemctl daemon-reload\n"
            "  sudo systemctl start taller-backend\n"
            "  sudo systemctl enable taller-backend"
        )
        
        if HAS_RICH:
            console.print(Panel(msg_rich, title="Instrucciones para VPS", border_style="yellow"))
        else:
            print("\n--- Instrucciones para VPS ---")
            print(msg_plain)
    else:
        cprint("\n[dim]Para aplicarlos fisicamente en esta maquina Linux, requeriras permisos root.[/dim]\n"
               "[dim]Usa los archivos generados en ./deploy/ copiandolos a /etc/ e invoca systemctl.[/dim]",
               "\nPara aplicarlos fisicamente en esta maquina Linux, requeriras permisos root.\n"
               "Usa los archivos generados en ./deploy/ copiandolos a /etc/ e invoca systemctl.")
