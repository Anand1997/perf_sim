# Agent Context: SICP Digital Circuit Simulator

This document provides a comprehensive technical reference and context for AI agents working on this codebase.

---

## 1. Project Overview & Background

- **Domain**: Discrete-Event Digital Hardware Simulation.
- **Reference**: Chapter 3.3.4 (*"A Simulator for Digital Circuits"*) of **Structure and Interpretation of Computer Programs (SICP)** by Harold Abelson & Gerald Jay Sussman.
- **Language**: Python 3.10+ (tested on Python 3.14).
- **Core Paradigm**: Functional programming with procedural data abstraction, closures, first-class procedures, and message passing, paired with optional **SimPy** discrete-event process capabilities.

---

## 2. Core Architecture & Module Reference

```
perf_sim/core/
├── circuit_sim/               # Main simulation engine package
│   ├── __init__.py           # Unified exports
│   ├── delays.py             # Delays namedtuple & DEFAULT_DELAYS configuration
│   ├── queue.py              # Functional FIFO Queue closure & message passing
│   ├── wire.py               # Functional Wire closure, signal transitions & bus helpers
│   ├── agenda.py             # SICP Agenda time-segment priority scheduler
│   ├── simpy_agenda.py       # SimPy-backed Agenda & process generators
│   ├── gates.py              # Pure boolean logic & primitive logic gates
│   ├── circuits.py           # Combinational circuits (adders, mux/demux)
│   ├── nbit.py               # N-bit datapath (bitwise ops, mux, register, ALU)
│   ├── sequential.py         # Sequential circuits (latches, flip-flops, counter)
│   └── probe.py              # Monitoring probes & test recording utilities
├── examples/                 # Executable walkthroughs and benchmarks
│   ├── half_adder_demo.py
│   ├── full_adder_demo.py
│   ├── ripple_carry_adder_demo.py
│   ├── simpy_clocked_counter_demo.py
│   ├── simpy_benchmark_demo.py
│   └── nbit_alu_demo.py
├── tests/                    # automated pytest unit & integration tests
│   ├── test_agenda.py
│   ├── test_circuits.py
│   ├── test_nbit.py
│   ├── test_gates.py
│   ├── test_probe.py
│   ├── test_queue.py
│   ├── test_simpy_agenda.py
│   └── test_wire.py
├── doc/                      # UML diagrams
│   ├── uml_class_circuit_sim.png
│   └── uml_sequence_circuit_sim.png
├── .vscode/                  # VS Code testing & debugging configurations
│   ├── settings.json
│   └── launch.json
├── README.md                 # User documentation & architecture guide
└── agent.md                  # This AI Agent context file
```

---

## 3. Design Patterns & Conventions

### A. Closures & Message Passing (SICP Style)
Objects are implemented using closures that encapsulate private state and return a dispatch function:
- **`make_wire(name=None)`**:
  - Enclosed state: `signal_value` (0 or 1), `action_procedures` (list of 0-arg callbacks), `name`.
  - Message dispatch: `wire("get_signal")`, `wire("set_signal!", new_val)`, `wire("add_action!", proc)`.
  - Also exposes methods: `wire.get_signal()`, `wire.set_signal(new_val)`, `wire.add_action(proc)`.
- **`make_queue()`**:
  - Enclosed state: `_items` (`collections.deque`).
  - Message dispatch: `queue("empty?")`, `queue("front")`, `queue("insert!", item)`, `queue("delete!")`.
- **`make_agenda()`**:
  - Enclosed state: `sim_time` (int), `segments` (sorted list of `TimeSegment(time, queue)`).
  - Message dispatch: `agenda("empty?")`, `agenda("current_time")`, `agenda("add_to_agenda!", time, action)`, `agenda("propagate")`.

### B. Dual Interface Support
Every component supports both:
1. **SICP Procedural Functions**:
   ```python
   w = make_wire("A")
   set_signal(w, 1)
   val = get_signal(w)
   add_action(w, my_action)
   ```
2. **Object/Method Interface**:
   ```python
   w = make_wire("A")
   w.set_signal(1)
   val = w.get_signal()
   w.add_action(my_action)
   ```

### C. Simulation Execution Semantics
1. **Immediate Execution on Connect**:
   When `add_action(wire, proc)` is called, `proc()` is executed **immediately** once to compute the initial gate outputs and schedule initialization events on the agenda.
2. **Signal Change Triggering**:
   `set_signal(wire, new_value)` ONLY invokes registered action procedures if `new_value != current_signal`.
3. **Propagation Delays**:
   Gates do NOT modify output wires synchronously. Instead, they calculate new outputs and schedule them:
   `after_delay(delay, lambda: set_signal(output_wire, new_val), agenda)`.
4. **Propagate Loop**:
   `propagate(agenda)` pops the earliest time segment, advances `current_time`, and executes all queued actions in FIFO order until the agenda is empty.

---

## 4. Gate Delays & Standard Timing Values

