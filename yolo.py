#!/usr/bin/env python3

# MIT License
# Copyright (c) 2023 wunderwuzzi23
# Greetings from Seattle!

import os
import sys
import subprocess
import pyperclip

from termcolor import colored
from colorama import init
from setup_utils import read_config, parse_initial_arguments
from api_utils import set_api_key, call_open_ai
from error_utils import check_for_issue, check_for_markdown, missing_posix_display 


if __name__ == "__main__":

    config = read_config()
    set_api_key(config)
    user_prompt = parse_initial_arguments()
    shell = os.environ.get("SHELL", "powershell.exe")

# Enable color output on Windows using colorama
init()

def prompt_user_input(response):
    print("Command: " + colored(response, 'blue'))
    if config["safety"] != "off" or sys.argv[1] == "-a":
        prompt_text = "Execute command? [Y]es [n]o [m]odify [c]opy to clipboard ==> "
        if os.name == "posix" and missing_posix_display():
            prompt_text = "Execute command? [Y]es [n]o [m]odify ==> "
        print(prompt_text, end='')
        user_input = input()
        return user_input


def evaluate_input(user_input, command):
    if user_input.upper() == "Y" or user_input == "":
        if shell == "powershell.exe":
            subprocess.run([shell, "/c", command], shell=False)
        else:
            # Unix: /bin/bash /bin/zsh: uses -c both Ubuntu and macOS should work, others might not
            subprocess.run([shell, "-c", command], shell=False)

    if user_input.upper() == "M":
        print("Modify prompt: ", end='')
        modded_query = input()
        modded_response = call_open_ai(modded_query, config)
        check_for_issue(modded_response)
        check_for_markdown(modded_response)
        modded_user_input = prompt_user_input(modded_response)
        print()
        evaluate_input(modded_user_input, modded_response)

    if user_input.upper() == "C":
        if os.name == "posix" and missing_posix_display():
            return
        pyperclip.copy(command)
        print("Copied command to clipboard.")


res_command = call_open_ai(user_prompt, config)
check_for_issue(res_command)
check_for_markdown(res_command)
user_iput = prompt_user_input(res_command)
print()
evaluate_input(user_iput, res_command)
