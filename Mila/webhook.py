import json
import os
from flask import Flask, request
from threading import Thread
import discord
from datetime import datetime

config_path = os.path.join(os.path.dirname(__file__), "canal.json")
with open(config_path, "r") as f:
    config = json.load(f)

CANAL_ID = config["canal_id"]
PUERTO = config["puerto"]

app = Flask(__name__)

def configurar_webhook(bot: discord.Client):
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

        canal = bot.get_channel(CANAL_ID)
        if canal:
            texto = (
                f"📢 **Nuevo commit en `{repo}`**\n"
                f"🌿 Rama: `{rama}`\n"
                f"👤 Autor: **{autor}**\n"
                f"📝 {mensaje_commit}\n"
                f"🕒 Fecha: `{fecha_commit}`\n"
                f"🔗 [Ver commit]({commit_url})"
            )
            bot.loop.create_task(canal.send(texto))
        else:
            print("⚠️ Canal no encontrado o sin permisos")
        return "OK", 200

def iniciar_webhook_server():
    Thread(target=app.run, kwargs={"port": PUERTO}).start()