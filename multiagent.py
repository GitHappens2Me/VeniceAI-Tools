from config import get_api_key
import http.client
import json

KEY = get_api_key("secrets.txt")

conn = http.client.HTTPSConnection("api.venice.ai")

def request(method, endpoint, payload, headers):
    conn.request(method, endpoint, payload, headers)
    response = conn.getresponse()
    return response.read()

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

models = {
    "llama-3.1": "llama-3.1-405b",
    "llama-3.2": "llama-3.2-3b",
    "llama-3.3": "llama-3.3-70b",
    "qwen":      "qwen32b",
    "dolphin":   "dolphin-2.9.2-qwen2-72b",
    "deepseek":  "deepseek-r1-llama-70b",
    "deepseek-full": "deepseek-r1-671b"
}

                    #role = (user/system)
def chat_completion(message, role, model):
    payload = json.dumps({
        "model": f"{models[model]}",
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
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    }
    print(f"[Requesting Repsonse from {model}]")
    response = request("POST", "/api/v1/chat/completions", payload, headers)
    #print(jsonfy(response))
    return response
    



def generate_prompt(name, models, discussion, rounds, user_prompt, final = False):
    prompt = f"[You are an AI-Assistant named {name}, tasked with answering a Question from the user. The Question is '{user_prompt}'. You are part of a Discussion abou how to best answer the user. There are {len(models)} Agents involved in the disscusion: {models}. You are one of them and will also be involved in the discussion. In total there wil be {rounds} Rounds of disscusion in which each AI-Agent gets a turn to speak, so keep that in mind when answering. If you dont see any improvments to the discussion just answer with 'pass'. Any System Message, for example who is speaking or what round it is, is put in square brackets '[...]'. You are not allowed to use squared Brackets at any time. You may not start rounds of discussion on you own. Do not start your answer with your name. You must follow the rules. This is what has been said so far:] {discussion if discussion.strip() else '[No discussion yet. You are the first to speak]'} [Now it is your turn:]\n"
    if final:
        prompt += "[You are the last AI to speak in this discussion. You now have the Task to summerize the disscusion and give the final answer to the user! The user must not now there was a discussion. Please let all the important parts of the discusion be reflected in the final answer.]"
    return prompt

def start_session(active_models = ["llama-3.1", "dolphin", "deepseek-full", "qwen"], rounds = 3):
    user_prompt = "abcdefghijklmnopqrstuvwxyz"
    discussion = ""
    for round in range(1, rounds + 1):
        discussion += f"\t[Round {round}:]\n"
        for model in active_models:
            prompt = generate_prompt(model, active_models, discussion, rounds, user_prompt)
            #print(prompt.upper())
            response = chat_completion(prompt, "user", model)
            message = extract_message(response)
            discussion += f"[{model.upper()}:] '{message}'\n\n"
            print("\n\n-----------------------\n", discussion, "\n-----------------------\n\n")
            

    prompt = generate_prompt(active_models[0], active_models, discussion, rounds, user_prompt, final= True)
    response = chat_completion(prompt, "user", active_models[0])
    message = extract_message(response)
    discussion += f"\t[Final Summery:]\n [{active_models[0].upper()}:] '{message}'\n\n"
    print("\n\n-----------------------\n", discussion, "\n-----------------------\n\n")
    
    sanitized_title = "".join(c for c in user_prompt if c not in '?/:\\')
    sanitized_title = sanitized_title.rstrip('.')  # Remove trailing dots


    with open(f"./results\discussions/{sanitized_title.lower().replace(' ','-')}.txt", "w", encoding="utf-8") as file:
        file.write(discussion)

start_session()