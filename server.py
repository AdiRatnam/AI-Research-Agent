import os
import sys
import subprocess
import time
from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS

def log(msg):
    """Write logs to stderr so we don't break the MCP stdio protocol."""
    print(msg, file=sys.stderr)
    sys.stderr.flush()

mcp = FastMCP("AI Research Agent Server")

@mcp.tool()
def research_topic(topic: str) -> dict:
    """Search the internet for any AI topic.
    
    Args:
        topic: The AI topic to research
    """
    log("Incoming Request")
    log("Executing Tool: research_topic")
    
    with DDGS() as ddgs:
        results = list(ddgs.text(topic, max_results=3))
    
    if not results:
        res = {"Title": topic, "Summary": "No results found.", "Key Points": [], "References": []}
    else:
        summary = results[0].get('body', '')
        key_points = [r.get('body', '') for r in results[1:]]
        references = [r.get('href', '') for r in results]

        res = {
            "Title": topic,
            "Summary": summary,
            "Key Points": key_points,
            "References": references
        }
        
    log("Returning Response")
    return res

@mcp.tool()
def manage_report(action: str, filename: str, content: str = "") -> str:
    """Perform CRUD operations on reports.
    
    Args:
        action: One of 'create', 'read', 'update', 'delete'.
        filename: The name of the file in the reports/ directory.
        content: The text content for create/update.
    """
    log("Incoming Request")
    log(f"Executing Tool: manage_report ({action})")
    
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    filepath = os.path.join(reports_dir, filename)

    result = "Invalid action"
    if action in ["create", "update"]:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        result = "Report Saved"
    elif action == "read":
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                result = f.read()
        else:
            result = "File not found"
    elif action == "delete":
        if os.path.exists(filepath):
            os.remove(filepath)
            result = "Report Deleted"
        else:
            result = "File not found"
            
    log("Returning Response")
    return result

@mcp.tool()
def render_dashboard(title: str, summary: str, key_points: list[str], references: list[str], file_name: str) -> str:
    """Use Prefab to display the report dashboard in the background and return the URL.
    
    Args:
        title: The research title.
        summary: The summary of the research.
        key_points: List of key points.
        references: List of references URLs.
        file_name: The saved file name.
    """
    log("Incoming Request")
    log("Executing Tool: render_dashboard")
    
    # Generate the prefab python file
    dashboard_code = f"""
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, Row, 
    H1, P, Badge, Separator, Markdown, Metric, Grid, GridItem, Tabs, Tab
)
from prefab_ui.app import PrefabApp as App

app = App(title="AI Research Dashboard")

with app:
    with Column(gap=6, className="p-8 max-w-6xl mx-auto"):
        with Row(className="justify-between items-center"):
            with Column(gap=1):
                H1("AI Research Report", className="text-4xl font-extrabold tracking-tight")
                P("{title}", className="text-muted-foreground text-lg")
            with Badge(variant="secondary", className="text-sm px-3 py-1"):
                P("Source: {file_name}")

        Separator()

        with Grid(columns=2, gap=4):
            with GridItem():
                with Card(className="shadow-sm"):
                    with CardContent(className="p-6"):
                        Metric(label="Key Points Extracted", value={len(key_points)})
            with GridItem():
                with Card(className="shadow-sm"):
                    with CardContent(className="p-6"):
                        Metric(label="References Found", value={len(references)})

        with Tabs(default_value="summary"):
            with Tab(value="summary", label="Summary"):
                with Card(className="mt-4 shadow-md border-t-4 border-t-blue-500"):
                    with CardHeader():
                        CardTitle("Research Summary", className="text-2xl text-blue-700")
                    with CardContent():
                        P(\"\"\"{summary}\"\"\", className="text-gray-700 leading-relaxed text-lg")

            with Tab(value="key_points", label="Key Points"):
                with Card(className="mt-4 shadow-md border-t-4 border-t-green-500"):
                    with CardHeader():
                        CardTitle("Key Points", className="text-2xl text-green-700")
                    with CardContent():
"""
    # Key points as markdown list
    kp_md = "\\n".join([f"- {kp}" for kp in key_points]).replace('"', '\\"').replace('\\', '\\\\')
    dashboard_code += f'                        Markdown(\"\"\"{kp_md}\"\"\")\n'

    dashboard_code += """
            with Tab(value="references", label="References"):
                with Card(className="mt-4 shadow-md border-t-4 border-t-purple-500"):
                    with CardHeader():
                        CardTitle("References", className="text-2xl text-purple-700")
                    with CardContent():
"""
    # References as markdown list
    ref_md = "\\n".join([f"- [{ref}]({ref})" for ref in references]).replace('"', '\\"').replace('\\', '\\\\')
    dashboard_code += f'                        Markdown(\"\"\"{ref_md}\"\"\")\n'

    with open("dashboard.py", "w", encoding="utf-8") as f:
        f.write(dashboard_code)
        
    # Find prefab in the .venv
    prefab_cmd = os.path.join(".venv", "Scripts", "prefab.exe")
    if not os.path.exists(prefab_cmd):
        prefab_cmd = "prefab" # Fallback to PATH
        
    # Start the prefab server in the background
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.Popen([prefab_cmd, "serve", "dashboard.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
    
    # Wait briefly for it to start
    time.sleep(2)
    
    log("Returning Response")
    return "Dashboard Generated"

if __name__ == "__main__":
    log("MCP SERVER STARTED\\n")
    log("Waiting for Client...\\n")
    log("Tool Registered:")
    log("✓ research_topic")
    log("✓ manage_report")
    log("✓ render_dashboard\\n")
    mcp.run()


