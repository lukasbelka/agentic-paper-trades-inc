from smolagents import LiteLLMModel
from config.settings import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

# Instantiate the Google Flash model using smolagents' LiteLLMModel wrapper
model = LiteLLMModel(
    model_id="gemini/gemini-2.5-flash",
    api_key=GEMINI_API_KEY
)

model_orchestrator = LiteLLMModel(
    model_id="gemini/gemini-2.5-pro",
    api_key=GEMINI_API_KEY
)

print("Models instantiated successfully via smolagents")
