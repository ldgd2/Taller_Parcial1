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

    # 1. Actualizar Backend .env (DATABASE_URL)
    # Asumimos que la DB es local, pero el Host del servidor de la App es el que cambia.
    # Sin embargo, si el usuario quiere que TODO se base en esa IP, podriamos cambiar el host de la DB.
    # Por ahora cambiamos el host del DATABASE_URL si contiene localhost.
    # 1. Actualizar .env en la raíz
    env_path = ".env"
    if os.path.exists(env_path):
        # Intentamos actualizar el host de la DB solo si el usuario lo confirma o es necesario.
        # Pero lo mas critico es el API URL del frontend.
        update_env_variable("APP_HOST", target_host)
        print(f"[OK] APP_HOST actualizado a {target_host} en .env")

    # 2. Actualizar Frontend environment.ts
    front_env = os.path.join("frontend", "src", "environments", "environment.ts")
    if os.path.exists(front_env):
        # Reemplazamos lo que este en apiUrl: 'http://...:8000/api/v1'
        # Buscamos 'http://localhost' o 'http://127.0.0.1' o una IP anterior.
        # Para ser mas precisos, leemos el archivo y buscamos el patron del apiUrl.
        import re
        with open(front_env, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex para capturar el host entre http:// y :8000
        # Corregimos el error del rf'\1...' que colisionaba con IPs que inician con 1 (\11)
        # Usamos \g<1> para evitar la ambigüedad con los dígitos de la IP
        new_content = re.sub(r'(http://).*?(:8000)', r'\g<1>' + target_host + r'\g<2>', content)
        with open(front_env, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[OK] Frontend API URL actualizado a http://{target_host}:8000 en environment.ts")

    if HAS_RICH:
        console.print(f"[bold green]Sincronización de red completada con éxito para host: {target_host}[/bold green]")

def interactive_menu():
    """Interfaz interactiva delegada para Red."""
    configure_network()
    input("\nPresiona Enter para continuar...")

def execute(args):
    """Ejecución desde línea de comandos."""
    configure_network()

if __name__ == "__main__":
    configure_network()
