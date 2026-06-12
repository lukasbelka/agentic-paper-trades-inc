from smolagents import tool, CodeAgent
from src.agents.core import model
from src.tools.inventory_tools import get_all_inventory, get_stock_level, get_supplier_delivery_date, create_transaction
from src.tools.finance_tools import search_quote_history, get_cash_balance, generate_financial_report

@tool
def get_all_inventory_tool(as_of_date: str) -> dict:
    """
    Retrieve a snapshot of available inventory as of a specific date.
    Only items with positive stock are included.

    Args:
        as_of_date: ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff date.

    Returns:
        A dictionary mapping item names to their current stock levels.
    """
    return get_all_inventory(as_of_date)

@tool
def get_stock_level_tool(item_name: str, as_of_date: str) -> int:
    """
    Retrieve the current stock level of a specific item as of a given date.

    Args:
        item_name: The exact name of the item to look up.
        as_of_date: The cutoff date (inclusive) for calculating stock, formatted as YYYY-MM-DD.

    Returns:
        The number of units in stock as an integer. Returns 0 if the item is not found or has no stock.
    """
    df = get_stock_level(item_name, as_of_date)
    if df.empty:
        return 0
    return int(df.iloc[0]["current_stock"])

@tool
def get_catalog_items_tool() -> list:
    """
    Retrieve the names of all paper products and items carried in Munder Difflin's catalog.
    Retrieves a list of items sold in the catalog, regardless of current stock levels.

    Returns:
        A list of catalog item names.
    """
    import pandas as pd
    from config.settings import db_engine
    df = pd.read_sql("SELECT item_name FROM inventory", db_engine)
    return df["item_name"].tolist()

@tool
def get_inventory_details_tool(item_name: str, as_of_date: str) -> dict:
    """
    Retrieve details for a specific catalog item, including its category, unit price, 
    minimum stock level, and current stock level as of a given date.

    Args:
        item_name: The exact catalog name of the item.
        as_of_date: The date to check stock as of, formatted as YYYY-MM-DD.

    Returns:
        A dictionary with 'item_name', 'category', 'unit_price', 'min_stock_level', and 'current_stock'.
        Returns an empty dictionary if the item is not in our catalog.
    """
    import pandas as pd
    from config.settings import db_engine
    from src.tools.inventory_tools import get_stock_level
    
    # Query catalog details
    df_cat = pd.read_sql("SELECT * FROM inventory WHERE item_name = :item_name", db_engine, params={"item_name": item_name})
    if df_cat.empty:
        return {}
        
    # Query stock level
    df_stock = get_stock_level(item_name, as_of_date)
    current_stock = int(df_stock.iloc[0]["current_stock"]) if not df_stock.empty else 0
    
    row = df_cat.iloc[0]
    return {
        "item_name": str(row["item_name"]),
        "category": str(row["category"]),
        "unit_price": float(row["unit_price"]),
        "min_stock_level": int(row["min_stock_level"]),
        "current_stock": current_stock
    }

# Create the Inventory Agent
inventory_agent = CodeAgent(
    tools=[get_all_inventory_tool, get_stock_level_tool, get_catalog_items_tool, get_inventory_details_tool],
    model=model,
    name="inventory_agent",
    description=(
        "Manages and checks the inventory of paper products. "
        "Capable of retrieving exact catalog item names and mapping inexact "
        "customer requests to the closest catalog match before checking stock "
        "levels and details."
    )
)

@tool
def search_quote_history_tool(search_terms: list, limit: int = 5) -> list:
    """
    Search historical quotes that match any of the search terms to see how similar jobs 
    and quantities were quoted in the past.

    Args:
        search_terms: A list of keyword search terms to search in quote requests and explanations.
        limit: The maximum number of historical quotes to return. Defaults to 5.

    Returns:
        A list of dictionaries containing matching historical quotes and their details.
    """
    return search_quote_history(search_terms, limit)

@tool
def get_item_price_tool(item_name: str) -> float:
    """
    Retrieve the standard unit price of a specific item from the inventory.

    Args:
        item_name: The exact name of the item.

    Returns:
        The standard unit price as a float. Returns 0.0 if the item is not found.
    """
    import pandas as pd
    from config.settings import db_engine
    df = pd.read_sql("SELECT unit_price FROM inventory WHERE item_name = :item_name", db_engine, params={"item_name": item_name})
    if df.empty:
        return 0.0
    return float(df.iloc[0]["unit_price"])

# Create the Quoting Agent
quoting_agent = CodeAgent(
    tools=[search_quote_history_tool, get_item_price_tool],
    model=model,
    name="quoting_agent",
    description=(
        "Responsible for generating price quotes for customer requests. "
        "It looks up standard unit prices, searches historical quotes for similar requests, "
        "applies bulk discounts, and calculates a rounded final total, "
        "providing a clear explanation of the calculation."
    )
)

@tool
def create_transaction_tool(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: str
) -> int:
    """
    Record a new transaction (either sales or stock_orders) in the database.

    Args:
        item_name: The exact name of the item. Pass "None" (as string) or empty if this is a general cash adjustment.
        transaction_type: Either 'sales' or 'stock_orders'.
        quantity: The number of units.
        price: The total price of the transaction (revenue for sales, cost for stock_orders).
        date: The transaction date formatted as YYYY-MM-DD.

    Returns:
        The transaction ID as an integer.
    """
    actual_item_name = None if item_name == "None" or not item_name else item_name
    actual_quantity = None if quantity == 0 else quantity
    return create_transaction(
        item_name=actual_item_name,
        transaction_type=transaction_type,
        quantity=actual_quantity,
        price=price,
        date=date
    )

@tool
def get_supplier_delivery_date_tool(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date for stock orders based on order quantity.

    Args:
        input_date_str: The starting/order date in YYYY-MM-DD format.
        quantity: The number of units being ordered.

    Returns:
        The estimated delivery date in YYYY-MM-DD format.
    """
    return get_supplier_delivery_date(input_date_str, quantity)

@tool
def get_cash_balance_tool(as_of_date: str) -> float:
    """
    Retrieve the current cash balance as of a specified date.

    Args:
        as_of_date: The date to calculate cash balance up to (inclusive), formatted as YYYY-MM-DD.

    Returns:
        The net cash balance as a float.
    """
    return get_cash_balance(as_of_date)

@tool
def generate_financial_report_tool(as_of_date: str) -> dict:
    """
    Generate a complete financial report for the company as of a specific date.

    Args:
        as_of_date: The date for the report, formatted as YYYY-MM-DD.

    Returns:
        A dictionary containing the financial report metrics.
    """
    return generate_financial_report(as_of_date)

# Create the Sales Closure Agent
sales_closure_agent = CodeAgent(
    tools=[
        create_transaction_tool,
        get_supplier_delivery_date_tool,
        get_cash_balance_tool,
        generate_financial_report_tool
    ],
    model=model,
    name="sales_closure_agent",
    description=(
        "Responsible for final order processing and bookkeeping. "
        "It registers transactions in the database (sales to customers or stock_orders to suppliers). "
        "It can check cash balances, generate financial reports, and check delivery dates for supplier orders. "
        "Used to finalize orders, record transactions, and run financial audits."
    )
)