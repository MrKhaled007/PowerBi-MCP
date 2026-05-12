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

You:    "Which reports depend on the ESM_MiddleOffice dataset?"
Claude: "1 report depends on it: ESM Middle Office Dashboard"
```

No SQL. No DAX knowledge required. Just conversation.

---

## How it works

```
┌─────────────────────────────────────────────────────────┐
│                     You (the user)                      │
│         "What datasets do I have?"                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Claude Desktop                         │
│         Understands your question                       │
│         Decides which tool to call                      │
└─────────────────────┬───────────────────────────────────┘
                      │  calls list_datasets()
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Power BI MCP Server                        │
│         (this project — mcp_server.py)                  │
│                                                         │
│   Tools          Resources           Prompts            │
│   ─────          ─────────           ───────            │
│   list_*         powerbi://          explore_dataset    │
│   get_*          datasets/{id}       explain_measure    │
│   search_*       reports/{id}        audit_report       │
│   generate_*                                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Source                           │
│   Phase 1: Mock ESM/Finance data (works immediately)    │
│   Phase 2: Real Power BI REST API (needs Azure AD)      │
└─────────────────────────────────────────────────────────┘
```

---

## The 3 MCP Primitives

This project implements all three primitives taught in Anthropic's MCP course.

---

### Tools — model-controlled
Claude calls these automatically when it needs data. Like buttons Claude presses on its own without you telling it to.

| Tool | What it does |
|---|---|
| `list_workspaces` | List all Power BI workspaces |
| `list_reports` | List reports, optionally filter by workspace |
| `list_datasets` | List datasets, optionally filter by workspace |
| `get_report_pages` | Get all pages and tabs in a report |
| `get_dataset_schema` | Full schema: tables, columns, data types |
| `list_measures` | All DAX measures with expressions and descriptions |
| `search_measures` | Search measures by keyword across name, description, DAX |
| `get_lineage` | Trace which reports depend on a dataset |
| `generate_measure` | Generate a DAX measure from plain English description |

---

### Resources — app-controlled
Read-only data exposed via URI addresses. Like files Claude can open and read passively.

| URI | What it returns |
|---|---|
| `powerbi://workspaces` | All workspaces |
| `powerbi://reports` | All reports |
| `powerbi://datasets` | All datasets |
| `powerbi://datasets/{id}/schema` | Schema for a specific dataset |
| `powerbi://datasets/{id}/measures` | DAX measures for a specific dataset |
| `powerbi://reports/{id}/pages` | Pages for a specific report |

---

### Prompts — user-controlled
Pre-built workflow templates you invoke for common tasks. Like pre-filled forms for professional Power BI workflows.

| Prompt | What it does |
|---|---|
| `explore_dataset` | Structured dataset exploration — understand tables, relationships, and measures |
| `explain_measure` | Plain-language DAX measure explainer — no jargon |
| `audit_report` | Governance and quality checklist before sharing a report |

---

## Quickstart

