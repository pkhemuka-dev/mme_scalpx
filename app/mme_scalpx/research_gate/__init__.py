"""Research Gate / RAW package.

RAW is a non-live, non-mutating evidence layer above research_capture and replay.
It does not trade, mutate production, write live Redis truth, or own broker/risk/execution truth.
"""

from .contracts import RAW_CONTRACT_VERSION, RAW_PACKAGE_NAME

__all__ = [
    "RAW_CONTRACT_VERSION",
    "RAW_PACKAGE_NAME",
]
