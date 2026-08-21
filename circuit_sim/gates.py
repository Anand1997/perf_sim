"""
Primitive Logic Gates and Function Boxes (SICP Section 3.3.4).

In SICP, primitive function boxes are constructed by connecting wires to
action procedures that compute logical transformations and schedule delayed
output updates on the agenda.
"""

from typing import Any, Callable, Optional, Sequence

from circuit_sim.agenda import after_delay, get_default_agenda
from circuit_sim.delays import DEFAULT_DELAYS, Delays
from circuit_sim.wire import add_action, get_signal, set_signal


# Pure logical operations
def logical_not(s: int) -> int:
    """Computes logical NOT (SICP logical-not)."""
    if s == 0:
        return 1
    elif s == 1:
        return 0
    else:
        raise ValueError(f"Invalid signal: {s}. Expected 0 or 1.")


def logical_and(s1: int, s2: int) -> int:
    """Computes logical AND (SICP logical-and)."""
    if s1 not in (0, 1) or s2 not in (0, 1):
        raise ValueError(f"Invalid signals: ({s1}, {s2}). Expected 0 or 1.")
    return 1 if (s1 == 1 and s2 == 1) else 0


def logical_or(s1: int, s2: int) -> int:
    """Computes logical OR (SICP logical-or)."""
    if s1 not in (0, 1) or s2 not in (0, 1):
        raise ValueError(f"Invalid signals: ({s1}, {s2}). Expected 0 or 1.")
    return 1 if (s1 == 1 or s2 == 1) else 0


def logical_nand(s1: int, s2: int) -> int:
    """Computes logical NAND."""
    return logical_not(logical_and(s1, s2))


def logical_nor(s1: int, s2: int) -> int:
    """Computes logical NOR."""
    return logical_not(logical_or(s1, s2))


def logical_xor(s1: int, s2: int) -> int:
    """Computes logical XOR."""
    if s1 not in (0, 1) or s2 not in (0, 1):
        raise ValueError(f"Invalid signals: ({s1}, {s2}). Expected 0 or 1.")
    return 1 if (s1 != s2) else 0


# Primitive Function Box Base Class / Abstraction
class PrimitiveFunctionBox:
    """
    Abstract base representation of a primitive logic function box
    as shown in the UML architecture.
    """

    def __init__(self, delay: int, agenda: Optional[Callable[..., Any]] = None):
        self.delay = delay
        self.agenda = agenda

    def action_procedure(self) -> None:
        """The callback executed when inputs change."""
        raise NotImplementedError("Subclasses must implement action_procedure")


# Primitive Gates (Procedural & Class Implementations)

