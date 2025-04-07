from helper import get_api_key
from helper import save_text_result
from api_client import *
from read_file import sanitize_code_from_file

#TODO Generate requirements.txt

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
    prompt = f"Give me a descriptive Filename for a Textfile containing a review of a text given by the user. The user said: '{user_prompt}'. Just return the Filename. Dont include any Extension (such as .txt). Do not answer with any text other than the filename. The Filename should have underscores to split words."
    response = chat_completion(prompt, "user", "llama-3.3")
    message = extract_message(response)
    print(message)
    return message


def generate_prompt(name: str, models: list, discussion: str, rounds: int, user_prompt: str, text:str, final: bool = False, specialty = "standard", specialties = [""]) -> str:
    models_list = ', '.join(models)  # Convert list to string for readability

    specialty_descriptions = {
        "moderator": "Analyze the review process holistically: ensure all specialties (content, facts, form) are addressed, resolve conflicting feedback, and maintain a constructive tone. Prioritize clarity and coherence in final recommendations without inserting personal opinions.",
        "content": "Evaluate the paper’s core arguments, logic, and originality. Identify gaps in reasoning, unsupported claims, or redundancies. Suggest additions/removals to strengthen narrative flow and academic rigor. Avoid nitpicking grammar or formatting.",
        "spelling": "Scan for mechanical errors: spelling, punctuation, syntax, and tense consistency. Flag ambiguous phrasing or overly complex sentences. Provide concise corrections without altering the author's intended meaning or voice.",
        "fact-checker": "Verify all data points, citations, and statistical claims against cited sources. Highlight unsourced assertions, outdated references, or misrepresented findings. Propose authoritative replacements for questionable material.",
        "form": "Assess adherence to formatting guidelines (e.g., APA/MLA), citation consistency, heading hierarchy, and visual elements (tables/figures). Note deviations from submission standards and recommend structural optimizations.",
    }

    initial_instructions = (
        f"["
        f"You are an AI-Assistant named {name}, tasked with participating in a collaborative review of the text given by the user."
        f"The user's question is: '{user_prompt}'\n"
        f"The text being reviewed is: ------------------Start of text-------------\n'{text}'\n------------------End of text-------------"
        f"There are {len(models)} AI-Agents involved in the discussion: {models_list}. "
        f"You are one of them and will contribute to the discussion. "
        f"Each of the participants has a different focus or specialty."
        f"The specialties are {specialties}\n"
        f"Your own specialty is {specialty}, which means you task is the following: {specialty_descriptions.get(specialty, 'You provide general feedback.')}\n"
        f"There will be {rounds} rounds of discussion, with each agent getting a turn to speak. "
         f"Here are the rules for the review:\n"
        #f"- Keep your responses focused and concise, aiming for a maximum of 150 words per turn.\n"
        #f"- The tone should be informative and professional.\n"
        f"- You are not allowed to use square brackets or initiate new rounds of discussion on your own.\n"
        f"- Do not start your answer with your name.\n"
        f"- Do not add additional empty lines in your answer.\n" 
        f"- Keep the format of you answer compact but readable.\n"
        #f"- If you do not see any improvements to the discussion, you may respond with 'pass'.\n"
        f"- All system messages, such as who is speaking or what round it is, will be in square brackets '[...]'.\n"
        #f"- Collaborate with the other agents to generate a comprehensive final answer.\n"
        #f"- If you're unsure about any aspect of the discussion or need clarification, please don't hesitate to ask a clarifying question. "
        #f"You can respond with a question like 'Can you provide more context about [topic]?' or 'I'm not sure I understand [concept], can you explain it further?'\n"
        f"[This is what has been said so far:]"
        f"{(discussion if discussion.strip() else '[No discussion yet. You are the first to speak.]')}\n"
        f"[Now it is your turn:]\n"
    )
    
    final_instructions = (
        f"[You are the final AI-Agent to speak in this review. Your task is to summarize the key points discussed and provide the final review to the user. "
        f"Ensure that the final answer reflects all important elements discussed. You may also give example improvements for certain parts. This review should be detailed and long. There is no word / character limit.]"
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
    active_models: list[str] = ["llama-3.1", "llama-3.3", "llama-3.2", "deepseek", "qwen"],
    model_specialties: list[str] = ["moderator", "content", "spelling", "fact-checker", "form"],
    text: str = "",
    rounds: int = 1,
    debug: bool = False,
    verbose: bool = False
) -> None:
    """Orchestrate a multi-agent discussion session.
    
    Args:
        user_prompt: Initial user question/request to discuss
        active_models: List of AI models participating in the discussion
        rounds: Number of discussion rounds
        debug: Enable debug output
    """

    discussion = ""
    for round in range(1, rounds + 1):
        discussion += f"\t[Round {round}:]\n"
        for index, model in enumerate(active_models):
            prompt = generate_prompt(model, active_models, discussion, rounds, user_prompt, text=text, specialty=model_specialties[index], specialties=model_specialties)
            #print(prompt.upper())
            response = chat_completion(prompt, "user", model, debug)
            message = extract_message(response)
            discussion += f"\n[{model.upper()} {(model_specialties[index])}:] '{message}'\n"

            if verbose:
                print(f"Prompt: \n{prompt}\n\nResponse:\n{message}")
            else:
                print(f"[{model.upper()}:] '{message}'\n")
            

    prompt = generate_prompt(active_models[0], active_models, discussion, rounds, user_prompt, text=text, final= True, specialty=model_specialties[0], specialties=model_specialties)
    response = chat_completion(prompt, "user", active_models[0])
    message = extract_message(response)
    discussion += f"\t[Final Summery:]\n [{active_models[0].upper()} {(model_specialties[index])}:] '{message}'\n\n"
    if verbose:
        print(f"Prompt: \n{prompt}\n\nResponse:\n{message}")
    else:
        print(f"[{active_models[0].upper()}:] '{message}'\n")
            
    sanitized_title = "".join(c for c in user_prompt if c not in '?/:\\')
    sanitized_title = sanitized_title.rstrip('.')  # Remove trailing dots

    discussion = "Prompt Format:\n" + generate_prompt(
        "{name}", active_models, "[...]", 420, user_prompt, final=True, text=text
    ) + "\n\n" + discussion
    
    save_text_result(f"{get_file_name(user_prompt)}.txt", "discussions", discussion)




