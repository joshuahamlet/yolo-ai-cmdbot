import sys
import subprocess
from termcolor import colored


def check_for_issue(response):
    prefixes = ("sorry", "i'm sorry",
                "the question is not clear", "i'm", "i am")
    if response.lower().startswith(prefixes):
        print(colored("There was an issue: "+response, 'red'))
        sys.exit(-1)


def check_for_markdown(response):
    # odd corner case, sometimes ChatCompletion returns markdown
    if response.count("```", 2):
        print(colored("The proposed command contains markdown, so I did not execute the response directly: \n", 'red')+response)
        sys.exit(-1)


def missing_posix_display():
    display = subprocess.check_output("echo $DISPLAY", shell=True)
    return display == b'\n'
