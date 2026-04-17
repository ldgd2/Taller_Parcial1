import os
import secrets

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

def process_input(rich_msg, plain_msg):
    if HAS_RICH:
        return console.input(f"[bold cyan]{rich_msg}[/bold cyan]: ")
    else:
        return input(f"{plain_msg}: ")

def add_subparser(parser):
    subparsers = parser.add_subparsers(dest="target")
    subparsers.required = True
    
    subparsers.add_parser("db", help="Configura interactivamente las credenciales de PostgreSQL")
    subparsers.add_parser("jwt", help="Genera dinamicamente un SECRET_KEY seguro para JWT")
    subparsers.add_parser("all", help="Configura todo interactivamente")

def update_env_variable(filepath, key, new_value):
    if not os.path.exists(filepath):
        cprint(f"[bold red]ERROR: No existe {filepath}[/bold red]", f"ERROR: No existe {filepath}")
        return

    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={new_value}\n"
            found = True
            break
            
    if not found:
        lines.append(f"{key}={new_value}\n")
        
    with open(filepath, 'w') as f:
        f.writelines(lines)

def config_db():
    env_file = ".env"
    if not os.path.exists(env_file):
        cprint("[bold red]Primero debes correr: python taller.py setup env[/bold red]", "Primero debes correr: python taller.py setup env")
        return
        
    cprint("\n[bold magenta]--- CONFIGURACION INDEPENDIENTE DE BASE DE DATOS ---[/bold magenta]", "\n--- CONFIGURACION INDEPENDIENTE DE BASE DE DATOS ---")
    user = process_input("Usuario (DB_USER, default: postgres)", "Usuario (DB_USER, default: postgres)") or "postgres"
    password = process_input("Contrasena (DB_PASSWORD, default: root)", "Contrasena (DB_PASSWORD, default: root)") or "root"
    host = process_input("Host (DB_HOST, default: localhost)", "Host (DB_HOST, default: localhost)") or "localhost"
    port = process_input("Puerto (DB_PORT, default: 5432)", "Puerto (DB_PORT, default: 5432)") or "5432"
    dbname = process_input("Nombre DB (DB_NAME, default: taller_db)", "Nombre DB (DB_NAME, default: taller_db)") or "taller_db"
    
    # Guardamos cada variable por separado para mayor limpieza
    update_env_variable(env_file, "DB_USER", user)
    update_env_variable(env_file, "DB_PASSWORD", password)
    update_env_variable(env_file, "DB_HOST", host)
    update_env_variable(env_file, "DB_PORT", port)
    update_env_variable(env_file, "DB_NAME", dbname)
    
    cprint(f"[bold green]Configuracion de Base de Datos guardada por componentes.[/bold green]", "Configuracion Guardada.")

def config_jwt():
    env_file = ".env"
    if not os.path.exists(env_file):
        cprint("[bold red]Primero debes correr: python taller.py setup env[/bold red]", "Primero debes correr: python taller.py setup env")
        return
        
    cprint("\n[bold magenta]--- GENERADOR JWT SECRET KEY ---[/bold magenta]", "\n--- GENERADOR JWT SECRET KEY ---")
    genrate = process_input("Generar una nueva llave segura aleatoria? (S/n)", "Generar una nueva llave segura aleatoria? (S/n)")
    
    if genrate.lower() != 'n':
        new_secret = secrets.token_hex(32)
        update_env_variable(env_file, "SECRET_KEY", new_secret)
        cprint(f"[bold green]Nueva llave generada y guardada exitosamente.[/bold green]", "Nueva llave generada y guardada exitosamente.")

def execute(args):
    target = args.target

    if target in ("db", "all"):
        config_db()
        
    if target in ("jwt", "all"):
        config_jwt()

def interactive_menu():
    """Interfaz interactiva delegada para Config."""
    import questionary
    import argparse
    
    opt = questionary.select(
        "Operación de Config:",
        choices=["DB (Credenciales PostgreSQL)", "JWT (Secret Key)", "All (Configuración completa)", "Volver"]
    ).ask()
    
    if opt == "Volver" or opt is None:
        return
        
    target = opt.split()[0].lower()
    execute(argparse.Namespace(target=target))
    input("\nPresiona Enter para continuar...")
