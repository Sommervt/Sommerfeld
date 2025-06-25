#import (COSAS IMPORTANTES NECESARIAS)
import discord
from discord.ext import commands
from discord import app_commands
import os
import re
import threading
import pygetwindow as gw
import random
import datetime
import subprocess
import asyncio
import psutil
import json
import sys
import re
import time
import sqlite3
from datetime import datetime 
from collections import defaultdict
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pymem
import struct
import itertools
import ctypes
from ctypes import wintypes
import pyperclip




#DISCORD TOKEN (EL TOKEN QUE OBTIENES EN EL PORTAL DE CREADORES DE DISCORD, CAMBIA ESTE VALOR EN token.txt)
TOKEN = "token.txt"

if not os.path.exists(TOKEN):
    print(f"[ERROR] No se encontró el archivo '{TOKEN}'.")
    print("Por favor, crea el archivo y coloca dentro tu token de Discord.")
    time.sleep(5)
    sys.exit(1)

with open(TOKEN, "r", encoding="utf-8") as f:
    DISCORD_BOT_TOKEN = f.read().strip()

if not DISCORD_BOT_TOKEN:
    print(f"[ERROR] El archivo '{TOKEN}' está vacío.")
    time.sleep(5)
    sys.exit(1)


#INTENTS (O PERMISOS QUE OBTENDRA EL BOT EN DISCORD)
intents = discord.Intents.all()
intents.messages = True 
intents.message_content = True 
intents.guilds = True 
intents.members = True

bot = commands.Bot(command_prefix=["!", "$"], intents=intents)
                   
# EVENT BOT ON (EVENTO DE ENCENDIDO)
@bot.event
async def on_ready():

    await bot.change_presence(
        status=discord.Status.idle, #PUEDES PONER LO QUE SEA
        activity=discord.Game(name="Help.") #PUEDES PONER LO QUE SEA
    )
    try:
         # Sincronizar los comandos slash con Discord 
        synced = await bot.tree.sync()
        print(f"Se han sincronizado {len(synced)} comandos slash (Sommerfeld).")
    except Exception as e:
        print(f"Error al sincronizar comandos slash: {e}")
    print(f"{bot.user.name} está en linea.")


#COMANDOS CON EL PREFIJO "/", ESTOS COMANDOS SE VEN EN DISCORD.


# /HELP
@bot.tree.command(name="help", description="Muestra los comandos disponibles.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Comandos Disponibles",
        description="Lista de comandos por categorías.",
        color=discord.Color.green()
    )

    # Comandos generales
    embed.add_field(name="!redescreator", value="Muestra las redes del creador del código.", inline=False)
    embed.add_field(name="/avatar", value="Muestra el avatar o perfil.", inline=False)
    embed.add_field(name="/lovecalc", value="Calcula el amor entre 2 personas.", inline=False)
    embed.add_field(name="/delete_after", value="Borra todos los mensajes enviados después de un mensaje por ID.", inline=False)
    embed.add_field(name="/clearchannel", value="Elimina y recrea el canal actual.", inline=False)
    embed.add_field(name="/avatarid", value="Obtén el avatar de un usuario usando su ID.", inline=False)
    embed.add_field(name="/ruletazo", value="Juega a la ruleta rusa eliminando participantes hasta que queden los ganadores.", inline=False)

    # Comandos importantes
    embed.add_field(name="‎", value="**__Comandos Importantes__**", inline=False)  # Separador visual
    embed.add_field(name="/serverinfo", value="Muestra información del servidor.", inline=False)
    embed.add_field(name="/userinfo", value="Muestra información de un usuario.", inline=False)
    embed.add_field(name="/botinfo", value="Muestra información del bot actual.", inline=False)

    await interaction.response.send_message(embed=embed)


