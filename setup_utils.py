import os
import yaml
import platform
import distro
import dotenv
import sys


def print_usage():
    config = read_config()
    print("Yolo v0.2 - by @wunderwuzzi23")
    print()
    print("Usage: yolo [-a] list the current directory information")
    print("Argument: -a: Prompt the user before running the command (only useful when safety is off)")
    print()

    yolo_safety_switch = "on"

    if config["safety"] != True:
        yolo_safety_switch = "off"

    print("Current configuration per yolo.yaml:")
    print("* Model        : " + str(config["model"]))
    print("* Temperature  : " + str(config["temperature"]))
    print("* Max. Tokens  : " + str(config["max_tokens"]))
    print("* Safety       : " + yolo_safety_switch)


def read_config() -> any:
    # Find the executing directory (e.g. in case an alias is set)
    # So we can find the config file
    yolo_path = os.path.abspath(__file__)
    prompt_path = os.path.dirname(yolo_path)

    config_file = os.path.join(prompt_path, "yolo.yaml")
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

# Construct the prompt


def get_full_prompt(user_prompt, shell):
    # Find the executing directory (e.g. in case an alias is set)
    # So we can find the prompt.txt file
    yolo_path = os.path.abspath(__file__)
    prompt_path = os.path.dirname(yolo_path)

    # Load the prompt and prep it
    prompt_file = os.path.join(prompt_path, "prompt.txt")
    with open(prompt_file, "r") as file:
        pre_prompt = file.read()
    pre_prompt = pre_prompt.replace("{shell}", shell)
    pre_prompt = pre_prompt.replace("{os}", get_os_friendly_name())
    prompt = pre_prompt + user_prompt

    # be nice and make it a question
    if prompt[-1:] != "?" and prompt[-1:] != ".":
        prompt += "?"

    return prompt


def get_os_friendly_name():
    # Get OS Name
    os_name = platform.system()

    if os_name == "Linux":
        return "Linux/"+distro.name(pretty=True)
    elif os_name == "Windows":
        return os_name
    elif os_name == "Darwin":
        return "Darwin/macOS"
    else:
        return os_name


def parse_initial_arguments():

    command_start_idx = 1     # Question starts at which argv index?
    ask_flag = False           # safety switch -a command line argument
    # user's answer to safety switch (-a) question y/n
    yolo = ""

    # Parse arguments and make sure we have at least a single word
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(-1)

    # Safety switch via argument -a (local override of global setting)
    # Force Y/n questions before running the command
    if sys.argv[1] == "-a":
        ask_flag = True
        command_start_idx = 2

    # To allow easy/natural use we don't require the input to be a
    # single string. So, the user can just type yolo what is my name?
    # without having to put the question between ''
    arguments = sys.argv[command_start_idx:]
    return " ".join(arguments)
