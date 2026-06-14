import pandas as pd
import time
import os

from config.settings import BASE_DIR, DATA_DIR, db_engine
from src.database.core import init_database
from src.tools.finance_tools import generate_financial_report
from src.agents.orchestrator import call_multi_agent_system

def run_test_scenarios():
    
    print("Initializing Database...")
    init_database(db_engine)
    try:
        quote_requests_path = os.path.join(DATA_DIR, "quote_requests_sample.csv")
        quote_requests_sample = pd.read_csv(quote_requests_path)
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############
    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############

        response = call_multi_agent_system(request_with_date)

        # Output-Sanitization Pass
        import re
        response_str = str(response)
        # Strip out any blocks enclosed in <code>...</code>
        response_str = re.sub(r'<code>.*?</code>', '', response_str, flags=re.DOTALL)
        # Remove any lines starting with `thought`
        response_lines = [line for line in response_str.split('\n') if not line.strip().startswith('thought')]
        response_str = '\n'.join(response_lines).strip()
        
        if not response_str:
            response_str = "I'm sorry, I couldn't process this request."
        response = response_str

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )

        time.sleep(8)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    results_path = os.path.join(BASE_DIR, "test_results.csv")
    pd.DataFrame(results).to_csv(results_path, index=False)
    return results

if __name__ == "__main__":
    results = run_test_scenarios()
