# Agent Payments Protocol (AP2)

[![Apache License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/google-agentic-commerce/AP2)

<!-- markdownlint-disable MD041 -->
<p align="center">
  <img src="docs/assets/ap2_graphic.png" alt="Agent Payments Protocol Graphic">
</p>

This repository contains code samples and demos of the Agent Payments Protocol.

## Intro to AP2 Video

[![A2A Intro Video](https://img.youtube.com/vi/yLTp3ic2j5c/hqdefault.jpg)](https://goo.gle/ap2-video)

### AP2 on The Agent Factory

[![The Agent Factory - Episode 8: Agent payments, can you do my shopping?](https://img.youtube.com/vi/T1MtWnEYXM0/hqdefault.jpg)](https://youtu.be/T1MtWnEYXM0?si=QkJWnAiav0JAP9F6)

## About the Samples

These samples use
[Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and Gemini 2.5
Flash.

The Agent Payments Protocol doesn't require the use of either. While these were
used in the samples, you're free to use any tools you prefer to build your
agents.

## Navigating the Repository

The **`samples`** directory contains a collection of curated scenarios meant to
demonstrate the key components of the Agent Payments Protocol.

The scenarios can be found in the
[**`samples/android/scenarios`**](samples/android/scenarios) and
[**`samples/python/scenarios`**](samples/python/scenarios) directories.

Each scenario contains:

-   a `README.md` file describing the scenario and instructions for running it.
-   a `run.sh` script to simplify the process of running the scenario locally.

This demonstration features various agents and servers, with most source code
located in [**`samples/python/src`**](samples/python/src/). Scenarios that use
an Android app as the shopping assistant have their source code in
[**`samples/android`**](samples/android/).

## Quickstart

### Prerequisites

-   Python 3.10 or higher
-   [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package
    manager

### Setup

You can authenticate using either a Google API Key or Vertex AI.

For either method, you can set the required credentials as environment variables
in your shell or place them in a `.env` file at the root of your project.

#### Option 1: Google API Key (Recommended for development)

1. Obtain a Google API key from
   [Google AI Studio](http://aistudio.google.com/apikey).
2. Set the `GOOGLE_API_KEY` environment variable.

    - **As an environment variable:**

        ```sh
        export GOOGLE_API_KEY='your_key'
        ```

    - **In a `.env` file:**

        ```sh
        GOOGLE_API_KEY='your_key'
        ```

#### Option 2: [Vertex AI](https://cloud.google.com/vertex-ai) (Recommended for production)

1. **Configure your environment to use Vertex AI.**

    - **As environment variables:**

        ```sh
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT='your-project-id'
        export GOOGLE_CLOUD_LOCATION='global' # or your preferred region
        ```

    - **In a `.env` file:**

        ```sh
        GOOGLE_GENAI_USE_VERTEXAI=true
        GOOGLE_CLOUD_PROJECT='your-project-id'
        GOOGLE_CLOUD_LOCATION='global'
        ```

2. **Authenticate your application.**

    - **Using the [`gcloud` CLI](https://cloud.google.com/sdk/docs/install):**

        ```sh
        gcloud auth login
        gcloud auth application-default login
        ```

    - **Using a Service Account:**

        ```sh
        export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your/service-account-key.json'
        ```

### How to Run a Scenario

To run a specific scenario, follow the instructions in its `README.md`. It will
generally follow this pattern:

1. Navigate to the root of the repository.

    ```sh
    cd AP2
    ```

1. Run the run script to install dependencies & start the agents.

    ```sh
    bash samples/python/scenarios/your-scenario-name/run.sh
    ```

1. Navigate to the Shopping Agent URL and begin engaging.

### Installing the AP2 Types Package

The protocol's core objects are defined in the [`src/ap2/types`](src/ap2/types)
directory. A PyPI package will be published at a later time. Until then, you can
install the types package directly using this command:

```sh
uv pip install git+https://github.com/google-agentic-commerce/AP2.git@main
```

## How to Understand This Repository

This guide will help you understand the codebase step by step. **We recommend
running a sample first to get a feel for how the system works, then diving into
the code.** Follow this order to build a comprehensive understanding of the
Agent Payments Protocol implementation.

### Step 0: Run the Sample First

Before diving into the code, run a sample scenario to see the system in action:

1. **Follow the Quickstart section above** to set up your environment and run a
   scenario.

2. **Try a complete purchase flow:**

    - Start a conversation with the Shopping Agent
    - Search for a product
    - Select a cart
    - Provide shipping address
    - Choose a payment method
    - Complete the payment

3. **Observe the behavior:**
    - Notice how the agent asks clarifying questions
    - See how different agents communicate
    - Watch the transaction flow from intent to receipt

This hands-on experience will make the code much easier to understand when you
read it.

### Step 1: Understand the Overall Architecture

Start by reading the scenario documentation to understand what the system does:

1. **Read the scenario README:**

    - [`samples/python/scenarios/a2a/human-present/cards/README.md`](samples/python/scenarios/a2a/human-present/cards/README.md)
        - Explains the "Human Present" purchase flow
        - Describes the key actors (Shopping Agent, Merchant Agent, etc.)
        - Shows the complete transaction flow

2. **Review the main Python README:**
    - [`samples/python/README.md`](samples/python/README.md)
        - Overview of Python samples structure

### Step 2: Learn the AP2 Core Data Types

The protocol's core objects are defined in the AP2 types package:

1. **Start with the type definitions:**

    - [`src/ap2/types/mandate.py`](src/ap2/types/mandate.py)
        - `IntentMandate`: User's shopping intent
        - `CartMandate`: Shopping cart with products
        - `PaymentMandate`: Payment authorization
    - [`src/ap2/types/payment_request.py`](src/ap2/types/payment_request.py)
        - `PaymentRequest`: Payment processing request
    - [`src/ap2/types/payment_receipt.py`](src/ap2/types/payment_receipt.py)
        - `PaymentReceipt`: Transaction receipt
    - [`src/ap2/types/contact_picker.py`](src/ap2/types/contact_picker.py)
        - `ContactAddress`: Shipping/billing address

    These types define the data structures that flow between agents.

### Step 3: Understand the Common Infrastructure

The `common` module provides shared functionality used by all agents:

1. **Core server infrastructure:**

    - [`samples/python/src/common/server.py`](samples/python/src/common/server.py)
        - Starlette/Uvicorn server setup
        - Request/response logging middleware
    - [`samples/python/src/common/base_server_executor.py`](samples/python/src/common/base_server_executor.py)
        - Base executor class for all agents
        - Handles A2A extensions and tool resolution

2. **Message handling:**

    - [`samples/python/src/common/message_utils.py`](samples/python/src/common/message_utils.py)
        - Utilities for parsing A2A message parts
        - Extracts canonical objects from messages
    - [`samples/python/src/common/a2a_message_builder.py`](samples/python/src/common/a2a_message_builder.py)
        - Helper for building A2A messages

3. **A2A extension utilities:**

    - [`samples/python/src/common/a2a_extension_utils.py`](samples/python/src/common/a2a_extension_utils.py)
        - AP2 extension URI and constants
    - [`samples/python/src/common/artifact_utils.py`](samples/python/src/common/artifact_utils.py)
        - Utilities for working with A2A artifacts

4. **Other utilities:**
    - [`samples/python/src/common/function_call_resolver.py`](samples/python/src/common/function_call_resolver.py)
        - Resolves function calls to appropriate tools
    - [`samples/python/src/common/validation.py`](samples/python/src/common/validation.py)
        - Validates payment mandate signatures
    - [`samples/python/src/common/watch_log.py`](samples/python/src/common/watch_log.py)
        - Logging utilities for debugging

### Step 4: Explore Individual Agents

Each agent is a self-contained module in `samples/python/src/roles/`. Start with
the simplest and work your way up:

1. **Merchant Payment Processor Agent** (simplest):

    - [`samples/python/src/roles/merchant_payment_processor_agent/`](samples/python/src/roles/merchant_payment_processor_agent/)
        - Processes payment requests
        - Handles OTP challenges
        - Returns payment receipts

    **Reading order for this agent:**

    1. [`agent.json`](samples/python/src/roles/merchant_payment_processor_agent/agent.json)
        - Understand the agent's capabilities and supported extensions
    2. [`agent_executor.py`](samples/python/src/roles/merchant_payment_processor_agent/agent_executor.py)
        - See how the agent is structured and which tools it uses
    3. [`tools.py`](samples/python/src/roles/merchant_payment_processor_agent/tools.py)
        - Learn the core payment processing logic (`initiate_payment` function)
    4. [`__main__.py`](samples/python/src/roles/merchant_payment_processor_agent/__main__.py)
        - Understand how the agent server is started

2. **Merchant Agent:**

    - [`samples/python/src/roles/merchant_agent/`](samples/python/src/roles/merchant_agent/)
        - Handles product queries
        - Manages shopping carts
        - Uses a sub-agent for catalog queries

    **Reading order for this agent:**

    1. [`agent.json`](samples/python/src/roles/merchant_agent/agent.json)
        - Understand the agent's capabilities and supported extensions
    2. [`agent_executor.py`](samples/python/src/roles/merchant_agent/agent_executor.py)
        - See how the agent handles `PaymentMandate` and `IntentMandate`
    3. [`tools.py`](samples/python/src/roles/merchant_agent/tools.py)
        - Learn the core merchant logic (`initiate_payment`, `update_cart`)
    4. [`sub_agents/catalog_agent.py`](samples/python/src/roles/merchant_agent/sub_agents/catalog_agent.py)
        - Understand how product search works
    5. [`storage.py`](samples/python/src/roles/merchant_agent/storage.py)
        - See how cart data is stored
    6. [`__main__.py`](samples/python/src/roles/merchant_agent/__main__.py)
        - Understand how the agent server is started

3. **Credentials Provider Agent:**

    - [`samples/python/src/roles/credentials_provider_agent/`](samples/python/src/roles/credentials_provider_agent/)
        - Manages user payment methods
        - Provides payment credentials
        - Handles payment authorization

    **Reading order for this agent:**

    1. [`agent.json`](samples/python/src/roles/credentials_provider_agent/agent.json)
        - Understand the agent's capabilities and supported extensions
    2. [`agent_executor.py`](samples/python/src/roles/credentials_provider_agent/agent_executor.py)
        - See how the agent is structured and which tools it uses
    3. [`account_manager.py`](samples/python/src/roles/credentials_provider_agent/account_manager.py)
        - Learn how user accounts and payment methods are managed
    4. [`tools.py`](samples/python/src/roles/credentials_provider_agent/tools.py)
        - Learn the core credential provision logic
    5. [`__main__.py`](samples/python/src/roles/credentials_provider_agent/__main__.py)
        - Understand how the agent server is started

4. **Shopping Agent** (most complex):

    - [`samples/python/src/roles/shopping_agent/`](samples/python/src/roles/shopping_agent/)
        - Main orchestrator for shopping flows
        - Uses ADK (Agent Development Kit) instead of base executor
        - Delegates to sub-agents:
            - `shopper/`: Product search and cart creation
            - `shipping_address_collector/`: Collects shipping addresses
            - `payment_method_collector/`: Collects payment method selection

    **Reading order for this agent:**

    1. [`agent.py`](samples/python/src/roles/shopping_agent/agent.py)
        - Understand the main agent's instructions and orchestration logic
    2. [`tools.py`](samples/python/src/roles/shopping_agent/tools.py)
        - Learn the main shopping agent tools (`update_cart`,
          `create_payment_mandate`, etc.)
    3. [`remote_agents.py`](samples/python/src/roles/shopping_agent/remote_agents.py)
        - See how the agent communicates with other agents
    4. **Sub-agents** (read in this order):
        - [`subagents/shopper/agent.py`](samples/python/src/roles/shopping_agent/subagents/shopper/agent.py)
          and
          [`tools.py`](samples/python/src/roles/shopping_agent/subagents/shopper/tools.py)
            - Product search and cart creation
        - [`subagents/shipping_address_collector/agent.py`](samples/python/src/roles/shopping_agent/subagents/shipping_address_collector/agent.py)
          and
          [`tools.py`](samples/python/src/roles/shopping_agent/subagents/shipping_address_collector/tools.py)
            - Shipping address collection
        - [`subagents/payment_method_collector/agent.py`](samples/python/src/roles/shopping_agent/subagents/payment_method_collector/agent.py)
          and
          [`tools.py`](samples/python/src/roles/shopping_agent/subagents/payment_method_collector/tools.py)
            - Payment method selection

### Step 5: Understand the Execution Flow

1. **Review the run script:**

    - [`samples/python/scenarios/a2a/human-present/cards/run.sh`](samples/python/scenarios/a2a/human-present/cards/run.sh)
        - Sets up the environment
        - Starts all agents in parallel
        - Shows how agents communicate

2. **Trace a complete transaction:**
    - Start with user intent → `IntentMandate`
    - Product search → `CartMandate`
    - Address collection → `ContactAddress`
    - Payment method selection → `PaymentMandate`
    - Payment processing → `PaymentRequest` → `PaymentReceipt`

### Step 6: Deep Dive into Specific Features

Once you understand the basics, explore specific features:

-   **A2A Extension Protocol:** How agents declare and use extensions
-   **Sub-agents:** How the Shopping Agent delegates to specialized sub-agents
-   **Remote Agent Communication:** How agents communicate via A2A protocol
-   **State Management:** How agents maintain session state
-   **Error Handling:** How failures are handled and retried

### Tips for Reading the Code

-   **Start with `agent.json` files:** Each agent has an `agent.json` that
    describes its capabilities and tools
-   **Follow the tool functions:** Tools are the entry points for agent actions
-   **Read the logs:** The `watch.log` file shows all A2A messages between
    agents
-   **Use the debugger:** Set breakpoints in tool functions to trace execution
