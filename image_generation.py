from helper import get_api_key
from api_client import *
import http.client
import json
import base64
import random
import time


styles = ["3D Model", "Analog Film", "Anime", "Cinematic", "Comic Book", "Craft Clay", "Digital Art", "Enhance", "Fantasy Art", "Isometric Style", "Line Art", "Lowpoly", "Neon Punk", "Origami", "Photographic", "Pixel Art", "Texture", "Advertising", "Food Photography", "Real Estate", "Abstract", "Cubist", "Graffiti", "Hyperrealism", "Impressionist", "Pointillism", "Pop Art", "Psychedelic", "Renaissance", "Steampunk", "Surrealist", "Typography", "Watercolor", "Fighting Game", "GTA", "Super Mario", "Minecraft", "Pokemon", "Retro Arcade", "Retro Game", "RPG Fantasy Game", "Strategy Game", "Street Fighter", "Legend of Zelda", "Architectural", "Disco", "Dreamscape", "Dystopian", "Fairy Tale", "Gothic", "Grunge", "Horror", "Minimalist", "Monochrome", "Nautical", "Space", "Stained Glass", "Techwear Fashion", "Tribal", "Zentangle", "Collage", "Flat Papercut", "Kirigami", "Paper Mache", "Paper Quilling", "Papercut Collage", "Papercut Shadow Box", "Stacked Papercut", "Thick Layered Papercut", "Alien", "Film Noir", "HDR", "Long Exposure", "Neon Noir", "Silhouette", "Tilt-Shift"]


def step_animation(prompt, x, y, seed, style, max_steps, model="stable-diffusion-3.5"):
    print(f"Starting Step Animation up to {max_steps} Steps:")
    print(f"Seed: {seed} ; Style: {style}")
    for i in range(1, max_steps + 1):
        image_gen(prompt, x = x, y = y, seed = seed, model=model, style=style, steps=i, file_name=f"{prompt.lower().replace(" ", "-")}_{seed}_{model}_{style}_{i}.png")

def seed_explorer(prompt, style, start_seed = 0, max_seeds = 50, x = 1280, y = 1280, model="stable-diffusion-3.5"):
    print(f"Starting Seed Explorer up to {max_seeds} Seeds:")
    print(f"Prompt: {prompt}, Style: {style}, model: {model}")
    for i in range(start_seed, start_seed+max_seeds):
        image_gen(prompt, x = x, y = y, seed = i, model=model, style=style, steps=30, file_name=f"{prompt.lower().replace(" ", "-")}_{i}_{model}_{style}_{i}.png")

## Returns a list of all Models available
#get_models()

## Simple Chat Completion
#print(extract_message(chat_completion("Why is the sky blue?", "user", model = "llama-3.3")))

## Simple Image Generation
#image_gen("Heaven", x = 960, y = 960, seed = random.randint(0, 99999), style=random.choice(styles))

## Generates an Image at each Step of the Generation Process
#step_animation("Heaven", 1280, 1280, seed = random.randint(0, 99999), style="Photographic", max_steps=30, model="stable-diffusion-3.5")

## Generates an Image for each Seed in a given Range
#seed_explorer("Eliptic Curve Cryptography", style=None, start_seed=random.randint(0, 99999), max_seeds = 500)