### What you need
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Desktop](https://claude.ai/download)

---

### Step 1 — Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen your terminal, then verify:
```bash
uv --version
```

---

### Step 2 — Clone and set up

```bash
git clone https://github.com/MrKhaled007/PowerBi-MCP.git
cd PowerBi-MCP
```

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

---

### Step 3 — Run the client demo

This connects the client to the server and tests all three primitives:

```bash
python mcp_client.py
```

Expected output:
```
Connected to Power BI MCP Server
============================================================
Tools     : 9
Resources : 3
Prompts   : 3
------------------------------------------------------------
TOOLS (model-controlled)
list_workspaces -> 2 workspaces:
  - ESM Risk & Finance (ID: ws-001)
  - Portfolio Analytics (ID: ws-002)
...
============================================================
All three MCP primitives working correctly.
```

---

### Step 4 — Test with MCP Inspector

The browser-based testing tool taught in Anthropic's MCP course:

```bash
mcp dev mcp_server.py
```

Open the URL shown in your terminal (usually `http://127.0.0.1:6274`) and click **Connect**.

```
┌──────────────────────────────────────────────────────┐
│  MCP Inspector                    ● Connected        │
│                                                      │
│  Resources │ Prompts │ Tools                        │
│  ────────────────────────────────────────────────    │
│                                                      │
│  Tools                                               │
│  ▶ list_workspaces          [Run Tool]               │
│  ▶ search_measures          keyword: [exposure]      │
│  ▶ generate_measure         dataset_id: [ds-001]     │
│                             description: [________]  │
│                                          [Run Tool]  │
└──────────────────────────────────────────────────────┘
```

You can test every tool, resource, and prompt interactively without connecting to Claude Desktop.

---

### Step 5 — Connect to Claude Desktop

Find your config file:

| OS | Location |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Windows Store | `%LOCALAPPDATA%\Packages\Claude*\LocalCache\Roaming\Claude\claude_desktop_config.json` |
| Mac | `~/Library/Application Support/Claude/claude_desktop_config.json` |

Add this to the config file — replace the path with your actual project path:

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

Fully quit and restart Claude Desktop. Open the `+` menu — you will see **powerbi** listed as a connected server. Start chatting.

---

## DAX Generation

The `generate_measure` tool generates DAX measures from plain English descriptions.

### Live mode (with Anthropic API credits)

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Create a `.env` file in the project folder:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```
3. Restart the server — Claude now generates real, schema-aware DAX on the fly

### Mock mode (without API credits)

If no API key is set or your account has no credits, the tool automatically falls back to realistic pre-built DAX examples. Everything still works — you just get mock responses instead of live generated ones.

```
"source": "live"  ← real Claude-generated DAX using your exact schema
"source": "mock"  ← pre-built fallback (add API credits to enable live)
```

---

## Phase 2 — Connect Your Own Power BI Data

By default this server runs with mock ESM/finance data so anyone can try it immediately. To connect your own real Power BI files, follow these steps.

---

### Step 1 — Publish your .pbix file to Power BI Service

Your reports need to be in the cloud for the API to reach them.

1. Open your `.pbix` file in **Power BI Desktop**
2. Click **Publish** in the top ribbon (Home tab, far right)
3. Select **My Workspace** and click **Select**
4. Go to [app.powerbi.com](https://app.powerbi.com) and verify your report appears

> You need a Power BI account to publish. Sign in with a Microsoft, work, or university email at app.powerbi.com — it is free.

---

### Step 2 — Register an Azure AD app

This gives the MCP server permission to read your Power BI workspace via the API.

1. Go to [portal.azure.com](https://portal.azure.com) and sign in
2. Search for **App registrations** → click **New registration**
3. Give it a name (e.g. `PowerBI MCP Server`) and click **Register**
4. Copy your **Tenant ID** and **Client ID** from the overview page
5. Go to **API permissions** → **Add a permission** → **Power BI Service**
6. Select **Delegated permissions** → check `Report.Read.All` and `Dataset.Read.All`
7. Click **Grant admin consent**
8. Go to **Certificates & secrets** → **New client secret**
9. Copy the secret value immediately — it only shows once

---

### Step 3 — Add your credentials to .env

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
PBI_TENANT_ID=your-tenant-id
PBI_CLIENT_ID=your-client-id
PBI_CLIENT_SECRET=your-client-secret
PBI_USERNAME=your-powerbi-email@domain.com
PBI_PASSWORD=your-powerbi-password
```

Restart Claude Desktop. The server automatically switches from mock data to your real Power BI workspace. No code changes needed.

```
Without .env:   Claude sees mock ESM/finance demo data
With .env:      Claude sees YOUR actual reports and datasets
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
├── .env.example        ← Credential template (copy to .env)
├── .gitignore          ← Keeps .env and .venv out of GitHub
└── README.md
```

---

## Troubleshooting

**Server not showing in Claude Desktop**
- Fully quit Claude Desktop (system tray → right click → Quit) before restarting
- Windows Store users: use the LocalCache path, not AppData\Roaming
- Make sure the Python path in your config points to `.venv\Scripts\python.exe` not system Python

**ModuleNotFoundError: No module named 'mcp'**
- Your terminal is using system Python instead of the venv
- Run `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac) first

**generate_measure returns mock response**
- The Anthropic API call failed — add credits at console.anthropic.com
- The mock fallback is working correctly — this is expected without credits

**401 error from Anthropic API**
- Your API key is wrong or has extra spaces
- Run: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"`
- Verify it starts with `sk-ant-`

**Power BI REST API returns 403**
- Your Azure AD app needs admin consent for the API permissions
- Go to portal.azure.com → App registrations → your app → API permissions → Grant admin consent

---

## Course Alignment

This project is fully aligned with **Anthropic's Introduction to MCP course**:

| Course requirement | Status |
|---|---|
| FastMCP decorator pattern (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`) | ✅ |
| All 3 primitives: tools, resources (direct + templated), prompts | ✅ |
| Async tool functions with type hints and docstrings | ✅ |
| Logging to stderr only — never stdout | ✅ |
| MCP Inspector compatible (`mcp dev mcp_server.py`) | ✅ |
| Both server and client built | ✅ |
| stdio transport with proper `main()` entry point | ✅ |
| Claude Desktop integration | ✅ |
| uv package manager | ✅ |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| MCP Python SDK (`mcp[cli]`) | FastMCP server and client |
| Anthropic SDK | DAX generation via Claude API |
| MSAL | Microsoft OAuth 2.0 for Power BI REST API |
| httpx | Async HTTP client |
| python-dotenv | Credential management via .env |
| uv | Fast Python package manager |

---

## Author

**Mohammed Khaled** — Final-year Data Science student, Thomas More University Mechelen

[LinkedIn](https://linkedin.com/in/mohammed-khaled-43a220183) · [GitHub](https://github.com/MrKhaled007)

Part of a broader data analytics portfolio targeting BI Analyst and Data Scientist roles in Brussels and Luxembourg.
