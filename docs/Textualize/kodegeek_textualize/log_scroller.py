#!/usr/bin/env python
"""
Author: Jose Vicente Nunez
"""
import asyncio
import shutil
from typing import List

from textual import on, work
from textual.app import ComposeResult, App
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Button, SelectionList, Label, Log
from textual.widgets.selection_list import Selection
from textual.worker import Worker

OS_COMMANDS = {
    "lSHW": ["lshw", "-json", "-sanitize", "-notime", "-quiet"],
    "LSCPU": ["lscpu", "--all", "--extended", "--json"],
    "LSMEM": ["lsmem", "--json", "--all", "--output-all"],
    "NUMASTAT": ["numastat", "-z"]
}


class LogScreen(ModalScreen):
    count = reactive(0)
    MAX_LINES = 10_000
    ENABLE_COMMAND_PALETTE = False
    CSS = """
        LogScreen {
        layout: vertical;
    }
    
    RichLog {
        width: 100%;
        height: auto;    
    }
    
    Button {
        dock: bottom;
        width: 100%;
        height: auto;
    }
    
    Label {
        dock: top;
        width: 100%;
        height: auto;
        align: center top;
    }
    """

    def __init__(
            self,
            name: str | None = None,
            ident: str | None = None,
            classes: str | None = None,
            selections: List = None
    ):
        super().__init__(name, ident, classes)
        self.selections = selections

    def compose(self) -> ComposeResult:
        yield Label(f"Visiting {len(self.selections)} sites")
        event_log = Log(
            id='event_log',
            max_lines=LogScreen.MAX_LINES,
            highlight=True
        )
        event_log.loading = True
        yield event_log
        button = Button("Close", id="close", variant="success")
        button.disabled = True
        yield button

    async def on_mount(self) -> None:
        event_log = self.query_one('#event_log', Log)
        event_log.clear()
        lst = '\n'.join(self.selections)
        event_log.write(f"Running:\n{lst}")
        event_log.write("\n")

        for command in self.selections:
            self.count += 1
            self.run_process(cmd=command)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if self.count == 0:
            button = self.query_one('#close', Button)
            button.disabled = False
        self.log(event)

    @work(exclusive=False)
    async def run_process(self, cmd: str) -> None:
        event_log = self.query_one('#event_log', Log)
        event_log.write_line(f"Running: {cmd}")
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            raise ValueError(f"'{cmd}' finished with errors ({proc.returncode})")
        stdout = stdout.decode(encoding='utf-8', errors='replace')
        if stdout:
            event_log.write(stdout)
        self.count -= 1

    @on(Button.Pressed, "#close")
    def on_button_pressed(self, _) -> None:
        self.app.pop_screen()


class OsApp(App):
    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]
    CSS_PATH = "os_app.tcss"
    ENABLE_COMMAND_PALETTE = False

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        selections = [Selection(name.title(), ' '.join(cmd), True) for name, cmd in OS_COMMANDS.items() if shutil.which(cmd[0].strip())]
        yield Header(show_clock=True)
        yield SelectionList(*selections, id='cmds')
        yield Button(f"Execute {len(selections)} commands", id="exec", variant="primary")
        yield Footer()

    @on(SelectionList.SelectedChanged)
    def on_selection(self, event: SelectionList.SelectedChanged) -> None:
        button = self.query_one("#exec", Button)
        selections = len(event.selection_list.selected)
        if selections:
            button.disabled = False
        else:
            button.disabled = True
        button.label = f"Execute {selections} commands"

    @on(Button.Pressed)
    def on_button_click(self):
        selection_list = self.query_one('#cmds', SelectionList)
        selections = selection_list.selected
        log_screen = LogScreen(selections=selections)
        self.push_screen(log_screen)


def main():
    app = OsApp()
    app.title = f"Output of multiple well known UNIX commands".title()
    app.sub_title = f"{len(OS_COMMANDS)} commands available"
    app.run()


if __name__ == "__main__":
    main()
