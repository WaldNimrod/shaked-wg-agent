"""Signal extractors for WG listings.

Available extractors:
  - diet_signals: detect vegetarian/vegan-friendly households
  - quiet_signals: detect quiet/calm households
  - social_signals: detect named roommates, age ranges, social vibe
"""
from shaked_wg_agent.extractors import diet_signals, quiet_signals, social_signals

__all__ = ["diet_signals", "quiet_signals", "social_signals"]
