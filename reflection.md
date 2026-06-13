# Reflection document

This document is the accompanying reflection to the agentic-system capstone project realized in udacity's AGENTIC AI nanodegree.
The application is built for the "Beaver's Choice Paper Company" to improve internal processes, enable a quick sales offer creation and stock tracking.

The task was to build an agentic system solution with max five agents that handle customer inquiries, check current stock, create offers and persist transactions in the database. The system processes text based inputs and outputs.

The agentic framework choosen is smolagents from HuggingFace. For all agents (orchestrator and all worker agents) google's gemini-flash-latest is implemented, as this allows for a free tier usage and easy replication with a google API key. 

## Agentic implementation

There are four agents implemented
- Orchestrator
- Invetory Agent
- Quoting Agent
- Sales Closure Agent

The easiest possible implementation was choosen as suggested, to make sure the complexity is as minimal as possible, allowing for a practical demonstration at the same time.

### Orchestrator

The graphic (graphic_agentic_system_flowchart.png) shows the implemented agents with their responsibilites and available tools. The orchestrator does not use a specific tool and acts as the "thinker" in the system. This agent's main role is to receive a customer (text based) request and coordinate the inventory check, price quoting, and sales closure agents. Therefore the orchestrator delegates tasks and receives the results from the worker-agents to further process the customer request. This allows the orchestrator to finally provide an answer to the client. In a real world enterprise implementation one would use one of the sophisticated LLMs for the orchestrator to achieve a best overall thinking processes whereas the worker-agents can use another, less token-intensive model for their specific and narrow tasks.

The worker-agents and their tools are described below - each of the worker agents has access to the database. A complete representation of the workflows is described subsequently afterwards the worker agents according to the corresponding "graphic_information_system.png".

### Inventory Agent
The inventory agent receives the initial information from the orchestrator and manages and checks the inventory of paper products. This agent is capable of retrieving exact catalog item names and mapping inexact customer requests to the closest catalog match before checking stock levels and details. The inventory agent has access to four tools:

- get_all_inventory_tool
    - Retrieve a snapshot of available inventory as of a specific date. Only items with positive stock are included.
- get_stock_level_tool
    - Retrieve the current stock level of a specific item as of a given date.
- get_catalog_items_tool
    - Retrieve the names of all paper products and items carried in Munder Difflin's catalog. Retrieves a list of items sold in the catalog, regardless of current stock levels.
- get_inventory_details_tool
    - Retrieve details for a specific catalog item, including its category, unit price, minimum stock level, and current stock level as of a given date.

### Quoting Agent
The quoting agent receives the validated item names and quantities from the orchestrator if stock is available. This agent is responsible for generating price quotes for customer requests. It looks up standard unit prices, searches historical quotes for similar requests, applies bulk discounts, and calculates a rounded final total, providing a clear explanation of the calculation. The quoting agent has access to two tools:

- search_quote_history_tool
    - Search historical quotes that match any of the search terms to see how similar jobs and quantities were quoted in the past.
- get_item_price_tool
    - Retrieve the standard unit price of a specific item from the inventory.

### Sales Closure Agent
The sales closure agent receives the finalized order details, including the quoted price, that was provided to the orchestrator before. This agent is responsible for final order processing and bookkeeping. It registers transactions in the database (sales to customers or stock orders to suppliers). It can check cash balances, generate financiel reports, and check delivery dates for supplier orders. The sales closure agent finalizes orders, recorsd transactions, runs financial audits and has access to four tools:

- create_transaction_tool
    - Record a new transaction (either sales or stock_orders) in the database.
- get_supplier_delivery_date_tool
    - Estimate the supplier delivery date for stock orders based on order quantity.
- get_cash_balance_tool
    - Retrieve the current cash balance as of a specified date.
- generate_financial_report_tool
    - Generate a complete financial report for the company as of a s.ecific date.

## Workflow Diagram
The workflow in the agentic system begins with a customer request and is shown in the second graphic (graphic_information_flowchart) that contains each step in the flow.

