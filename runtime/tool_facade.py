"""runtime.tool_facade

A minimal tool facade for MetaBlooms runtime.

MetaBlooms historically used a placeholder ToolFacade class. This implementation is
intentionally conservative: it provides a single, deterministic entrypoint for invoking
named tools that are registered at runtime.

The registry is an in-memory dict mapping tool names to callables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict


ToolFn = Callable[..., Any]


@dataclass
class ToolFacade:
    """Simple in-process tool registry + invoker."""

    tools: Dict[str, ToolFn] = field(default_factory=dict)

    def register(self, name: str, fn: ToolFn) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("tool name must be a non-empty string")
        if not callable(fn):
            raise TypeError("tool function must be callable")
        self.tools[name] = fn

    def call(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in self.tools:
            raise KeyError(f"unknown tool: {name}")
        return self.tools[name](*args, **kwargs)
