import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import db_engine
from src.database.core import init_database
from src.agents.worker_agents import quoting_agent

def run_quoting_agent_tests():
    print("=== 1. Initializing predictable database state (seed 137) ===")
    init_database(db_engine, seed=137)

    # Let's check the price of "Glossy paper"
    # standard price in seed data is $0.20. For 200 sheets, total is $40.00.
    # A bulk discount might be applied or history searched.
    print("\n=== 2. Running Agent Test: Generate quote for Glossy paper ===")
    prompt = (
        "Generate a quote for 200 sheets of 'Glossy paper' for a ceremony. "
        "Use get_item_price_tool to find standard prices, search quote history for similar "
        "ceremony/glossy paper requests to see how much we charged, apply a bulk discount "
        "if appropriate, and output a rounded final total and a detailed explanation of the quote."
    )
    print(f"Prompt: {prompt}")
    
    response = quoting_agent.run(prompt)
    
    print("\n=== 3. Evaluation Result ===")
    print(f"Agent final response:\n{response}")

if __name__ == "__main__":
    run_quoting_agent_tests()
