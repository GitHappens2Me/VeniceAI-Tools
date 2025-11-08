from helper import get_api_key
from api_client import *
import http.client
import json
import base64
import random
import time

places = [
    "paris", 
    "hell", 
    "summer", 
    "nighttime", 
    "beach",
    "tokyo street at night",
    "enchanted forest",
    "underwater coral reef",
    "mars surface",
    "victorian library",
    "cyberpunk city",
    "ancient greek ruins",
    "snowy mountain peak",
    "nebula in space",
    "medieval castle",
    "tropical rainforest",
    "abandoned warehouse",
    "sahara desert",
    "northern lights",
    "viking village"
]


prompt = "Make the lake slightly larger without changing anything about the rest of the image"
#prompt_template = "Change nothing about the image except the background. Change the Background to "
last_image = "./input4.jpg"

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

for i in range(25):

    #prompt = prompt_template + random.choice(places)

    output_filename = f"{prompt.replace(" ", "_").replace(".", "_").replace("/", "_").strip()}_{i}.png"
    full_output_path = f"results/inpaint/{output_filename}"
    


    try:
        image_inpaint(prompt, last_image, file_name=output_filename)
        # Update last_image to the full path of the newly created image
        last_image = full_output_path
        print(f"Successfully created {output_filename}")
        
        
    except ValueError as e:
        print(f"Failed to create {output_filename}: {e}")
        # Stop the loop if there's an error
        break