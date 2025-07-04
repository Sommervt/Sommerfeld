import os
import time
import sys
import json
import pyperclip
from datetime import datetime
from flask import Flask, request
from threading import Thread
import subprocess
import discord
from discord.ext import commands

import sys
import os

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

TOKEN_FILE = os.path.join(BASE_DIR, "tokenmila.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "canal.json")

if not os.path.exists(TOKEN_FILE):
    print(f"[ERROR] No se encontró el archivo '{TOKEN_FILE}'.")
    time.sleep(5)
    sys.exit(1)

with open(TOKEN_FILE, "r", encoding="utf-8") as f:
    DISCORD_BOT_TOKEN = f.read().strip()

if not DISCORD_BOT_TOKEN:
    print(f"[ERROR] El archivo '{TOKEN_FILE}' está vacío.")
    time.sleep(5)
    sys.exit(1)

# === Cargar configuración del canal y puerto ===
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

CANAL_ID = config["canal_id"]
PUERTO = config["puerto"]

# === Bot Discord ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# === Flask App para Webhook ===
app = Flask("webhook")

@app.route("/github", methods=["POST"])
def github_webhook():
    data = request.json
    if not data:
        return "No data", 400

    try:
        repo = data["repository"]["name"]
        autor = data["pusher"]["name"]
        commit = data["head_commit"]
        mensaje_commit = commit["message"]
        commit_url = commit["url"]
        timestamp = commit["timestamp"]
        fecha_commit = datetime.fromisoformat(timestamp.rstrip("Z")).strftime("%Y-%m-%d %H:%M:%S")
        rama = data["ref"].split("/")[-1]
    except KeyError as e:
        print(f"❌ Error extrayendo datos del webhook: {e}")
        return "Invalid data", 400

    canal = bot.get_channel (CANAL_ID)
    if canal:
        mensaje = (
            f"📢 **Nuevo commit en `{repo}`**\n"
            f"🌿 Rama: `{rama}`\n"
            f"👤 Autor: **{autor}**\n"
            f"📝 {mensaje_commit}\n"
            f"🕒 Fecha: `{fecha_commit}`\n"
            f"🔗 [Ver commit]({commit_url})"
        )
        bot.loop.create_task(canal.send(mensaje))
    else:
        print("⚠️ Canal no encontrado o sin permisos")

    return "OK", 200

def iniciar_webhook_server():
    Thread(target=app.run, kwargs={"port": PUERTO}).start()

# === LocalTunnel ===
url_localtunnel = None

def _run_tunnel():
    global url_localtunnel
    LT_PATH = r"C:\Users\didie\AppData\Roaming\npm\lt.cmd"
    try:
        process = subprocess.Popen(
            [LT_PATH, "--port", str(PUERTO)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print("[LocalTunnel] Esperando URL...")
        for line in process.stdout:
            print("[LocalTunnel]", line.strip())
            if "your url is:" in line:
                url_localtunnel = line.split("your url is:")[1].strip()
                print(f"🌐 LocalTunnel URL activa: {url_localtunnel}")
                break
    except Exception as e:
        print(f"❌ Error ejecutando LocalTunnel: {e}")

def iniciar_localtunnel():
    Thread(target=_run_tunnel).start()

    def obtener_url():
        return url_localtunnel

    return obtener_url

# === Evento Bot Discord ===
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Watch GitHub"))
    try:
        synced = await bot.tree.sync()
        print(f"Se han sincronizado {len(synced)} comandos slash (Mila).")
    except Exception as e:
        print(f"Error al sincronizar comandos slash (Mila): {e}")
    print(f"{bot.user.name} está en linea.")

# === Inicialización ===
iniciar_webhook_server()
obtener_url = iniciar_localtunnel()

# Esperar por la URL pública
public_url = None
for _ in range(30):
    public_url = obtener_url()
    if public_url:
        break
    time.sleep(0.5)

if public_url:
    full_url = f"{public_url}/github"
    print(f"✅ URL pública de GitHub webhook: {full_url}")
    try:
        pyperclip.copy(full_url)
        print(f"📋 Copiado al portapapeles: {full_url}")
    except:
        print("⚠️ No se pudo copiar al portapapeles.")
else:
    print("❌ No se pudo obtener la URL de LocalTunnel (timeout)")

# Iniciar bot
bot.run(DISCORD_BOT_TOKEN)

