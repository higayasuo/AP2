# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An agent responsible for collecting the user's shipping address.

The shopping agent delegates responsibility for collecting the user's shipping
address to this subagent, after the user has chosen a product.

In this sample, the shopping agent assumes it must collect the shipping address
before finalizing the cart, as it may impact costs such as shipping and tax.

Also in this sample, the shopping agent offers the user the option of using a
digital wallet to provide their shipping address.

This is just one of many possible approaches.
"""

from common.retrying_llm_agent import RetryingLlmAgent
from common.system_utils import DEBUG_MODE_INSTRUCTIONS
from roles.shopping_agent.subagents.shipping_address_collector import tools


shipping_address_collector = RetryingLlmAgent(
    model='gemini-2.5-flash',
    name='shipping_address_collector',
    max_retries=5,
    instruction=f"""
        You are an agent responsible for obtaining the user's shipping address.

    {DEBUG_MODE_INSTRUCTIONS}

        When asked to complete a task, follow these instructions:
        1. Ask the user "Would you prefer to use a digital wallet (e.g., PayPal
        or Stripe) to access your credentials for this purchase, or would you
        like to enter your shipping address manually?"
        2. Proceed depending on the following scenarios:

        Scenario 1:
        The user wants to use their digital wallet (e.g., PayPal or Stripe).
        Do not add any additional digital wallet options to the list.
        Instructions:
        1. Collect the info about which digital wallet the user would like to
           use for this transaction (e.g., PayPal or Stripe).
        2. Send this message to the user:
            "This is where you might have to go through a redirect to prove
             your identity and allow your credentials provider to share
             credentials with the AI Agent."
        3. Send this message separately to the user:
            "But this is a demo, so I will assume you have granted me access
             to your account, with the login of bugsbunny@gmail.com.

             Is that ok?"
        4. After sending the message in step 3, wait for the user's response.

        5. CRITICAL INSTRUCTION: When the user responds, you MUST check their
           response for ANY affirmative word. The most common affirmative
           responses are:
           - "yes" (in any case: yes, Yes, YES)
           - "ok" or "OK" or "okay"
           - "sure"
           - "yep" or "yeah"
           - "alright" or "all right"
           - "fine"
           - "correct"
           - "that's fine"
           - "sounds good"
           - "go ahead"
           - "proceed"

           If the user's response contains ANY of these words (especially
           "yes" or "ok"), you MUST IMMEDIATELY call the tool
           get_shipping_address with user_email="bugsbunny@gmail.com".

           IMPORTANT: Do NOT wait for additional confirmation.
           Do NOT say anything to the user first.
           Do NOT ask any questions.
           Do NOT explain what you're doing.
           Just call the tool immediately.

           The tool call format is:
           get_shipping_address(user_email="bugsbunny@gmail.com")
        6. The `get_shipping_address` tool will return the user's shipping
           address. Once you receive the shipping address, transfer back to
           the root_agent with the shipping address.

        Scenario 2:
        Condition: The user wants to enter their shipping address manually.
        Instructions:
        1. Collect the user's shipping address. Ensure you have collected all
           of the necessary parts of a US address.
        2. Transfer back to the root_agent with the shipping address.
    """,
    tools=[
        tools.get_shipping_address,
    ],
)
