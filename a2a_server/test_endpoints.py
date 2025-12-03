# a2a_server/test_endpoints.py

from fastapi.testclient import TestClient
from a2a_server.http_service import app


def run_http_tests():
    """
    Runs sanity checks across all A2A HTTP endpoints.
    This ensures that agent-card discovery and /tasks APIs behave correctly.
    """

    client = TestClient(app)

    print("\n==================== A2A HTTP ENDPOINT TESTS ====================\n")

    # --------------------------------------------------------------
    # 1. CoordinatorUnit AgentCard
    # --------------------------------------------------------------
    print("▶ Test 1: CoordinatorUnit AgentCard")
    r = client.get("/a2a/coordinator/.well-known/agent-card.json")
    print("Status:", r.status_code)
    print("Name:", r.json().get("name"))
    print("URL:", r.json().get("url"))
    print()

    # --------------------------------------------------------------
    # 2. CoordinatorUnit /tasks
    # --------------------------------------------------------------
    print("▶ Test 2: CoordinatorUnit /tasks")
    payload = {"input": "Show customer 2 history"}
    r = client.post("/a2a/coordinator/tasks", json=payload)
    print("Status:", r.status_code)
    body = r.json()
    print("Route:", body.get("route"))
    print("Messages:", len(body.get("messages", [])))
    print()

    # --------------------------------------------------------------
    # 3. RecordsUnit AgentCard
    # --------------------------------------------------------------
    print("▶ Test 3: RecordsUnit AgentCard")
    r = client.get("/a2a/records/.well-known/agent-card.json")
    print("Status:", r.status_code)
    print("Name:", r.json().get("name"))
    print("URL:", r.json().get("url"))
    print()

    # --------------------------------------------------------------
    # 4. RecordsUnit /tasks
    # --------------------------------------------------------------
    print("▶ Test 4: RecordsUnit /tasks")
    payload = {"input": "Show customer id 1 history"}
    r = client.post("/a2a/records/tasks", json=payload)
    print("Status:", r.status_code)
    body = r.json()
    print("Invoked tool:", body.get("tool"))
    print("Found:", (body.get("result") or {}).get("found"))
    print("Messages:", len(body.get("messages", [])))
    print()

    # --------------------------------------------------------------
    # 5. AssistUnit AgentCard
    # --------------------------------------------------------------
    print("▶ Test 5: AssistUnit AgentCard")
    r = client.get("/a2a/assist/.well-known/agent-card.json")
    print("Status:", r.status_code)
    print("Name:", r.json().get("name"))
    print("URL:", r.json().get("url"))
    print()

    # --------------------------------------------------------------
    # 6. AssistUnit /tasks
    # --------------------------------------------------------------
    print("▶ Test 6: AssistUnit /tasks (ticket creation)")
    payload = {"input": "Create a high priority ticket for customer id 1 about billing error"}
    r = client.post("/a2a/assist/tasks", json=payload)
    print("Status:", r.status_code)
    body = r.json()
    print("Last step:", body.get("last_step"))
    print("Missing fields:", body.get("missing"))
    print("Created:", (body.get("result") or {}).get("created"))
    print("Messages:", len(body.get("messages", [])))
    print()

    print("==================== END OF TESTS ====================\n")


if __name__ == "__main__":
    run_http_tests()
