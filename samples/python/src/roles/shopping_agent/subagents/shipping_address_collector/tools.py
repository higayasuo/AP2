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

"""Tools used by the shipping address collector subagent.

Each agent uses individual tools to handle distinct tasks throughout the
shopping and purchasing process.
"""

import logging

from a2a.types import Artifact
from common import artifact_utils
from common.a2a_message_builder import A2aMessageBuilder
from common.watch_log import create_file_handler
from google.adk.tools.tool_context import ToolContext
from roles.shopping_agent.remote_agents import credentials_provider_client

from ap2.types.contact_picker import CONTACT_ADDRESS_DATA_KEY, ContactAddress


_logger = logging.getLogger(__name__)

# Ensure logger has a file handler for .logs/watch.log
if not _logger.handlers:
    _logger.addHandler(create_file_handler())
    _logger.setLevel(logging.INFO)


async def get_shipping_address(
    user_email: str,
    tool_context: ToolContext,
) -> ContactAddress:
    """Gets the user's shipping address from the credentials provider.

    Args:
      user_email: The ID of the user to get the shipping address for.
      tool_context: The ADK supplied tool context.

    Returns:
      The user's shipping address.

    Raises:
      RuntimeError: If shopping_context_id is not found in state.
    """
    _logger.info('get_shipping_address: Called with user_email=%s', user_email)
    try:
        state_keys = (
            list(tool_context.state.keys())
            if hasattr(tool_context.state, 'keys')
            else 'N/A'
        )
        _logger.info(
            'get_shipping_address: tool_context.state keys: %s', state_keys
        )
        _logger.info('get_shipping_address: Full state: %s', tool_context.state)
    except Exception as e:
        _logger.warning(
            'get_shipping_address: Could not log state details: %s', e
        )

    shopping_context_id = tool_context.state.get('shopping_context_id')
    if not shopping_context_id:
        try:
            available_keys = (
                list(tool_context.state.keys())
                if hasattr(tool_context.state, 'keys')
                else 'Cannot list keys'
            )
        except Exception as e:
            available_keys = f'Error listing keys: {e}'
        error_msg = (
            f'No shopping_context_id found in tool context state. '
            f'Available keys: {available_keys}. '
            f'State type: {type(tool_context.state)}. '
            f'State value: {tool_context.state}'
        )
        _logger.error('get_shipping_address: %s', error_msg)
        raise RuntimeError(error_msg)
    _logger.info(
        'get_shipping_address: Using shopping_context_id: %s',
        shopping_context_id,
    )

    try:
        message = (
            A2aMessageBuilder()
            .set_context_id(shopping_context_id)
            .add_text("Get the user's shipping address.")
            .add_data('user_email', user_email)
            .build()
        )
        _logger.info(
            'get_shipping_address: Sending message to credentials provider...'
        )
        task = await credentials_provider_client.send_a2a_message(message)
        _logger.info('get_shipping_address: Task status: %s', task.status.state)
        _logger.info(
            'get_shipping_address: Task artifacts count: %d',
            len(task.artifacts),
        )

        shipping_address = artifact_utils.only(_parse_addresses(task.artifacts))
        _logger.info(
            'get_shipping_address: Successfully retrieved shipping address: %s',
            shipping_address,
        )
        return shipping_address
    except Exception as e:
        _logger.error(
            'get_shipping_address: Exception occurred: %s: %s',
            type(e).__name__,
            e,
        )
        import traceback

        _logger.error(
            'get_shipping_address: Traceback:\n%s', traceback.format_exc()
        )
        raise


def _parse_addresses(artifacts: list[Artifact]) -> list[ContactAddress]:
    """Parses a list of artifacts into a list of ContactAddress objects."""
    return artifact_utils.find_canonical_objects(
        artifacts, CONTACT_ADDRESS_DATA_KEY, ContactAddress
    )
