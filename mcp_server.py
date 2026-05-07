import json
import logging
import sys
from mcp.server.fastmcp import FastMCP
import mock_data as db

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("powerbi-mcp-server")


# ═══════════════════════════════════════════════════════
# TOOLS — model-controlled
# Claude decides when to call these automatically.
# Think of these like buttons Claude can press on its own.
# ═══════════════════════════════════════════════════════

@mcp.tool()
async def list_workspaces() -> str:
    """List all Power BI workspaces available in the connected account."""
    logger.info("Tool called: list_workspaces")
    return json.dumps({"workspaces": db.WORKSPACES, "count": len(db.WORKSPACES)}, indent=2)


@mcp.tool()
async def list_reports(workspace_id: str = "") -> str:
    """List all Power BI reports, optionally filtered by workspace.

    Args:
        workspace_id: Optional workspace ID to filter results (e.g. ws-001). Leave empty for all reports.
    """
    logger.info("Tool called: list_reports workspace_id=%s", workspace_id)
    reports = db.REPORTS
    if workspace_id:
        reports = [r for r in reports if r["workspaceId"] == workspace_id]
    result = [
        {
            "id": r["id"],
            "name": r["name"],
            "datasetId": r["datasetId"],
            "workspaceId": r["workspaceId"],
            "webUrl": r["webUrl"],
        }
        for r in reports
    ]
    return json.dumps({"reports": result, "count": len(result)}, indent=2)


@mcp.tool()
async def list_datasets(workspace_id: str = "") -> str:
    """List all Power BI datasets, optionally filtered by workspace.

    Args:
        workspace_id: Optional workspace ID to filter results (e.g. ws-001). Leave empty for all datasets.
    """
    logger.info("Tool called: list_datasets workspace_id=%s", workspace_id)
    datasets = db.DATASETS
    if workspace_id:
        datasets = [d for d in datasets if d["workspaceId"] == workspace_id]
    result = [
        {
            "id": d["id"],
            "name": d["name"],
            "workspaceId": d["workspaceId"],
            "isRefreshable": d["isRefreshable"],
            "configuredBy": d["configuredBy"],
        }
        for d in datasets
    ]
    return json.dumps({"datasets": result, "count": len(result)}, indent=2)


@mcp.tool()
async def get_report_pages(report_id: str) -> str:
    """Get all pages (tabs) within a specific Power BI report.

    Args:
        report_id: The report ID to look up (e.g. rpt-001). Get valid IDs from list_reports.
    """
    logger.info("Tool called: get_report_pages report_id=%s", report_id)
    for r in db.REPORTS:
        if r["id"] == report_id:
            return json.dumps(
                {
                    "report_id": report_id,
                    "report_name": r["name"],
                    "pages": r["pages"],
                    "count": len(r["pages"]),
                },
                indent=2,
            )
    return json.dumps({"error": f"Report '{report_id}' not found"})


@mcp.tool()
async def get_dataset_schema(dataset_id: str) -> str:
    """Get the full schema of a dataset — tables, columns, and data types.

    Args:
        dataset_id: The dataset ID to look up (e.g. ds-001). Get valid IDs from list_datasets.
    """
    logger.info("Tool called: get_dataset_schema dataset_id=%s", dataset_id)
    for d in db.DATASETS:
        if d["id"] == dataset_id:
            return json.dumps(
                {
                    "id": d["id"],
                    "name": d["name"],
                    "tables": d["tables"],
                    "table_count": len(d["tables"]),
                },
                indent=2,
            )
    return json.dumps({"error": f"Dataset '{dataset_id}' not found"})


@mcp.tool()
async def list_measures(dataset_id: str = "") -> str:
    """List DAX measures with their expressions and descriptions.

    Args:
        dataset_id: Optional dataset ID to filter measures (e.g. ds-001). Leave empty for all measures.
    """
    logger.info("Tool called: list_measures dataset_id=%s", dataset_id)
    measures = db.MEASURES
    if dataset_id:
        measures = [m for m in measures if m["datasetId"] == dataset_id]
    return json.dumps({"measures": measures, "count": len(measures)}, indent=2)


