from config import get_api_key
import http.client
import json
import base64
import random
import time

KEY = get_api_key("secrets.txt")

conn = http.client.HTTPSConnection("api.venice.ai")

def request(method, endpoint, payload, headers):
    conn.request(method, endpoint, payload, headers)
    response = conn.getresponse()
    print_rate_info(response)
    return response.read()
     
def jsonfy(data):
    try:
        data = json.loads(data.decode("utf-8"))
        data = {key: value for key, value in data.items() if key != "images"}  # remove binary image data if applicable
       
        return(json.dumps(data, indent=4))  # Pretty-print with indentation
    except json.JSONDecodeError:
        print("Response is not in JSON format:")
        return(data.decode("utf-8"))

def print_rate_info(response):
    rate_limit = response.headers.get("x-ratelimit-limit-requests")
    if(rate_limit):
        print("Rate Limit:", response.headers.get("x-ratelimit-limit-requests"))
        print("Remaining Requests:", response.headers.get("x-ratelimit-remaining-requests"))
        print("Reset Time:", response.headers.get("x-ratelimit-reset-requests"))

def get_models():
    headers = {'Authorization': f'Bearer {KEY}' }
    payload = ""
    response = request("GET", "/api/v1/models", payload, headers)
    print(jsonfy(response))



def chat_completion(prompt):
    payload = json.dumps({
        "model": "dolphin-2.9.2-qwen2-72b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }).encode('utf-8')
    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }

    response = request("POST", "/api/v1/chat/completions", payload, headers)
    print(jsonfy(response))


styles = ["3D Model", "Analog Film", "Anime", "Cinematic", "Comic Book", "Craft Clay", "Digital Art", "Enhance", "Fantasy Art", "Isometric Style", "Line Art", "Lowpoly", "Neon Punk", "Origami", "Photographic", "Pixel Art", "Texture", "Advertising", "Food Photography", "Real Estate", "Abstract", "Cubist", "Graffiti", "Hyperrealism", "Impressionist", "Pointillism", "Pop Art", "Psychedelic", "Renaissance", "Steampunk", "Surrealist", "Typography", "Watercolor", "Fighting Game", "GTA", "Super Mario", "Minecraft", "Pokemon", "Retro Arcade", "Retro Game", "RPG Fantasy Game", "Strategy Game", "Street Fighter", "Legend of Zelda", "Architectural", "Disco", "Dreamscape", "Dystopian", "Fairy Tale", "Gothic", "Grunge", "Horror", "Minimalist", "Monochrome", "Nautical", "Space", "Stained Glass", "Techwear Fashion", "Tribal", "Zentangle", "Collage", "Flat Papercut", "Kirigami", "Paper Mache", "Paper Quilling", "Papercut Collage", "Papercut Shadow Box", "Stacked Papercut", "Thick Layered Papercut", "Alien", "Film Noir", "HDR", "Long Exposure", "Neon Noir", "Silhouette", "Tilt-Shift"]

    
def image_gen(prompt, x, y, seed, style, model="stable-diffusion-3.5", file_name = "", steps = 50):
    if(len(file_name) == 0):
        file_name=f"{prompt.lower().replace(' ','-')}_{seed}_{style}.png"

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "width": x,
        "height": y,
        "steps": steps,
        "hide_watermark": True,
        "return_binary": True,
        "seed": seed,
        "cfg_scale": 10,
        **({"style_preset": style} if style is not None else {}),  # Conditionally added
        "negative_prompt": "",
        "safe_mode": False
    }).encode('utf-8')

    #print(style, payload)

    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }

    response = request("POST", "/api/v1/image/generate", payload, headers)
    #print(response)

    with open("results/"+file_name, "wb") as image_file:
        image_file.write(response)
        print(f"Image saved as '{file_name}'")


def step_animation(prompt, x, y, seed, style, max_steps, model="stable-diffusion-3.5"):
    print(f"Starting Step Animation up to {max_steps} Steps:")
    print(f"Seed: {seed} ; Style: {style}")
    for i in range(1, max_steps + 1):
        image_gen(prompt, x = x, y = y, seed = seed, model=model, style=style, steps=i, file_name=f"{prompt.lower().replace(" ", "-")}_{seed}_{model}_{style}_{i}.png")

def seed_explorer(prompt, style, start_seed = 0, max_seeds = 50, x = 1280, y = 1280, model="stable-diffusion-3.5"):
    print(f"Starting Seed Explorer up to {max_seeds} Seeds:")
    print(f"Prompts: {prompt}, Style: {style}, model: {model}")
    for i in range(start_seed, start_seed+max_seeds):
        image_gen(prompt, x = x, y = y, seed = i, model=model, style=style, steps=50, file_name=f"{prompt.lower().replace(" ", "-")}_{i}_{model}_{style}_{i}.png")


#get_models()

#chat_completion("Give me an interesting image prompt for ai,something special")


#image_gen("Test", x = 960, y = 960, seed = random.randint(0, 99999), style=random.choice(styles))

#image_gen("Test", x = 960, y = 960, seed = 123, style="Cinematic")

#step_animation("Bob WOOOOOO LAAAAALA", 960, 960, model="stable-diffusion-3.5", seed = random.randint(0, 99999), style=random.choice(styles), max_steps=50)

#step_animation("Heaven", 1280, 1280, model="stable-diffusion-3.5", seed = random.randint(0, 99999), style=random.choice(styles), max_steps=50)

#step_animation("", 1280, 1280, model="lustify-sdxl", seed = random.randint(0, 99999), style="Photographic", max_steps=50)

seed_explorer("Eliptic Curve Cryptography", style=None, start_seed=random.randint(0, 99999), max_seeds = 500)
#"Abstract", "Cubist", "Graffiti", "Hyperrealism", "Impressionist", "Pointillism",


#image_gen("Explosion HD", x = 1280, y = 1280, seed = random.randint(0, 99999), model="flux-dev", style="HDR", steps=50, file_name="image.png")

