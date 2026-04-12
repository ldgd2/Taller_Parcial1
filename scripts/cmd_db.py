import os
import subprocess
import platform

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
    
    subparsers.add_parser("init", help="Crea todas las tablas directamente (sin Alembic)")
    subparsers.add_parser("seed", help="Rellena la base de datos con informacion base")
    
    parser_migrate = subparsers.add_parser("migrate", help="Autogenera un script de migracion Alembic")
    parser_migrate.add_argument("-m", "--message", required=True, help="Mensaje para documentar la migracion")
    
    subparsers.add_parser("upgrade", help="Aplica las migraciones Alembic pendientes a la Base de Datos")

def execute(args):
    target = args.target

    is_windows = platform.system() == "Windows"
    python_cmd = os.path.join(".venv", "Scripts", "python") if is_windows else os.path.join(".venv", "bin", "python")
    alembic_cmd = os.path.join(".venv", "Scripts", "alembic") if is_windows else os.path.join(".venv", "bin", "alembic")

    os.chdir("backend")
    
    try:
        if target == "init":
            do_status("Inicializando Base de Datos (SQLAlchemy)...", "Inicializando Base de Datos (SQLAlchemy)...", 
                      lambda: subprocess.run([python_cmd, "init_db.py"], check=True))
            cprint("[bold green]Base de datos inicializada correctamente.[/bold green]", "Base de datos inicializada correctamente.")
            
        elif target == "seed":
            do_status("Sembrando la Base de Datos (Seed)...", "Sembrando la Base de Datos (Seed)...", 
                      lambda: subprocess.run([python_cmd, "seed.py"], check=True))
            cprint("[bold green]Semilla plantada con exito.[/bold green]", "Semilla plantada con exito.")
            
        elif target == "migrate":
            msg = args.message
            do_status(f"Generando archivo de migracion: '{msg}'...", f"Generando archivo de migracion: '{msg}'...", 
                      lambda: subprocess.run([alembic_cmd, "revision", "--autogenerate", "-m", msg], check=True))
            cprint("[bold green]Migracion autogenerada exitosamente. Revisa la carpeta backend/alembic/versions.[/bold green]", "Migracion autogenerada exitosamente.")
            
        elif target == "upgrade":
            do_status("Aplicando migraciones estructurales a Head...", "Aplicando migraciones estructurales a Head...", 
                      lambda: subprocess.run([alembic_cmd, "upgrade", "head"], check=True))
            cprint("[bold green]Base de datos actualizada a la version Head.[/bold green]", "Base de datos actualizada a la version Head.")
            
    except subprocess.CalledProcessError as e:
        cprint(f"\n[bold red][ERROR] Al ejecutar el comando en DB:[/bold red] {e}", f"\n[ERROR] Al ejecutar el comando en DB: {e}")
    finally:
        os.chdir("..")
