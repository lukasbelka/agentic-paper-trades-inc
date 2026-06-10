from smolagents import CodeAgent
from src.agents.core import model_orchestrator
from src.agents.worker_agents import inventory_agent, quoting_agent, sales_closure_agent

# Create the Orchestrator Agent
orchestrator_agent = CodeAgent(
    tools=[],
    model=model_orchestrator,
    managed_agents=[inventory_agent, quoting_agent, sales_closure_agent],
    name="orchestrator_agent",
    description="Orchestrator that receives customer quote requests and coordinates the inventory check, price quoting, and sales closure."
)

def call_your_multi_agent_system(request_with_date: str) -> str:
    prompt = f"""
You are the business manager orchestrator for Munder Difflin Paper Company.
You have received the following customer request:
"{request_with_date}"

Your task is to coordinate the worker agents to process this request:
1. First, call `inventory_agent` to check if all requested items are in stock as of the request date.
   - Note: The customer may use slightly different names (e.g. 'A4 glossy paper' instead of 'Glossy paper', or 'heavy cardstock' instead of 'Cardstock', or 'standard printer paper' instead of 'A4 paper'). The inventory agent should map these to the closest matching item in our database catalog.
   - If we have sufficient stock for all requested items:
     - Call `quoting_agent` to generate a price quote for the items, applying bulk discounts and historical pricing if applicable.
     - Call `sales_closure_agent` to record the 'sales' transaction in the database on the request date with the total price.
     - Provide the finalized quote and confirmation to the customer.
   - If any item is out of stock or has insufficient quantity:
     - Check if we carry the item in our catalog (inventory table).
     - If we do carry the item, check if we can reorder it from the supplier:
       - Use `sales_closure_agent` to check if we have enough cash balance to cover the reorder cost (cost = quantity needed * unit price).
       - Calculate the supplier delivery date using `sales_closure_agent` (get_supplier_delivery_date_tool).
       - If the delivery date is on or before the customer's requested delivery deadline:
         - Create a `stock_orders` transaction using `sales_closure_agent` with the transaction date set to the supplier delivery date (when the stock arrives).
         - Since the stock arrives in time, we can now fulfill the customer's request. Proceed to call `quoting_agent` to get a quote, and `sales_closure_agent` to record the customer sale transaction on the customer's requested delivery date (when we ship the fulfilled order).
         - Confirm to the customer that their order will be delivered, explaining that we restocked the items.
       - If the delivery date is after the customer's deadline, or we don't have enough cash:
         - Respond politely explaining that we cannot fulfill the order because restocking would take too long or we lack stock.
     - If we do not carry the item in our catalog at all:
       - Respond politely explaining that we do not sell this item.

Always return the final outcome clearly as your final answer.
"""
    return orchestrator_agent.run(prompt)