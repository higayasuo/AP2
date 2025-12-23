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

"""Tools used by the shopper subagent.

Each agent uses individual tools to handle distinct tasks throughout the
shopping and purchasing process.
"""

import logging

from datetime import UTC, datetime, timedelta

from a2a.types import Artifact
from common.a2a_message_builder import A2aMessageBuilder
from common.artifact_utils import find_canonical_objects
from google.adk.tools.tool_context import ToolContext
from roles.shopping_agent.remote_agents import merchant_agent_client


_logger = logging.getLogger(__name__)

from ap2.types.mandate import (
    CART_MANDATE_DATA_KEY,
    INTENT_MANDATE_DATA_KEY,
    CartMandate,
    IntentMandate,
)


def create_intent_mandate(
    natural_language_description: str,
    user_cart_confirmation_required: bool,
    merchants: list[str],
    skus: list[str],
    requires_refundability: bool,
    tool_context: ToolContext,
) -> IntentMandate:
    """Creates an IntentMandate object.

    Args:
      natural_language_description: The description of the user's intent.
      user_cart_confirmation_required: If the user must confirm the cart.
      merchants: A list of allowed merchants.
      skus: A list of allowed SKUs.
      requires_refundability: If the items must be refundable.
      tool_context: The ADK supplied tool context.

    Returns:
      An IntentMandate object valid for 1 day.
    """
    intent_mandate = IntentMandate(
        natural_language_description=natural_language_description,
        user_cart_confirmation_required=user_cart_confirmation_required,
        merchants=merchants,
        skus=skus,
        requires_refundability=requires_refundability,
        intent_expiry=(datetime.now(UTC) + timedelta(days=1)).isoformat(),
    )
    # Store as dict for JSON serialization in ADK session state
    tool_context.state['intent_mandate'] = intent_mandate.model_dump()
    _logger.info(
        'create_intent_mandate: Stored intent_mandate in state. State keys: %s',
        list(tool_context.state.keys())
        if hasattr(tool_context.state, 'keys')
        else 'N/A',
    )
    return intent_mandate


async def find_products(
    tool_context: ToolContext, debug_mode: bool = False
) -> list[CartMandate]:
    """Calls the merchant agent to find products matching the user's intent.

    Args:
      tool_context: The ADK supplied tool context.
      debug_mode: Whether the agent is in debug mode.

    Returns:
      A list of CartMandate objects.

    Raises:
      RuntimeError: If the merchant agent fails to provide products.
    """
    _logger.info(
        'find_products: Checking for intent_mandate in state. State keys: %s',
        list(tool_context.state.keys())
        if hasattr(tool_context.state, 'keys')
        else 'N/A',
    )
    intent_mandate_dict = tool_context.state.get('intent_mandate')
    if not intent_mandate_dict:
        available_keys = (
            list(tool_context.state.keys())
            if hasattr(tool_context.state, 'keys')
            else []
        )
        _logger.error(
            'find_products: No IntentMandate found. Available keys: %s',
            available_keys,
        )
        raise RuntimeError(
            f'No IntentMandate found in tool context state. '
            f'Available keys: {available_keys}. '
            f'Please call create_intent_mandate first.'
        )
    # Convert dict back to IntentMandate object
    intent_mandate = (
        IntentMandate(**intent_mandate_dict)
        if isinstance(intent_mandate_dict, dict)
        else intent_mandate_dict
    )
    risk_data = _collect_risk_data(tool_context)
    if not risk_data:
        raise RuntimeError('No risk data found in tool context state.')
    message = (
        A2aMessageBuilder()
        .add_text("Find products that match the user's IntentMandate.")
        .add_data(INTENT_MANDATE_DATA_KEY, intent_mandate.model_dump())
        .add_data('risk_data', risk_data)
        .add_data('debug_mode', debug_mode)
        .add_data('shopping_agent_id', 'trusted_shopping_agent')
        .build()
    )
    task = await merchant_agent_client.send_a2a_message(message)

    if task.status.state != 'completed':
        raise RuntimeError(f'Failed to find products: {task.status}')

    tool_context.state['shopping_context_id'] = task.context_id
    cart_mandates = _parse_cart_mandates(task.artifacts)
    # Store as list of dicts for JSON serialization in ADK session state
    tool_context.state['cart_mandates'] = [
        cart.model_dump() for cart in cart_mandates
    ]
    return cart_mandates


def update_chosen_cart_mandate(cart_id: str, tool_context: ToolContext) -> str:
    """Updates the chosen CartMandate in the tool context state.

    Args:
      cart_id: The ID of the chosen cart.
      tool_context: The ADK supplied tool context.
    """
    cart_mandates_data = tool_context.state.get('cart_mandates', [])
    if not cart_mandates_data:
        available_keys = list(tool_context.state.keys())
        return (
            f'No cart mandates found in state. Available keys: {available_keys}'
        )

    # Convert list of dicts back to list of CartMandate objects
    cart_mandates = []
    for cart_dict in cart_mandates_data:
        if isinstance(cart_dict, dict):
            try:
                cart_mandates.append(CartMandate(**cart_dict))
            except Exception as e:
                print(f'Error converting cart dict to CartMandate: {e}')
                print(f'Cart dict: {cart_dict}')
        else:
            cart_mandates.append(cart_dict)

    print(
        f'Found {len(cart_mandates)} cart mandates. '
        f'Looking for cart_id: {cart_id}'
    )
    for cart in cart_mandates:
        print(
            f'Checking cart with ID: {cart.contents.id} '
            f'with chosen ID: {cart_id}'
        )
        if cart.contents.id == cart_id:
            tool_context.state['chosen_cart_id'] = cart_id
            return f'CartMandate with ID {cart_id} selected.'

    available_ids = [cart.contents.id for cart in cart_mandates]
    return (
        f'CartMandate with ID {cart_id} not found. '
        f'Available cart IDs: {available_ids}'
    )


def _parse_cart_mandates(artifacts: list[Artifact]) -> list[CartMandate]:
    """Parses a list of artifacts into a list of CartMandate objects."""
    return find_canonical_objects(artifacts, CART_MANDATE_DATA_KEY, CartMandate)


def _collect_risk_data(tool_context: ToolContext) -> dict:
    """Creates a risk_data in the tool_context."""
    # This is a fake risk data for demonstration purposes.
    risk_data = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fake_risk_data'
    tool_context.state['risk_data'] = risk_data
    return risk_data
