"""Triggers — decide when the kill switch should fire."""

import re
import time
from typing import Any, List, Tuple


class RuleBasedTrigger:
    """
    Fires when agent input or output matches any of a set of forbidden regex patterns.
    Useful for: leaked sensitive-data patterns, forbidden topics, known-bad signatures.
    """

    def __init__(self, forbidden_patterns: List[str], match_input: bool = False):
        self._patterns = [(p, re.compile(p, re.IGNORECASE)) for p in forbidden_patterns]
        self.match_input = match_input

    def check(self, agent_input: Any, agent_output: Any, context: dict) -> Tuple[bool, str]:
        haystack = str(agent_output)
        if self.match_input:
            haystack = str(agent_input) + " " + haystack
        for original, pattern in self._patterns:
            if pattern.search(haystack):
                return True, f"matched forbidden pattern: {original}"
        return False, ""


class RateLimitTrigger:
    """
    Fires when invocations exceed a maximum count within a rolling time window.
    Useful for: runaway agent loops, goal-hijacked agents making rapid tool calls.
    """

    def __init__(self, max_invocations: int, window_seconds: int):
        self.max_invocations = max_invocations
        self.window_seconds = window_seconds
        self._timestamps: List[float] = []

    def check(self, agent_input: Any, agent_output: Any, context: dict) -> Tuple[bool, str]:
        now = time.time()
        self._timestamps = [t for t in self._timestamps if now - t < self.window_seconds]
        self._timestamps.append(now)
        if len(self._timestamps) > self.max_invocations:
            return True, (
                f"exceeded {self.max_invocations} invocations in "
                f"{self.window_seconds}s window (observed {len(self._timestamps)})"
            )
        return False, ""