# /AVATAR 
@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario.")
async def avatar(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    embed = discord.Embed(title=f"Avatar de {usuario.display_name}", color=discord.Color.blue())
    embed.set_image(url=usuario.avatar.url)
    await interaction.response.send_message(embed=embed)

# /LOVECALC
@bot.tree.command(name="lovecalc", description="Calcula la compatibilidad de amor entre dos personas")
async def lovecalc(interaction: discord.Interaction, name1: str, name2: str):
    
    compatibility = random.randint(0, 100)

    if compatibility >= 50:
        message = f"Calculando la compatibilidad entre {name1} y {name2}...\nLa compatibilidad de amor es: **{compatibility}%**. Cojan. 👻"
    else:
        message = f"Calculando la compatibilidad entre {name1} y {name2}...\nLa compatibilidad de amor es: **{compatibility}%**. No cojan, uno tiene Sida. 👻"

    await interaction.response.send_message(message)


# /DELETE_AFTER
@bot.tree.command(name="delete_after", description="Borrar todos los mensajes enviados después de un mensaje por ID")
async def delete_after(interaction: discord.Interaction, message_id: str):
    """Borra mensajes enviados después de un mensaje específico por su ID"""
    await interaction.response.defer(ephemeral=True)  
    try:
    
        message = await interaction.channel.fetch_message(int(message_id))

        
        async for msg in interaction.channel.history(after=message, limit=None):
            await msg.delete()

        await interaction.followup.send("¡Todos los mensajes posteriores han sido borrados!", ephemeral=True)
    except discord.NotFound:
        
        await interaction.followup.send("No se encontró el mensaje especificado.", ephemeral=True)
    except discord.Forbidden:
        
        await interaction.followup.send("No tengo permisos para borrar estos mensajes.", ephemeral=True)
    except discord.HTTPException as e:
        
        await interaction.followup.send(f"Hubo un error al intentar borrar los mensajes: {e}", ephemeral=True)






#
@bot.tree.command(name="clearchannel", description="Elimina y recrea el canal actual.")
async def clearchannel(interaction: discord.Interaction):
    """Elimina el canal actual y lo recrea con el mismo nombre, categoría y permisos."""
    try:
        old_channel = interaction.channel
        channel_name = old_channel.name
        category = old_channel.category  # Guarda la categoría
        overwrites = old_channel.overwrites  # Guarda los permisos

        await interaction.response.defer(ephemeral=True)

        # Eliminar el canal original
        await old_channel.delete()

        # Crear el nuevo canal con la misma categoría y permisos
        new_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        print(f"El canal {channel_name} ha sido eliminado y recreado.")
    except discord.Forbidden:
        await interaction.followup.send("No tengo permisos para eliminar y recrear el canal.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"Hubo un error al intentar eliminar y recrear el canal: {e}", ephemeral=True)
# /AVATARID
@bot.tree.command(name="avatarid", description="Obtén el avatar de un usuario usando su ID.")
@app_commands.describe(user_id="El ID del usuario cuyo avatar deseas ver.")
async def avatar_id(interaction: discord.Interaction, user_id: str):
    try:
        
        user = await bot.fetch_user(user_id)
        if user.avatar:
            embed = discord.Embed(
                title=f"Avatar de {user.name}",
                color=discord.Color.blue()
            )
            embed.set_image(url=user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("El usuario no tiene un avatar establecido.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("No se encontró un usuario con ese ID.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"Hubo un error al obtener el avatar: {e}", ephemeral=True)

# /RULETAZO

@bot.tree.command(name="ruletazo", description="Juega a la ruleta rusa eliminando participantes hasta que queden los ganadores.")
@app_commands.describe(
    participantes="Menciona a los usuarios que participarán en el juego.",
    ganadores="Cantidad de ganadores que quedarán al final."
)
async def ruletazo(interaction: discord.Interaction, participantes: str, ganadores: int):
    """
    Comando para jugar a la ruleta rusa con los miembros mencionados.
    """
    
    mentioned_members = []
    for word in participantes.split():
        if word.startswith("<@") and word.endswith(">"):
            member_id = int(word.replace("<@", "").replace(">", "").replace("!", ""))
            member = interaction.guild.get_member(member_id)
            if member:
                mentioned_members.append(member)

    if not mentioned_members:
        await interaction.response.send_message(
            "⚠️ Por favor, menciona a los usuarios que participarán en el ruletazo.", ephemeral=True
        )
        return

    if len(mentioned_members) <= ganadores:
        await interaction.response.send_message(
            f"⚠️ El número de ganadores ({ganadores}) debe ser menor al número de participantes ({len(mentioned_members)}).",
            ephemeral=True,
        )
        return

    if ganadores < 1:
        await interaction.response.send_message(
            "⚠️ Debe haber al menos 1 ganador.", ephemeral=True
        )
        return

   
    participants = "\n".join([member.mention for member in mentioned_members])
    embed_intro = discord.Embed(
        title="🔫 Ruletazo 🔫",
        description=f"¡La ruleta ha girado! 🎲 Participantes:\n{participants}\n\n"
                    f"Solo quedarán **{ganadores}** ganadores.",
        color=discord.Color.blue()
    )
    embed_intro.set_footer(text="Preparando el tambor... ¿Quién será el siguiente eliminado?")
    await interaction.response.send_message(embed=embed_intro)

   
    remaining = mentioned_members[:]
    while len(remaining) > ganadores:
        await asyncio.sleep(3) 
        eliminated = random.choice(remaining)
        remaining.remove(eliminated)

        
        embed_eliminated = discord.Embed(
            title="💥 Eliminado 💥",
            description=f"**{eliminated.mention}** ha sido eliminado de la ruleta.",
            color=discord.Color.red()
        )
        embed_eliminated.set_footer(text=f"Quedan {len(remaining)} participantes.")
        await interaction.channel.send(embed=embed_eliminated)

   
    winners = "\n".join([member.mention for member in remaining])
    embed_winners = discord.Embed(
        title="🏆 ¡Ganadores del Ruletazo! 🏆",
        description=f"🎉 Felicidades a los sobrevivientes:\n{winners}",
        color=discord.Color.green()
    )
    embed_winners.set_footer(text="¡Gracias por participar!")
    await interaction.channel.send(embed=embed_winners)

# /SERVERINFO
@bot.tree.command(name="serverinfo", description="Muestra información del servidor.")
async def serverinfo(interaction: discord.Interaction):
    """Comando para mostrar información del servidor."""
    guild = interaction.guild
    roles = [role.name for role in guild.roles if role.name != "@everyone"]
    roles_display = ", ".join(roles) if roles else "No hay roles."

    embed = discord.Embed(title=f"Información del servidor: {guild.name}", color=discord.Color.blue())
    embed.add_field(name="ID del Servidor", value=guild.id, inline=False)
    embed.add_field(name="Propietario", value=guild.owner, inline=False)
    embed.add_field(name="Miembros", value=guild.member_count, inline=False)
    embed.add_field(name="Canales", value=len(guild.channels), inline=False)
    embed.add_field(name="Roles", value=roles_display[:1024], inline=False)  
    embed.add_field(name="Fecha de creación", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)

    await interaction.response.send_message(embed=embed)

# /USERINFO
@bot.tree.command(name="userinfo", description="Muestra la información de un usuario.")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    """Muestra información sobre un usuario específico."""  

    if user.status == discord.Status.online:
        status = "Online"
    elif user.status == discord.Status.idle:
        status = "Idle"
    elif user.status == discord.Status.dnd:
        status = "Do Not Disturb"
    elif user.status == discord.Status.offline:
        status = "Offline"

    embed = discord.Embed(title=f"Información de {user.name}", color=discord.Color.blue())
    embed.add_field(name="Nombre", value=user.name, inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Estado", value=status, inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]), inline=False)
    embed.add_field(name="Fecha de creación", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="Fecha de ingreso", value=user.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.set_thumbnail(url=user.avatar.url)

    await interaction.response.send_message(embed=embed)


# /BOTINFO
@bot.tree.command(name="botinfo", description="Muestra información sobre el bot.")
async def bot_info(interaction: discord.Interaction):
    creator_id = 1221348290982056098
    guild = interaction.guild
    creator = guild.get_member(creator_id) if guild else None

    if creator:
        status = creator.status
        creator_name = f"{creator.name}#{creator.discriminator}"
    else:
        status = "No está en el servidor"
        creator_name = "Sommerfeld"

    embed = discord.Embed(title="Información del Bot", color=discord.Color.green())
    embed.add_field(name="Creador", value=creator_name, inline=False)
    embed.add_field(name="Estado", value=str(status), inline=False)
    embed.add_field(name="ID", value=str(creator_id), inline=False)
    embed.add_field(name="Ping", value=f"{bot.latency * 1000:.2f}ms", inline=False)
    embed.add_field(name="Versión", value="Windows Edition", inline=False)

    await interaction.response.send_message(embed=embed)

#FUNCION PARA LEER COMANDOS DE COMMANDS
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Comandos tipo JSON con prefijo "!"
    if message.content.startswith("!"):
        command_name = message.content[1:].split()[0]
        command_path = f"commands/{command_name}.json"
        if os.path.exists(command_path):
            with open(command_path, 'r', encoding='utf-8') as file:
                command_data = json.load(file)
                if command_data.get("enabled", False):
                    response = command_data.get("response", "Este comando no tiene respuesta configurada.")
                    await message.channel.send(response.format(member_name=message.author.name))
                else:
                    await message.channel.send(f"El comando `{command_name}` está deshabilitado.")
        else:
            await message.channel.send(f"El comando `{command_name}` no se encuentra en nuestra base de datos.")

    # Comandos tipo Python con prefijo "&"
    elif message.content.startswith("&"):
        command_name = message.content[1:].split()[0]
        command_path = f"commands/{command_name}.py"
        if os.path.exists(command_path):
            try:
                command_globals = {}
                with open(command_path, 'r', encoding='utf-8') as file:
                    exec(file.read(), command_globals)
                if command_globals.get("enabled", False):
                    if "run" in command_globals:
                        await command_globals["run"](bot, message)
                    else:
                        await message.channel.send(f"El comando `&{command_name}` no tiene una función `run()` definida.")
                else:
                    await message.channel.send(f"El comando `&{command_name}` está deshabilitado.")
            except Exception as e:
                await message.channel.send(f"Error al ejecutar `&{command_name}`: {e}")
        else:
            await message.channel.send(f"El comando `&{command_name}` no se encuentra en nuestra base de datos.")

    else:
        await bot.process_commands(message)



#COMANDOS CON PREFIJO "$" (ESTOS COMANDOS NO SE VEN EN DISCORD, SON CONSIDERADOS OCULTOS).
# $bateria
@bot.command()
async def bateria(ctx):
    """Muestra el porcentaje de batería de la PC/Host que ejecuta el bot."""
    
    battery = psutil.sensors_battery()

    if battery is None:
        await ctx.send("No se detecta una batería en esta PC.")
        return

    porcentaje = battery.percent
    estado_cargando = "Sí" if battery.power_plugged else "No"
    tiempo_restante = (
        f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m"
        if battery.secsleft != psutil.POWER_TIME_UNLIMITED and not battery.power_plugged
        else "Cargando o tiempo ilimitado"
    )

    response_template = (
        "Estado de la batería: \n"
        "- Porcentaje: $porcentaje%\n"
        "- Cargando: $estado_cargando\n"
        "- Tiempo restante: $tiempo_restante"
    )

    mensaje = response_template.replace("$porcentaje", str(porcentaje)) \
                               .replace("$estado_cargando", estado_cargando) \
                               .replace("$tiempo_restante", tiempo_restante)

    await ctx.send(mensaje)

    # $kick
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    """Expulsa a un miembro del servidor solo si el ejecutor tiene permisos de moderador o admin."""


    if not any(role.permissions.kick_members for role in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
        await ctx.send("No tienes permisos suficientes para expulsar miembros.")
        return


    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("No tengo permisos suficientes para expulsar usuarios.")
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member} ha sido expulsado del servidor. Razón: {reason if reason else 'No especificada'}")
    except discord.Forbidden:
        await ctx.send("No puedo expulsar a este usuario. Puede que tenga más permisos que yo.")
    except discord.HTTPException:
        await ctx.send("Hubo un error al intentar expulsar al usuario.")

# $ban
@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason=None):
    """Banea a un miembro del servidor solo si el ejecutor tiene permisos de moderador o admin."""

    
    if not member:
        await ctx.send("Por favor, menciona al usuario que deseas banear.")
        return

    
    if not any(role.permissions.ban_members for role in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
        await ctx.send("No tienes permisos suficientes para banear miembros.")
        return

    
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("No tengo permisos suficientes para banear usuarios.")
        return

    try:
        
        await member.ban(reason=reason)
        ban_message = f"Baneo: Exitoso"
    except discord.Forbidden as e:
        ban_message = f"Baneo: Error. {str(e)}"
    except discord.HTTPException as e:
        ban_message = f"Baneo: Error. {str(e)}"
        print(f"Error al intentar banear al usuario: {str(e)}")  

    try:
        
        await member.send(f"Has sido baneado del servidor {ctx.guild.name}. Razón: {reason if reason else 'No especificada'}")
        dm_message = "DM: Exitoso"
    except discord.Forbidden as e:
        dm_message = f"DM: Error. No se pudo enviar el DM, el usuario tiene los DMs desactivados o tiene el bot bloqueado. {str(e)}"
        print(f"Error al intentar enviar el DM al usuario baneado: {str(e)}")  

    
    await ctx.send(f"{ban_message}\n{dm_message}")

# Función para eliminar decimales cuando no son necesarios
def format_result(result):
    if result.is_integer():
        return int(result)
    return result

# $suma
@bot.command()
async def suma(ctx, num1: float, operador: str, num2: float):
    if operador == "+":
        resultado = num1 + num2
        await ctx.send(f"El resultado de {int(num1)} + {int(num2)} es {int(resultado) if resultado.is_integer() else resultado}")
    else:
        await ctx.send("Operador no válido")

# $resta
@bot.command()
async def resta(ctx, num1: float, operador: str, num2: float):
    if operador == "-":
        resultado = num1 - num2
        await ctx.send(f"El resultado de {int(num1)} - {int(num2)} es {int(resultado) if resultado.is_integer() else resultado}")
    else:
        await ctx.send("Operador no válido")

# $multiplicacion
@bot.command()
async def multiplicacion(ctx, num1: float, operador: str, num2: float):
    if operador == "*":
        resultado = num1 * num2
        await ctx.send(f"El resultado de {int(num1)} * {int(num2)} es {int(resultado) if resultado.is_integer() else resultado}")
    else:
        await ctx.send("Operador no válido")

# $division
@bot.command()
async def division(ctx, num1: float, operador: str, num2: float):
    if operador == "/":
        if num2 == 0:
            await ctx.send("No se puede dividir por cero.")
            return
        resultado = num1 / num2
        await ctx.send(f"El resultado de {int(num1)} / {int(num2)} es {int(resultado) if resultado.is_integer() else resultado}")
    else:
        await ctx.send("Operador no válido")

# $porcentaje
@bot.command()
async def porcentaje(ctx, porcentaje: float, operador: str, total: float):
    if operador == "%":
        resultado = (porcentaje / 100) * total
        await ctx.send(f"El {int(porcentaje)}% de {int(total)} es {int(resultado) if resultado.is_integer() else resultado}")
    else:
        await ctx.send("Operador no válido")

# $raiz
@bot.command()
async def raiz(ctx, num: float):
    resultado = num ** 0.5
    await ctx.send(f"La raíz cuadrada de {int(num)} es {int(resultado) if resultado.is_integer() else resultado}")

# $potencia
@bot.command()
async def potencia(ctx, num: float, operador: str, exponente: float):
    if operador == "^":
        resultado = num ** exponente
        await ctx.send(f"{int(num)} elevado a la {int(exponente)} es {int(resultado) if resultado.is_integer() else resultado}")
    else:
        await ctx.send("Operador no válido")

# $hora - Muestra la hora actual
@bot.command()
async def hora(ctx):
    ahora = datetime.now().strftime("%I:%M:%S %p")
    await ctx.send(f"🕒 Hora actual: {ahora}")

# $fecha - Muestra la fecha actual
@bot.command()
async def fecha(ctx):
    hoy = datetime.now().strftime("%d/%m/%Y")
    await ctx.send(f"📅 Fecha de hoy: {hoy}")

    # $clear <número> - Borra una cantidad de mensajes del canal
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, cantidad: int):
    await ctx.channel.purge(limit=cantidad + 1)
    await ctx.send(f"🧹 {cantidad} mensajes eliminados.", delete_after=3)

# $mute @usuario <tiempo> - Silencia a un usuario por un tiempo
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, miembro: discord.Member, tiempo: str):
    duracion = 0
    if tiempo.endswith("s"):
        duracion = int(tiempo[:-1])
    elif tiempo.endswith("m"):
        duracion = int(tiempo[:-1]) * 60
    elif tiempo.endswith("h"):
        duracion = int(tiempo[:-1]) * 3600
    elif tiempo.endswith("d"):
        duracion = int(tiempo[:-1]) * 86400
    else:
        await ctx.send("❌ Formato de tiempo inválido. Usa s, m, h o d.")
        return

    rol = discord.utils.get(ctx.guild.roles, name="Muted")
    if not rol:
        rol = await ctx.guild.create_role(name="Muted")
        for canal in ctx.guild.channels:
            await canal.set_permissions(rol, send_messages=False)

    await miembro.add_roles(rol)
    await ctx.send(f"🔇 {miembro.mention} ha sido silenciado por {tiempo}.")

    await asyncio.sleep(duracion)
    await miembro.remove_roles(rol)
    await ctx.send(f"🔊 {miembro.mention} ya no está silenciado.")

# $unmute @usuario - Quita el silencio
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, miembro: discord.Member):
    rol = discord.utils.get(ctx.guild.roles, name="Muted")
    if rol in miembro.roles:
        await miembro.remove_roles(rol)
        await ctx.send(f"🔊 {miembro.mention} ya no está silenciado.")
    else:
        await ctx.send("❌ Ese usuario no está silenciado.")

# $rol <usuario> <rol> - Asigna un rol a un usuario
@bot.command()
@commands.has_permissions(manage_roles=True)
async def rol(ctx, miembro: discord.Member, *, nombre_rol):
    rol = discord.utils.get(ctx.guild.roles, name=nombre_rol)
    if rol:
        await miembro.add_roles(rol)
        await ctx.send(f"✅ {miembro.mention} ahora tiene el rol `{nombre_rol}`.")
    else:
        await ctx.send("❌ Rol no encontrado.")
# $dltrol
@bot.command()
async def dltrol(ctx, member: discord.Member, *, role: discord.Role):
    """Quita un rol a un usuario. Solo para administradores."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ No tienes permisos de administrador para usar este comando.")
        return

    if role not in member.roles:
        await ctx.send(f"⚠️ El usuario {member.display_name} no tiene el rol {role.name}.")
        return

    try:
        await member.remove_roles(role)
        await ctx.send(f"✅ Se ha quitado el rol **{role.name}** de {member.display_name}.")
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos suficientes para quitar ese rol.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Hubo un error al quitar el rol: {e}")

#BRILLO DE LA PC
@bot.command()
async def brillo(ctx, porcentaje: int):
    if not 0 <= porcentaje <= 100:
        await ctx.send("El brillo debe estar entre 0 y 100.")
        return

    try:
        sbc.set_brightness(porcentaje)
        await ctx.send(f"💡 Brillo ajustado al {porcentaje}%.")
    except Exception as e:
        await ctx.send(f"No se pudo ajustar el brillo: {e}")

#VOLUMEN
@bot.command()
async def volumen(ctx, porcentaje: int):
    if not 0 <= porcentaje <= 100:
        await ctx.send("El volumen debe estar entre 0 y 100.")
        return

    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Convertir el porcentaje a decibelios (rango entre -65.25 y 0)
        min_vol, max_vol = volume.GetVolumeRange()[:2]
        db_vol = min_vol + (porcentaje / 100) * (max_vol - min_vol)
        volume.SetMasterVolumeLevel(db_vol, None)

        await ctx.send(f"Volumen ajustado al {porcentaje}%.")
    except Exception as e:
        await ctx.send(f"No se pudo cambiar el volumen: {e}")

#OFF
@bot.command()
@commands.has_permissions(administrator=True)
async def off(ctx):
    confirm_msg = await ctx.send("¿Estás seguro de que quieres **apagar** la PC? Reacciona con ✅ para confirmar.")
    await confirm_msg.add_reaction("✅")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirm_msg.id

    try:
        await bot.wait_for("reaction_add", timeout=20.0, check=check)
        await ctx.send("Apagando la PC en 5 segundos...")
        await asyncio.sleep(5)
        os.system("shutdown /s /t 1")
    except asyncio.TimeoutError:
        await ctx.send("Tiempo agotado. Cancelado.")

@bot.command()
@commands.has_permissions(administrator=True)
async def rboot(ctx):
    confirm_msg = await ctx.send("¿Estás seguro de que quieres **reiniciar** la PC? Reacciona con ✅ para confirmar.")
    await confirm_msg.add_reaction("✅")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirm_msg.id

    try:
        await bot.wait_for("reaction_add", timeout=20.0, check=check)
        await ctx.send("Reiniciando la PC en 5 segundos...")
        await asyncio.sleep(5)
        os.system("shutdown /r /t 1")
    except asyncio.TimeoutError:
        await ctx.send("Tiempo agotado. Cancelado.")


# Variable global para poder detener el monitoreo desde $mntoff
monitoring_task = None

EXCLUDED_USERS = {1221348290982056098, 1358591377688100966}

monitoring_task = None
procesos_tasks = {}

#MONITOR
@bot.command()
@commands.has_permissions(administrator=True)
async def monitor(ctx, action: str = None):
    """Monitorea CPU y RAM en tiempo real.
    Uso: $monitor start | $monitor stop
    Solo admins pueden usarlo."""
    global monitoring_task

    if action not in ("start", "stop"):
        await ctx.send("Uso incorrecto. Usa `$monitor start` para iniciar o `$monitor stop` para detener.")
        return

    if action == "start":
        if monitoring_task is not None and not monitoring_task.done():
            await ctx.send("⚠️ Ya hay un monitoreo en curso. Usa `$monitor stop` para detenerlo.")
            return

        mensaje = await ctx.send("🔍 Iniciando monitoreo en tiempo real...")

        async def monitorear():
            for _ in range(180):  # 3 minutos
                uso_cpu = psutil.cpu_percent(interval=0.8)
                ram = psutil.virtual_memory()
                ram_porcentaje = ram.percent

                texto = (
                    "**🖥️ Monitoreo en tiempo real:**\n"
                    f"🧠 CPU: {uso_cpu}%\n"
                    f"📦 RAM: {ram.used // (1024 ** 2)}MB / {ram.total // (1024 ** 2)}MB ({ram_porcentaje}%)\n"
                    "_Actualizando cada segundo. Usa `$monitor stop` para detener._"
                )

                try:
                    await mensaje.edit(content=texto)
                except discord.HTTPException:
                    break

                if uso_cpu > 90:
                    await ctx.send("⚠️ **ALERTA:** CPU ha superado el 90%")
                if ram_porcentaje > 90:
                    await ctx.send("⚠️ **ALERTA:** RAM ha superado el 90%")

                await asyncio.sleep(0.2)  # para completar el segundo

            try:
                await mensaje.edit(content="✅ Monitoreo finalizado tras 3 minutos.")
            except discord.HTTPException:
                pass

        monitoring_task = asyncio.create_task(monitorear())
        return

    # action == "stop"
    if monitoring_task is not None and not monitoring_task.done():
        monitoring_task.cancel()
        monitoring_task = None
        await ctx.send("🛑 Monitoreo detenido manualmente.")
    else:
        await ctx.send("⚠️ No hay ningún monitoreo en curso.")


@bot.command()
async def procesos(ctx, action: str = None):
    """
    Monitorea procesos (top 10 por RAM).
    Uso: $procesos start | $procesos stop
    Solo usuarios en EXCLUDED_USERS pueden usarlo.
    """
    if ctx.author.id not in EXCLUDED_USERS:
        await ctx.send("❌ No tienes permiso para usar este comando.")
        return

    if action not in ("start", "stop"):
        await ctx.send("Uso incorrecto. Usa `$procesos start` para iniciar o `$procesos stop` para detener.")
        return

    if action == "start":
        if procesos_tasks.get(ctx.author.id, None) is not None and not procesos_tasks[ctx.author.id].done():
            await ctx.send("⚠️ Ya tienes un monitoreo de procesos en curso. Usa `$procesos stop` para detenerlo.")
            return

        message = await ctx.send("Iniciando monitoreo de procesos...")

        async def monitorear_procesos():
            top_count = 10
            monitor_duration = 180
            update_interval = 1
            start_time = asyncio.get_event_loop().time()

            def format_memory(bytes_amount):
                return f"{bytes_amount / (1024 ** 2):.2f} MB"

            while True:
                procesos = sorted(
                    psutil.process_iter(['pid', 'name', 'memory_info']),
                    key=lambda p: p.info['memory_info'].rss if p.info['memory_info'] else 0,
                    reverse=True
                )[:top_count]

                lines = []
                for p in procesos:
                    pid = p.info['pid']
                    name = p.info['name'] or "Desconocido"
                    mem = format_memory(p.info['memory_info'].rss) if p.info['memory_info'] else "N/A"
                    lines.append(f"PID: `{pid}` | Nombre: `{name}` | Memoria: `{mem}`")

                embed = discord.Embed(
                    title="🖥️ Monitor de Procesos (Top 10 por RAM)",
                    description="\n".join(lines),
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Monitoreo activo por 3 minutos - Actualización cada {update_interval} segundo(s)")

                try:
                    await message.edit(embed=embed)
                except discord.HTTPException:
                    break

                if asyncio.get_event_loop().time() - start_time > monitor_duration:
                    await message.edit(content="⏰ Tiempo de monitoreo finalizado (3 minutos).")
                    procesos_tasks.pop(ctx.author.id, None)
                    break

                await asyncio.sleep(update_interval)

        task = asyncio.create_task(monitorear_procesos())
        procesos_tasks[ctx.author.id] = task
        return

    # action == "stop"
    task = procesos_tasks.get(ctx.author.id, None)
    if task is not None and not task.done():
        task.cancel()
        procesos_tasks.pop(ctx.author.id, None)
        await ctx.send("🛑 Monitoreo de procesos detenido manualmente.")
    else:
        await ctx.send("⚠️ No tienes ningún monitoreo de procesos activo para detener.")

@bot.command()
@commands.has_permissions(administrator=True)
async def stopall(ctx):
    """Detiene todos los monitoreos activos (CPU/RAM y procesos). Solo admins."""
    global monitoring_task
    stopped_any = False

    if monitoring_task is not None and not monitoring_task.done():
        monitoring_task.cancel()
        monitoring_task = None
        stopped_any = True

    for user_id, task in list(procesos_tasks.items()):
        if not task.done():
            task.cancel()
            procesos_tasks.pop(user_id)
            stopped_any = True

    if stopped_any:
        await ctx.send("🛑 Todos los monitoreos activos han sido detenidos.")
    else:
        await ctx.send("⚠️ No hay monitoreos activos para detener.")

# Lista de IDs de usuarios permitidos (además de los administradores)
USUARIOS_PERMITIDOS_KILL = [1365834204927098940, 1358591377688100966]  # Reemplaza con los IDs reales

@bot.command()
async def kill(ctx, pid: int):
    """Finaliza un proceso por su PID. Permitido solo para admins o usuarios autorizados."""

    # Verifica si el usuario es admin o está en la lista de permitidos
    es_admin = ctx.author.guild_permissions.administrator
    es_permitido = ctx.author.id in USUARIOS_PERMITIDOS_KILL

    if not es_admin and not es_permitido:
        await ctx.send("⛔ No tienes permiso para usar este comando.")
        return

    try:
        proceso = psutil.Process(pid)
        nombre = proceso.name()
        proceso.terminate()
        proceso.wait(timeout=3)
        await ctx.send(f"✅ Proceso `{nombre}` (PID: {pid}) terminado correctamente.")
    except psutil.NoSuchProcess:
        await ctx.send(f"❌ No se encontró un proceso con PID {pid}.")
    except psutil.AccessDenied:
        await ctx.send(f"⛔ Permisos insuficientes para terminar el proceso con PID {pid}.")
    except psutil.TimeoutExpired:
        await ctx.send(f"⚠️ El proceso con PID {pid} no respondió a la señal de terminación.")
    except Exception as e:
        await ctx.send(f"❌ Error al intentar finalizar el proceso: `{e}`.")



# moderator
cpt = os.path.dirname(os.path.abspath(__file__))
moderator = os.path.join(cpt, "moderador.exe")
JSON_FILE = os.path.join(cpt, "badwords.json")

def cargar_palabras():
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_palabras(palabras):
    with open(JSON_FILE, "w") as f:
        json.dump(palabras, f, indent=2)

@bot.command()
@commands.has_permissions(administrator=True)
async def addbadword(ctx, palabra):
    palabra = palabra.lower()
    palabras = cargar_palabras()
    if palabra not in palabras:
        palabras.append(palabra)
        guardar_palabras(palabras)
        await ctx.send(f"✅ Palabra '{palabra}' añadida.")
    else:
        await ctx.send("⚠️ Esa palabra ya está en la lista.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removebadword(ctx, palabra):
    palabra = palabra.lower()
    palabras = cargar_palabras()
    if palabra in palabras:
        palabras.remove(palabra)
        guardar_palabras(palabras)
        await ctx.send(f"✅ Palabra '{palabra}' eliminada.")
    else:
        await ctx.send("⚠️ Esa palabra no está en la lista.")

def moderar_mensaje(mensaje: str) -> str:
    print(f"Ejecutando moderador.exe con mensaje: {mensaje}")
    if not os.path.exists(moderator):
        print(f"⚠️ No se encontró el ejecutable: {moderator}")
        return "permitido"
    try:
        proceso = subprocess.Popen(
            [moderator],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            cwd=cpt
        )
        salida, err = proceso.communicate(mensaje)
        print(f"Salida Rust: {salida.strip()}")
        if err:
            print(f"Error Rust: {err.strip()}")
        return salida.strip()
    except Exception as e:
        print(f"⚠️ Error al ejecutar moderador.exe: {e}")
        return "permitido"

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"Mensaje recibido: {message.content}")
    resultado = moderar_mensaje(message.content)
    print(f"Resultado moderación: {resultado}")

    if resultado == "bloqueado":
        print(f"Borrando mensaje de {message.author} por palabra prohibida.")
        await message.delete()
        await message.channel.send(
            f"🚫 {message.author.mention}, tu mensaje contenía palabras prohibidas.",
            delete_after=5
        )

    await bot.process_commands(message)

#PROCESO DE ARRANQUE DEL BOT.
bot.run(DISCORD_BOT_TOKEN)