Defined in [`circuit_sim/delays.py`](file:///C:/dev/perf_sim/core/circuit_sim/delays.py):
- `inverter_delay` = 2
- `and_gate_delay` = 3
- `or_gate_delay` = 5
- `nand_gate_delay` = 3
- `nor_gate_delay` = 5
- `xor_gate_delay` = 8

### Canonical SICP Half-Adder Timing Trace
For Half-Adder with inputs $A, B$, sum $S$, carry $C$:
1. $t=0$: Initialized to $A=0, B=0, S=0, C=0$.
2. $t=0$: `set_signal(A, 1)` and `propagate()`.
   - $t=8$: $S \rightarrow 1$ (`sum 8 New-value = 1`).
3. $t=8$: `set_signal(B, 1)` and `propagate()`.
   - $t=11$: $C \rightarrow 1$ (`carry 11 New-value = 1`).
   - $t=16$: $S \rightarrow 0$ (`sum 16 New-value = 0`).

---

## 5. SimPy Engine Backend & Extensions

Located in [`circuit_sim/simpy_agenda.py`](file:///C:/dev/perf_sim/core/circuit_sim/simpy_agenda.py):
- **`SimPyAgenda` / `make_simpy_agenda(env=None)`**:
  - Uses `simpy.Environment` event queue.
  - 100% API-compatible drop-in replacement for the native SICP `Agenda`.
- **`make_realtime_agenda(factor=0.01)`**:
  - Uses `simpy.rt.RealtimeEnvironment` for wall-clock paced execution.
- **Process Generators**:
  - `clock_generator(agenda, wire, high_duration=5, low_duration=5, cycles=None)`: Periodic square wave.
  - `pulse_generator(agenda, wire, sequence=[(duration, value), ...])`: Timed stimulus.
  - `signal_schedule(agenda, wire, schedule=[(abs_time, value), ...])`: Absolute timestamp transitions.

---

## 6. Circuit Catalog

### Combinational Logic ([`circuit_sim/circuits.py`](file:///C:/dev/perf_sim/core/circuit_sim/circuits.py))
- `half_adder(a, b, s, c, delays, agenda)`
- `full_adder(a, b, c_in, sum_wire, c_out, delays, agenda)`
- `ripple_carry_adder(a_bus, b_bus, sum_bus, c_out, c_in=None, delays, agenda)`
- `multiplexer(a, b, sel, out_wire, delays, agenda)` (2-to-1 Mux)
- `demultiplexer(in_wire, sel, out_a, out_b, delays, agenda)` (1-to-2 Demux)

### N-bit Datapath ([`circuit_sim/nbit.py`](file:///C:/dev/perf_sim/core/circuit_sim/nbit.py))
- `n_bit_not` / `n_bit_and` / `n_bit_or` / `n_bit_xor` / `n_bit_mux` / `or_reduce`
- `n_bit_register(d_bus, clk, q_bus, load=None, delays, agenda)`
- `alu(x, y, out, zx, nx, zy, ny, f, no, zr, ng, delays, agenda)` (Nand2Tetris control)

### Sequential Logic ([`circuit_sim/sequential.py`](file:///C:/dev/perf_sim/core/circuit_sim/sequential.py))
- `sr_latch(s, r, q, q_bar, delays, agenda)`
- `d_latch(d, enable, q, q_bar, delays, agenda)`
- `d_flip_flop(d, clk, q, q_bar, delays, agenda)` (Positive-edge Master-Slave)
- `t_flip_flop(t, clk, q, q_bar, delays, agenda)`
- `binary_counter(clk, count_bus, agenda)` (Ripple binary counter)

---

## 7. Testing & Verification Guide

### Test Suite Structure (43 Tests)
All tests run with `pytest`:
```powershell
python -m pytest -v
```

| Test File | Focus Areas |
|---|---|
| [`tests/test_agenda.py`](file:///C:/dev/perf_sim/core/tests/test_agenda.py) | Agenda creation, time advancement, delay scheduling, step limits, default agenda. |
| [`tests/test_wire.py`](file:///C:/dev/perf_sim/core/tests/test_wire.py) | Wire closure state, signal validation, callback dispatch, bus helpers. |
| [`tests/test_queue.py`](file:///C:/dev/perf_sim/core/tests/test_queue.py) | FIFO queue ordering, empty errors, message passing interface. |
| [`tests/test_gates.py`](file:///C:/dev/perf_sim/core/tests/test_gates.py) | Pure logic functions, propagation delays, De Morgan OR, OOP gate aliases. |
| [`tests/test_circuits.py`](file:///C:/dev/perf_sim/core/tests/test_circuits.py) | Half-adder / Full-adder truth tables, exact SICP timing trace, 4-bit adder, Mux/Demux. |
| [`tests/test_nbit.py`](file:///C:/dev/perf_sim/core/tests/test_nbit.py) | N-bit bitwise ops, mux, load/hold register, Nand2Tetris ALU functions. |
| [`tests/test_simpy_agenda.py`](file:///C:/dev/perf_sim/core/tests/test_simpy_agenda.py) | SimPyAgenda, clock_generator, pulse_generator, 8-bit ripple adder on SimPy, SR latch, RealtimeAgenda. |
| [`tests/test_probe.py`](file:///C:/dev/perf_sim/core/tests/test_probe.py) | Probe output formatting, callback hooks, `ProbeRecorder`. |

---

## 8. Guidelines for Future AI Agents Extending This Codebase

1. **Maintain Functional Style**:
   When implementing new components, encapsulate state via closures or callable dispatch objects. Preserve the message-passing dispatch protocol (`obj("message", *args)`).
2. **Preserve Dual Interfaces**:
   Always provide procedural functions (e.g. `do_something(obj)`) alongside method attributes on dispatchers.
3. **Respect Agenda Delays**:
   Never mutate connected output wires immediately in response to an input change; always schedule the change via `after_delay(delay, lambda: set_signal(out_wire, val), agenda)`.
4. **Immediate Action Execution**:
   When adding callbacks via `add_action(wire, proc)`, remember that `proc()` must run once at registration to initialize downstream wire states.
5. **Agenda Agnosticism**:
   Keep all circuit and gate functions agnostic to the backend: they should accept any `agenda` supporting `after_delay` and `get_current_time` (works transparently with both native SICP `Agenda` and `SimPyAgenda`).
