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
        1. Ask the user with the following message:
           "How would you like to provide your shipping address?

           1. Account address
           2. Manual entry"

           CRITICAL: After sending this message, you MUST stop and wait
           for the user's response. Do NOT proceed to step 2 until you
           have received a user response in the conversation. If you
           have not yet received a user response, you must wait. Do not
           make any tool calls or send any additional messages until the
           user responds.

        2. When the user responds, check their response:
           - If the response contains "1" or "Account address":
             IMMEDIATELY call get_shipping_address(
                 user_email="bugsbunny@gmail.com"
             )
             Do not say anything else. Do not ask for confirmation. Just call
             the tool right away. The `get_shipping_address` tool will return
             the user's shipping address. Once you receive the shipping
             address, immediately transfer back to the root_agent with the
             shipping address. Do not display the address yourself - the
             root_agent will display it to the user. Your task is then
             complete.
           - If the response contains "2" or "Manual entry":
             Collect the user's shipping address. Ensure you have collected all
             of the necessary parts of a US address (recipient name, street
             address, city, state/region, postal code, country). Once you have
             collected all the required address information, immediately
             transfer back to the root_agent with the shipping address. Do not
             display the address yourself - the root_agent will display it to
             the user. Your task is then complete.
           - If the response is unclear or you cannot determine the user's
             intent: Ask the user to clarify their response. You can say:
             "I didn't understand your response. Please choose 1 for Account
             address or 2 for Manual entry."
           - If you do not receive a response after waiting: Ask the user again
             to respond. You can say: "Please respond with 1 for Account
             address or 2 for Manual entry."
    """,
    tools=[
        tools.get_shipping_address,
    ],
)
