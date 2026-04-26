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
        with console.status(f"[cyan]{rich_msg}[/cyan]", spinner="dots"):
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
    subparsers.add_parser("notifications", help="Test de Notificaciones Push (Broadcast/Personalizadas)")

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
        diag_script = os.path.join(script_dir, "test_ia", "diag_openrouter.py")
        subprocess.run([sys_exe, diag_script])

    elif target == "notifications":
        import questionary
        tipo = questionary.select(
            "Tipo de Notificación a enviar:",
            choices=["Broadcast (A todos)", "Personalizada (A un Usuario)", "Directa (Por Token)", "Cancelar"]
        ).ask()

        if tipo == "Cancelar": return

        # 1. Si es directa, pedir el token PRIMERO como pidió el usuario
        target_token = None
        target_user_id = None
        if tipo == "Directa (Por Token)":
            target_token = questionary.text("Token del dispositivo destino:").ask()
            if not target_token: return
        elif tipo == "Personalizada (A un Usuario)":
            target_user_id = questionary.text("ID del Usuario destino:").ask()
            if not target_user_id: return

        # 2. Elegir un "Template" o estilo
        estilo = questionary.select(
            "Estilo/Tipo de Notificación:",
            choices=["Estándar", "Alerta Crítica (Roja)", "Actualización de Estado", "Mensaje de Soporte"]
        ).ask()

        # Configurar según estilo
        default_title = "TEST NAVAJA SUIZA"
        default_body = "Esta es una prueba desde la estación de control."
        extra_data = {"type": "test"}

        if estilo == "Alerta Crítica (Roja)":
            default_title = "⚠️ ALERTA DE EMERGENCIA"
            default_body = "Se requiere atención inmediata en su ubicación."
            extra_data = {"priority": "high", "color": "red", "type": "emergency"}
        elif estilo == "Actualización de Estado":
            default_title = "✅ Estado Actualizado"
            default_body = "Su vehículo ha sido asignado a un técnico."
            extra_data = {"status": "assigned", "type": "update"}
        elif estilo == "Mensaje de Soporte":
            default_title = "💬 Nuevo Mensaje"
            default_body = "El taller te ha enviado un mensaje."
            extra_data = {"channel": "chat", "type": "message"}

        titulo = questionary.text("Título de la notificación:", default=default_title).ask()
        cuerpo = questionary.text("Cuerpo de la notificación:", default=default_body).ask()

        def send_notification():
            try:
                base_url = "http://localhost:8000/api/v1/notificaciones"
                
                if tipo == "Broadcast (A todos)":
                    url = f"{base_url}/test-broadcast?titulo={urllib.parse.quote(titulo)}&cuerpo={urllib.parse.quote(cuerpo)}"
                    data_json = json.dumps(extra_data).encode()
                    req = urllib.request.Request(url, data=data_json, method="POST", headers={"Content-Type": "application/json"})
                elif tipo == "Personalizada (A un Usuario)":
                    url = f"{base_url}/test-personalizada"
                    # Nota: El schema CustomNotificationRequest no tiene 'data' aún, lo dejamos simple o lo agregamos
                    payload = {"user_id": int(target_user_id), "titulo": titulo, "cuerpo": cuerpo}
                    data_json = json.dumps(payload).encode()
                    req = urllib.request.Request(url, data=data_json, method="POST", headers={"Content-Type": "application/json"})
                else: # Directa (Por Token)
                    url = f"{base_url}/test-token?token={urllib.parse.quote(target_token)}&titulo={urllib.parse.quote(titulo)}&cuerpo={urllib.parse.quote(cuerpo)}"
                    data_json = json.dumps(extra_data).encode()
                    req = urllib.request.Request(url, data=data_json, method="POST", headers={"Content-Type": "application/json"})

                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode())
                    panel_print(f"[bold green]Éxito:[/bold green] {res_data.get('message')}", "Notificación enviada correctamente", "green", "Resultado Push")
            except Exception as e:
                panel_print(f"[bold red]Error al enviar:[/bold red] {str(e)}", f"Error: {e}", "red", "Push Failed")

        do_status("Enviando notificación push...", "Enviando notificación push...", send_notification)

def interactive_menu():
    """Interfaz interactiva delegada para Tests."""
    import questionary
    choices = [
        "IA (Whisper/OpenRouter)", 
        "Diagnóstico de Créditos AI",
        "Notificaciones Push (Test)",
        "Ping/Health Backend", 
        "Frontend (Unit Tests)", 
        "Volver"
    ]
    opt = questionary.select("Módulo de Test:", choices=choices).ask()
    
    if opt == "Volver":
        return
        
    if "IA (Whisper" in opt: target = "ia"
    elif "Diagnóstico" in opt: target = "diag_ai"
    elif "Notificaciones" in opt: target = "notifications"
    elif "Ping" in opt: target = "ping"
    else: target = "frontend"
    
    execute(argparse.Namespace(target=target))
    input("\nPresiona Enter para continuar...")
