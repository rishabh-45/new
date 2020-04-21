import requests
import re
from difflib import SequenceMatcher
import sys
import subprocess
import os
import asyncio
from uniborg.util import admin_cmd

url="https://chromedriver.chromium.org/downloads"
pat=r"https://chromedriver.storage.googleapis.com/index.html[\w?=.]+"

def getResponse(version_needed):
    response=requests.get(url)
    # print("Getting for",version_needed)
    links=re.findall(pat,response.text)
    bestlink=""
    ratiobest=0

    for link in links:
        ratio=SequenceMatcher(a=version_needed,b=link).ratio()
        # print("current rat ",ratio)
        if ratio>ratiobest:
            ratiobest=ratio
            bestlink=link
    return bestlink

async def run(event,caller="None"):
    try:
        await event.edit("Running from "+caller)
        await asyncio.sleep(1)
        zz=subprocess.run(['google-chrome', '--version'],stdout=subprocess.PIPE)
        version=re.findall(r'[\d.]+',str(zz.stdout))[0]
        print(f"Current Chrome Version->{version}")
        await event.edit("Chrome version-> "+version)
        await asyncio.sleep(2)

        link=getResponse(version)
        print(f"Best Available link->{link}")

        version_available=re.findall(r'\d[\d.]+',link)[0]

        # print(version_available)

        url1="https://chromedriver.storage.googleapis.com/"
        url2="/chromedriver_linux64.zip"
        driver_url=url1+version_available+url2

        print("Formed Link->",driver_url)
        await event.edit("Getting from "+driver_url)
        await asyncio.sleep(2)

        cmdlist=[]
        cmdlist.append("wget "+driver_url)

        cmdlist.append("unzip -o chromedriver_linux64.zip -d /app/.chromedriver/bin/")

        cmdlist.append("unzip -o chromedriver_linux64.zip -d stdplugins/")



        cmdlist.append("rm chrome*.zip*")


        for cmd in cmdlist:
            print("Executing ",cmd)
            await event.edit("Executing "+f"`{cmd}`")
            # await asyncio.sleep(1)
            os.system(cmd)
        return "Successfully Done"
    except Exception as e:
        print ("Error ",e)
        return "Error"+str(e)
#commands
# unzip -o chromedriver_linux64.zip -d /app/.chromedriver/bin/
# unzip -o chromedriver_linux64.zip 

# rm chrome*.zip*


