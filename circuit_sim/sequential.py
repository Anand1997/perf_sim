"""
Sequential Digital Circuits & Memory Elements.

This module implements sequential logic components (latches, flip-flops, and counters)
leveraging clock signals and feedback loops supported by the discrete-event engine:
- SR Latch (Set-Reset Latch)
- D Latch (Data / Transparent Latch)
- D Flip-Flop (Edge-Triggered Data Flip-Flop)
- T Flip-Flop (Toggle Flip-Flop)
- Synchronous Binary Counter
"""

from typing import Any, Callable, List, Optional, Sequence

from circuit_sim.delays import DEFAULT_DELAYS, Delays
from circuit_sim.gates import and_gate, inverter, nor_gate, or_gate, xor_gate
from circuit_sim.wire import get_signal, make_wire, set_signal


def sr_latch(
    s: Callable[..., Any],
    r: Callable[..., Any],
    q: Callable[..., Any],
    q_bar: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs an active-high NOR-based SR (Set-Reset) Latch.
    
    Q = NOR(R, Q_bar)
    Q_bar = NOR(S, Q)
    """
    d_delays = delays or DEFAULT_DELAYS
    nor_gate(r, q_bar, q, delay=d_delays.nor_gate, agenda=agenda)
    nor_gate(s, q, q_bar, delay=d_delays.nor_gate, agenda=agenda)
    return "ok"


def d_latch(
    d: Callable[..., Any],
    enable: Callable[..., Any],
    q: Callable[..., Any],
    q_bar: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a Level-Sensitive D (Data) Latch.
    
    When enable == 1, Q tracks D.
    When enable == 0, Q retains its previous state.
    """
    d_delays = delays or DEFAULT_DELAYS
    not_d = make_wire("dl_not_d")
    s = make_wire("dl_s")
    r = make_wire("dl_r")

    inverter(d, not_d, delay=d_delays.inverter, agenda=agenda)
    and_gate(d, enable, s, delay=d_delays.and_gate, agenda=agenda)
    and_gate(not_d, enable, r, delay=d_delays.and_gate, agenda=agenda)
    sr_latch(s, r, q, q_bar, delays=d_delays, agenda=agenda)
    return "ok"


def d_flip_flop(
    d: Callable[..., Any],
    clk: Callable[..., Any],
    q: Callable[..., Any],
    q_bar: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a Positive-Edge-Triggered D Flip-Flop using a Master-Slave topology:
    - Master D Latch (enabled on NOT CLK)
    - Slave D Latch (enabled on CLK)
    """
    d_delays = delays or DEFAULT_DELAYS
    clk_bar = make_wire("dff_clk_bar")
    master_q = make_wire("dff_master_q")
    master_q_bar = make_wire("dff_master_q_bar")

    inverter(clk, clk_bar, delay=d_delays.inverter, agenda=agenda)
    # Master enabled when CLK is low
    d_latch(d, clk_bar, master_q, master_q_bar, delays=d_delays, agenda=agenda)
    # Slave enabled when CLK is high (transfers master state on rising edge)
    d_latch(master_q, clk, q, q_bar, delays=d_delays, agenda=agenda)
    return "ok"


def t_flip_flop(
    t: Callable[..., Any],
    clk: Callable[..., Any],
    q: Callable[..., Any],
    q_bar: Callable[..., Any],
    delays: Optional[Delays] = None,
    agenda: Optional[Callable[..., Any]] = None,
) -> str:
    """
    Constructs a Toggle (T) Flip-Flop:
    D = T XOR Q
    """
    d_delays = delays or DEFAULT_DELAYS
    d = make_wire("tff_d")
    xor_gate(t, q, d, delay=d_delays.xor_gate, agenda=agenda)
    d_flip_flop(d, clk, q, q_bar, delays=d_delays, agenda=agenda)
    return "ok"


def binary_counter(
    clk: Callable[..., Any],
    count_bus: Sequence[Callable[..., Any]],
    agenda: Optional[Callable[..., Any]] = None,
) -> List[Callable[..., Any]]:
    """
    Constructs an n-bit asynchronous/ripple binary counter driven by a clock signal.
    
    Each stage consists of a T flip-flop configured to toggle (T=1).
    """
    n = len(count_bus)
    q_bars = [make_wire(f"q_bar_{i}") for i in range(n)]
    vcc = make_wire("vcc")
    set_signal(vcc, 1)

    current_clk = clk
    for i in range(n):
        t_flip_flop(vcc, current_clk, count_bus[i], q_bars[i], agenda=agenda)
        current_clk = q_bars[i]

    return q_bars