@mcp.tool()
async def search_measures(keyword: str) -> str:
    """Search for DAX measures by keyword across name, description, or DAX expression.

    Args:
        keyword: Search term to match (e.g. exposure, default, anomaly).
    """
    logger.info("Tool called: search_measures keyword=%s", keyword)
    kw = keyword.lower()
    matches = [
        m for m in db.MEASURES
        if kw in m["name"].lower()
        or kw in m.get("description", "").lower()
        or kw in m.get("expression", "").lower()
    ]
    return json.dumps({"keyword": keyword, "matches": matches, "count": len(matches)}, indent=2)


@mcp.tool()
async def get_lineage(dataset_id: str) -> str:
    """Show which reports depend on a given dataset — dataset-to-report lineage.

    Args:
        dataset_id: The dataset ID to trace (e.g. ds-001). Get valid IDs from list_datasets.
    """
    logger.info("Tool called: get_lineage dataset_id=%s", dataset_id)
    dependent_reports = [
        {"id": r["id"], "name": r["name"], "webUrl": r["webUrl"]}
        for r in db.REPORTS
        if r["datasetId"] == dataset_id
    ]
    dataset_name = next(
        (d["name"] for d in db.DATASETS if d["id"] == dataset_id), "Unknown"
    )
    return json.dumps(
        {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "dependent_reports": dependent_reports,
            "count": len(dependent_reports),
        },
        indent=2,
    )


# ═══════════════════════════════════════════════════════
# RESOURCES — app-controlled
# Read-only data loaded into context via URI addresses.
# Think of these like files Claude can open and read.
# ═══════════════════════════════════════════════════════

@mcp.resource("powerbi://workspaces")
def resource_workspaces() -> str:
    """All Power BI workspaces as a readable resource."""
    lines = ["# Power BI Workspaces\n"]
    for ws in db.WORKSPACES:
        lines.append(f"- **{ws['name']}** (ID: `{ws['id']}`, State: {ws['state']})")
    return "\n".join(lines)


@mcp.resource("powerbi://reports")
def resource_reports() -> str:
    """All Power BI reports as a readable resource."""
    lines = ["# Power BI Reports\n"]
    for r in db.REPORTS:
        lines.append(
            f"- **{r['name']}** (ID: `{r['id']}`, Dataset: `{r['datasetId']}`, Workspace: `{r['workspaceId']}`)"
        )
    return "\n".join(lines)


@mcp.resource("powerbi://datasets")
def resource_datasets() -> str:
    """All Power BI datasets as a readable resource."""
    lines = ["# Power BI Datasets\n"]
    for d in db.DATASETS:
        col_count = sum(len(t["columns"]) for t in d["tables"])
        lines.append(
            f"- **{d['name']}** (ID: `{d['id']}`, Tables: {len(d['tables'])}, Columns: {col_count})"
        )
    return "\n".join(lines)


@mcp.resource("powerbi://datasets/{dataset_id}/schema")
def resource_dataset_schema(dataset_id: str) -> str:
    """Schema for a specific dataset — tables and columns.

    Args:
        dataset_id: The dataset ID (e.g. ds-001, ds-002, ds-003).
    """
    for d in db.DATASETS:
        if d["id"] == dataset_id:
            lines = [f"# Schema: {d['name']}\n"]
            for table in d["tables"]:
                lines.append(f"## Table: {table['name']}")
                for col in table["columns"]:
                    lines.append(f"  - `{col['name']}` ({col['dataType']})")
                lines.append("")
            return "\n".join(lines)
    return f"# Error\nDataset '{dataset_id}' not found."


@mcp.resource("powerbi://datasets/{dataset_id}/measures")
def resource_measures(dataset_id: str) -> str:
    """All DAX measures for a specific dataset.

    Args:
        dataset_id: The dataset ID (e.g. ds-001, ds-002, ds-003).
    """
    measures = [m for m in db.MEASURES if m["datasetId"] == dataset_id]
    dataset_name = next(
        (d["name"] for d in db.DATASETS if d["id"] == dataset_id), dataset_id
    )
    lines = [f"# DAX Measures: {dataset_name}\n"]
    for m in measures:
        lines.append(f"## {m['name']}")
        lines.append(f"**Table:** {m['table']}")
        lines.append(f"**Description:** {m.get('description', 'N/A')}")
        lines.append(f"**Expression:**\n```dax\n{m['expression']}\n```")
        lines.append("")
    return "\n".join(lines)


