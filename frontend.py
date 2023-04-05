from textual.app import App, ComposeResult, Binding
from textual.containers import Horizontal
from textual.widgets import Label, Footer, Input, Static, LoadingIndicator, ContentSwitcher
from textual.reactive import reactive
from setup_utils import read_config, parse_initial_arguments
from api_utils import set_api_key, call_open_ai
from yolo import evaluate_input
import os
import warnings


class Hint(Label):
    focus_flag = reactive("")

    def render(self):
        return f"{self.focus_flag + self.name}"


class InputApp(App[str]):
    CSS_PATH = "frontend.css"
    res_command = reactive("")

    BINDINGS = [
        Binding("ctrl+o", "unfocus_modify",
                "unfocus modify", show=False, priority=True),
        Binding("o", "modify", "modify", show=False),
        Binding("ctrl+e", "unfocus_edit", "unfocus edit",
                show=False, priority=True),
        Binding("e", "edit", "edit", show=False),
        ("q", "quit", "quit"),
        ("escape", "unfocus", "unfocus"),
        Binding("x", "key_submit", "input submit", show=False),
        Binding("ctrl+x", "key_submit", "input submit", show=False),
        Binding("p", "copy", "copy to clipboard", show=False),
        Binding("ctrl+p", "copy", "copy to clipboard", show=False)
    ]

    def action_modify(self):
        self.query_one("#prompt", Input).focus()

    def action_edit(self):
        self.query_one("#command", Input).focus()

    def action_unfocus_edit(self):
        self.set_focus(None)
        self.query_one("#command", Input).focus()

    def action_unfocus_modify(self):
        self.set_focus(None)
        self.query_one("#prompt", Input).focus()

    def action_unfocus(self):
        self.set_focus(None)

    def on_descendant_blur(self, event):
        if not self.query_one("#command", Input).has_focus and not self.query_one("#prompt", Input).has_focus:
            self.query_one("#modify", Hint).focus_flag = ""
            self.query_one("#confirm", Hint).focus_flag = ""
            self.query_one("#edit", Hint).focus_flag = ""
            self.query_one("#copy", Hint).focus_flag = ""

    def on_descendant_focus(self):
        self.query_one("#edit", Hint).focus_flag = "^"
        self.query_one("#confirm", Hint).focus_flag = "^"
        self.query_one("#modify", Hint).focus_flag = "^"
        self.query_one("#copy", Hint).focus_flag = "^"

    async def action_key_submit(self):
        await self.query_one("#command", Input).action_submit()

    def watch_res_command(self):
        if self.res_command != "":
            self.query_one(ContentSwitcher).current = "command"
        else:
            self.query_one(ContentSwitcher).current = "loading"

    async def on_input_submitted(self, event: Input.Submitted):
        self.set_focus(None)
        input_id = event.input.id
        if input_id == "prompt":
            self.query_one("#command", Input).value = ""
            new_query = self.query_one("#prompt", Input).value
            self.res_command = ""
            config = read_config()
            set_api_key(config)
            self.shell = os.environ.get("SHELL", "powershell.exe")
            self.res_command = await call_open_ai(new_query, config)
            self.query_one("#command", Input).insert_text_at_cursor(
                self.res_command)
        else:
            self.exit(["Y", self.query_one("#command", Input).value])

    def action_copy(self):
        self.exit(["C", self.query_one("#command", Input).value])

    def compose(self) -> ComposeResult:
        yield Static("Prompt")
        yield Input(id="prompt", placeholder="Enter Prompt...")
        with Horizontal():
            yield Hint(id="modify", name=r"m\[o]dify")
        yield Static("Command")
        with ContentSwitcher(initial='loading'):
            yield LoadingIndicator(id="loading")
            yield Input(id="command", placeholder="...")
        with Horizontal():
            yield Hint(id="confirm", name=r"e\[x]ecute")
            yield Hint(id="edit", name=r"\[e]dit")
            yield Hint(id="copy", name=r"co\[p]y")
            # yield Button("e\[x]plain")
        yield Footer()

    async def on_ready(self) -> None:
        self.query_one(ContentSwitcher).current = "loading"
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
    passed_comand = app.run()
    if passed_comand:
        shell = os.environ.get("SHELL", "powershell.exe")
        evaluate_input(passed_comand[0], passed_comand[1], shell)
warnings.simplefilter("ignore", ResourceWarning)
