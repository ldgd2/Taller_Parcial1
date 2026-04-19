import urllib.request
import urllib.error
import json
import os
import platform
import subprocess
import sys
import argparse

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

def panel_print(rich_content, plain_content, border="blue", title=""):
    if HAS_RICH:
        console.print(Panel(rich_content, title=title, border_style=border))
    else:
        print("-" * 40)
        if title: print(f"--- {title} ---")
        print(plain_content)
        print("-" * 40)

def do_status(rich_msg, plain_msg, action_lambda):
    if HAS_RICH:
        with console.status(f"[cyan]{rich_msg}[/cyan]", spinner="status"):
            action_lambda()
    else:
        print(plain_msg)
        action_lambda()

def add_subparser(parser):
    subparsers = parser.add_subparsers(dest="target")
    subparsers.required = True
    
    subparsers.add_parser("ping", help="Revisa si el servidor FastAPI backend esta respondiendo")
    subparsers.add_parser("frontend", help="Ejecuta ng test")
    subparsers.add_parser("ia", help="Ejecuta el paquete de test de Inteligencia Artificial (Whisper y OpenRouter)")
    subparsers.add_parser("diag_ai", help="Diagnóstico profundo de cuotas y créditos de OpenRouter")

def execute(args):
    target = args.target

    if target == "ping":
        def ping_test():
            try:
                req = urllib.request.Request("http://localhost:8000/api/v1/")
                with urllib.request.urlopen(req) as response:
                    status = response.getcode()
                    data = json.loads(response.read().decode())
                    
                    if status == 200:
                        panel_print(
                            f"[bold green]Backend Saludable[/bold green]\n"
                            f"Estado: [cyan]{status}[/cyan]\n"
                            f"Respuesta: [white]{data.get('message', data)}[/white]",
                            f"Backend Saludable\nEstado: {status}\nRespuesta: {data.get('message', data)}",
                            "green", "Healthcheck API"
                        )
                    else:
                        cprint(f"[bold red][ATENCION] Backend respondio con codigo {status}: {data}[/bold red]", 
                               f"[ATENCION] Backend respondio con codigo {status}: {data}")
                        
            except urllib.error.URLError as e:
                panel_print(
                    f"[bold red][ERROR] De Conexion:[/bold red] {e.reason}\n\n"
                    f"[yellow]Asegurate de que el backend ha sido levantado usando:[/yellow]\n"
                    f"python taller.py run backend",
                    f"[ERROR] De Conexion: {e.reason}\n\nAsegurate de que el backend ha sido levantado usando:\npython taller.py run backend",
                    "red", "Error 503"
                )
                
        do_status("Haciendo Healthcheck del Backend (http://localhost:8000/api/v1/)...", "Haciendo Healthcheck del Backend (http://localhost:8000/api/v1/)...", ping_test)
            
    elif target == "frontend":
        cprint("\n[bold magenta]Lanzando Pruebas (Tests) del Frontend...[/bold magenta]", "\nLanzando Pruebas (Tests) del Frontend...")
        is_windows = platform.system() == "Windows"
        ng_cmd = "ng.cmd" if is_windows else "ng"
        
        os.chdir("frontend")
        try:
            subprocess.run([ng_cmd, "test", "--watch=false"], check=True)
            cprint("[bold green]Pruebas finalizadas.[/bold green]", "Pruebas finalizadas.")
        except FileNotFoundError:
            cprint("[bold red][ERROR] No se encontro 'ng'. Ejecutaste 'python taller.py setup frontend'?[/bold red]", "[ERROR] No se encontro 'ng'. Ejecutaste 'python taller.py setup frontend'?")
        finally:
            os.chdir("..")

    elif target == "ia":
        cprint("\n[bold magenta]Lanzando Pruebas (Tests) de Inteligencia Artificial...[/bold magenta]", "\nLanzando Pruebas del modulo IA...")
        
        sys_exe = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        test_ia_dir = os.path.join(script_dir, "test_ia")
        
        panel_print("[cyan]Módulo: Transcripción (faster-whisper)[/cyan]", "Módulo: Whisper Local")
        subprocess.run([sys_exe, os.path.join(test_ia_dir, "test_whisper.py")])
        
        panel_print("[cyan]Módulo: Análisis Inteligente (OpenRouter)[/cyan]", "Módulo: OpenRouter y Pydantic")
        subprocess.run([sys_exe, os.path.join(test_ia_dir, "test_openrouter.py")])

    elif target == "diag_ai":
        cprint("\n[bold magenta]Consultando Estado de Créditos en OpenRouter...[/bold magenta]", "\nConsultando Créditos de IA...")
        sys_exe = sys.executable
        script_dir = os.path.dirname(os.path.abspath(__file__))
        diag_script = os.path.join(script_dir, "test_ia", "diag_openrouter.py")
        subprocess.run([sys_exe, diag_script])

def interactive_menu():
    """Interfaz interactiva delegada para Tests."""
    import questionary
    choices = [
        "IA (Whisper/OpenRouter)", 
        "Diagnóstico de Créditos AI",
        "Ping/Health Backend", 
        "Frontend (Unit Tests)", 
        "Volver"
    ]
    opt = questionary.select("Módulo de Test:", choices=choices).ask()
    
    if opt == "Volver":
        return
        
    if "IA (Whisper" in opt: target = "ia"
    elif "Diagnóstico" in opt: target = "diag_ai"
    elif "Ping" in opt: target = "ping"
    else: target = "frontend"
    
    execute(argparse.Namespace(target=target))
    input("\nPresiona Enter para continuar...")
