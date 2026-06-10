import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import db_engine
from src.database.core import init_database
from src.agents.orchestrator import call_your_multi_agent_system

def run_orchestrator_test():
    print("=== 1. Initializing predictable database state (seed 137) ===")
    init_database(db_engine, seed=137)

    request = (
        "I would like to request the following paper supplies for the ceremony:\n"
        "- 200 sheets of A4 glossy paper\n"
        "- 100 sheets of heavy cardstock (white)\n"
        "- 100 sheets of colored paper (assorted colors)\n"
        "I need these supplies delivered by April 15, 2025. Thank you."
    )
    request_date = "2025-04-01"
    request_with_date = f"{request} (Date of request: {request_date})"

    print("\n=== 2. Running Orchestrator Agent Test ===")
    print(f"Request: {request_with_date}")
    
    response = call_your_multi_agent_system(request_with_date)
    
    print("\n=== 3. Evaluation Result ===")
    print(f"Orchestrator final response:\n{response}")

if __name__ == "__main__":
    run_orchestrator_test()