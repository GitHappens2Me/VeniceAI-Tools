"""
This file handles all Communication with the Venice.ai API
Find the API Reference at https://docs.venice.ai/api-reference/api-spec
The API is still evolving and might change
"""

from helper import get_api_key
import http.client
import json


API_KEY = get_api_key("secrets.txt")
conn = http.client.HTTPSConnection("api.venice.ai")

#TODO model_mapping is doubled in this file and multiagent.py
model_mapping = {
    "llama-3.1": "llama-3.1-405b",
    "llama-3.2": "llama-3.2-3b",
    "llama-3.3": "llama-3.3-70b",
    "qwen":      "qwen2.5-coder-32b", #old: "qwen32b",
    "dolphin":   "dolphin-2.9.2-qwen2-72b",
    "deepseek":  "deepseek-r1-llama-70b",
    "deepseek-full": "deepseek-r1-671b"         # deepseek stops returning any content if the discussion gets to long
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
    conn.request(method, endpoint, payload, headers)
    response = conn.getresponse()
    return response.read()

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


def chat_completion(message, role, model, debug = False):
    payload = json.dumps({
        "model": f"{model_mapping[model]}",
        "messages": [
            {
                "role": role,
                "content": message
            }
        ],
        "venice_parameters": {
            "include_venice_system_prompt": False
        }
    }).encode('utf-8')
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print(f"[Requesting Repsonse from {model}]")
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



def image_gen(prompt, x, y, seed, style, model="stable-diffusion-3.5", file_name = "", steps = 30):
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
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"[Requesting Repsonse from {model}]")
    response = request("POST", "/api/v1/image/generate", payload, headers)
    #print(response)

    with open("results/"+file_name, "wb") as image_file:
        image_file.write(response)
        print(f"Image saved as '{file_name}'")