## The AI-Agents will discuss how to answer the following prompt:
user_prompt = "This is an academic text about Chaumian e-cash I wrote. Please review."
text = r"""
    \subsection{The double spend Problem}
\label{sec:DoubleSpend}

Double spending describes the process of using the same banknote to pay twice, in turn creating money at will. 
A monetary system suffering from double spending problems will suffer from severe inflation and loss of confidence in the system.
Therefore, solving the double spend problem is essential. 
With traditional money, more precisely cash, this problem is inherently solved by the physical nature of banknotes.
Once exchanged, one cannot use the same banknote again as it is not in one's possession anymore. 
\par\vspace{\baselineskip}
When money became more and more digital, the solution included centralized authorities, verifying all transactions. 
This authority, usually a Bank or Payment provider like Paypal, knows the balance of your account and the amount you want to transact and can therefore prevent you from spending more money than is available to you. 
The result of this system, is the banks complete knowledge and control over their users transactions. 

This centralization of information and control raised stark privacy concerns, as noted by Chaum in his 1985 paper \cite{chaum1985security}:
"The foundation is being laid for a dossier society, in which computers could be used to infer individuals' life-styles, habits, whereabouts, and associations from data collected in ordinary consumer transactions." 
\par\vspace{\baselineskip}
Chaum's 1983 solution also included a central authority, but crucially made it impossible to trace payments or even keep track of individual balances \cite{chaum1983blind}.
It took additional 25 years before a decentralized solution to the double spend problem was proposed \cite{nakamoto2008bitcoin}.

"""
# Starting the discussion 
start_session(user_prompt, rounds = 2, text=text, verbose = True)


