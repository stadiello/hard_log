# !/usr/bin/env python3

import os
from rich.console import Console
from rich.text import Text
from datetime import datetime
import time

class SoftLog:
    def __init__(self, path: str = "logs/", file_name: str = "log.txt"):
        self.console = Console()
        self.path = path
        self.file_name = file_name
    
    def _color(self, tag) -> str:
        colors = {
            "BOOT": "bright_red",
            "ERROR": "orange1",
            "WARN": "bright_yellow",
            "INFO": "bright_cyan",
            "DEBUG": "bright_magenta",
            "SUCCESS": "bright_green",
        }
        return colors.get(tag, "bright_white")

    def _make_line(self, ts, tag, msg, color="bright_red") -> Text:
        t = Text(f"[", style="bright_white")
        t.append(f"{ts[:2]}", style="bright_white")
        t.append(f"{ts[2:]}", style="bold " + color)
        t.append("] ", style="bright_white")
        t.append(f"{tag:<8}", style="bold bright_white")
        t.append(" :: ", style="bright_white")
        t.append(msg, style=color)
        return t
    
    def _archive_log(self, log_content: str) -> None:
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        log_file = open(os.path.join(self.path, self.file_name), "a")
        log_file.write(str(log_content) + "\n")
        log_file.close()

    def log(self, tag, message) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        color = self._color(tag)
        log_content = self._make_line(ts, tag, message, color)
        if tag == "ERROR":
            log_content.stylize("bold underline")
        self.console.print(log_content)
        self._archive_log(log_content)
    