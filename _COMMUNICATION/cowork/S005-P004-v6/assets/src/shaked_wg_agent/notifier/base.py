"""Abstract base for notification channel implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypedDict


class NotificationResult(TypedDict, total=False):
    """Result dict returned by notify_digest (when notifications run)."""

    channels: list[dict[str, Any]]
    total_sent: int
    total_failed: int


@dataclass
class ChannelResult:
    """Result of a single channel send attempt."""

    channel_type: str
    label: str | None
    success: bool
    error: str | None


class BaseNotifier(ABC):
    """Abstract base for all notification channels."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.last_error: str | None = None
        self.last_error_transient: bool = False

    @abstractmethod
    def send(self, digest_payload: dict[str, Any]) -> bool:
        """Send the digest via this channel. Never raises."""
        ...

    @abstractmethod
    def format_message(self, digest_payload: dict[str, Any]) -> Any:
        """Format digest for this channel."""
        ...
