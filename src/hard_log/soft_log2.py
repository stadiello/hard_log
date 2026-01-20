#!/usr/bin/env python3
from __future__ import annotations

import os
import queue
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.text import Text


class Level(str, Enum):
    BOOT = "BOOT"
    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"
    SUCCESS = "SUCCESS"


@dataclass(frozen=True)
class Theme:
    icon: str
    color: str


THEME: dict[Level, Theme] = {
    Level.BOOT: Theme("⟡", "bright_red"),
    Level.ERROR: Theme("✖", "orange1"),
    Level.WARN: Theme("▲", "bright_yellow"),
    Level.INFO: Theme("▣", "bright_cyan"),
    Level.DEBUG: Theme("⧉", "bright_magenta"),
    Level.SUCCESS: Theme("✔", "bright_green"),
}


class SoftLog:
    """
    Futuristic Rich logger:
    - cyber HUD-style line format
    - async file writes (non-blocking)
    - simple log rotation by size
    - convenience methods: .info/.warn/.error...
    """

    def __init__(
        self,
        path: str = "logs",
        file_name: str = "log.txt",
        *,
        max_bytes: int = 2_000_000,   # ~2 MB
        keep_files: int = 5,
        highlight: tuple[str, ...] = ("FAIL", "ERROR", "WARN", "OK", "DONE"),
        show_ms: bool = True,
        console: Optional[Console] = None,
    ):
        self.console = console or Console()
        self.dir = Path(path)
        self.file = self.dir / file_name
        self.max_bytes = max_bytes
        self.keep_files = keep_files
        self.highlight = highlight
        self.show_ms = show_ms

        self.dir.mkdir(parents=True, exist_ok=True)

        # Async writer
        self._q: "queue.Queue[str]" = queue.Queue(maxsize=10_000)
        self._stop = threading.Event()
        self._writer = threading.Thread(target=self._writer_loop, daemon=True)
        self._writer.start()

    # ---------- public API ----------
    def log(self, level: Level | str, message: str) -> None:
        lvl = Level(level) if isinstance(level, str) else level
        line = self._make_line(lvl, message)

        self.console.print(line)

        # archive as plain text (no Rich markup)
        try:
            self._q.put_nowait(line.plain + "\n")
        except queue.Full:
            # In overload, degrade gracefully (drop file write, keep console)
            pass

    def boot(self, msg: str) -> None: self.log(Level.BOOT, msg)
    def info(self, msg: str) -> None: self.log(Level.INFO, msg)
    def debug(self, msg: str) -> None: self.log(Level.DEBUG, msg)
    def warn(self, msg: str) -> None: self.log(Level.WARN, msg)
    def success(self, msg: str) -> None: self.log(Level.SUCCESS, msg)
    def error(self, msg: str) -> None: self.log(Level.ERROR, msg)

    def close(self) -> None:
        """Flush pending logs and stop writer thread."""
        self._stop.set()
        self._writer.join(timeout=1.0)
        self._drain_queue()

    # ---------- formatting ----------
    def _timestamp(self) -> str:
        if self.show_ms:
            # HH:MM:SS.mmm
            return datetime.now().strftime("%H:%M:%S.%f")[:-3]
        return datetime.now().strftime("%H:%M:%S")

    def _make_line(self, level: Level, msg: str) -> Text:
        ts = self._timestamp()
        theme = THEME.get(level, Theme("·", "bright_white"))

        # HUD-like prefix: [12:34:56.789]  ▣ INFO     ::
        t = Text()

        # Brackets + timestamp
        t.append("[", style="bright_white")
        t.append(ts, style="bright_white")
        t.append("] ", style="bright_white")

        # Icon + level badge
        t.append(theme.icon + " ", style=theme.color)
        t.append(f"{level.value:<7}", style="bold " + theme.color)

        # Separator
        t.append("  ::  ", style="bright_white")

        # Message with highlights
        body = Text(msg, style=theme.color)
        for token in self.highlight:
            body.highlight_words([token], style="bold underline " + theme.color)

        t.append(body)

        # Extra “danger” effect for errors
        if level == Level.ERROR:
            t.stylize("bold")
        return t

    # ---------- file writer ----------
    def _rotate_if_needed(self) -> None:
        if not self.file.exists():
            return
        if self.file.stat().st_size < self.max_bytes:
            return

        # Rotate: log.txt -> log.1.txt -> log.2.txt ...
        stem = self.file.stem
        suffix = self.file.suffix

        for i in range(self.keep_files - 1, 0, -1):
            src = self.dir / f"{stem}.{i}{suffix}"
            dst = self.dir / f"{stem}.{i+1}{suffix}"
            if src.exists():
                src.replace(dst)

        self.file.replace(self.dir / f"{stem}.1{suffix}")

    def _writer_loop(self) -> None:
        while not self._stop.is_set():
            try:
                chunk = self._q.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                self._rotate_if_needed()
                with open(self.file, "a", encoding="utf-8") as f:
                    f.write(chunk)
            finally:
                self._q.task_done()

        self._drain_queue()

    def _drain_queue(self) -> None:
        while True:
            try:
                chunk = self._q.get_nowait()
            except queue.Empty:
                break
            try:
                self._rotate_if_needed()
                with open(self.file, "a", encoding="utf-8") as f:
                    f.write(chunk)
            finally:
                self._q.task_done()