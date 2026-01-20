# !/usr/bin/env python3

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
from datetime import datetime
import time

class SoftLog:
    def __init__(self):
        self.console = Console()

    # def make_line(self, ts, tag, msg, color="bright_red"):
    #     t = Text(f"[{ts}] ", style="bright_red")
    #     t.append(f"{tag:<8}", style="bold bright_green")
    #     t.append(" :: ", style="bright_white")
    #     t.append(msg, style=color)
    #     return t
    def make_line(self, ts, tag, msg, color="bright_red"):
        t = Text(f"[{ts[:2]}", style="bright_white")
        t.append(f"{ts[2:]}", style="bold bright_red")
        t.append(f"] {tag:<8}", style="bold bright_white")
        t.append(" :: ", style="bright_white")
        t.append(msg, style=color)
        return t
    
    def render(self, lines_top, lines_bottom, tick):
        table = Table.grid(padding=(0, 1))
        table.add_column()

        for line in lines_top:
            table.add_row(line)
        # "scanline" separator (simple)
        sep = Text("─" * 78, style="orange1")
        if tick % 2 == 0:
            sep.stylize("dim")
        table.add_row(sep)
        table.add_row(Text(" "))

        for line in lines_bottom:
            table.add_row(line)
        table.add_row(Text("─" * 78, style="orange1 dim"))
        return table
    
    def log(self, tag, message, color):
        ts = datetime.now().strftime("%H:%M:%S")
        return self.make_line(ts, tag, message, color)