"""Lightweight SCPI parser and command registry.

Features:
- register command handlers with exact match (case-insensitive)
- support for query commands ending with '?'
- handler signature: handler(params_str: str) -> str
"""
from typing import Callable, Dict, Optional

CommandHandler = Callable[[Optional[str]], str]

_registry: Dict[str, CommandHandler] = {}


def register(command: str):
    """Decorator to register a handler for a command.

    The command is normalized to uppercase.
    """
    def deco(fn: CommandHandler):
        _registry[command.upper()] = fn
        return fn

    return deco


def handle(raw: str) -> str:
    if raw is None:
        return ""
    s = raw.strip()
    if not s:
        return ""
    key = s.upper()
    # split params if any (space-separated)
    parts = key.split(None, 1)
    cmd = parts[0]
    params = parts[1] if len(parts) > 1 else None

    # direct match
    if cmd in _registry:
        return _registry[cmd](params)

    # try query form
    if cmd.endswith('?') and cmd[:-1] in _registry:
        return _registry[cmd[:-1]](params)

    # fallback: unknown
    return "ERR"


# Register built-ins
@register("*IDN")
def _idn(params: Optional[str]) -> str:
    return "SCPI_Emu,Model1,Serial0001,1.0"


@register("MEAS:VOLT")
def _meas_volt(params: Optional[str]) -> str:
    import random

    return f"{random.uniform(0.0, 5.0):.4f}"


@register("SYST:ERR")
def _syst_err(params: Optional[str]) -> str:
    return "0,No error"


@register("SYST:EXIT")
def _exit(params: Optional[str]) -> str:
    return "Bye"
