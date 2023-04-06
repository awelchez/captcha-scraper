import httpx
import logging
import threading
import random
import secrets
from PIL import Image
import os
import concurrent.futures
import datetime, pystyle, colorama, sys
from colorama import Fore, Style

lock = threading.Lock()


class Console:
    def __init__(self, level):
        self.level = level
        self.color_map = {
            "INFO": (Fore.LIGHTMAGENTA_EX, "+"),
            "INFO2": (Fore.LIGHTYELLOW_EX, "*"),
            "INFO3": (Fore.LIGHTBLUE_EX, "#"),
            "INFO4": (Fore.LIGHTCYAN_EX, "~"),
            "CAPTCHA": (Fore.LIGHTMAGENTA_EX, "C"),
            "ERROR": (Fore.LIGHTRED_EX, "!"),
            "SUCCESS": (Fore.LIGHTGREEN_EX, "$")
        }
        colorama.init()

    def log(self, *args, **kwargs):
        color, text = self.color_map.get(self.level, (Fore.LIGHTWHITE_EX, self.level))
        time_now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]

        base = f"[{Fore.LIGHTBLACK_EX}{time_now}{Fore.RESET}] ({color}{text.upper()}{Fore.RESET})"
        for arg in args:
            base += f"{Fore.RESET} {arg}"
        if kwargs:
            base += f"{Fore.RESET} {arg}"
        lock.acquire()
        print(base)
        lock.release()

hf_id = secrets.token_hex(16)

class generator():
    def __init__(self):
        self.hf_id = hf_id
        self.session = httpx.Client()
        self.data_directory = 'data'

    def generateCaptcha(self):
        url: str = f"https://client.hip.live.com/GetHIP/GetHIPAMFE/HIPAMFE?id=15041&mkt=en-US&fid" \
                   f"={self.hf_id}&type=visual&rand={random.randint(0, 1000000)}"
        data: str = self.session.get(url, headers={
            "Accept-Encoding": "identity"
        }).text
        dcid: str = data.split('"dataCenter":"')[1].split('"')[0]
        ht: str = data.split('"hipToken":"')[1].split('"')[0].split(".")[1]
        self.ht = dcid + "." + ht
        image_url: str = f"https://{dcid}.client.hip.live.com/GetHIPData?hid={dcid}" \
                     f".{ht}&fid={self.hf_id}" \
                     f"&id=15041&type=visual&cs=HIPAMFE"
        image_bytes: bytes = httpx.get(image_url).content

        image_filename = os.path.join(self.data_directory, f"{secrets.token_hex(16)}.jpg")
        with open(image_filename, "wb") as f:
            f.write(image_bytes)

        image = Image.open(image_filename)

        return image

generate = generator()

if not os.path.exists(generate.data_directory):
    os.makedirs(generate.data_directory)

with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
    for i in range(100):
        executor.submit(generate.generateCaptcha)
        executor.submit(Console("SUCCESS").log("Successfuly scraped " + f"{secrets.token_hex(16)}.jpg"))

quit()

