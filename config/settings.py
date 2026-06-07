import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Define project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Load environment variables explicitly from the root .env file
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Create an SQLite database engine (pointing to the data folder)
db_engine = create_engine(f"sqlite:///{os.path.join(DATA_DIR, 'munder_difflin.db')}")

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
