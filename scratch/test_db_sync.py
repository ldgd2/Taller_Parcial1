import psycopg2
import os

def test_sync_connection():
    # Datos del .env
    user = "postgres"
    password = "Li62156478"
    host = "127.0.0.1"
    port = "5432"
    database = "taller_db"
    
    print(f"Probando conexión SÍNCRONA (psycopg2) a {host}:{port}...")
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        print("[OK] ¡Conexión exitosa via psycopg2!")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Psycopg2 falló: {e}")
        
        print("\nIntentando conectar a la base de datos 'postgres' por defecto...")
        try:
            conn = psycopg2.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database="postgres"
            )
            print("[OK] Conexión exitosa a 'postgres'. La base de datos 'taller_db' probablemente no existe.")
            conn.close()
        except Exception as e2:
            print(f"[ERROR] También falló la conexión a 'postgres': {e2}")

if __name__ == "__main__":
    test_sync_connection()
