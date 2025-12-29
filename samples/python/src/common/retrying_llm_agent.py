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

"""An LLM agent that surfaces errors to the user and then retries.

This implementation enhances the ADK's LlmAgent by automatically retrying
requests and surfacing errors captured from the LLM.
"""

import logging

from typing import Any, override

from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.events.event import Event
from typing_extensions import AsyncGenerator


_logger = logging.getLogger(__name__)


class RetryingLlmAgent(LlmAgent):
    """An LLM agent that surfaces errors to the user and then retries."""

    def __init__(
        self,
        *args: Any,  # noqa: ANN401
        max_retries: int = 1,
        **kwargs: Any,  # noqa: ANN401
    ):
        super().__init__(*args, **kwargs)
        self._max_retries = max_retries

    async def _retry_async(
        self, ctx: InvocationContext, retries_left: int = 0
    ) -> AsyncGenerator[Event, None]:
        if retries_left <= 0:
            _logger.error(
                'Maximum retries exhausted for agent %s',
                ctx.agent.name,
            )
            yield Event(
                author=ctx.agent.name,
                invocation_id=ctx.invocation_id,
                error_message=(
                    'Maximum retries exhausted. The remote Gemini server '
                    'failed to respond. Please try again later.'
                ),
            )
        else:
            try:
                async for event in super()._run_async_impl(ctx):
                    yield event
            except Exception as e:  # pylint: disable=broad-exception-caught
                _logger.error(
                    'Gemini server error in agent %s (retries_left=%d): %s',
                    ctx.agent.name,
                    retries_left,
                    str(e),
                    exc_info=True,
                )
                yield Event(
                    author=ctx.agent.name,
                    invocation_id=ctx.invocation_id,
                    error_message='Gemini server error. Retrying...',
                    custom_metadata={'error': str(e)},
                )
                async for event in self._retry_async(ctx, retries_left - 1):
                    yield event

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in self._retry_async(
            ctx, retries_left=self._max_retries
        ):
            yield event
