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

"""Objects for the Agent Payments Protocol Payment Receipt."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from ap2.types.payment_request import PaymentCurrencyAmount


PAYMENT_RECEIPT_DATA_KEY = 'ap2.PaymentReceipt'


class Success(BaseModel):
    """Details about a successful payment."""

    merchant_confirmation_id: str = Field(
        ...,
        description='Unique ID for transaction confirmation at merchant.',
    )
    psp_confirmation_id: str | None = Field(
        None,
        description='Unique ID for transaction confirmation at PSP.',
    )
    network_confirmation_id: str | None = Field(
        None,
        description='Unique ID for transaction confirmation at network.',
    )


class Error(BaseModel):
    """Details about an errored payment."""

    error_message: str = Field(
        ...,
        description='Human-readable message explaining error & how to proceed.',
    )


class Failure(BaseModel):
    """Details about a failed payment."""

    failure_message: str = Field(
        ...,
        description='Human-readable message explaining failure & how to proceed.',
    )


class PaymentReceipt(BaseModel):
    """Supplies information about the final state of a payment."""

    payment_mandate_id: str = Field(
        ...,
        description='A unique identifier for the processed payment mandate.',
    )
    timestamp: str = Field(
        description='Date and time payment receipt created in ISO 8601.',
        default_factory=lambda: datetime.now(UTC).isoformat(),
    )
    payment_id: str = Field(
        ..., description='A unique identifier for the payment.'
    )
    amount: PaymentCurrencyAmount = Field(
        ..., description='The monetary amount of the payment.'
    )
    payment_status: Success | Error | Failure = Field(
        ..., description='The status of the payment.'
    )
    payment_method_details: dict[str, Any] | None = Field(
        None,
        description='The payment method used for the transaction.',
    )
