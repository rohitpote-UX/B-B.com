"""
Brand Battle — Event Listener Module
Listens for price drops, recommendation updates, and wishlist changes.
"""

from typing import Dict, Any


class NotificationEventListener:
    """Event listener subscribing to core system events."""

    def on_price_changed(self, product_id: int, old_price: float, new_price: float) -> None:
        """Handle price change event."""
        pass


# Singleton
event_listener = NotificationEventListener()
