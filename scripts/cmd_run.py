import os
import subprocess
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

def add_subparser(parser):
    subparsers = parser.add_subparsers(dest="target")
    subparsers.required = True
    
    subparsers.add_parser("backend", help="Abre Uvicorn en modo desarrollo (FastAPI)")
    subparsers.add_parser("frontend", help="Abre ng serve en modo desarrollo (Angular)")
    subparsers.add_parser("all", help="Inicia ambos servidores simultaneamente")

def execute(args):
    target = args.target
    is_windows = platform.system() == "Windows"
    
    python_cmd = os.path.join(".venv", "Scripts", "python") if is_windows else os.path.join(".venv", "bin", "python")
    uvicorn_cmd = os.path.join("backend", ".venv", "Scripts", "uvicorn") if is_windows else os.path.join("backend", ".venv", "bin", "uvicorn")
    npm_cmd = "npm.cmd" if is_windows else "npm"

    if target == "backend":
        panel_print(
            "[bold cyan]Iniciando Backend (FastAPI)[/bold cyan] en http://localhost:8000\n[dim]Usa Ctrl+C para salir[/dim]",
            "Iniciando Backend (FastAPI) en http://localhost:8000\nUsa Ctrl+C para salir",
            "cyan"
        )
        os.chdir("backend")
        subprocess.run([uvicorn_cmd.replace("backend\\", "").replace("backend/", ""), "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
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
            "[cyan]Backend[/cyan]:  http://localhost:8000\n"
            "[magenta]Frontend[/magenta]: http://localhost:4200\n"
            "[dim]Sigue los logs de ambos servidores (Ctrl+C para salir)[/dim]",
            "Iniciando TODO de forma concurrente...\nBackend: http://localhost:8000\nFrontend: http://localhost:4200\nSigue los logs de ambos (Ctrl+C para salir)",
            "green"
        )
        
        import threading
        
        def run_back():
            os.chdir("backend")
            subprocess.run([uvicorn_cmd.replace("backend\\", "").replace("backend/", ""), "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
            
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
