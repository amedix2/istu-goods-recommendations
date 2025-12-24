import sys
from pythonjsonlogger.json import JsonFormatter
import logging

ANSI = {
    "reset": "\033[0m",
    "debug": "\033[90m",
    "info": "\033[96m",
    "warning": "\033[93m",
    "error": "\033[91m",
    "critical": "\033[95m",
}


class PrettyFormatter(logging.Formatter):
    """Красивый DEV-форматтер"""

    def __init__(self, *args, exclude_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.exclude_fields = (set(exclude_fields or []) |
                               set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()))

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)

        color = ANSI.get(record.levelname.lower(), "")
        reset = ANSI["reset"]

        extra = self._extract_extra(record)

        if not extra:
            return f"{color}{base}{reset}"

        tree = self._format_tree(extra)
        colored_tree = "\n".join(color + line + reset for line in tree.splitlines())

        return f"{color}{base}{reset}\n{colored_tree}"

    def _extract_extra(self, record: logging.LogRecord):
        return {
            k: v
            for k, v in record.__dict__.items()
            if k not in self.exclude_fields
        }

    def _format_tree(self, obj, indent=""):
        lines = []
        if isinstance(obj, dict):
            items = list(obj.items())
            for i, (k, v) in enumerate(items):
                last = i == len(items) - 1
                branch = "└── " if last else "├── "
                next_indent = indent + ("    " if last else "│   ")
                if isinstance(v, (dict, list, tuple)):
                    lines.append(f"{indent}{branch}{k}:")
                    lines.extend(self._format_tree(v, next_indent).splitlines())
                else:
                    lines.append(f"{indent}{branch}{k}: {v}")
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                last = i == len(obj) - 1
                branch = "└── " if last else "├── "
                next_indent = indent + ("    " if last else "│   ")
                if isinstance(v, (dict, list, tuple)):
                    lines.append(f"{indent}{branch}[{i}]")
                    lines.extend(self._format_tree(v, next_indent).splitlines())
                else:
                    lines.append(f"{indent}{branch}[{i}] {v}")

        return "\n".join(lines)


def setup_logging(debug: bool, level: int, exclude_extra_fields=None):
    """
    - dev (debug = True) -> PrettyFormatter
    - prod (debug = False) -> JSON
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    if debug:
        handler.setFormatter(
            PrettyFormatter(
                exclude_fields=exclude_extra_fields,
                fmt="[{asctime}] {levelname:<8} [{name}] {message}",
                datefmt="%Y-%m-%d %H:%M:%S",
                style="{",
            )
        )
    else:
        handler.setFormatter(
            JsonFormatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(module)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                json_ensure_ascii=False,
            )
        )

    root.addHandler(handler)

    return root
