import os
import socket
import sys
import re

# Agregamos la ruta para utilidades si es necesario
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

HAS_RICH = False
try:
    from rich.console import Console
    from rich.panel import Panel
    import questionary
    console = Console()
    HAS_RICH = True
except ImportError:
    pass

def get_local_ip():
    """Detecta la IP local de la maquina en la red."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def update_file_content(filepath, old_url_part, new_url_part):
    """Reemplaza una parte de la URL/Texto en un archivo."""
    if not os.path.exists(filepath):
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace(old_url_part, new_url_part)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def update_env_variable(key, value):
    """Actualiza o agrega una variable en el .env de la raíz."""
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    
    lines = []
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}\n")
        
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def configure_network():
    local_ip = get_local_ip()
    
    if HAS_RICH:
        console.print(Panel(f"[bold cyan]Configurador de Red Inteligente[/bold cyan]\nIP Detectada: [green]{local_ip}[/green]", expand=False))
        
        choice = questionary.select(
            "¿Qué dirección Host deseas utilizar para el sistema?",
            choices=[
                f"Local Host (localhost / 127.0.0.1)",
                f"IP Local de Red ({local_ip})",
                "Personalizada (Escribir manualmente)"
            ]
        ).ask()
    else:
        print(f"IP Detectada: {local_ip}")
        print("1. Localhost\n2. IP Local\n3. Personalizada")
        choice_idx = input("Selecciona una opcion: ")
        choice = "Local Host" if choice_idx == "1" else ("IP Local" if choice_idx == "2" else ("Personalizada" if choice_idx == "3" else None))

    if choice is None:
        return

    target_host = "localhost"
    if "IP Local" in choice:
        target_host = local_ip
    elif "Personalizada" in choice:
        target_host = questionary.text("Introduce la IP o Host deseado:").ask() if HAS_RICH else input("IP/Host: ")

    if HAS_RICH:
        target_port = questionary.text("Introduce el puerto del Backend (default: 8000):", default="8000").ask()
    else:
        target_port = input("Introduce el puerto del Backend (default: 8000): ")
        if not target_port:
            target_port = "8000"

    # 1. Actualizar .env en la raíz
    env_path = ".env"
    if os.path.exists(env_path):
        update_env_variable("APP_HOST", target_host)
        update_env_variable("APP_PORT_BACKEND", target_port)
        print(f"[OK] APP_HOST y APP_PORT_BACKEND actualizados a {target_host}:{target_port} en .env")

    # 2. Actualizar Frontend environment.ts
    front_env = os.path.join("frontend", "src", "environments", "environment.ts")
    if os.path.exists(front_env):
        import re
        with open(front_env, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex para reemplazar http://[host]:[port]/api/v1
        new_content = re.sub(r'(http://)[^/:]+(:\d+)?(/api/v1)', r'\g<1>' + target_host + f':{target_port}' + r'\g<3>', content)
        with open(front_env, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[OK] Frontend API URL actualizado a http://{target_host}:{target_port} en environment.ts")

    # 3. Actualizar Frontend config.json
    config_json_path = os.path.join("frontend", "src", "assets", "config.json")
    import json
    config_dir = os.path.dirname(config_json_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
        
    config_data = {}
    if os.path.exists(config_json_path):
        try:
            with open(config_json_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception:
            pass
            
    config_data["apiUrl"] = f"http://{target_host}:{target_port}/api/v1"
    with open(config_json_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    print(f"[OK] Frontend API URL actualizado a http://{target_host}:{target_port}/api/v1 en config.json")

    if HAS_RICH:
        console.print(f"[bold green]Sincronización de red completada con éxito para host: {target_host}:{target_port}[/bold green]")

def interactive_menu():
    """Interfaz interactiva delegada para Red."""
    configure_network()
    input("\nPresiona Enter para continuar...")

def execute(args):
    """Ejecución desde línea de comandos."""
    configure_network()

if __name__ == "__main__":
    configure_network()
