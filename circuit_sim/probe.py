"""
Circuit Monitoring Probe (SICP Section 3.3.4).

A probe is an action procedure attached to a wire that observes signal changes
and reports the wire name, timestamp, and new signal value.
"""

from typing import Any, Callable, List, NamedTuple, Optional, Tuple

from circuit_sim.agenda import current_time, get_default_agenda
from circuit_sim.wire import add_action, get_signal


class ProbeEvent(NamedTuple):
    """Immutable record of an observed wire state transition."""
    name: str
    time: int
    value: int
    message: str


def probe(
    name: str,
    wire: Callable[..., Any],
    agenda: Optional[Callable[..., Any]] = None,
    callback: Optional[Callable[[str, int, int, str], Any]] = None,
) -> Callable[[], None]:
    """
    Attaches a monitoring probe to a wire.
    
    Whenever the wire's signal changes, the probe prints:
        <name> <current_time>  New-value = <new_signal_value>
        
    Args:
        name: Name of the probe / signal identifier.
        wire: The Wire to observe.
        agenda: Optional specific agenda (defaults to global default agenda).
        callback: Optional custom callable(name, time, value, formatted_msg).
                  If None, prints formatted message to standard output.
                  
    Returns:
        The action procedure registered with the wire.
    """
    def probe_action() -> None:
        t = current_time(agenda)
        val = get_signal(wire)
        msg = f"{name} {t}  New-value = {val}"
        if callback is not None:
            callback(name, t, val, msg)
        else:
            print(msg)

    add_action(wire, probe_action)
    return probe_action


class ProbeRecorder:
    """Helper utility for capturing and inspecting probe events during testing."""

    def __init__(self):
        self.events: List[ProbeEvent] = []

    def callback(self, name: str, time: int, value: int, msg: str) -> None:
        self.events.append(ProbeEvent(name=name, time=time, value=value, message=msg))

    def clear(self) -> None:
        self.events.clear()

    @property
    def latest(self) -> Optional[ProbeEvent]:
        return self.events[-1] if self.events else None

    @property
    def transitions(self) -> List[Tuple[str, int, int]]:
        return [(e.name, e.time, e.value) for e in self.events]

    def __len__(self) -> int:
        return len(self.events)


def make_probe_recorder() -> ProbeRecorder:
    """Creates a ProbeRecorder instance to collect probed transitions."""
    return ProbeRecorder()
