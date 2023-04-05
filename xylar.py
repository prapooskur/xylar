import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import json
import io
import base64
from PIL import Image, PngImagePlugin

from dotenv import load_dotenv
load_dotenv()

intents=discord.Intents.default()
intents.message_content = True #v2

bot = commands.Bot(command_prefix="/",intents=intents)

sdurl = os.getenv('SDURL')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    try:
        synced=await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"error syncing commands: {e}")
    
@bot.tree.command(name='simulate', description="generate an image with stable-diffusion-webui api")
async def simulate(interaction: discord.Interaction, prompt: str, negativeprompt: str="", batchsize: int=1, seed: int=-1):
    if batchsize>4:
        batchsize=4
    payload = {
        "prompt": prompt,
        "negative_prompt": negativeprompt,
        "batch_size": 1,
        "seed": seed
    }
    if (negativeprompt == ""):
        print("requesting prompt "+prompt+" with no negative prompt")
    else:
        print("requesting prompt "+prompt+" with negative prompt "+negativeprompt)
    response = requests.post(url=f'{sdurl}/sdapi/v1/txt2img', json=payload)
    imagelist=response.json().get("images","")
    for i in imagelist:
        outputimg = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        outputimg.save('output.png')
    await interaction.response.send_message(file=discord.File(outputimg))

@bot.tree.command(name='sync', description='sync commands with discord')
async def sync(interaction: discord.Interaction):
    try:
        synced=await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        interaction.response.send_message(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"error syncing commands: {e}")
        interaction.response.send_message(f"error syncing commands: {e}")


bot.run(os.getenv('TOKEN'))
