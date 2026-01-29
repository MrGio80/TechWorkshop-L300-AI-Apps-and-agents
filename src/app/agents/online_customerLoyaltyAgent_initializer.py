# Workflow: run customer loyalty agent when relevant files change
# Triggers on push and pull_request when any of the tracked files change; also supports manual run.
name: Run Customer Loyalty Agent

on:
  push:
    paths:
      - 'src/app/agents/customerLoyaltyAgent_initializer.py'
      - 'src/prompts/CustomerLoyaltyAgentPrompt.txt'
      - 'src/app/tools/discountLogic.py'
  pull_request:
    paths:
      - 'src/app/agents/customerLoyaltyAgent_initializer.py'
      - 'src/prompts/CustomerLoyaltyAgentPrompt.txt'
      - 'src/app/tools/discountLogic.py'
  workflow_dispatch:

jobs:
  run-agent:
    name: Install deps and run initializer
    runs-on: ubuntu-latest
    env:
      # Provide Azure credentials and any endpoint your code uses via repository secrets
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      # If your azure.ai.projects usage requires a specific endpoint, set it as a secret (optional)
      AZURE_PROJECTS_ENDPOINT: ${{ secrets.AZURE_PROJECTS_ENDPOINT }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        # If you maintain requirements.txt it will be used; otherwise we install the Azure packages needed.
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          else
            # Install the SDK used to connect to Azure and credential helpers.
            # If your project uses a different package name (e.g. azure-ai-ml), adjust here.
            pip install azure-ai-projects azure-identity
          fi

      - name: Run customer loyalty agent initializer
        run: |
          python src/app/agents/customerLoyaltyAgent_initializer.py
        # Re-export secrets here to ensure subprocess visibility
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          AZURE_PROJECTS_ENDPOINT: ${{ secrets.AZURE_PROJECTS_ENDPOINT }}
