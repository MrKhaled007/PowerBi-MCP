# Power BI MCP Server

A Model Context Protocol (MCP) server that exposes Power BI workspace metadata — reports, datasets, DAX measures, and schemas — as MCP primitives that Claude can interact with in natural language.

Built as a portfolio project aligned with Anthropic's Introduction to MCP course.

---

## What is MCP?

Model Context Protocol (MCP) is an open standard by Anthropic that lets AI assistants like Claude connect to external data sources through a consistent interface. This server implements all three MCP primitives:

| Primitive | Who controls it | What it does |
|---|---|---|
| **Tools** | Model (Claude) | Functions Claude calls automatically when it needs data |
| **Resources** | Application | Read-only data exposed via URI addresses |
| **Prompts** | User | Pre-built workflow templates the user invokes |

---

## Demo

Once connected to Claude Desktop you can ask:

> "What reports exist in the ESM workspace?"
> "Show me the schema for the credit scorecard dataset."
> "Which reports depend on the ESM_MiddleOffice dataset?"
> "Find all DAX measures related to exposure."

---

## Project Structure

powerbi-mcp-server/
├── mcp_server.py       # MCP server — tools, resources, prompts
├── mcp_client.py       # MCP client — tests all three primitives
├── mock_data.py        # Phase 1 static data (no credentials needed)
├── powerbi_client.py   # Phase 2 real Power BI REST API
├── .env.example        # Credential template for Phase 2
├── .gitignore
└── README.md

---

## Quickstart (Phase 1 — Mock Data)

### 1. Clone the repo

```bash
git clone https://github.com/MrKhaled007/powerbi-mcp-server.git
cd powerbi-mcp-server
```

### 2. Set up environment

```bash
uv venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Mac/Linux
uv add "mcp[cli]" httpx python-dotenv msal
```

### 3. Run the client demo

```bash
python mcp_client.py
```

### 4. Test with MCP Inspector

```bash
mcp dev mcp_server.py
```

Open the URL shown in your terminal (usually `http://127.0.0.1:6274`) and click Connect.

---

## Connect to Claude Desktop

Add this to your `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "powerbi": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourName\\Desktop\\powerbi-mcp-server",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop after saving.

---

## Tools (8)

| Tool | Description |
|---|---|
| `list_workspaces` | List all Power BI workspaces |
| `list_reports` | List reports, optionally filtered by workspace |
| `list_datasets` | List datasets, optionally filtered by workspace |
| `get_report_pages` | Get all pages/tabs in a report |
| `get_dataset_schema` | Full schema: tables, columns, data types |
| `list_measures` | All DAX measures with expressions and descriptions |
| `search_measures` | Keyword search across measure names, descriptions, DAX |
| `get_lineage` | Trace which reports depend on a dataset |

---

## Resources (6)

| URI | Description |
|---|---|
| `powerbi://workspaces` | All workspaces |
| `powerbi://reports` | All reports |
| `powerbi://datasets` | All datasets |
| `powerbi://datasets/{id}/schema` | Schema for a specific dataset |
| `powerbi://datasets/{id}/measures` | DAX measures for a specific dataset |
| `powerbi://reports/{id}/pages` | Pages for a specific report |

---

## Prompts (3)

| Prompt | Description |
|---|---|
| `explore_dataset` | Structured dataset exploration |
| `explain_measure` | Plain-language DAX measure explainer |
| `audit_report` | Governance and quality checklist |

---

## Phase 2 — Real Power BI API

1. Copy `.env.example` to `.env`
2. Register an app at [Azure Portal](https://portal.azure.com)
3. Fill in your credentials in `.env`
4. The server auto-switches to live data — no code changes needed

---

## Tech Stack

- Python 3.10+
- MCP Python SDK (`mcp[cli]`)
- FastMCP decorator pattern
- MSAL for Azure AD OAuth
- httpx for async HTTP
- uv for package management

---

## Author

**Mohammed Khaled** — Final-year Data Science student, Thomas More University
[LinkedIn](https://linkedin.com/in/mohammed-khaled-43a220183) · [GitHub](https://github.com/MrKhaled007)