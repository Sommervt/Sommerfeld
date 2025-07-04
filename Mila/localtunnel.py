import subprocess
import threading
import time
import re

# Ruta completa al ejecutable lt.cmd
LT_PATH = r"C:\Users\didie\AppData\Roaming\npm\lt.cmd"

url_localtunnel = None

def _run_tunnel():
    global url_localtunnel
    try:
        process = subprocess.Popen(
            [LT_PATH, "--port", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        print("[LocalTunnel] Esperando URL...")
        for line in process.stdout:
            print("[LocalTunnel]", line.strip())
            match = re.search(r'(https:\/\/[a-zA-Z0-9\-]+\.loca\.lt)', line)
            if match:
                url_localtunnel = match.group(1)
                print(f"🌐 LocalTunnel URL activa: {url_localtunnel}")
                break

    except Exception as e:
        print(f"❌ Error ejecutando LocalTunnel: {e}")

def iniciar_localtunnel():
    threading.Thread(target=_run_tunnel).start()

    def obtener_url():
        return url_localtunnel

    return obtener_url

