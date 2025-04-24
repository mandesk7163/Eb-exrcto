# Harpy Bot para Render

Bot de moderação com IA para detectar conteúdo impróprio em imagens, vídeos e mensagens de texto no Discord.

## Setup

1. Suba este projeto como Web Service no [Render](https://render.com)
2. Configure a variável de ambiente DISCORD_BOT_TOKEN no painel do Render, ou edite o arquivo `.env`
3. Comando de build:
    pip install -r requirements.txt
4. Comando de start:
    python main.py

## Segurança
**Nunca poste seu token de bot em público!** Use sempre `.env` ou as variáveis de ambiente da plataforma.