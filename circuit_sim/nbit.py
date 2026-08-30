"""
N-bit datapath primitives.

Extends the 1-bit SICP gates and the n-bit ripple-carry adder with bus-wide
combinational operators, a 2-to-1 bus multiplexer, a clocked n-bit register,
and a Nand2Tetris-style ALU (zx/nx/zy/ny/f/no plus zr/ng flags).
"""

from typing import Any, Callable, List, Optional, Sequence

from circuit_sim.circuits import multiplexer, ripple_carry_adder
from circuit_sim.delays import DEFAULT_DELAYS, Delays
from circuit_sim.gates import and_gate, inverter, or_gate, xor_gate
from circuit_sim.sequential import d_flip_flop
from circuit_sim.wire import make_wire, set_signal


def _require_width(*buses: Sequence[Callable[..., Any]], name: str = "bus") -> int:
    if not buses:
        raise ValueError(f"{name} requires at least one bus")
    n = len(buses[0])
    if n == 0:
        raise ValueError(f"{name} requires at least 1 bit")
    for bus in buses[1:]:
        if len(bus) != n:
            raise ValueError(f"{name} width mismatch: expected {n}, got {len(bus)}")
    return n


def n_bit_not(
    in_bus: Sequence[Callable[..., Any]],
    out_bus: Sequence[Callable[..., Any]],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """Bitwise inverter: out[i] = NOT in[i]."""
    n = _require_width(in_bus, out_bus, name="n_bit_not")
    d_delays = delays or DEFAULT_DELAYS
    for i in range(n):
        inverter(in_bus[i], out_bus[i], delay=d_delays.inverter, agenda=agenda)
    return "ok"


def n_bit_and(
    a_bus: Sequence[Callable[..., Any]],
    b_bus: Sequence[Callable[..., Any]],
    out_bus: Sequence[Callable[..., Any]],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """Bitwise AND: out[i] = a[i] AND b[i]."""
    n = _require_width(a_bus, b_bus, out_bus, name="n_bit_and")
    d_delays = delays or DEFAULT_DELAYS
    for i in range(n):
        and_gate(a_bus[i], b_bus[i], out_bus[i], delay=d_delays.and_gate, agenda=agenda)
    return "ok"


def n_bit_or(
    a_bus: Sequence[Callable[..., Any]],
    b_bus: Sequence[Callable[..., Any]],
    out_bus: Sequence[Callable[..., Any]],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """Bitwise OR: out[i] = a[i] OR b[i]."""
    n = _require_width(a_bus, b_bus, out_bus, name="n_bit_or")
    d_delays = delays or DEFAULT_DELAYS
    for i in range(n):
        or_gate(a_bus[i], b_bus[i], out_bus[i], delay=d_delays.or_gate, agenda=agenda)
    return "ok"


def n_bit_xor(
    a_bus: Sequence[Callable[..., Any]],
    b_bus: Sequence[Callable[..., Any]],
    out_bus: Sequence[Callable[..., Any]],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """Bitwise XOR: out[i] = a[i] XOR b[i]."""
    n = _require_width(a_bus, b_bus, out_bus, name="n_bit_xor")
    d_delays = delays or DEFAULT_DELAYS
    for i in range(n):
        xor_gate(a_bus[i], b_bus[i], out_bus[i], delay=d_delays.xor_gate, agenda=agenda)
    return "ok"


def n_bit_and_bit(
    in_bus: Sequence[Callable[..., Any]],
    control: Callable[..., Any],
    out_bus: Sequence[Callable[..., Any]],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """AND every bit of in_bus with a single control wire."""
    n = _require_width(in_bus, out_bus, name="n_bit_and_bit")
    d_delays = delays or DEFAULT_DELAYS
    for i in range(n):
        and_gate(in_bus[i], control, out_bus[i], delay=d_delays.and_gate, agenda=agenda)
    return "ok"


def n_bit_mux(
    a_bus: Sequence[Callable[..., Any]],
    b_bus: Sequence[Callable[..., Any]],
    sel: Callable[..., Any],
    out_bus: Sequence[Callable[..., Any]],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    n-bit 2-to-1 multiplexer.

    sel == 0 -> out = a
    sel == 1 -> out = b
    """
    n = _require_width(a_bus, b_bus, out_bus, name="n_bit_mux")
    d_delays = delays or DEFAULT_DELAYS
    for i in range(n):
        multiplexer(a_bus[i], b_bus[i], sel, out_bus[i], delays=d_delays, agenda=agenda)
    return "ok"


def or_reduce(
    in_bus: Sequence[Callable[..., Any]],
    out_wire: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """OR-reduction of an n-bit bus onto a single wire."""
    n = _require_width(in_bus, name="or_reduce")
    d_delays = delays or DEFAULT_DELAYS
    if n == 1:
        # Identity delay-0 path would skip the agenda; use OR with 0 instead
        # so the output still updates through a gate delay.
        zero = make_wire("or_reduce_zero")
        or_gate(in_bus[0], zero, out_wire, delay=d_delays.or_gate, agenda=agenda)
        return "ok"

    current = in_bus[0]
    for i in range(1, n):
        nxt = out_wire if i == n - 1 else make_wire(f"or_reduce_{i}")
        or_gate(current, in_bus[i], nxt, delay=d_delays.or_gate, agenda=agenda)
        current = nxt
    return "ok"


def n_bit_register(
    d_bus: Sequence[Callable[..., Any]],
    clk: Callable[..., Any],
    q_bus: Sequence[Callable[..., Any]],
    load: Optional[Callable[..., Any]] = None,
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> List[Callable[..., Any]]:
    """
    Positive-edge-triggered n-bit register built from D flip-flops.

    If `load` is provided, the register holds its previous value when load=0
    and captures `d_bus` when load=1. If `load` is omitted, every rising clock
    edge stores `d_bus`.
    """
    n = _require_width(d_bus, q_bus, name="n_bit_register")
    d_delays = delays or DEFAULT_DELAYS
    q_bars = [make_wire(f"reg_qbar_{i}") for i in range(n)]

    d_inputs: Sequence[Callable[..., Any]] = d_bus
    if load is not None:
        muxed = [make_wire(f"reg_mux_{i}") for i in range(n)]
        n_bit_mux(q_bus, d_bus, load, muxed, delays=d_delays, agenda=agenda)
        d_inputs = muxed

    for i in range(n):
        d_flip_flop(d_inputs[i], clk, q_bus[i], q_bars[i], delays=d_delays, agenda=agenda)
    return q_bars


def alu(
    x_bus: Sequence[Callable[..., Any]],
    y_bus: Sequence[Callable[..., Any]],
    out_bus: Sequence[Callable[..., Any]],
    zx: Callable[..., Any],
    nx: Callable[..., Any],
    zy: Callable[..., Any],
    ny: Callable[..., Any],
    f: Callable[..., Any],
    no: Callable[..., Any],
    zr: Callable[..., Any],
    ng: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    n-bit ALU following the Nand2Tetris / Hack control convention:

        if zx then x = 0
        if nx then x = NOT x
        if zy then y = 0
        if ny then y = NOT y
        if f  then out = x + y  else  out = x AND y
        if no then out = NOT out
        zr = 1 iff out == 0
        ng = 1 iff out is negative (MSB set; two's-complement)
    """
    n = _require_width(x_bus, y_bus, out_bus, name="alu")
    d_delays = delays or DEFAULT_DELAYS

    zx_bar = make_wire("alu_zx_bar")
    zy_bar = make_wire("alu_zy_bar")
    inverter(zx, zx_bar, delay=d_delays.inverter, agenda=agenda)
    inverter(zy, zy_bar, delay=d_delays.inverter, agenda=agenda)

    x_zeroed = [make_wire(f"alu_xz_{i}") for i in range(n)]
    y_zeroed = [make_wire(f"alu_yz_{i}") for i in range(n)]
    n_bit_and_bit(x_bus, zx_bar, x_zeroed, delays=d_delays, agenda=agenda)
    n_bit_and_bit(y_bus, zy_bar, y_zeroed, delays=d_delays, agenda=agenda)

    x_not = [make_wire(f"alu_xn_{i}") for i in range(n)]
    y_not = [make_wire(f"alu_yn_{i}") for i in range(n)]
    n_bit_not(x_zeroed, x_not, delays=d_delays, agenda=agenda)
    n_bit_not(y_zeroed, y_not, delays=d_delays, agenda=agenda)

    x_pre = [make_wire(f"alu_xp_{i}") for i in range(n)]
    y_pre = [make_wire(f"alu_yp_{i}") for i in range(n)]
    n_bit_mux(x_zeroed, x_not, nx, x_pre, delays=d_delays, agenda=agenda)
    n_bit_mux(y_zeroed, y_not, ny, y_pre, delays=d_delays, agenda=agenda)

    and_out = [make_wire(f"alu_and_{i}") for i in range(n)]
    add_out = [make_wire(f"alu_add_{i}") for i in range(n)]
    c_out = make_wire("alu_cout")
    n_bit_and(x_pre, y_pre, and_out, delays=d_delays, agenda=agenda)
    ripple_carry_adder(x_pre, y_pre, add_out, c_out, delays=d_delays, agenda=agenda)

    f_out = [make_wire(f"alu_f_{i}") for i in range(n)]
    n_bit_mux(and_out, add_out, f, f_out, delays=d_delays, agenda=agenda)

    f_not = [make_wire(f"alu_fn_{i}") for i in range(n)]
    n_bit_not(f_out, f_not, delays=d_delays, agenda=agenda)
    n_bit_mux(f_out, f_not, no, out_bus, delays=d_delays, agenda=agenda)

    any_one = make_wire("alu_any")
    or_reduce(out_bus, any_one, delays=d_delays, agenda=agenda)
    inverter(any_one, zr, delay=d_delays.inverter, agenda=agenda)

    # ng follows the MSB; copy through an OR-with-0 so it is delay-scheduled.
    zero = make_wire("alu_ng_zero")
    or_gate(out_bus[n - 1], zero, ng, delay=d_delays.or_gate, agenda=agenda)
    return "ok"


def bus_to_int(bus: Sequence[Callable[..., Any]]) -> int:
    """Interpret a bus (LSB at index 0) as an unsigned integer."""
    from circuit_sim.wire import get_signal

    return sum(get_signal(w) << i for i, w in enumerate(bus))
