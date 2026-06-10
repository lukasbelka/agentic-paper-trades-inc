import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import db_engine
from src.database.core import init_database
from src.agents.worker_agents import sales_closure_agent

def run_sales_closure_agent_tests():
    print("=== 1. Initializing predictable database state (seed 137) ===")
    init_database(db_engine, seed=137)

    # Let's test registering a sale and checking cash
    print("\n=== 2. Running Agent Test: Record sale of A4 paper and audit cash ===")
    prompt = (
        "We sold 100 sheets of A4 paper for $5.00 on 2025-01-02. "
        "Please: "
        "1) Use create_transaction_tool to record this sale. "
        "2) Use get_cash_balance_tool to check the updated cash balance as of 2025-01-02. "
        "3) Use generate_financial_report_tool to print the final report on 2025-01-02. "
        "Explain all results clearly."
    )
    print(f"Prompt: {prompt}")
    
    response = sales_closure_agent.run(prompt)
    
    print("\n=== 3. Evaluation Result ===")
    print(f"Agent final response:\n{response}")

if __name__ == "__main__":
    run_sales_closure_agent_tests()
