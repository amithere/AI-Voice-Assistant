import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

def open_images(prompt):
    folder_path = r"Data"
    prompt = prompt.replace(" ", "")

    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)

        except IOError:
            print(f"Unable to open {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
api_key = get_key('.env', 'HUGGING_FACE_API_KEY')
if not api_key:
    raise ValueError("HUGGING_FACE_API_KEY not found in .env file")
headers = {"Authorization": f"Bearer {api_key}"}
#headers = {"Authorization": f"Bearer {get_key('.env', 'HUGGING_FACE_API_KEY')}"}

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

    if response.status_code == 200 and response.headers['content-type'].startswith("image/"):
        return response.content
    else:
        print("Failed to generate image:", response.status_code, response.text)
        return b""

async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High Details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        # with open(fr"Data/{prompt.replace(' ', '')}{i + 1}.jpg", "wb") as File:
        #     File.write(image_bytes)
        if image_bytes:
            file_path = f"Data/{prompt.replace(' ','')}{i + 1}.jpg"
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            print(f"[INFO] Saved: {file_path}")
        else:
            print(f"[WARNING] Image {i+1} not saved due to empty response.")

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        with open(r"Frontend/Files/ImageGeneration.data", "r") as File:
            Data: str = File.read()

        Prompt, Status = Data.split(",")

        if (Status == "True"):
            print(f"Generating Images...")
            ImageStatus = GenerateImages(prompt=Prompt)

            with open(r"Frontend/Files/ImageGeneration.data", "w") as File:
                File.write("False,False")
                break

        else:
            sleep(1)

    except:
        pass 


# if __name__ == "__main__":
#     GenerateImages("a sunset over a mountain")