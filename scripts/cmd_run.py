import os
import subprocess
import platform
import sys

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

def add_subparser(parser):
    subparsers = parser.add_subparsers(dest="target")
    subparsers.required = True
    
    subparsers.add_parser("backend", help="Abre Uvicorn en modo desarrollo (FastAPI)")
    subparsers.add_parser("frontend", help="Abre ng serve en modo desarrollo (Angular)")
    subparsers.add_parser("all", help="Inicia ambos servidores simultaneamente")

def execute(args):
    target = args.target
    is_windows = platform.system() == "Windows"
    python_cmd = sys.executable
    uvicorn_cmd = [sys.executable, "-m", "uvicorn"]
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    # Intentar leer el host del .env para el mensaje
    app_host = "localhost"
    try:
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("APP_HOST="):
                        app_host = line.split("=")[1].strip()
                        break
    except:
        pass

    if target == "backend":
        panel_print(
            f"[bold cyan]Iniciando Backend (FastAPI)[/bold cyan] en http://{app_host}:8000\n[dim]Usa Ctrl+C para salir[/dim]",
            f"Iniciando Backend (FastAPI) en http://{app_host}:8000\nUsa Ctrl+C para salir",
            "cyan"
        )
        os.chdir("backend")
        subprocess.run([*uvicorn_cmd, "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
        os.chdir("..")

    elif target == "frontend":
        panel_print(
            "[bold magenta]Iniciando Frontend (Angular)[/bold magenta] en http://localhost:4200\n[dim]Usa Ctrl+C para salir[/dim]",
            "Iniciando Frontend (Angular) en http://localhost:4200\nUsa Ctrl+C para salir",
            "magenta"
        )
        os.chdir("frontend")
        try:
            subprocess.run([npm_cmd, "start"])
        except KeyboardInterrupt:
            pass
        finally:
            os.chdir("..")

    elif target == "all":
        panel_print(
            "[bold green]Iniciando TODO de forma concurrente...[/bold green]\n"
            f"[cyan]Backend[/cyan]:  http://{app_host}:8000\n"
            f"[magenta]Frontend[/magenta]: http://{app_host}:4200\n"
            "[dim]Sigue los logs de ambos servidores (Ctrl+C para salir)[/dim]",
            f"Iniciando TODO de forma concurrente...\nBackend: http://{app_host}:8000\nFrontend: http://{app_host}:4200\nSigue los logs de ambos (Ctrl+C para salir)",
            "green"
        )
        
        import threading
        
        def run_back():
            os.chdir("backend")
            subprocess.run([*uvicorn_cmd, "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
            
        def run_front():
            os.chdir("frontend")
            subprocess.run([npm_cmd, "start"])

        tb = threading.Thread(target=run_back)
        tf = threading.Thread(target=run_front)
        
        tb.start()
        tf.start()
        
        try:
            tb.join()
            tf.join()
        except KeyboardInterrupt:
            cprint("\n[bold yellow]Apagando servidores...[/bold yellow]", "\nApagando servidores...")

def interactive_menu():
    """Interfaz interactiva delegada para Servidores."""
    import questionary
    import argparse
    
    opt = questionary.select(
        "Iniciar Servidor:",
        choices=["Backend (FastAPI)", "Frontend (Angular)", "Ambos (Concurrente)", "Volver"]
    ).ask()
    
    if opt == "Volver" or opt is None:
        return
        
    target = opt.split()[0].lower()
    execute(argparse.Namespace(target=target))
    input("\nPresiona Enter para volver...")
