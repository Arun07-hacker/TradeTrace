import logging
import functools
import inspect
from typing import Any, Optional, Dict
from pydantic import BaseModel

logger = logging.getLogger("tradetrace.tools")


class ToolResult(BaseModel):
    tool: str
    status: str  # "success" or "error"
    data: Optional[Any] = None
    error: Optional[str] = None


def format_log(prefix: str, message: str) -> None:
    print(f"{prefix} {message}")
    logger.info(f"{prefix} {message}")


def log_tool_execution(tool_name: str):
    """Decorator to log tool lifecycle: START, INPUT, RESULT, COMPLETE."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            format_log("[TOOL START]", tool_name)
            input_summary = str(kwargs) if kwargs else (str(args) if args else "None")
            format_log("[TOOL INPUT]", input_summary[:200])
            try:
                result = await func(*args, **kwargs)
                if isinstance(result, ToolResult):
                    data_str = str(result.data)[:200] if result.data is not None else "None"
                    format_log("[TOOL RESULT]", f"status={result.status}, data={data_str}")
                else:
                    format_log("[TOOL RESULT]", str(result)[:200])
                format_log("[TOOL COMPLETE]", tool_name)
                return result
            except Exception as e:
                err_msg = str(e)
                format_log("[TOOL RESULT]", f"ERROR: {err_msg}")
                format_log("[TOOL COMPLETE]", tool_name)
                return ToolResult(tool=tool_name, status="error", data=None, error=err_msg)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            format_log("[TOOL START]", tool_name)
            input_summary = str(kwargs) if kwargs else (str(args) if args else "None")
            format_log("[TOOL INPUT]", input_summary[:200])
            try:
                result = func(*args, **kwargs)
                if isinstance(result, ToolResult):
                    data_str = str(result.data)[:200] if result.data is not None else "None"
                    format_log("[TOOL RESULT]", f"status={result.status}, data={data_str}")
                else:
                    format_log("[TOOL RESULT]", str(result)[:200])
                format_log("[TOOL COMPLETE]", tool_name)
                return result
            except Exception as e:
                err_msg = str(e)
                format_log("[TOOL RESULT]", f"ERROR: {err_msg}")
                format_log("[TOOL COMPLETE]", tool_name)
                return ToolResult(tool=tool_name, status="error", data=None, error=err_msg)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator
