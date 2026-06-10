import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import db_engine
from src.database.core import init_database
from src.agents.worker_agents import inventory_agent

def run_inventory_agent_tests():
    print("=== 1. Initializing predictable database state (seed 137) ===")
    init_database(db_engine, seed=137)

    # We know that with seed=137, "A4 paper" has a current stock of 272
    test_item = "A4 paper"
    test_date = "2025-01-02"
    expected_stock = 272

    print(f"\n=== 2. Running Agent Test: Check stock of '{test_item}' ===")
    prompt = f"Please check the stock level of '{test_item}' as of {test_date}."
    print(f"Prompt: {prompt}")
    
    response = inventory_agent.run(prompt)
    
    print("\n=== 3. Evaluation Result ===")
    print(f"Agent final response: {response}")
    print(f"Expected stock quantity: {expected_stock}")
    
    if str(expected_stock) in str(response):
        print("\nSUCCESS: Agent correctly retrieved and reported the stock level!")
    else:
        print("\nWARNING: Agent response did not match the expected stock level.")

if __name__ == "__main__":
    run_inventory_agent_tests()
