# Welcome to VeniceAI-Tools 🛠️

A practical collection of Python tools designed to work with VeniceAI's API.

## What's Inside? 📦

- **Image Generation**: Tools for creating and processing images
- **Multi-Agent Discussion**: A framework for managing conversations between multiple agents
- **Helper Functions**: Useful utilities for common tasks
- **Step Animation**: Tools for handling sequential animations of Image generation
- **Seed Explorer**: Generate many different Images from the same prompt

## Getting Started 🚀

1. **API Key Required**: 
   - Rename `example.secrets.txt` to `secrets.txt`
   - Add your VeniceAI API key to this file



## Contributing 🤝

We welcome all kinds of contributions! If you'd like to help:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

Have questions or suggestions? Feel free to reach out.



BATCH_SIZE = 20
DELAY_BETWEEN_BATCHES = 10  # 10 seconds

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