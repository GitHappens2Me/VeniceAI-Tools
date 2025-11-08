from helper import get_api_key
from api_client import *
import threading
import re
import random 
import os
import time

def generate_and_create_images(topic, number_of_images = 10, image_model = "Venice-SD35", text_model = "Uncencored"):
    """
    Generate prompts using a text AI model and then create images based on those prompts
    
    Args:
        topic (str): The topic/concept for which to generate image prompts
    """
    # Step 1: Get prompts from text AI
    prompt_request = f"Write me a list of {number_of_images} well though-out prompts I can then give to an image generator to generate the best possible images of '{topic}'. Be creative but follow the topic. Be detailed and write sufficiantly long prompts. Split the prompts using empty lines. Do not format them in any other way." #Return exactly one prompt per line with no numbering."
    print(f"Prompt: '{prompt_request}'")
    # Use llama-3.3 for prompt generation
    response = chat_completion(prompt_request, "user", text_model, strip_thinking=True)
    prompts_text = extract_message(response)
    print(f"Response:\n{prompts_text}")
    
    # Extract prompts
    prompts = [line.strip() for line in prompts_text.strip().split('\n') if line.strip()]

    print(f"Generated {len(prompts)} prompts for topic: {topic}")
    for i, prompt in enumerate(prompts):
        print(f"{i}: {prompt}")

    if not prompts:
        print("No prompts found in the response")
        return
    
    # Step 2: Generate images for each prompt using threads
    threads = []
    
    def generate_image_for_prompt(index, prompt):
        """Generate a single image for a given prompt"""
        folder_path = f"prompt_assisted/{topic.lower().replace(' ', '-')}"
        os.makedirs(f"results/"+ folder_path, exist_ok=True)
        filename = f"{folder_path}/{index+1}.png"
        try:
            image_gen(
                prompt=prompt,
                x=1280,
                y=1280,
                seed = random.randint(0, 99999),  # Let Venice choose random seed
                style=None,  # No specific style
                model=image_model,
                file_name=filename,
                steps=30
            )
            print(f"Generated image {index+1}: {filename}")
        except Exception as e:
            print(f"Error generating image {index+1}: {e}")
    
    BATCH_SIZE = 20
    DELAY_BETWEEN_BATCHES = 60  # 10 seconds

    print(f"Starting generation for {len(prompts)} images in batches of {BATCH_SIZE}.")

    # Process prompts in chunks (batches)
    for i in range(0, len(prompts), BATCH_SIZE):
        # Get the current batch of prompts
        batch = prompts[i:i + BATCH_SIZE]
        batch_number = (i // BATCH_SIZE) + 1
        
        print(f"\n--- Starting Batch {batch_number} (Images {i+1} to {i+len(batch)}) ---")
        
        threads = []
        
        # Create and start a thread for each prompt in the current batch
        for prompt_index, prompt_text in enumerate(batch):
            actual_index = i + prompt_index
            thread = threading.Thread(
                target=generate_image_for_prompt,
                args=(actual_index, prompt_text),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            # Optional: A very small delay here can still be helpful to smooth the initial request spike
            time.sleep(0.1)

        # Wait for all threads in the current batch to complete
        print(f"Waiting for {len(threads)} threads in Batch {batch_number} to finish...")
        for thread in threads:
            thread.join()
            
        print(f"--- Batch {batch_number} Complete ---")

        # If there are more prompts left to process, wait before starting the next batch
        if i + BATCH_SIZE < len(prompts):
            print(f"Waiting for {DELAY_BETWEEN_BATCHES} seconds before starting the next batch...")
            time.sleep(DELAY_BETWEEN_BATCHES)

    print("\nAll image generation batches have completed successfully.")

    

# Example usage
if __name__ == "__main__":
    # Get topic from user input or use a default
    topic = input("Enter a topic for image generation: ").strip()
    if not topic:
        topic = "Futuristic City at Sunset"
    
    generate_and_create_images(topic, 20, image_model = "Anime", text_model="GLM")