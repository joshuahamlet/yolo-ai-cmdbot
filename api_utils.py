import openai
import dotenv
import os
import sys
from setup_utils import get_full_prompt, read_config

def set_api_key(config):
    # Two options for the user to specify they openai api key.
    # 1. Place a ".env" file in same directory as this with the line:
    #   OPENAI_API_KEY="<yourkey>"
    #   or do `export OPENAI_API_KEY=<yourkey>` before use
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # 2. Place a ".openai.apikey" in the home directory that holds the line:
    #   <yourkey>
    #   Note: This options will likely be removed in the future
    if not openai.api_key:  # If statement to avoid "invalid filepath" error
        home_path = os.path.expanduser("~")
        openai.api_key_path = os.path.join(home_path, ".openai.apikey")

    # 3. Final option is the key might be in the yolo.yaml config file
    #   openai_apikey: <yourkey>
    if not openai.api_key:
        openai.api_key = config["openai_api_key"]

def call_open_ai(query, config):
    # Unix based SHELL (/bin/bash, /bin/zsh), otherwise assuming it's Windows
    shell = os.environ.get("SHELL", "powershell.exe")

    # do we have a prompt from the user?
    if query == "":
        print("No user prompt specified.")
        sys.exit(-1)

    # Load the correct prompt based on Shell and OS and append the user's prompt
    prompt = get_full_prompt(query, shell)

    # Make the first line also the system prompt
    system_prompt = prompt[1]
    # print(prompt)

    # Call the ChatGPT API
    response = openai.ChatCompletion.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
    )

    return response.choices[0].message.content.strip()
