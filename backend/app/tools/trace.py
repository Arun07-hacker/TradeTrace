import sys
import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class TraceEntry(BaseModel):
    """A single step in the execution trace."""
    type: str = Field(..., description="'tool' or 'agent'")
    name: str = Field(..., description="Name of the tool or agent")
    status: str = Field("pending", description="'pending', 'completed', 'error', 'skipped'")
    duration_ms: float = Field(0.0, description="Execution duration in milliseconds")
    result_summary: Optional[str] = Field(None, description="Brief summary of the result")
    tools_used: Optional[List[str]] = Field(None, description="Tools used (for agent entries)")
    error: Optional[str] = Field(None, description="Error message if failed")


class ExecutionTrace:
    """
    Maintains an ordered list of execution steps (tools and agents)
    for the TradeTrace analysis pipeline.
    Provides both programmatic access and formatted terminal display.
    """

    def __init__(self):
        self.entries: List[TraceEntry] = []
        self._timers: Dict[str, float] = {}

    def start(self, entry_type: str, name: str) -> None:
        """Mark the start of a tool or agent execution."""
        self._timers[f"{entry_type}:{name}"] = time.time()
        self.entries.append(TraceEntry(type=entry_type, name=name, status="pending"))

    def complete(
        self,
        entry_type: str,
        name: str,
        result_summary: Optional[str] = None,
        tools_used: Optional[List[str]] = None,
    ) -> None:
        """Mark a tool or agent as completed."""
        key = f"{entry_type}:{name}"
        elapsed_ms = 0.0
        if key in self._timers:
            elapsed_ms = round((time.time() - self._timers.pop(key)) * 1000, 1)

        for entry in reversed(self.entries):
            if entry.type == entry_type and entry.name == name and entry.status == "pending":
                entry.status = "completed"
                entry.duration_ms = elapsed_ms
                entry.result_summary = result_summary
                if tools_used:
                    entry.tools_used = tools_used
                break

    def fail(self, entry_type: str, name: str, error: str) -> None:
        """Mark a tool or agent as failed."""
        key = f"{entry_type}:{name}"
        elapsed_ms = 0.0
        if key in self._timers:
            elapsed_ms = round((time.time() - self._timers.pop(key)) * 1000, 1)

        for entry in reversed(self.entries):
            if entry.type == entry_type and entry.name == name and entry.status == "pending":
                entry.status = "error"
                entry.duration_ms = elapsed_ms
                entry.error = error
                break

    def skip(self, entry_type: str, name: str, reason: str = "requires database") -> None:
        """Mark a tool or agent as skipped."""
        self.entries.append(TraceEntry(
            type=entry_type,
            name=name,
            status="skipped",
            result_summary=f"Skipped — {reason}",
        ))

    def to_list(self) -> List[Dict[str, Any]]:
        """Export trace as a list of dicts (JSON-serializable)."""
        return [entry.model_dump(exclude_none=True) for entry in self.entries]

    def print_summary(self) -> None:
        """Print a formatted execution trace summary to the terminal."""
        print("\n" + "=" * 50)
        print("  EXECUTION TRACE")
        print("=" * 50)
        for entry in self.entries:
            icon = _status_icon(entry.status)
            type_label = entry.type.upper()
            duration = f" ({entry.duration_ms:.0f}ms)" if entry.duration_ms > 0 else ""
            line = f"  {icon} [{type_label}] {entry.name}{duration}"
            if entry.result_summary:
                line += f" -- {entry.result_summary}"
            if entry.error:
                line += f" -- ERROR: {entry.error}"
            if entry.tools_used:
                line += f" [tools: {', '.join(entry.tools_used)}]"
            print(line)
        print("=" * 50 + "\n")


def _status_icon(status: str) -> str:
    """Return a terminal-friendly icon for a trace entry status."""
    return {
        "completed": "[OK]",
        "error": "[!!]",
        "skipped": "[--]",
        "pending": "[..]",
    }.get(status, "[??]")
