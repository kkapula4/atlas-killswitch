"""Audit log — standardized JSON schema for federal SIEM ingestion."""

import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Optional

from atlas_killswitch.core import KillDecision


@dataclass
class AuditEvent:
    event_id: str
    timestamp_utc: str
    schema_version: str
    framework: str
    agent_id: Optional[str]
    use_case: Optional[str]
    agency: Optional[str]
    triggered: bool
    trigger_name: Optional[str]
    reason: Optional[str]
    action_taken: Optional[str]
    input_excerpt: str
    output_excerpt: str

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


class AuditLog:
    """
    Append-only JSON-lines audit log. One event per line.
    Designed for ingestion by Splunk, Microsoft Sentinel, or agency SIEM tooling.
    """

    SCHEMA_VERSION = "atlas-killswitch.audit.v0.1"
    FRAMEWORK = "atlas-killswitch"

    def __init__(self, sink: Optional[str] = None, excerpt_chars: int = 200):
        self.sink = sink
        self.excerpt_chars = excerpt_chars

    def record(self, decision: KillDecision, agent_input: Any, agent_output: Any, context: dict) -> AuditEvent:
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            schema_version=self.SCHEMA_VERSION,
            framework=self.FRAMEWORK,
            agent_id=context.get("agent_id"),
            use_case=context.get("use_case"),
            agency=context.get("agency"),
            triggered=decision.triggered,
            trigger_name=decision.trigger_name,
            reason=decision.reason,
            action_taken=decision.action_taken,
            input_excerpt=str(agent_input)[: self.excerpt_chars],
            output_excerpt=str(agent_output)[: self.excerpt_chars],
        )
        if self.sink:
            with open(self.sink, "a", encoding="utf-8") as f:
                f.write(event.to_json_line() + "\n")
        return event
