import os
import subprocess
import platform
import shutil
import sys

HAS_RICH = False
try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

def cprint(rich_msg, plain_msg):
    if HAS_RICH:
        console.print(rich_msg)
    else:
        print(plain_msg)

def do_status(rich_msg, plain_msg, action_lambda):
    if HAS_RICH:
        with console.status(f"[cyan]{rich_msg}[/cyan]", spinner="dots"):
            action_lambda()
    else:
        print(plain_msg)
        action_lambda()

def add_subparser(parser):
    subparsers = parser.add_subparsers(dest="target")
    subparsers.required = True
    
    subparsers.add_parser("backend", help="Instala el venv y Dependencias del Backend")
    subparsers.add_parser("frontend", help="Instala node_modules en Frontend")
    subparsers.add_parser("all", help="Configura todo (Backend y Frontend)")
    subparsers.add_parser("env", help="Copia .env.example a .env si no existe")

def execute(args):
    target = args.target

    if target in ("backend", "all"):
        cprint("\n[bold cyan]--- Configurando Backend ---[/bold cyan]", "\n--- Configurando Backend ---")
        setup_backend()
        
    if target in ("frontend", "all"):
        cprint("\n[bold magenta]--- Configurando Frontend ---[/bold magenta]", "\n--- Configurando Frontend ---")
        setup_frontend()

    if target in ("env", "all"):
        cprint("\n[bold yellow]--- Configurando Variables de Entorno ---[/bold yellow]", "\n--- Configurando Variables de Entorno ---")
        setup_env()

def setup_backend():
    # Ya no entramos en backend/ para crear un venv nuevo.
    # Usamos el entorno actual (sys.executable) que ya tiene el usuario activo.
    
    pip_cmd = [sys.executable, "-m", "pip"]
    
    def _install_reqs():
        # Intentamos actualizar pip, pero no morimos si falla (común en Windows si está en uso)
        try:
            subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=False, capture_output=True)
        except:
            pass
            
        # Instalamos los requerimientos en el entorno activo
        subprocess.run([*pip_cmd, "install", "-r", os.path.join("backend", "requirements.txt")], check=True)
        
    do_status("Sincronizando dependencias en el entorno activo...", "Sincronizando dependencias...", _install_reqs)
        
    cprint("[bold green]Entorno único sincronizado con éxito.[/bold green]", "Entorno sincronizado.")

def setup_frontend():
    os.chdir("frontend")
    
    is_windows = platform.system() == "Windows"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    cprint("[dim]Esto puede demorar unos minutos... (npm install)[/dim]", "Esto puede demorar unos minutos... (npm install)")
    subprocess.run([npm_cmd, "install"])
    
    cprint("[bold green]Frontend configurado con exito.[/bold green]", "Frontend configurado con exito.")
    os.chdir("..")

def setup_env():
    root_env = ".env"
    backend_example = os.path.join("backend", ".env.example")
    
    if not os.path.exists(root_env) and os.path.exists(backend_example):
        cprint("[cyan] Copiando backend/.env.example a .env en la raíz[/cyan]", "Copiando backend/.env.example a .env en la raíz")
        shutil.copyfile(backend_example, root_env)
        generate_secret_keys(root_env)
    elif os.path.exists(root_env):
        cprint("[dim] -> El archivo .env ya existe en la raíz.[/dim]", "-> El archivo .env ya existe en la raíz.")
        generate_secret_keys(root_env)

def generate_secret_keys(env_path):
    """Genera llaves secretas seguras si detecta valores por defecto."""
    import secrets
    
    if not os.path.exists(env_path):
        return
        
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("SECRET_KEY=") and ("cambia_esto" in line or "secret_key_placeholder" in line):
            new_key = secrets.token_hex(32)
            lines[i] = f"SECRET_KEY={new_key}\n"
            updated = True
            cprint(f"[bold green] -> [OK] Generada nueva SECRET_KEY segura.[/bold green]", "Generada nueva SECRET_KEY.")
            
    if updated:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

def interactive_menu():
    """Interfaz interactiva delegada para Setup."""
    import questionary
    import argparse
    
    opt = questionary.select(
        "¿Qué deseas instalar/configurar?",
        choices=["Backend (Python Venv/Reqs)", "Frontend (Node Modules)", "Env (Crear .env inicial)", "All (Instalación completa)", "Volver"]
    ).ask()
    
    if opt == "Volver" or opt is None:
        return
        
    target = opt.split()[0].lower()
    execute(argparse.Namespace(target=target))
    input("\nPresiona Enter para continuar...")
