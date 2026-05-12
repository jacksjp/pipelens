"""Test script to verify FastMCP client connection."""

import asyncio

from fastmcp import Client


async def test_mcp():
    try:
        async with Client("http://127.0.0.1:9000/mcp") as client:
            result = await client.call_tool("ping", {})
            print(f"MCP Ping Result: {result}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp())
