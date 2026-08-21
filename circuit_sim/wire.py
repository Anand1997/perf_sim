"""
Functional Wire Abstraction (SICP Section 3.3.4).

In SICP, a Wire is represented as a computational object via a closure that
maintains local state:
- signal_value: Current logical state (0 or 1, defaults to 0)
- action_procedures: List of zero-argument procedures triggered on signal transitions

When a wire's signal changes value, all registered action procedures are called.
When an action procedure is newly added to a wire, it is executed immediately
to synchronize the initial state of connected components.
"""

from typing import Any, Callable, List, Optional, Sequence, Union


def call_each(procedures: Sequence[Callable[[], Any]]) -> None:
    """
    Higher-order procedure: calls each 0-argument procedure in the sequence.
    Corresponds to SICP (call-each procedures).
    """
    for proc in list(procedures):
        proc()


def make_wire(name: Optional[str] = None) -> Callable[..., Any]:
    """
    Constructs a new Wire computational object using closure encapsulation
    and message passing dispatch.
    
    Args:
        name: Optional human-readable name for debugging and probing.
        
    Returns:
        A dispatch function representing the Wire.
    """
    signal_value: int = 0
    action_procedures: List[Callable[[], Any]] = []

    def get_signal_fn() -> int:
        return signal_value

    def set_signal_fn(new_value: int) -> str:
        nonlocal signal_value
        if new_value not in (0, 1):
            raise ValueError(f"Invalid signal value: {new_value}. Signal must be 0 or 1.")
        if signal_value != new_value:
            signal_value = new_value
            call_each(action_procedures)
        return "done"

    def accept_action_procedure_fn(proc: Callable[[], Any]) -> str:
        if not callable(proc):
            raise TypeError("Action procedure must be callable")
        action_procedures.append(proc)
        # In SICP, newly registered action procedures are run immediately
        proc()
        return "done"

    def get_actions_fn() -> List[Callable[[], Any]]:
        return list(action_procedures)

    def dispatch(message: str, *args: Any) -> Any:
        if message in ("get_signal", "get-signal", "signal"):
            return get_signal_fn()
        elif message in ("set_signal!", "set-signal!", "set_signal"):
            if len(args) == 0:
                return set_signal_fn
            return set_signal_fn(args[0])
        elif message in ("add_action!", "add-action!", "add_action"):
            if len(args) == 0:
                return accept_action_procedure_fn
            return accept_action_procedure_fn(args[0])
        elif message == "name":
            return name
        elif message == "actions":
            return get_actions_fn()
        else:
            raise ValueError(f"Unknown operation -- WIRE: {message}")

    # Attach convenience attributes & methods for idiomatic Python access
    dispatch.get_signal = get_signal_fn
    dispatch.set_signal = set_signal_fn
    dispatch.add_action = accept_action_procedure_fn
    dispatch.name = name
    dispatch.actions = get_actions_fn
    
    # Expose signal_value as property-like attribute
    class WireDispatcher:
        def __call__(self, *a, **kw):
            return dispatch(*a, **kw)
        
        def __getattr__(self, item):
            return getattr(dispatch, item)
            
        @property
        def signal_value(self) -> int:
            return get_signal_fn()
            
        def __repr__(self) -> str:
            name_str = f"'{name}'" if name else "unnamed"
            return f"Wire({name_str}, signal={signal_value})"

    return dispatch


# Procedural interface (SICP style)
def get_signal(wire: Callable[..., Any]) -> int:
    """Returns the current signal value of a wire (SICP get-signal)."""
    if hasattr(wire, "get_signal"):
        return wire.get_signal()
    return wire("get_signal")


def set_signal(wire: Callable[..., Any], new_value: int) -> str:
    """Sets the signal value of a wire (SICP set-signal!)."""
    if hasattr(wire, "set_signal"):
        return wire.set_signal(new_value)
    return wire("set_signal!", new_value)


def add_action(wire: Callable[..., Any], action_proc: Callable[[], Any]) -> str:
    """Registers an action procedure with a wire (SICP add-action!)."""
    if hasattr(wire, "add_action"):
        return wire.add_action(action_proc)
    return wire("add_action!", action_proc)


def get_wire_name(wire: Callable[..., Any]) -> Optional[str]:
    """Returns the name of a wire if specified."""
    if hasattr(wire, "name"):
        return wire.name
    return wire("name")


# Alias for class diagram / object-oriented style compatibility
Wire = make_wire


# Bus utilities for multi-bit circuits
def make_bus(size: int, prefix: str = "wire") -> List[Callable[..., Any]]:
    """Creates a list of `size` distinct wires forming a bus."""
    if size <= 0:
        raise ValueError("Bus size must be positive")
    return [make_wire(f"{prefix}[{i}]") for i in range(size)]


def get_bus_values(bus: Sequence[Callable[..., Any]]) -> List[int]:
    """Reads the current signal value of each wire in the bus."""
    return [get_signal(w) for w in bus]


def set_bus_values(bus: Sequence[Callable[..., Any]], values: Union[int, Sequence[int]]) -> None:
    """
    Sets the signals of a wire bus.
    
    Args:
        bus: List of wires (index 0 is least significant bit if integer passed).
        values: Either an integer (converted to binary) or a list/tuple of 0s and 1s.
    """
    if isinstance(values, int):
        # Convert integer to bit list (LSB at index 0)
        bit_list = [(values >> i) & 1 for i in range(len(bus))]
    else:
        bit_list = list(values)
        if len(bit_list) != len(bus):
            raise ValueError(f"Values length ({len(bit_list)}) does not match bus width ({len(bus)})")

    for wire, val in zip(bus, bit_list):
        set_signal(wire, val)
