"""Emotional/behavioral signal extraction, per E4_REQUIREMENTS.md.

Per idea.md's own scope: "understand the user's emotional/behavioral
state ... purely from the language used in conversation transcripts —
no separate mood-logging mechanism." A small, built-in lexicon,
zero new dependency (E4_HARD_CONSTRAINTS_PRECHECK.md's resolution of
Hard Constraint #9) — no persistence, computed fresh from the
existing conversations/messages tables every call.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .conversation import get_conversation, get_messages
from .core import MemoryStore

# Small, explicit, inspectable lexicons — not a black-box score. Each
# match is returned alongside the label, so the signal's basis is
# always visible (this project's evidence-over-assertion discipline,
# applied to a heuristic instead of a claim).
_FRUSTRATION_CUES = frozenset({
    "stuck", "frustrated", "frustrating", "broken", "annoying", "annoyed",
    "ugh", "argh", "hate", "can't figure out", "cant figure out",
    "doesn't work", "does not work", "not working", "give up", "giving up",
    "so confusing", "waste of time", "sick of", "tired of",
})
_POSITIVE_CUES = frozenset({
    "finally works", "finally", "great", "excited", "love", "nice",
    "works now", "figured it out", "solved", "progress", "excellent",
    "awesome", "happy", "relieved", "good news",
})

@dataclass(frozen=True)
class BehavioralSignal:
    available: bool
    label: str = "unavailable"
    frustration_matches: tuple[str, ...] = field(default_factory=tuple)
    positive_matches: tuple[str, ...] = field(default_factory=tuple)
    message_count: int = 0


def _find_cues(text: str, cues: frozenset[str]) -> list[str]:
    lowered = text.lower()
    return [cue for cue in cues if cue in lowered]


def extract_behavioral_signal(store: MemoryStore, conversation_id: str) -> BehavioralSignal:
    """Extract a frustration/positive/neutral signal from one
    conversation's own message text. Never writes anything — purely
    a read computed fresh from `conversations`/`messages`, per
    idea.md's "no separate mood-logging mechanism" constraint.
    """
    get_conversation(store, conversation_id)  # raises KeyError if missing
    messages = get_messages(store, conversation_id)
    if not messages:
        return BehavioralSignal(available=False)

    full_text = " ".join(m["content"] for m in messages)
    frustration_matches = _find_cues(full_text, _FRUSTRATION_CUES)
    positive_matches = _find_cues(full_text, _POSITIVE_CUES)

    if len(frustration_matches) > len(positive_matches):
        label = "frustrated"
    elif len(positive_matches) > len(frustration_matches):
        label = "positive"
    else:
        label = "neutral"

    return BehavioralSignal(
        available=True,
        label=label,
        frustration_matches=tuple(frustration_matches),
        positive_matches=tuple(positive_matches),
        message_count=len(messages),
    )


def render_behavioral_signal(store: MemoryStore, conversation_id: str) -> str:
    signal = extract_behavioral_signal(store, conversation_id)
    if not signal.available:
        return f"# Behavioral signal: {conversation_id}\n\nUnavailable — no messages recorded for this conversation."
    lines = [
        f"# Behavioral signal: {conversation_id}",
        "",
        f"Label: **{signal.label}**",
        f"Messages analyzed: {signal.message_count}",
    ]
    if signal.frustration_matches:
        lines.append(f"Frustration cues matched: {', '.join(signal.frustration_matches)}")
    if signal.positive_matches:
        lines.append(f"Positive cues matched: {', '.join(signal.positive_matches)}")
    if not signal.frustration_matches and not signal.positive_matches:
        lines.append("No frustration or positive cues matched.")
    return "\n".join(lines)


__all__ = ["BehavioralSignal", "extract_behavioral_signal", "render_behavioral_signal"]
