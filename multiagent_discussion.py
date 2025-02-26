from helper import get_api_key
from helper import save_text_result
from api_client import *
from read_file import sanitize_code_from_file

"""
This Program creates Discussions with multiple AI-Agents about how to best answer the users' prompt.
"""

MODEL_MAPPING = {
    "llama-3.1": "llama-3.1-405b",
    "llama-3.2": "llama-3.2-3b",
    "llama-3.3": "llama-3.3-70b",
    "qwen":      "qwen2.5-coder-32b",
    "dolphin":   "dolphin-2.9.2-qwen2-72b",
    "deepseek":  "deepseek-r1-llama-70b",
    "deepseek-full": "deepseek-r1-671b"
}
def get_file_name(user_prompt):
    print("Generating File Name")
    prompt = f"Give me a descriptive Filename for a Textfile containing a discussion about the Question '{user_prompt}'. Just return the Filename. Dont include any Extension (such as .txt). Do not answer with any text other than the filename. The Filename should have underscores to split words."
    response = chat_completion(prompt, "user", "llama-3.3")
    message = extract_message(response)
    print(message)
    return message


def generate_prompt(name: str, models: list, discussion: str, rounds: int, user_prompt: str, final: bool = False) -> str:
    models_list = ', '.join(models)  # Convert list to string for readability

    initial_instructions = (
        f"["
        f"You are an AI-Assistant named {name}, tasked with participating in a collaborative discussion about how to best answer a user's question. "
        f"The user's question is: '{user_prompt}'\n"
        f"There are {len(models)} AI-Agents involved in the discussion: {models_list}. "
        f"You are one of them and will contribute to the discussion. "
        f"There will be {rounds} rounds of discussion, with each agent getting a turn to speak. "
        f"Your goal is to build upon the ideas presented by the previous agents and provide new ideas that aid the discussion.\n"
        f"You may disagree with the other agents. If so, explain why and convince them of your idea. \n"
        f"Here are the rules for the discussion:\n"
        f"- Keep your responses focused and concise, aiming for a maximum of 150 words per turn.\n"
        f"- The tone should be informative and professional.\n"
        f"- You are not allowed to use square brackets or initiate new rounds of discussion on your own.\n"
        f"- Do not start your answer with your name.\n"
        f"- Do not add additional empty lines in your answer.\n" 
        f"- Keep the format of you answer compact but readable.\n"
        f"- If you do not see any improvements to the discussion, you may respond with 'pass'.\n"
        f"- All system messages, such as who is speaking or what round it is, will be in square brackets '[...]'.\n"
        f"- Collaborate with the other agents to generate a comprehensive final answer.\n"
        f"- If you're unsure about any aspect of the discussion or need clarification, please don't hesitate to ask a clarifying question. "
        f"You can respond with a question like 'Can you provide more context about [topic]?' or 'I'm not sure I understand [concept], can you explain it further?'\n"
        f"[This is what has been said so far:]"
        f"{(discussion if discussion.strip() else '[No discussion yet. You are the first to speak.]')}\n"
        f"[Now it is your turn:]\n"
    )
    
    final_instructions = (
        f"[You are the final AI-Agent to speak in this discussion. Your task is to summarize the key points discussed and provide the final answer to the user. "
        f"The user should not be aware that there was a discussion. Ensure that the final answer reflects all important elements discussed.]"
    )

    return initial_instructions + (final_instructions if final else "")

## Modelnames: You can use the Names (instead) of their IDs
## Names are defined in api_client.py
#  "llama-3.1": "llama-3.1-405b",
#  "llama-3.2": "llama-3.2-3b",
#  "llama-3.3": "llama-3.3-70b",
#  "qwen":      "qwen2.5-coder-32b",            # old: "qwen32b",
#  "dolphin":   "dolphin-2.9.2-qwen2-72b",
#  "deepseek":  "deepseek-r1-llama-70b",
#  "deepseek-full": "deepseek-r1-671b"          # deepseek stops returning any content if the discussion gets to long
    

def start_session(
    user_prompt: str,
    active_models: list[str] = ["llama-3.3", "deepseek", "dolphin", "qwen"],
    rounds: int = 5,
    debug: bool = False
) -> None:
    """Orchestrate a multi-agent discussion session.
    
    Args:
        user_prompt: Initial user question/request to discuss
        active_models: List of AI models participating in the discussion
        rounds: Number of discussion rounds
        debug: Enable debug output
    """
    #print(sanitize_code_from_file("multiagent.py")[:25]+ "...")
    user_prompt += sanitize_code_from_file("multiagent_discussion.py")
    discussion = ""
    for round in range(1, rounds + 1):
        discussion += f"\t[Round {round}:]\n"
        for model in active_models:
            prompt = generate_prompt(model, active_models, discussion, rounds, user_prompt)
            #print(prompt.upper())
            response = chat_completion(prompt, "user", model, debug)
            message = extract_message(response)
            discussion += f"\n[{model.upper()}:] '{message}'\n"
            #print("\n\n-----------------------\n", discussion, "\n-----------------------\n\n")
            print(f"[{model.upper()}:] '{message}'\n")
            

    prompt = generate_prompt(active_models[0], active_models, discussion, rounds, user_prompt, final= True)
    response = chat_completion(prompt, "user", active_models[0])
    message = extract_message(response)
    discussion += f"\t[Final Summery:]\n [{active_models[0].upper()}:] '{message}'\n\n"
    print(f"[{active_models[0].upper()}:] '{message}'\n")
    #print("\n\n-----------------------\n", discussion, "\n-----------------------\n\n")
    
    sanitized_title = "".join(c for c in user_prompt if c not in '?/:\\')
    sanitized_title = sanitized_title.rstrip('.')  # Remove trailing dots

    discussion = "Prompt Format:\n" + generate_prompt(
        "{name}", active_models, "[...]", 420, user_prompt, final=True
    ) + "\n\n" + discussion
    
    save_text_result(f"{get_file_name(user_prompt)}.txt", "discussions", discussion)




## The AI-Agents will discuss how to answer the following prompt:
user_prompt = "Can you improve the following Code for me? : "

# Starting the discussion 
start_session(user_prompt, rounds = 1)


