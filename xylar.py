import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp  
import asyncio
import json
import io
import base64
from PIL import Image, PngImagePlugin
from typing import Literal

from dotenv import load_dotenv
load_dotenv()

intents=discord.Intents.default()
intents.message_content = True #v2

bot = commands.Bot(command_prefix="/",intents=intents)

sdurl = os.getenv('SDURL')
outlist=[[discord.File('output1.png')],[discord.File('output1.png'),discord.File('output2.png')],[discord.File('output1.png'),discord.File('output2.png'),discord.File('output3.png')],[discord.File('output1.png'),discord.File('output2.png'),discord.File('output3.png'),discord.File('output4.png')]]

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    try:
        synced=await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"error syncing commands: {e}")
    
@bot.tree.command(name='simulate', description="generate an image with stable-diffusion-webui api")
async def simulate(interaction: discord.Interaction, prompt: str, negativeprompt: str="", batchsize: Literal[tuple([i for i in range(0,19)])] = 0, seed: int=-1):

    if batchsize>4:
        batchsize=4
    url = sdurl+'/sdapi/v1/txt2img'
    print("url is "+url)
    payload = {
        "prompt": prompt,
        "negative_prompt": negativeprompt,
        "batch_size": batchsize,
        "seed": seed
    }
    if (negativeprompt == ""):
        print("requesting prompt "+prompt+" with no negative prompt")
    else:
        print("requesting prompt "+prompt+" with negative prompt "+negativeprompt)
    async with aiohttp.ClientSession() as session:
            await interaction.response.defer()
            print("starting")
            async with session.post(url,json=payload) as response:
                output=await response.json()
                imagelist=output.get("images","")
                count=0
                outfiles=outlist[batchsize-1]
                for i in imagelist:
                    outputimg = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
                    count+=1
                    filename="output"+str(count)+".png"
                    outputimg.save(filename)
                outfiles=[discord.File('output1.png'),discord.File('output2.png'),discord.File('output3.png'),discord.File('output4.png')]
            await interaction.followup.send(files=outfiles)


bot.run(os.getenv('TOKEN'))