def inverter(
    input_wire: Callable[..., Any],
    output_wire: Callable[..., Any],
    delay: Optional[int] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> "Inverter":
    """
    Constructs an Inverter gate (SICP inverter).
    
    Inverts the signal on input_wire and sets output_wire after inverter_delay.
    """
    inv_delay = delay if delay is not None else DEFAULT_DELAYS.inverter
    return Inverter(input_wire, output_wire, delay=inv_delay, agenda=agenda)


class Inverter(PrimitiveFunctionBox):
    """Inverter (NOT gate) component."""

    def __init__(
        self,
        input_wire: Callable[..., Any],
        output_wire: Callable[..., Any],
        delay: Optional[int] = None,
        agenda: Optional[Callable[..., Any]] = None,
    ):
        inv_delay = delay if delay is not None else DEFAULT_DELAYS.inverter
        super().__init__(delay=inv_delay, agenda=agenda)
        self.input = input_wire
        self.output = output_wire

        def invert_input() -> None:
            new_value = logical_not(get_signal(self.input))
            after_delay(self.delay, lambda: set_signal(self.output, new_value), self.agenda)

        self._action_proc = invert_input
        add_action(self.input, self._action_proc)

    def action_procedure(self) -> None:
        self._action_proc()

    def __repr__(self) -> str:
        return f"Inverter(input={self.input}, output={self.output}, delay={self.delay})"


def and_gate(
    a1: Callable[..., Any],
    a2: Callable[..., Any],
    output_wire: Callable[..., Any],
    delay: Optional[int] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> "AndGate":
    """
    Constructs a 2-input AND gate (SICP and-gate).
    
    Computes logical AND of a1 and a2 and sets output_wire after and_gate_delay.
    """
    g_delay = delay if delay is not None else DEFAULT_DELAYS.and_gate
    return AndGate(a1, a2, output_wire, delay=g_delay, agenda=agenda)


class AndGate(PrimitiveFunctionBox):
    """AND gate component."""

    def __init__(
        self,
        a1: Callable[..., Any],
        a2: Callable[..., Any],
        output_wire: Callable[..., Any],
        delay: Optional[int] = None,
        agenda: Optional[Callable[..., Any]] = None,
    ):
        g_delay = delay if delay is not None else DEFAULT_DELAYS.and_gate
        super().__init__(delay=g_delay, agenda=agenda)
        self.a1 = a1
        self.a2 = a2
        self.output = output_wire

        def and_action_procedure() -> None:
            new_value = logical_and(get_signal(self.a1), get_signal(self.a2))
            after_delay(self.delay, lambda: set_signal(self.output, new_value), self.agenda)

        self._action_proc = and_action_procedure
        add_action(self.a1, self._action_proc)
        add_action(self.a2, self._action_proc)

    def action_procedure(self) -> None:
        self._action_proc()

    def __repr__(self) -> str:
        return f"AndGate(a1={self.a1}, a2={self.a2}, output={self.output}, delay={self.delay})"


def or_gate(
    o1: Callable[..., Any],
    o2: Callable[..., Any],
    output_wire: Callable[..., Any],
    delay: Optional[int] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> "OrGate":
    """
    Constructs a 2-input OR gate (SICP or-gate).
    
    Computes logical OR of o1 and o2 and sets output_wire after or_gate_delay.
    """
    g_delay = delay if delay is not None else DEFAULT_DELAYS.or_gate
    return OrGate(o1, o2, output_wire, delay=g_delay, agenda=agenda)


class OrGate(PrimitiveFunctionBox):
    """OR gate component."""

    def __init__(
        self,
        o1: Callable[..., Any],
        o2: Callable[..., Any],
        output_wire: Callable[..., Any],
        delay: Optional[int] = None,
        agenda: Optional[Callable[..., Any]] = None,
    ):
        g_delay = delay if delay is not None else DEFAULT_DELAYS.or_gate
        super().__init__(delay=g_delay, agenda=agenda)
        self.o1 = o1
        self.o2 = o2
        self.output = output_wire

        def or_action_procedure() -> None:
            new_value = logical_or(get_signal(self.o1), get_signal(self.o2))
            after_delay(self.delay, lambda: set_signal(self.output, new_value), self.agenda)

        self._action_proc = or_action_procedure
        add_action(self.o1, self._action_proc)
        add_action(self.o2, self._action_proc)

    def action_procedure(self) -> None:
        self._action_proc()

    def __repr__(self) -> str:
        return f"OrGate(o1={self.o1}, o2={self.o2}, output={self.output}, delay={self.delay})"


def nand_gate(
    a1: Callable[..., Any],
    a2: Callable[..., Any],
    output_wire: Callable[..., Any],
    delay: Optional[int] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> "NandGate":
    """Constructs a 2-input NAND gate."""
    g_delay = delay if delay is not None else DEFAULT_DELAYS.nand_gate
    return NandGate(a1, a2, output_wire, delay=g_delay, agenda=agenda)


class NandGate(PrimitiveFunctionBox):
    """NAND gate component."""

    def __init__(
        self,
        a1: Callable[..., Any],
        a2: Callable[..., Any],
        output_wire: Callable[..., Any],
        delay: Optional[int] = None,
        agenda: Optional[Callable[..., Any]] = None,
    ):
        g_delay = delay if delay is not None else DEFAULT_DELAYS.nand_gate
        super().__init__(delay=g_delay, agenda=agenda)
        self.a1 = a1
        self.a2 = a2
        self.output = output_wire

        def nand_action() -> None:
            new_value = logical_nand(get_signal(self.a1), get_signal(self.a2))
            after_delay(self.delay, lambda: set_signal(self.output, new_value), self.agenda)

        self._action_proc = nand_action
        add_action(self.a1, self._action_proc)
        add_action(self.a2, self._action_proc)

    def action_procedure(self) -> None:
        self._action_proc()


def nor_gate(
    o1: Callable[..., Any],
    o2: Callable[..., Any],
    output_wire: Callable[..., Any],
    delay: Optional[int] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> "NorGate":
    """Constructs a 2-input NOR gate."""
    g_delay = delay if delay is not None else DEFAULT_DELAYS.nor_gate
    return NorGate(o1, o2, output_wire, delay=g_delay, agenda=agenda)


class NorGate(PrimitiveFunctionBox):
    """NOR gate component."""

    def __init__(
        self,
        o1: Callable[..., Any],
        o2: Callable[..., Any],
        output_wire: Callable[..., Any],
        delay: Optional[int] = None,
        agenda: Optional[Callable[..., Any]] = None,
    ):
        g_delay = delay if delay is not None else DEFAULT_DELAYS.nor_gate
        super().__init__(delay=g_delay, agenda=agenda)
        self.o1 = o1
        self.o2 = o2
        self.output = output_wire

        def nor_action() -> None:
            new_value = logical_nor(get_signal(self.o1), get_signal(self.o2))
            after_delay(self.delay, lambda: set_signal(self.output, new_value), self.agenda)

        self._action_proc = nor_action
        add_action(self.o1, self._action_proc)
        add_action(self.o2, self._action_proc)

    def action_procedure(self) -> None:
        self._action_proc()


def xor_gate(
    a1: Callable[..., Any],
    a2: Callable[..., Any],
    output_wire: Callable[..., Any],
    delay: Optional[int] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> "XorGate":
    """Constructs a 2-input XOR gate."""
    g_delay = delay if delay is not None else DEFAULT_DELAYS.xor_gate
    return XorGate(a1, a2, output_wire, delay=g_delay, agenda=agenda)


class XorGate(PrimitiveFunctionBox):
    """XOR gate component."""

    def __init__(
        self,
        a1: Callable[..., Any],
        a2: Callable[..., Any],
        output_wire: Callable[..., Any],
        delay: Optional[int] = None,
        agenda: Optional[Callable[..., Any]] = None,
    ):
        g_delay = delay if delay is not None else DEFAULT_DELAYS.xor_gate
        super().__init__(delay=g_delay, agenda=agenda)
        self.a1 = a1
        self.a2 = a2
        self.output = output_wire

        def xor_action() -> None:
            new_value = logical_xor(get_signal(self.a1), get_signal(self.a2))
            after_delay(self.delay, lambda: set_signal(self.output, new_value), self.agenda)

        self._action_proc = xor_action
        add_action(self.a1, self._action_proc)
        add_action(self.a2, self._action_proc)

    def action_procedure(self) -> None:
        self._action_proc()


def compound_or_gate(
    a1: Callable[..., Any],
    a2: Callable[..., Any],
    output_wire: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs an OR gate using De Morgan's laws: A OR B = NOT (NOT A AND NOT B)
    as presented in SICP Exercise 3.29.
    
    Propagation delay is 2 * inverter_delay + and_gate_delay.
    """
    from circuit_sim.wire import make_wire

    d = delays or DEFAULT_DELAYS
    not_a1 = make_wire("not_a1")
    not_a2 = make_wire("not_a2")
    nand_out = make_wire("nand_out")

    inverter(a1, not_a1, delay=d.inverter, agenda=agenda)
    inverter(a2, not_a2, delay=d.inverter, agenda=agenda)
    and_gate(not_a1, not_a2, nand_out, delay=d.and_gate, agenda=agenda)
    inverter(nand_out, output_wire, delay=d.inverter, agenda=agenda)
    return "ok"
