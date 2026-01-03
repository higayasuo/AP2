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

"""An agent responsible for collecting the user's choice of payment method.

The shopping agent delegates responsibility for collecting the user's choice of
payment method to this subagent, after the user has finalized their cart.

Through the get_payment_methods tool, the agent retrieves a list of eligible
payment methods from the credentials provider agent. The agent then presents the
list to the user, allowing them to select their preferred payment method.

After selection, the agent gets a purchase token from the credentials
provider, which is then sent to the merchant agent for payment.
"""

from common.retrying_llm_agent import RetryingLlmAgent
from common.system_utils import DEBUG_MODE_INSTRUCTIONS
from roles.shopping_agent.subagents.payment_method_collector import tools


payment_method_collector = RetryingLlmAgent(
    model='gemini-2.5-flash',
    name='payment_method_collector',
    max_retries=5,
    instruction=f"""
    You are an agent responsible for obtaining the user's payment method for a
    purchase.

    {DEBUG_MODE_INSTRUCTIONS}

    When asked to complete a task, follow these instructions:
    1. Ensure a CartMandate object was provided to you.
    2. Present a clear and organized summary of the cart to the user. The
       summary should be divided into two main sections:
       a. Order Summary: Format EXACTLY as shown below, with each element on
          its own line (you MUST add a line break after each element):

          Merchant: [merchant name]

          Item: [item_name]

          Price Breakdown:
          Shipping: [shipping cost]
          Tax: [tax amount]
          Total: [total price]

          Format all amounts with commas and the currency symbol.

          Expires: [cart_expiry in human-readable format]

          Refund Period: [refund_period in human-readable format]

          CRITICAL: You MUST add a line break (newline) after EACH element in
          the Order Summary. Never put multiple elements on the same line.
       b. Show the full shipping address collected earlier in a well-formatted
          manner. Format it EXACTLY as shown below, with each element on its
          own line (you MUST add a line break after each element):

          Recipient: [recipient name]

          Organization: [organization] (only if present, on its own line)

          Address: [address_line[0]]

          [address_line[1]] (if present, on its own line)

          City: [city]

          State: [region]

          Postal Code: [postal_code]

          Country: [country]

          Phone: [phone_number] (only if present, on its own line)

          CRITICAL: You MUST add a line break (newline) after EACH element.
          Never put multiple elements on the same line. Never display raw JSON.
          Each element must be separated by a blank line or at least be on
          separate lines.
       Ensure the entire presentation is well-formatted and easy to read.
    3. Call the `get_payment_methods` tool to get eligible
       payment_method_aliases with the method_data from the CartMandate's
       payment_request. Present the payment_method_aliases to the user in
       a numbered list (e.g., "1. American Express ending in 4444",
       "2. American Express ending in 8888").
    4. Ask the user to choose which payment method they would like to use
       by responding with the number (e.g., "1" or "2"). Do not ask for
       the full alias. When the user responds with a number, map it to the
       corresponding payment_method_alias from the list and remember that
       payment_method_alias.
    5. Call the `get_payment_credential_token` tool to get the payment
       credential token with the user_email and payment_method_alias.
    6. Transfer back to the root_agent with the payment_method_alias.
    """,
    tools=[
        tools.get_payment_methods,
        tools.get_payment_credential_token,
    ],
)
