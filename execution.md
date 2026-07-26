# AI Research Agent 
## Objective
Build an AI Research Agent using Model Context Protocol (MCP).
The project should demonstrate:
- MCP Server
- MCP Client
- Internet Tool
- File CRUD Tool
- Prefab UI
- Clear Client & Server Logs

## Project Structure
(you can choose your own what best fits)
project/

server.py
client.py

tools/
    research_tool.py
    file_tool.py
    prefab_tool.py

reports/
README.md
## MCP Tools
1. research_topic()
Search the internet for any AI topic.
Return:
- Title
- Summary
- Key Points
- References
2. manage_report()
Perform CRUD operations.
Support:
- Create
- Read
- Update
- Delete
Store reports inside the `reports/` folder.
### 3. render_dashboard()
Use **Prefab** to display the report.
Dashboard should show:
- Research Title
- Summary
- Key Points
- References
- Saved File Name

Do not create a custom HTML page. Use Prefab.

## Client Workflow

`client.py` should contain a user prompt like:

```python
user_prompt = """
Research Model Context Protocol (MCP),
prepare a short research report,
save it as mcp_report.md,
and display it on a Prefab dashboard.
"""
```
(or use `input()` to accept a prompt from the user.)

The client sends this prompt to Gemini/LLM.

The LLM should automatically discover and use the MCP tools.

## Expected Workflow

User Prompt

↓

research_topic()

↓

manage_report()

↓

render_dashboard()

↓

Final Response
```

The tools must be selected automatically by the Agent.

Do not manually call each tool.

---

## Client Logs

Display logs similar to:

```
==============================
MCP CLIENT
==============================

Round 1

Thinking...

Calling research_topic()

Success

------------------------------

Round 2

Calling manage_report()

Report Saved

------------------------------

Round 3

Calling render_dashboard()

Dashboard Generated

------------------------------

Mission Complete
```

---

## Server Logs

Display logs like:

```
MCP SERVER STARTED

Waiting for Client...

Tool Registered:
✓ research_topic
✓ manage_report
✓ render_dashboard

Incoming Request

Executing Tool

Returning Response
```

---

## Final Demo Prompt

Use this prompt during the demo:

```
Research "Model Context Protocol (MCP)",
prepare a concise research report,
save it locally as mcp_report.md,
and display it on a Prefab dashboard.
```

This prompt should force the Agent to use:

1. Internet Tool
2. File CRUD Tool
3. Prefab UI

without any manual tool selection.

---

## Goal

The final demo should clearly show:

✓ MCP Server running

✓ MCP Client running

✓ Agent automatically selecting tools

✓ Internet search

✓ Report saved locally

✓ Prefab dashboard displayed

✓ Clean client and server logs