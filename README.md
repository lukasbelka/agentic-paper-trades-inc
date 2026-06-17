# Munder Difflin Multi-Agent System Project

Welcome to the repository for the **Munder Difflin Paper Company Multi-Agent System Project**! This repository contains the starter code and tools I used to design, build, and test a multi-agent system that supports core business operations at a fictional paper manufacturing company.

## Capstone Project of Udacity's "AGENTIC AI"-Nanogegree

The Munder Difflin Paper Company, a fictional enterprise is looking to modernize their workflows. They need a smart, modular **multi-agent system** to automate:

- **Inventory checks** and restocking decisions
- **Quote generation** for incoming sales inquiries
- **Order fulfillment** including supplier logistics and transactions

The solution uses **4 agents** and processes inputs and outputs entirely via **text-based communication**.

This project challenges the ability to orchestrate agents using modern Python frameworks like `smolagents` and `pydantic-ai`, and combines that with real data tools like `sqlite3`, `pandas`, and LLM prompt engineering.

---

## Local setup instructions

1. Install dependencies

Make sure you have Python 3.8+ installed.

You can install all required packages using the provided requirements.txt file:

`pip install -r requirements.txt`

If you're using smolagents, install it separately:

`pip install smolagents`


2. Create .env File

Add your Google API key.

This project uses Gemini's flash-2.5-model for the orchestrator and the three working agents.

---

The output includes:

- Agent responses
- Cash and inventory updates
- Final financial report
- A `test_results.csv` file with all interaction logs

---
