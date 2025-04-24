import discord
import torch
import clip
import requests
import io
import os
from PIL import Image
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Webserver para manter o bot online no Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Harpy voando alto!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# Discord e IA
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
tags = ["gore", "nudity", "violence", "blood", "weapon", "porn", "gun", "knife", "sex", "dead body", "fight"]
text_inputs = torch.cat([clip.tokenize(f"a photo of {t}") for t in tags]).to(device)
bad_words = ['puto', 'puta', 'caralho', 'fdp', 'desgraça', 'merda', 'buceta', 'viado']

async def analyze_image_url(url):
    response = requests.get(url)
    image = Image.open(io.BytesIO(response.content)).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits_per_image, _ = model(image_input, text_inputs)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

    result = {tags[i]: float(probs[i]) for i in range(len(tags)) if probs[i] > 0.3}
    return result

@bot.event
async def on_ready():
    print(f"[+] Harpy está online como {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        await message.channel.send(f"[MOD-IA] Linguagem ofensiva detectada de {message.author.mention}")

    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".mp4"]):
            detections = await analyze_image_url(attachment.url)
            if detections:
                await message.delete()
                alert = f"**[ALERTA] Conteúdo suspeito detectado de {message.author.mention}:**
"
                for k, v in detections.items():
                    alert += f"- `{k}`: {round(v * 100, 2)}%
"
                await message.channel.send(alert)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.run(TOKEN)