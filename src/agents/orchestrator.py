from smolagents import CodeAgent
from src.agents.core import model_orchestrator
from src.agents.worker_agents import inventory_agent, quoting_agent, sales_closure_agent

# Create the Orchestrator Agent
orchestrator_agent = CodeAgent(
    tools=[],
    model=model_orchestrator,
    managed_agents=[inventory_agent, quoting_agent, sales_closure_agent],
    max_steps=8,
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

You MUST end every conversation by calling final_answer(...) with a customer-facing string. Never include raw code,
internal tool names, or reasoning traces in the final answer."""
)

def call_multi_agent_system(request_with_date: str) -> str:
    return orchestrator_agent.run(request_with_date)