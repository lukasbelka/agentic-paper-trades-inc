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

def format_customer_response(response_str: str) -> str:
    import litellm
    from config.settings import GEMINI_API_KEY
    
    prompt = f"""
Please rewrite the following text so that it is exclusively a professional, synthesized customer email.
You MUST completely remove and rephrase the following to hide all internal system operations:
1. Transaction IDs or database references (e.g. "transaction ID: 20", "recorded in the database", "registered as sales transactions").
2. Agent-Trace headings and metadata (e.g. "Task outcome", "Here is the final answer...", "observation above").
3. Exact inventory quantities and diagnostics (e.g. "272 sheets", "-105 sheets", "0 units", "inventory discrepancy"). Replace with simple availability phrases (e.g. "currently unavailable", "not in our catalog", "out of stock").
4. Tool names (e.g. get_supplier_delivery_date_tool, *_tool).
5. Internal system errors (e.g. "failed to extract details", "quoting system", "system lacks pricing information").
6. Do NOT use placeholders like "[Your Company Name]". Instead, end the email with a fixed signature:
"Best regards,
Munder Difflin Paper Co."

Output ONLY the rewritten customer email, nothing else. Do not hallucinate details not present in the original message.

Original Text:
{response_str}
"""
    try:
        llm_response = litellm.completion(
            model="gemini/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            api_key=GEMINI_API_KEY
        )
        return llm_response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback if LLM fails
        return "Your order has been processed. Thank you!\n\nBest regards,\nMunder Difflin Paper Co."

def call_multi_agent_system(request_with_date: str) -> str:
    result = orchestrator_agent.run(request_with_date)
    result_str = str(result).strip()
    
    if result_str.startswith('<code>') or result_str.startswith('thought') or 'Calling tools:' in result_str[:200]:
        return _fallback_message(request_with_date)
        
    # Use robust LLM-based sanitization
    return format_customer_response(result_str)