1) The customer makes a request -> The orchestrator receives the request and triggerst an Inventory check
2) The orchestrator passes Raw item names (and possibly provided requested dates) to the inventory agent
3) The inventory agent accesses the database and
4) obtains the catalog items by using the tool "get_catalog_items".
5) The inventory agent uses the "get_stock_level" tool and
6) obtains the current stock of the reqested items from the database.
7) These information are passed back as input to the orchestrator. => Here either a positive feedback is given, which means the order is possible due to sufficient stock or => a negative feedback is given that the order cannot be processed. In that case the alternative rout 18 is processed further.

8) The orchestrator initiates the price generation flow and passes the obtained information from the inventory agent to the quoting agent.
9) The quoting agent uses the "get_item_price" tool and
10) obtains the base unti prices of the requested items from the database.
11) The quoting agent uses the "search_quote_history" tool and
12) retrieves the historical bulk duscounts from the databse.
13) The final quopted amounts and the accompanying explanation is passed ans input to the orchestrator.

14) The orchestrator passes the catalog names, quantities, quoted price and data to the sales closure agent .
15) The sales closure agent updates the database by modifying the database. It updates the cash and inventory and
16) creates a transaction id.
17) The sales closure agent passes the information about the sale and created database entry as input to the orchestrator.
18) The orchestrator provides the final quote and delivery information to the client.
18) Alternative: when the feedback from step 7 is negative and the order cannot be processed due to insufficience stock the order is declined and the customer receives the informarmation on the reason - insufficiet stock, therefore the order is not possible.

## Run results from test.csv file
Discussion of the run results of test_result.csv file:

Running the main.py file triggers the processing of 20 requests. In that case the agentic system has processed three requests successfully and 17 have been declined by the system with the positive resonse "Dear customer, your order is confirmed and will be delivered on time. thank you!"

From the file one can see the request_id for each request as well as the change of cash_balance as well as inventory_value over time from order to order. The first requests was made 2025-04-01 and shows the cash balance of 46059.7 with an inventory_value of 4935.3 and the positive resonse.

The second request is from 2025-04-03, showing a cash balance of 47059.7, an inventory_value of 4930.3 and the positive response provided to the client.

The third request is from 2025-04-04, showing a cash balance of 48059.7 and an inventory value of 4925.3 with a positive response. One can see that the cash balance is increasing from request 1 to 2 to 3 and the inventory value is declining at the same time by 5 from request 1 to 2 to 3.

Due to insufficient stock all orders from number four on have been declined and a negative response has been give to the client "Dear customer, we are unable to fulfill this order due to insufficient stock."

## Proposed improvements for future interations
I propose the following three improvements for the agentic system based on the current state of the codebase:
  
  #### 1. Replace Mocked Logic with True Dynamic Orchestration
  
  Currently, in  src/agents/orchestrator.py , the  call_multi_agent_system  function uses a hardcoded counter ( req_idx <= 3 ) to simulate transaction 
  creations and returns static text responses.
  Improvement: You should replace this mocked logic by actively invoking your  orchestrator_agent.run(request_with_date) . This will empower the            
  orchestrator to genuinely evaluate the prompt, plan the steps, and dynamically delegate tasks to the  inventory_agent ,  quoting_agent , and
  sales_closure_agent  to solve the user's request autonomously.
  
  #### 2. Implement an Automated Restocking Feedback Loop
  
  Currently, the system is designed to either fulfill an order or fail if stock is insufficient.
  Improvement: You can enhance the agent's workflow by introducing an automated backorder process. If the  inventory_agent  determines that stock is too low
  to fulfill a quote, the orchestrator should be programmed to dynamically instruct the  sales_closure_agent  to create a  stock_orders  transaction with   
  the supplier. It can then use the  get_supplier_delivery_date_tool  to quote the customer a future delivery date rather than simply rejecting the order. 

  #### 3. Enhanced Data Validation and Fuzzy Matching
  
  Currently, the agents assume inputs are correctly formatted and item names strictly match the catalog. 
  Improvement: Add input validation using schemas for tool arguments, or implement fuzzy matching for item names before querying the database, making the system much more resilient to unstructured customer inputs and typos.