@mcp.resource("powerbi://reports/{report_id}/pages")
def resource_report_pages(report_id: str) -> str:
    """Pages (tabs) for a specific Power BI report.

    Args:
        report_id: The report ID (e.g. rpt-001, rpt-002, rpt-003).
    """
    for r in db.REPORTS:
        if r["id"] == report_id:
            lines = [f"# Pages: {r['name']}\n"]
            for p in r["pages"]:
                lines.append(
                    f"{p['order']}. **{p['displayName']}** (internal name: `{p['name']}`)"
                )
            return "\n".join(lines)
    return f"# Error\nReport '{report_id}' not found."


# ═══════════════════════════════════════════════════════
# PROMPTS — user-controlled
# Reusable workflow templates the user picks and runs.
# Think of these like pre-filled forms for common tasks.
# ═══════════════════════════════════════════════════════

@mcp.prompt()
def explore_dataset(dataset_id: str) -> str:
    """Generate a structured exploration prompt for a Power BI dataset.

    Args:
        dataset_id: The dataset ID to explore (e.g. ds-001, ds-002, ds-003).
    """
    dataset = next((d for d in db.DATASETS if d["id"] == dataset_id), None)
    if not dataset:
        return f"Dataset '{dataset_id}' not found. Use list_datasets to find valid IDs."
    table_names = ", ".join(t["name"] for t in dataset["tables"])
    measures = [m for m in db.MEASURES if m["datasetId"] == dataset_id]
    measure_names = ", ".join(m["name"] for m in measures) or "None defined"
    return f"""You are a Power BI expert helping analyse the '{dataset['name']}' dataset.

Dataset overview:
- Tables: {table_names}
- Measures: {measure_names}
- Refreshable: {dataset['isRefreshable']}

Please help me:
1. Understand what this dataset represents and its business purpose
2. Identify the key relationships between tables
3. Explain what each measure calculates in plain business language
4. Suggest 3 insightful questions this dataset could answer in a Power BI report
"""


@mcp.prompt()
def explain_measure(measure_name: str) -> str:
    """Generate a prompt to explain a DAX measure in plain business language.

    Args:
        measure_name: The exact name of the DAX measure (e.g. Expected Loss, Default Rate).
    """
    measure = next(
        (m for m in db.MEASURES if m["name"].lower() == measure_name.lower()), None
    )
    if not measure:
        return f"Measure '{measure_name}' not found. Use list_measures or search_measures to find valid names."
    return f"""You are a Power BI and DAX expert. Please explain the following DAX measure clearly.

Measure name: {measure['name']}
Table: {measure['table']}
Description: {measure.get('description', 'N/A')}
DAX Expression:
{measure['expression']}

Please provide:
1. A plain-language explanation of what this measure calculates (no DAX jargon)
2. A business use case — when would a BI analyst use this?
3. Any potential performance considerations or improvement suggestions
"""


@mcp.prompt()
def audit_report(report_id: str) -> str:
    """Generate a structured audit prompt for a Power BI report.

    Args:
        report_id: The report ID to audit (e.g. rpt-001, rpt-002, rpt-003).
    """
    report = next((r for r in db.REPORTS if r["id"] == report_id), None)
    if not report:
        return f"Report '{report_id}' not found. Use list_reports to find valid IDs."
    dataset = next((d for d in db.DATASETS if d["id"] == report["datasetId"]), None)
    dataset_name = dataset["name"] if dataset else "Unknown"
    pages = "\n".join(f"  - {p['displayName']}" for p in report["pages"])
    return f"""You are a Power BI governance expert conducting a report audit.

Report: {report['name']}
Dataset: {dataset_name}
Pages:
{pages}

Please audit this report and provide:
1. A summary of what business questions each page appears to answer
2. Data governance checklist — what should be verified before sharing this report?
3. Recommendations to improve clarity, performance, or usability
4. Suggested KPIs or visuals that might be missing based on the dataset available
"""


# ═══════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════

def main():
    logger.info("Starting Power BI MCP Server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()