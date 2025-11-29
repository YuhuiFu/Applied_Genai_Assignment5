# Applied_Genai_Assignment5
# Multi-Agent Customer Service System with MCP

This repository contains my solution for the **"Multi-Agent Customer Service System with A2A and MCP"** assignment.

It includes:

1. **MCP server implementation**  
   - `mcp_server/mcp.py` (`CustomerDatabaseMCP`)

2. **Agent implementations**  
   - `agents/router_agent.py` (`RouterAgent`)  
   - `agents/customer_data_agent.py` (`CustomerDataAgent`)  
   - `agents/support_agent.py` (`SupportAgent`)  
   - Shared definitions in `agents/base.py`

3. **Configuration and deployment scripts**  
   - `scripts/setup_venv.sh` – create & configure Python virtual environment  
   - `scripts/run_demo.sh` – run all scenarios end-to-end  
   - `scripts/reset_db.sh` – reset the SQLite database

4. **README with setup instructions**  
   - This file, plus `requirements.txt` for Python environment separation.

---

## Repository Structure

```text
.
├── mcp_server/
│   ├── __init__.py
│   └── mcp.py
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── router_agent.py
│   ├── customer_data_agent.py
│   └── support_agent.py
├── database/
│   ├── __init__.py
│   └── database_setup.py
├── scripts/
│   ├── setup_venv.sh
│   ├── run_demo.sh
│   └── reset_db.sh
├── multi_agent_system.py
├── requirements.txt
└── README.md
