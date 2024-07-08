## Prerequisites

Python poackages:

- langchain
- operator

## Setup

Ollama service must be running with `mistral:instruct` installed

More info on installation here: https://dev.to/avatsaev/local-intelligence-how-to-set-up-a-local-gpt-chat-for-secure-private-document-analysis-workflow-1lnm

### Run mock API

`uvicorn mock_api:app --reload`

### Run the chatbot app

`streamlit run ./chatbot.py`
