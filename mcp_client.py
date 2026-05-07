import asyncio
import json
import logging
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=["mcp_server.py"],
)


async def run_demo():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("Connected to Power BI MCP Server\n")
            print("=" * 60)

            # ── Discover capabilities ──────────────────────────────
            tools    = await session.list_tools()
            resources = await session.list_resources()
            prompts  = await session.list_prompts()

            print(f"Tools     : {len(tools.tools)}")
            print(f"Resources : {len(resources.resources)}")
            print(f"Prompts   : {len(prompts.prompts)}")
            print()

            # ── TOOLS ─────────────────────────────────────────────
            print("-" * 60)
            print("TOOLS (model-controlled)")
            print("-" * 60)

            result = await session.call_tool("list_workspaces", {})
            data = json.loads(result.content[0].text)
            print(f"\nlist_workspaces -> {data['count']} workspaces:")
            for ws in data["workspaces"]:
                print(f"  - {ws['name']} (ID: {ws['id']})")

            result = await session.call_tool("list_reports", {"workspace_id": "ws-001"})
            data = json.loads(result.content[0].text)
            print(f"\nlist_reports (ws-001) -> {data['count']} report(s):")
            for r in data["reports"]:
                print(f"  - {r['name']} (ID: {r['id']})")

            result = await session.call_tool("search_measures", {"keyword": "exposure"})
            data = json.loads(result.content[0].text)
            print(f"\nsearch_measures 'exposure' -> {data['count']} match(es):")
            for m in data["matches"]:
                print(f"  - {m['name']}: {m['description']}")

            result = await session.call_tool("get_lineage", {"dataset_id": "ds-001"})
            data = json.loads(result.content[0].text)
            print(f"\nget_lineage (ds-001) -> {data['count']} dependent report(s):")
            for r in data["dependent_reports"]:
                print(f"  - {r['name']}")

            # ── RESOURCES ─────────────────────────────────────────
            print()
            print("-" * 60)
            print("RESOURCES (app-controlled)")
            print("-" * 60)

            r = await session.read_resource("powerbi://workspaces")
            print(f"\npowerbi://workspaces\n{r.contents[0].text}")

            r = await session.read_resource("powerbi://datasets/ds-001/schema")
            print(f"\npowerbi://datasets/ds-001/schema\n{r.contents[0].text[:300]}...")

            r = await session.read_resource("powerbi://reports/rpt-001/pages")
            print(f"\npowerbi://reports/rpt-001/pages\n{r.contents[0].text}")

            # ── PROMPTS ───────────────────────────────────────────
            print()
            print("-" * 60)
            print("PROMPTS (user-controlled)")
            print("-" * 60)

            print("\nAvailable prompts:")
            for p in prompts.prompts:
                print(f"  - {p.name}")

            result = await session.get_prompt(
                "explain_measure", {"measure_name": "Expected Loss"}
            )
            text = result.messages[0].content.text
            print(f"\nexplain_measure 'Expected Loss' preview:\n{text[:400]}...")

            result = await session.get_prompt(
                "audit_report", {"report_id": "rpt-001"}
            )
            text = result.messages[0].content.text
            print(f"\naudit_report 'rpt-001' preview:\n{text[:400]}...")

            print()
            print("=" * 60)
            print("All three MCP primitives working correctly.")


def main():
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()