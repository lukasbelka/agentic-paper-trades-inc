import pandas as pd
import ast
import os
from datetime import datetime, timedelta
from typing import Union
from sqlalchemy import Engine

from config.settings import db_engine, DATA_DIR
from src.database.seed_data import paper_supplies, generate_sample_inventory

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_path = os.path.join(DATA_DIR, "quote_requests.csv")
        if os.path.exists(quote_requests_path):
            quote_requests_df = pd.read_csv(quote_requests_path)
            quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
            quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)
        else:
            print(f"Warning: {quote_requests_path} not found.")

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_path = os.path.join(DATA_DIR, "quotes.csv")
        if os.path.exists(quotes_path):
            quotes_df = pd.read_csv(quotes_path)
            quotes_df["request_id"] = range(1, len(quotes_df) + 1)
            quotes_df["order_date"] = initial_date

            # Unpack metadata fields (job_type, order_size, event_type) if present
            if "request_metadata" in quotes_df.columns:
                quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                )
                quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
                quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
                quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

            # Retain only relevant columns
            quotes_df = quotes_df[[
                "request_id",
                "total_amount",
                "quote_explanation",
                "order_date",
                "job_type",
                "order_size",
                "event_type"
            ]]
            quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)
        else:
            print(f"Warning: {quotes_path} not found.")

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise