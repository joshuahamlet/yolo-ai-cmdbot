from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Static, LoadingIndicator, Button, ContentSwitcher
from textual.reactive import reactive
from textual import events

import os
from setup_utils import read_config, parse_initial_arguments
from api_utils import set_api_key, call_open_ai


class InputApp(App):
    CSS_PATH = "frontend.css"
    res_command = reactive("")
    command_loading = reactive("loading")

    BINDINGS = [
        ("m", "modify", "modify"),
        ("e", "edit", "edit"),
        ("q", "escape", "escape"),
        ("escape", "unfocus", "unfocus"),
    ]

    def action_modify(self):
        self.query_one("#prompt", Input).focus()

    def action_edit(self):
        self.query_one("#command", Input).focus()
    
    def action_unfocus(self):
        self.set_focus(None)


    def watch_res_command(self):
        if self.res_command != "":
            self.query_one(ContentSwitcher).current = "command"
        else:
            self.query_one(ContentSwitcher).current = "loading"

    def compose(self) -> ComposeResult:
        yield Static("Prompt")
        yield Input(id="prompt", placeholder="Enter Prompt...")
        with Horizontal():
            yield Button("\[m]odify")
        yield Static("Command")
        with ContentSwitcher(initial='loading'):
            yield LoadingIndicator(id="loading")
            yield Input(id="command", placeholder="...")
        with Horizontal():
            yield Button("\[c]onfirm")
            yield Button("\[e]dit")
            # yield Button("e\[x]plain")

    # async def on_mount(self) -> None:

    async def on_ready(self) -> None:
        self.query_one(ContentSwitcher).current = self.command_loading
        user_prompt = parse_initial_arguments()
        self.query_one("#prompt", Input).insert_text_at_cursor(user_prompt)
        config = read_config()
        set_api_key(config)
        self.shell = os.environ.get("SHELL", "powershell.exe")
        self.res_command = await call_open_ai(user_prompt, config)
        self.query_one("#command", Input).insert_text_at_cursor(
            self.res_command)


if __name__ == "__main__":
    app = InputApp()
    app.run()
