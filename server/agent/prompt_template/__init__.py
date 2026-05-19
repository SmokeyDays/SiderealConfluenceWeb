import os
import re

from server.utils.config import get_config


JSON_ACTION_PROMPT_START = "[[JSON_ACTION_PROMPT_START]]"
JSON_ACTION_PROMPT_END = "[[JSON_ACTION_PROMPT_END]]"


def _strip_json_action_prompt(prompt: str):
    pattern = re.compile(
        rf"\n?{re.escape(JSON_ACTION_PROMPT_START)}.*?{re.escape(JSON_ACTION_PROMPT_END)}\n?",
        re.DOTALL,
    )
    return pattern.sub("\n", prompt)

def load_prompt(filename: str):
    if not filename.endswith(".txt"):
        filename += ".txt"
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, "r") as f:
            prompt = f.read()
        if str(get_config("agent_function_calling_mode")).lower() == "on":
            prompt = _strip_json_action_prompt(prompt)
        prompt = prompt.replace(JSON_ACTION_PROMPT_START, "").replace(JSON_ACTION_PROMPT_END, "")
        return prompt
    except Exception as e:
        print(f"Error loading prompt from {filepath}: {e}")
        return ""
