**Assignment 5 — Multi-Agent Customer Service System

(A2A Coordination + MCP Integration + LangGraph)**

This project implements a multi-agent customer-support system using LangGraph, Agent-to-Agent (A2A) communication, and the Model Context Protocol (MCP). The system consists of three cooperating agents — CoordinatorUnit, RecordsUnit, and AssistUnit — which together perform routing, database retrieval, negotiation, and ticket creation. All database operations are abstracted behind an MCP server exposing five standard tools.

This repository includes the complete implementation, modularized into separate Python files to make the system easier to deploy, test, and demonstrate.
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
Assignment5/
│
├── README.md
├── requirements.txt
├── database_setup.py
├── support.db         
│
├── mcp_server/
│   ├── __init__.py
│   ├── mcp_core.py              
│
├── agents/
│   ├── __init__.py
│   ├── coordinator.py          
│   ├── records.py               
│   ├── assist.py                
│
├── a2a_server/
│   ├── __init__.py
│   ├── http_service.py          
│   ├── test_endpoints.py        
│
└── notebook/
    ├── Assignment5.ipynb       
