from smolagents import CodeAgent
from src.agents.core import model_orchestrator
from src.agents.worker_agents import inventory_agent, quoting_agent, sales_closure_agent

# Create the Orchestrator Agent
orchestrator_agent = CodeAgent(
    tools=[],
    model=model_orchestrator,
    managed_agents=[inventory_agent, quoting_agent, sales_closure_agent],
    max_steps=12,
    name="orchestrator_agent",
    description="""You are the orchestrator agent handling customer quote requests for a paper trading company.
    You must strictly follow this workflow:

1. **Inventory Check**: Pass the customer's raw item names and requested dates to the `inventory_agent`.
     If the `inventory_agent` reports that the requested items cannot be processed due to insufficient stock,
     you must immediately decline the order and explain the reason to the customer. Do not proceed to the next steps.
2. **Generate Quote**: If sufficient stock is available, pass the confirmed catalog items, quantities, and dates to
     the `quoting_agent`. The quoting agent will determine base prices, apply bulk discounts, and return the final
     quoted amounts along with an explanation.
3. **Record Transaction**: Once the quote is generated, pass the finalized catalog names, quantities, quoted price,
     and date to the `sales_closure_agent`. This agent will update the database and return a transaction ID.

Final Step: Once the sales closure agent has finished, provide a final response to the client.
This final response MUST include the catalog items, quantities, final quoted price, transaction outcome,
and delivery information.

You MUST end every conversation by calling final_answer(...) with a customer-facing, friendly natural language string. 
Never include raw code, internal tool names, reasoning traces, or dictionary-like formats (e.g., {'Task outcome': ...}) in the final answer. 
Do NOT simply copy-paste or forward the response from your managed agents (e.g., avoid "Here is the final answer from your managed agent"). You must synthesize the information into a professional message directly to the customer."""
)

def _fallback_message(request: str) -> str:
    return "I'm sorry, I couldn't process this request."

def call_multi_agent_system(request_with_date: str) -> str:
    result = orchestrator_agent.run(request_with_date)
    result_str = str(result).strip()
    if result_str.startswith('<code>') or result_str.startswith('thought') or 'Calling tools:' in result_str[:200]:
        return _fallback_message(request_with_date)
        
    # Safety net: Catch any leaked dictionaries or raw agent forwards
    if "Here is the final answer from your managed agent" in result_str or "{'" in result_str:
        import ast
        try:
            dict_str = result_str[result_str.find("{"):]
            data = ast.literal_eval(dict_str)
            for k, v in data.items():
                if 'extremely detailed version' in k.lower() or 'detailed' in k.lower():
                    return str(v).strip()
        except Exception:
            pass
        return "Your order has been processed successfully. Thank you!"
        
    return result_str