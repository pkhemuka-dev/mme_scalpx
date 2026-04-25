from __future__ import annotations

"""
app/mme_scalpx/integrations/dhan_execution.py

Explicit disabled Dhan execution surface for ScalpX MME Batch 5 freeze.

Purpose
-------
This module exists to remove ambiguity while the provider runtime already knows
about Dhan as the target execution-fallback provider.

Current freeze law
------------------
- Dhan execution transport is NOT active.
- Dhan may be used for market data / option context where separately configured.
- Dhan execution fallback must remain disabled until a concrete transport client,
  order contract mapping, reconciliation mapping, and execution safety proof are
  implemented.

Non-responsibilities
--------------------
- no order placement
- no Redis IO
- no provider role resolution
- no auth/session lifecycle
- no main.py composition
"""

from dataclasses import dataclass
from typing import Any, Mapping

from app.mme_scalpx.core import names

VERSION = "mme-dhan-execution-disabled-v1"
PROVIDER_ID = getattr(names, "PROVIDER_DHAN", "DHAN")
STATUS = getattr(names, "PROVIDER_STATUS_DISABLED", "DISABLED")


class DhanExecutionUnavailableError(RuntimeError):
    """Raised when Dhan execution is requested before implementation/proof."""


@dataclass(frozen=True, slots=True)
class DisabledDhanExecutionTransport:
    provider_id: str = PROVIDER_ID
    status: str = STATUS
    reason: str = (
        "Dhan execution fallback disabled until concrete Dhan execution transport "
        "is implemented and proof-enabled"
    )

    def info(self) -> dict[str, Any]:
        return {
            "adapter_name": self.__class__.__name__,
            "version": VERSION,
            "provider_id": self.provider_id,
            "status": self.status,
            "execution_supported": False,
            "transport_configured": False,
            "reason": self.reason,
        }

    def healthcheck(self, **_: Any) -> dict[str, Any]:
        return self.info()

    def place_order(self, payload: Mapping[str, Any], **_: Any) -> Any:
        raise DhanExecutionUnavailableError(self.reason)

    def get_order(self, order_id: str, **_: Any) -> Any:
        raise DhanExecutionUnavailableError(self.reason)

    def cancel_order(self, order_id: str, payload: Mapping[str, Any] | None = None, **_: Any) -> Any:
        raise DhanExecutionUnavailableError(self.reason)

    def reconcile_positions(self, **_: Any) -> Any:
        raise DhanExecutionUnavailableError(self.reason)

    def reconcile_open_orders(self, **_: Any) -> Any:
        raise DhanExecutionUnavailableError(self.reason)


def build_disabled_dhan_execution_transport() -> DisabledDhanExecutionTransport:
    return DisabledDhanExecutionTransport()


__all__ = [
    "DisabledDhanExecutionTransport",
    "DhanExecutionUnavailableError",
    "PROVIDER_ID",
    "STATUS",
    "VERSION",
    "build_disabled_dhan_execution_transport",
]
