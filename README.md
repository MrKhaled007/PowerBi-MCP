# Power BI MCP Server

> Talk to your Power BI workspace in plain English — powered by Claude and the Model Context Protocol.

Built as a portfolio project fully aligned with **Anthropic's Introduction to MCP course**.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What does it do?

Instead of clicking through Power BI's interface, you just ask Claude:

```
You:    "What reports do I have in the ESM workspace?"
Claude: "You have 1 report: ESM Middle Office Dashboard (ID: rpt-001)"

You:    "Show me the schema for the credit scorecard dataset"
Claude: "The CreditScorecard_Basel3 dataset has 2 tables:
         - FactLoans (8 columns: LoanId, LoanAmount, PD_Score, LGD, EAD...)
         - FactSHAP (4 columns: LoanId, Feature, SHAPValue, ImportanceRank)"

You:    "Generate a DAX measure for average loan amount by risk band"
Claude: "Here's your measure:
         Avg Loan Amount by Risk Band =
         AVERAGEX(VALUES(FactLoans[RiskBand]),
             CALCULATE(AVERAGE(FactLoans[LoanAmount])))"
```

No SQL. No DAX knowledge required. Just conversation.

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│                     You (the user)                       │
│         "What datasets do I have?"                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Claude Desktop                          │
│         Understands your question                        │
│         Decides which tool to call                       │
└─────────────────────┬───────────────────────────────────┘
                      │  calls list_datasets()
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Power BI MCP Server                         │
│         (this project — mcp_server.py)                  │
│                                                          │
│   Tools        Resources          Prompts                │
│   ─────        ─────────          ───────                │
│   list_*       powerbi://         explore_dataset        │
│   get_*        datasets/{id}      explain_measure        │
│   search_*     reports/{id}       audit_report           │
│   generate_*                                             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Data Source                                 │
│   Phase 1: Mock ESM/Finance data (works immediately)     │
│   Phase 2: Real Power BI REST API (needs Azure AD)       │
└─────────────────────────────────────────────────────────┘
```

---

## The 3 MCP Primitives

This project implements all three primitives taught in Anthropic's MCP course:

### Tools — model-controlled
Claude calls these automatically when it needs data. Like buttons Claude presses on its own.

| Tool | What it does |
|---|---|
| `list_workspaces` | List all Power BI workspaces |
| `list_reports` | List reports, filter by workspace |
| `list_datasets` | List datasets, filter by workspace |
| `get_report_pages` | Get all pages/tabs in a report |
| `get_dataset_schema` | Full schema: tables, columns, data types |
| `list_measures` | All DAX measures with expressions |
| `search_measures` | Search measures by keyword |
| `get_lineage` | Which reports depend on a dataset |
| `generate_measure` | Generate DAX from plain English |

### Resources — app-controlled
Read-only data exposed via URI addresses. Like files Claude can open and read.

| URI | What it returns |
|---|---|
| `powerbi://workspaces` | All workspaces |
| `powerbi://reports` | All reports |
| `powerbi://datasets` | All datasets |
| `powerbi://datasets/{id}/schema` | Schema for a specific dataset |
| `powerbi://datasets/{id}/measures` | DAX measures for a specific dataset |
| `powerbi://reports/{id}/pages` | Pages for a specific report |

### Prompts — user-controlled
Pre-built workflow templates you invoke for common tasks.

| Prompt | What it does |
|---|---|
| `explore_dataset` | Structured dataset exploration prompt |
| `explain_measure` | Plain-language DAX measure explainer |
| `audit_report` | Governance and quality checklist |

---

