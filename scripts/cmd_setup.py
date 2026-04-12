import os
import subprocess
import platform
import shutil

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
    os.chdir("backend")
    
    if not os.path.exists(".venv"):
        do_status("Creando entorno virtual (.venv)...", "Creando entorno virtual (.venv)...", 
                  lambda: subprocess.run(["python", "-m", "venv", ".venv"], check=True))
            
    is_windows = platform.system() == "Windows"
    pip_cmd = os.path.join(".venv", "Scripts", "pip") if is_windows else os.path.join(".venv", "bin", "pip")
    
    def _install_reqs():
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True, capture_output=True)
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
    do_status("Instalando dependencias de Python (requirements.txt)...", "Instalando dependencias de Python (requirements.txt)...", _install_reqs)
        
    cprint("[bold green]Backend configurado con exito.[/bold green]", "Backend configurado con exito.")
    os.chdir("..")

def setup_frontend():
    os.chdir("frontend")
    
    is_windows = platform.system() == "Windows"
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    cprint("[dim]Esto puede demorar unos minutos... (npm install)[/dim]", "Esto puede demorar unos minutos... (npm install)")
    subprocess.run([npm_cmd, "install"])
    
    cprint("[bold green]Frontend configurado con exito.[/bold green]", "Frontend configurado con exito.")
    os.chdir("..")

def setup_env():
    backend_env = os.path.join("backend", ".env")
    backend_example = os.path.join("backend", ".env.example")
    
    if not os.path.exists(backend_env) and os.path.exists(backend_example):
        cprint("[cyan] Copiando backend/.env.example a backend/.env[/cyan]", "Copiando backend/.env.example a backend/.env")
        shutil.copyfile(backend_example, backend_env)
        cprint("[bold yellow] -> [IMPORTANTE] Recuerda configurar tu 'DATABASE_URL' en backend/.env antes de levantar la App.[/bold yellow]", "-> [IMPORTANTE] Recuerda configurar tu 'DATABASE_URL' en backend/.env antes de levantar la App.")
    elif os.path.exists(backend_env):
        cprint("[dim] -> El archivo backend/.env ya existe. Omitido.[/dim]", "-> El archivo backend/.env ya existe. Omitido.")
