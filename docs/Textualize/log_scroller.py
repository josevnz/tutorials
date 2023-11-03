#!/usr/bin/env python
"""
Author: Jose Vicente Nunez
"""
import asyncio
import shlex
from typing import List

from textual import on, work
from textual.app import ComposeResult, App
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Button, SelectionList, Label, Log
from textual.widgets.selection_list import Selection
from textual.worker import Worker

SITES = {
    "Daily Mail": "https://dailymail.co.uk/",
    "NY Post": "https://nypost.com/",
    "The Sun": "https://www.thesun.co.uk/",
    "DrudgeReport": "https://drudgereport.com/",
    "CNN": "https://cnn.com",
    "Fox News": "https://www.foxnews.com/",
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
        yield Log(
            id='event_log',
            max_lines=LogScreen.MAX_LINES,
            highlight=True
        )
        button = Button("Close", id="close", variant="success")
        button.disabled = True
        yield button

    async def on_mount(self) -> None:
        button = self.query_one('#close', Button)
        event_log = self.query_one('#event_log', Log)
        event_log.clear()
        lst = '\n'.join(self.selections)
        event_log.write(f"Visiting:\n{lst}")
        event_log.write("\n")

        for site in self.selections:
            command = ' '.join(["/usr/bin/curl", "--verbose", "--location", "--fail", shlex.quote(site)])
            self.count += 1
            self.run_process(cmd=command)
        # button.disabled = False

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if self.count == 0:
            button = self.query_one('#close', Button)
            button.disabled = False
        self.log(event)

    @work(exclusive=False)
    async def run_process(self, cmd: str) -> None:
        event_log = self.query_one('#event_log', Log)
        event_log.write_line(f"Running: {cmd}")
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.STDOUT)
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


class WebsiteApp(App):
    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]
    CSS = """
    Screen {
        layout: vertical;
    }

    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }

    SelectionList {
        padding: 1;
        border: solid $accent;
        width: 1fr;
        height: 80%;
    }
    Button {
        width: 1fr
    }
    """
    ENABLE_COMMAND_PALETTE = False

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        selections = [Selection(name.title(), url, True) for name, url in SITES.items()]
        yield Header(show_clock=True)
        yield SelectionList(*selections, id='sites')
        yield Button(f"Visit {len(selections)} websites", id="visit", variant="primary")
        yield Footer()

    @on(SelectionList.SelectedChanged)
    def on_selection(self, event: SelectionList.SelectedChanged) -> None:
        button = self.query_one("#visit", Button)
        selections = len(event.selection_list.selected)
        if selections:
            button.disabled = False
        else:
            button.disabled = True
        button.label = f"Visit {selections} websites"

    @on(Button.Pressed)
    def on_button_click(self):
        selection_list = self.query_one('#sites', SelectionList)
        selections = selection_list.selected
        log_screen = LogScreen(selections=selections)
        self.push_screen(log_screen)


def main():
    app = WebsiteApp()
    app.title = f"Output of HTTP data from multiple websites".title()
    app.sub_title = f"{len(SITES)} websites available"
    app.run()


if __name__ == "__main__":
    main()