## Quickstart

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [Claude Desktop](https://claude.ai/download)

### 1. Clone the repo

```bash
git clone https://github.com/MrKhaled007/PowerBi-MCP.git
cd PowerBi-MCP
```

### 2. Set up the environment

**Windows:**
```powershell
uv venv
.venv\Scripts\activate
uv add "mcp[cli]" httpx python-dotenv msal anthropic
```

**Mac/Linux:**
```bash
uv venv
source .venv/bin/activate
uv add "mcp[cli]" httpx python-dotenv msal anthropic
```

### 3. Run the client demo

This tests all three primitives against the server:

```bash
python mcp_client.py
```

You should see:
```
Connected to Power BI MCP Server
Tools     : 9
Resources : 3
Prompts   : 3
...
All three MCP primitives working correctly.
```

### 4. Test with MCP Inspector

The browser-based testing tool taught in the MCP course:

```bash
mcp dev mcp_server.py
```

Open the URL shown (usually `http://127.0.0.1:6274`) and click **Connect**. You can then test every tool, resource, and prompt interactively.

```
┌─────────────────────────────────────────┐
│  MCP Inspector                          │
│  ● Connected                            │
│                                         │
│  Resources  Prompts  Tools              │
│  ────────────────────────────────────   │
│  ▶ list_workspaces    [Run Tool]        │
│  ▶ search_measures    keyword: ____     │
│  ▶ generate_measure   dataset: ____     │
│                       description: ____ │
└─────────────────────────────────────────┘
```

### 5. Connect to Claude Desktop

Find your config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this (replace the path with your actual project path):

**Windows:**
```json
{
  "mcpServers": {
    "powerbi": {
      "command": "C:\\path\\to\\PowerBi-MCP\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\PowerBi-MCP\\mcp_server.py"]
    }
  }
}
```

**Mac/Linux:**
```json
{
  "mcpServers": {
    "powerbi": {
      "command": "/path/to/PowerBi-MCP/.venv/bin/python",
      "args": ["/path/to/PowerBi-MCP/mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop. The **powerbi** connector will appear in the `+` menu. Start chatting.

---

## DAX Generation (Path 5)

The `generate_measure` tool uses Claude to generate DAX measures from plain English descriptions.

**With Anthropic API credits (live mode):**

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Create a `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```
3. Claude generates real, schema-aware DAX expressions on the fly

**Without API credits (mock mode):**

The tool automatically falls back to realistic pre-built DAX examples. The server still works — you just get mock responses instead of live generated ones.

```
source: "live"   ← real Claude-generated DAX
source: "mock"   ← fallback response (add API credits to enable live)
```

---

## Project Structure

```
PowerBi-MCP/
│
├── mcp_server.py       ← The MCP server (main file)
│                          9 tools, 6 resources, 3 prompts
│                          FastMCP decorators, async, stderr logging
│
├── mcp_client.py       ← MCP client that tests all 3 primitives
│                          Run this to verify everything works
│
├── mock_data.py        ← Phase 1 static data
│                          Realistic ESM/finance workspace
│                          Works immediately, no credentials needed
│
├── powerbi_client.py   ← Phase 2 real API client
│                          Power BI REST API via MSAL OAuth
│                          Auto-activates when .env is configured
│
├── .env.example        ← Credential template
├── .gitignore          ← Keeps .env and .venv out of GitHub
└── README.md
```

---

## Phase 2 — Real Power BI Data

To connect to your actual Power BI workspace:

### Step 1 — Publish your reports
Open Power BI Desktop → click **Publish** → select **My Workspace**. Your reports are now accessible via the API.

### Step 2 — Register an Azure AD app
1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **App registrations** → **New registration**
3. Add API permissions: `Power BI Service` → `Delegated` → `Report.Read.All`, `Dataset.Read.All`
4. Create a client secret under **Certificates & secrets**
5. Note your Tenant ID, Client ID, and Client Secret

### Step 3 — Configure credentials
Copy `.env.example` to `.env` and fill in your values:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
PBI_TENANT_ID=your-tenant-id
PBI_CLIENT_ID=your-client-id
PBI_CLIENT_SECRET=your-client-secret
PBI_USERNAME=your@email.com
PBI_PASSWORD=yourpassword
```

The server auto-switches from mock data to live Power BI data. No code changes needed.

---

## Course Alignment

This project is fully aligned with **Anthropic's Introduction to MCP course**:

| Course requirement | Status |
|---|---|
| FastMCP decorator pattern (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`) | ✅ |
| All 3 primitives: tools, resources (direct + templated), prompts | ✅ |
| Async tool functions with type hints and docstrings | ✅ |
| Logging to stderr only (never stdout) | ✅ |
| MCP Inspector compatible (`mcp dev mcp_server.py`) | ✅ |
| Both server and client built | ✅ |
| stdio transport with proper `main()` entry point | ✅ |
| Claude Desktop integration | ✅ |
| uv package manager | ✅ |

---

## Tech Stack

- **Python 3.10+**
- **MCP Python SDK** (`mcp[cli]`) — FastMCP server and client
- **Anthropic SDK** — DAX generation via Claude
- **MSAL** — Microsoft OAuth 2.0 for Power BI REST API
- **httpx** — async HTTP client
- **python-dotenv** — credential management
- **uv** — package management

---

## Author

**Mohammed Khaled** — Final-year Data Science student, Thomas More University Mechelen

[LinkedIn](https://linkedin.com/in/mohammed-khaled-43a220183) · [GitHub](https://github.com/MrKhaled007)

Part of a broader data analytics portfolio targeting BI Analyst and Data Scientist roles in Brussels/Luxembourg.
