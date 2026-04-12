import argparse
import sys

# --- Auto-deteccion de dependencias visuales ---
HAS_RICH = False
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

from scripts import cmd_setup, cmd_db, cmd_run, cmd_deploy, cmd_test, cmd_config

def print_banner():
    if HAS_RICH:
        banner = """
████████╗ █████╗ ██╗     ██╗     ███████╗██████╗ 
╚══██╔══╝██╔══██╗██║     ██║     ██╔════╝██╔══██╗
   ██║   ███████║██║     ██║     █████╗  ██████╔╝
   ██║   ██╔══██║██║     ██║     ██╔══╝  ██╔══██╗
   ██║   ██║  ██║███████╗███████╗███████╗██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝

        """
        console.print(f"[bold cyan]{banner}[/bold cyan]", justify="center")
    else:
        print("=============================================")
        print("                 TALLER AI                   ")
        print(" Plataforma Inteligente - Navaja Suiza CLI   ")
        print("=============================================")

def custom_help():
    print_banner()
    if HAS_RICH:
        console.print("\n[bold yellow]Uso:[/bold yellow] python taller.py [categoria] [comando]")
        
        table = Table(title="Categorias y Comandos Disponibles", title_style="bold green")
        table.add_column("Categoria", justify="right", style="cyan", no_wrap=True)
        table.add_column("Comandos", style="magenta")
        table.add_column("Descripcion", style="white")

        table.add_row("setup", "backend, frontend, env, all", "Instalacion de entornos y dependencias")
        table.add_row("config", "db, jwt, all", "Configuracion interactiva de variables (.env)")
        table.add_row("db", "init, seed, migrate, upgrade", "Gestion SQLAlchemy y Migraciones Alembic")
        table.add_row("run", "backend, frontend, all", "Inicia los servidores asincronamente")
        table.add_row("test", "ping, frontend", "Pruebas de salud del sistema")
        table.add_row("deploy", "services", "Genera archivos Systemd (.service) para Produccion Linux")

        console.print(table)
        console.print("\n[italic dim]Agrega '--help' al final de cualquier categoria para ver parametros especificos.[/italic dim]\n")
    else:
        print("\nUso: python taller.py [categoria] [comando]")
        print("\nCategorias Disponibles:")
        print("  setup   - backend, frontend, env, all     (Instalacion de entornos)")
        print("  config  - db, jwt, all                    (Configuracion interactiva env)")
        print("  db      - init, seed, migrate, upgrade    (Base de Datos & Alembic)")
        print("  run     - backend, frontend, all          (Run servers)")
        print("  test    - ping, frontend                  (Pruebas y Healthchecks)")
        print("  deploy  - services                        (Genera systemd services)")
        print("\nNota: Instala 'rich' (pip install rich) para ver la interfaz a color.\n")

def main():
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]):
        custom_help()
        sys.exit(0)
        
    print_banner()

    parser = argparse.ArgumentParser(
        description="Administrador de Plataforma Taller AI",
        add_help=False
    )

    subparsers = parser.add_subparsers(dest="category")
    subparsers.required = True

    parser_setup = subparsers.add_parser("setup")
    cmd_setup.add_subparser(parser_setup)
    
    parser_config = subparsers.add_parser("config")
    cmd_config.add_subparser(parser_config)

    parser_db = subparsers.add_parser("db")
    cmd_db.add_subparser(parser_db)

    parser_run = subparsers.add_parser("run")
    cmd_run.add_subparser(parser_run)

    parser_deploy = subparsers.add_parser("deploy")
    cmd_deploy.add_subparser(parser_deploy)

    parser_test = subparsers.add_parser("test")
    cmd_test.add_subparser(parser_test)

    if "-h" in sys.argv or "--help" in sys.argv:
        parser.parse_args()

    args, _ = parser.parse_known_args()

    try:
        if args.category == "setup":
            cmd_setup.execute(args)
        elif args.category == "config":
            cmd_config.execute(args)
        elif args.category == "db":
            cmd_db.execute(args)
        elif args.category == "run":
            cmd_run.execute(args)
        elif args.category == "deploy":
            cmd_deploy.execute(args)
        elif args.category == "test":
            cmd_test.execute(args)
    except Exception as e:
        if HAS_RICH:
            console.print(f"\n[bold red][ERROR] Durante la ejecucion:[/bold red] {str(e)}")
        else:
            print(f"\n[ERROR] Durante la ejecucion: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if HAS_RICH:
            console.print("\n\n[bold yellow]Saliendo del administrador...[/bold yellow]")
        else:
            print("\n\nSaliendo del administrador...")
        sys.exit(0)
