import argparse
import sys
import os
import time

# --- Detección de dependencias visuales ---
HAS_RICH = False
HAS_QUESTIONARY = False
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    pass

from scripts import cmd_setup, cmd_db, cmd_run, cmd_deploy, cmd_test, cmd_config, cmd_network

def print_banner():
    banner = """
████████╗ █████╗ ██╗     ██╗     ███████╗██████╗ 
╚══██╔══╝██╔══██╗██║     ██║     ██╔════╝██╔══██╗
   ██║   ███████║██║     ██║     █████╗  ██████╔╝
   ██║   ██╔══██║██║     ██║     ██╔══╝  ██╔══██╗
   ██║   ██║  ██║███████╗███████╗███████╗██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
    """
    if HAS_RICH:
        text = Text(banner)
        text.stylize("bold cyan", 0, 100)
        text.stylize("bold magenta", 100, 200)
        text.stylize("bold white", 200, len(banner))
        return text
    else:
        return banner

def get_current_host():
    """Lee el host actual del archivo .env en la raíz."""
    try:
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                for line in f:
                    if line.startswith("APP_HOST="):
                        return line.split("=")[1].strip()
    except:
        pass
    return "localhost"

def make_dashboard(selected_action="Menu Principal"):
    if not HAS_RICH:
        return "Modo Simple"
        
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=8),
        Layout(name="main", size=15),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Align.center(print_banner()))
    
    app_host = get_current_host()
    status_db = "[bold green]ONLINE[/bold green]"
    
    main_panel = Panel(
        Align.center(f"\n[bold green]SISTEMA OPERATIVO[/bold green]\n\n"
                     f"DB Status: {status_db}  |  API Host: [bold cyan]{app_host}[/bold cyan]\n"
                     f"Config File: [dim].env (Root)[/dim]\n"
                     f"Categoría: [bold yellow]{selected_action}[/bold yellow]"),
        title="[bold magenta]Estación de Control AI[/bold magenta]",
        border_style="cyan"
    )
    layout["main"].update(main_panel)
    layout["footer"].update(Panel(Align.center("[italic]Usa las flechas para navegar • 'q' para salir[/italic]"), border_style="dim"))
    
    return layout

def interactive_menu():
    if not HAS_QUESTIONARY or not HAS_RICH:
        print("\n[AVISO] Instalando componentes visuales faltantes...")
        os.system(f"{sys.executable} -m pip install rich questionary")
        os.execv(sys.executable, ['python'] + sys.argv)

    os.system('cls' if os.name == 'nt' else 'clear')
    
    while True:
        console.clear()
        console.print(make_dashboard())
        
        category = questionary.select(
            "Selecciona una categoría de operación:",
            choices=[
                "Red y Host (Nueva Configuración)",
                "Configuración Inicial (.env)",
                "Base de Datos (SQLAlchemy/Alembic)",
                "Ejecución de Servidores",
                "Pruebas y QA (IA/Whisper)",
                "Instalación de Dependencias",
                "Salir"
            ],
            style=questionary.Style([
                ('qmark', 'fg:#673ab7 bold'),
                ('pointer', 'fg:#ff9800 bold'),
                ('selected', 'fg:#ccddff bold'),
                ('highlighted', 'fg:#00ff00 bold'),
                ('answer', 'fg:#f44336 bold'),
            ])
        ).ask()

        if category == "Salir" or category is None:
            console.print("[bold yellow]Cerrando Navaja Suiza. ¡Hasta pronto![/bold yellow]")
            break

        # Delegación modular
        if "Red" in category:
            cmd_network.interactive_menu()
        elif "Configuración" in category:
            cmd_config.interactive_menu()
        elif "Base" in category:
            cmd_db.interactive_menu()
        elif "Servidores" in category:
            cmd_run.interactive_menu()
        elif "Pruebas" in category:
            cmd_test.interactive_menu()
        elif "Instalación" in category:
            cmd_setup.interactive_menu()

def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ["--help", "-h"]:
        parser = argparse.ArgumentParser(description="Navaja Suiza CLI")
        subparsers = parser.add_subparsers(dest="category")
        
        cmd_setup.add_subparser(subparsers.add_parser("setup"))
        cmd_config.add_subparser(subparsers.add_parser("config"))
        cmd_db.add_subparser(subparsers.add_parser("db"))
        cmd_run.add_subparser(subparsers.add_parser("run"))
        cmd_deploy.add_subparser(subparsers.add_parser("deploy"))
        cmd_test.add_subparser(subparsers.add_parser("test"))
        
        args, _ = parser.parse_known_args()
        if args.category:
            # Ejecución directa heredando el contexto
            getattr(globals()[f"cmd_{args.category}"], "execute")(args)
            return

    try:
        interactive_menu()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
