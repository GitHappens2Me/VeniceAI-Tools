"""
This file handles all Communication with the Venice.ai API
Find the API Reference at https://docs.venice.ai/api-reference/api-spec
The API is still evolving and might change
"""

from helper import get_api_key
import http.client
import json
import os
import base64

API_KEY = get_api_key("secrets.txt")
conn = http.client.HTTPSConnection("api.venice.ai")

#TODO model_mapping is doubled in this file and multiagent.py
#https://docs.venice.ai/overview/models
model_mapping = {
    # Deprecated:
    "llama-3.1": "llama-3.1-405b",
    "qwen":      "qwen2.5-coder-32b", #old: "qwen32b",
    "dolphin":   "dolphin-2.9.2-qwen2-72b",
    "deepseek":  "deepseek-r1-llama-70b",
    "deepseek-full": "deepseek-r1-671b",         # deepseek stops returning any content if the discussion gets to long
    

    "Uncencored": "venice-uncensored",
    "Small": "qwen3-4b",
    "Medium": "mistral-31-24b",
    "Large": "qwen3-235b",
    "llama-3.2": "llama-3.2-3b",
    "llama-3.3": "llama-3.3-70b",
    "GLM": "zai-org-glm-4.6", # BETA MODEL might change
    "Qwen-next": "qwen3-next-80b",
    "Qwen-coder": "qwen3-coder-480b-a35b-instruct",
    "Hermes": "hermes-3-llama-3.1-405b",

    "Venice-SD35": "venice-sd35",
    "Hidream": "hidream",
    "Qwen-image": "qwen-image",
    "Anime": "wai-Illustrious",
    "Lustify" : "lustify-sdxl", # older model
}

def request(method, endpoint, payload, headers):
    """Make an HTTP request to the Venice API
    
    Args:
        method (str): HTTP method (GET/POST/PUT etc)
        endpoint (str): API endpoint URL path
        payload (bytes): Request body content
        headers (dict): HTTP headers to include
    
    Returns:
        bytes: Raw response content
    """
    conn = http.client.HTTPSConnection("api.venice.ai")
    try:
        conn.request(method, endpoint, payload, headers)
        response = conn.getresponse()
        return response.read()
    finally:
        conn.close()

def get_models():
    headers = {'Authorization': f'Bearer {API_KEY}' }
    payload = ""
    response = request("GET", "/api/v1/models", payload, headers)
    print(jsonfy(response))

def print_rate_info(response):
    rate_limit = response.headers.get("x-ratelimit-limit-requests")
    if(rate_limit):
        print("Rate Limit:", response.headers.get("x-ratelimit-limit-requests"))
        print("Remaining Requests:", response.headers.get("x-ratelimit-remaining-requests"))
        print("Reset Time:", response.headers.get("x-ratelimit-reset-requests"))


def chat_completion(message, role, model, debug = False, strip_thinking = False, disable_thinking = False ):
    payload = json.dumps({
        "model": f"{model_mapping[model]}",
        "messages": [
            {
                "role": role,
                "content": message
            }
        ],
        "venice_parameters": {
            "include_venice_system_prompt": False,
            "strip_thinking_response": strip_thinking,
            "disable_thinking": disable_thinking,
        }
    }).encode('utf-8')
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print(f"[Requesting Response from {model}]")
    response = request("POST", "/api/v1/chat/completions", payload, headers)
    if(debug):
        print(jsonfy(response))
    return response


def jsonfy(data):
    data = json.loads(data.decode("utf-8"))
    return(json.dumps(data, indent=4))  # Pretty-print with indentation


def extract_message(data):
    try:
        data = json.loads(data.decode("utf-8"))
        message = data.get("choices", [{}])[0].get("message", {}).get("content", "No message content")
        return message
    except Exception as e:
        print(e)
        print(data)
        return ""



def image_gen(prompt, x, y, seed, style= None, model="Venice-SD35", file_name = "", steps = 30):
    if(len(file_name) == 0):
        file_name=f"{prompt.lower().replace(' ','-')}_{seed}_{style}.png"

    payload = json.dumps({
        "model": f"{model_mapping[model]}",
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
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"[Requesting Response from {model}]")
    response = request("POST", "/api/v1/image/generate", payload, headers)
    #print(response)

    with open("results/"+file_name, "wb") as image_file:
        image_file.write(response)
        print(f"Image saved as '{file_name}'")


def image_inpaint(prompt, image_input, model="stable-diffusion-3.5", file_name=""):
    """
    Edit or modify an image based on the supplied prompt (inpainting).
    
    Args:
        prompt (str): The text directions to edit or modify the image
        image_input (str): Either a base64-encoded string, file path, or URL starting with http:// or https://
        model (str): Model to use for inpainting (default: stable-diffusion-3.5)
        file_name (str): Output filename (optional)
    """
    if len(file_name) == 0:
        file_name = f"inpaint_{prompt.lower().replace(' ', '-')}_{model}.png"
    
    # Handle different input types (file path, URL, or base64)
    if isinstance(image_input, str) and (image_input.startswith('http://') or image_input.startswith('https://')):
        # Use URL directly
        image_data = image_input
    elif os.path.exists(image_input):
        # Convert file to base64
        with open(image_input, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
    else:
        # Assume it's already base64 encoded
        image_data = image_input
    
    payload = json.dumps({
        "prompt": prompt,
        "image": image_data
    }).encode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"[Requesting Inpaint from {model} on Image {image_input}]")
    response = request("POST", "/api/v1/image/edit", payload, headers)
    
    # Check if response is JSON (error) or binary (image)
    try:
        # Try to decode as JSON first
        error_data = json.loads(response.decode('utf-8'))
        # If successful, it's an error response
        error_msg = error_data.get('error', 'Unknown error')
        details = error_data.get('details', {})
        issues = error_data.get('issues', [])
        
        # Format a detailed error message
        error_details = []
        if details:
            error_details.append(f"Details: {json.dumps(details, indent=2)}")
        if issues:
            error_details.append("Issues:")
            for issue in issues:
                error_details.append(f"  - {issue.get('message', '')}")
        
        full_error = f"API Error: {error_msg}\n" + "\n".join(error_details)
        raise ValueError(full_error)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # If JSON decoding fails, it's likely binary image data
        with open("results/inpaint/" + file_name, "wb") as image_file:
            image_file.write(response)
            print(f"Inpainted image saved as '{file_name}'")