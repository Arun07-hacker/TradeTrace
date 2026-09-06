from fastapi import APIRouter
from typing import Optional
from app.tools.registry import TOOLS, get_tool, list_tools, get_tool_categories

router = APIRouter(prefix="/tools", tags=["Tool Registry"])


@router.get("")
async def list_registered_tools(category: Optional[str] = None):
    """List all registered TradeTrace tools with metadata."""
    tools = list_tools(category=category)
    return {
        "total": len(tools),
        "categories": get_tool_categories(),
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "requires_db": t.requires_db,
                "requires_user": t.requires_user,
                "parameters": t.parameters,
            }
            for t in tools
        ],
    }


@router.get("/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get metadata for a specific registered tool."""
    tool_def = get_tool(tool_name)
    if not tool_def:
        return {"error": f"Tool '{tool_name}' not found", "available": list(TOOLS.keys())}
    return {
        "name": tool_def.name,
        "description": tool_def.description,
        "category": tool_def.category,
        "requires_db": tool_def.requires_db,
        "requires_user": tool_def.requires_user,
        "parameters": tool_def.parameters,
    }
