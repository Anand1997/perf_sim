"""
N-bit datapath demo: 8-bit ALU and clocked register.

Computes several Nand2Tetris ALU functions, then loads the result into an
8-bit register on a rising clock edge.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from circuit_sim import (
    alu,
    bus_to_int,
    get_signal,
    make_agenda,
    make_bus,
    make_wire,
    n_bit_register,
    propagate,
    set_bus_values,
    set_signal,
)


def run_alu(x_val, y_val, controls, label):
    zx_v, nx_v, zy_v, ny_v, f_v, no_v = controls
    agenda = make_agenda()
    x = make_bus(8, "X")
    y = make_bus(8, "Y")
    out = make_bus(8, "OUT")
    zx, nx, zy, ny, f, no = [make_wire(n) for n in ("zx", "nx", "zy", "ny", "f", "no")]
    zr = make_wire("zr")
    ng = make_wire("ng")
    alu(x, y, out, zx, nx, zy, ny, f, no, zr, ng, agenda=agenda)
    set_bus_values(x, x_val)
    set_bus_values(y, y_val)
    set_signal(zx, zx_v)
    set_signal(nx, nx_v)
    set_signal(zy, zy_v)
    set_signal(ny, ny_v)
    set_signal(f, f_v)
    set_signal(no, no_v)
    propagate(agenda)
    print(
        f"  {label:8}  out={bus_to_int(out):3}  zr={get_signal(zr)}  ng={get_signal(ng)}"
    )
    return bus_to_int(out)


def main():
    print("8-bit ALU  (x=15, y=51)")
    x, y = 15, 51
    run_alu(x, y, (1, 0, 1, 0, 1, 0), "0")
    run_alu(x, y, (1, 1, 1, 1, 1, 1), "1")
    run_alu(x, y, (0, 0, 1, 0, 1, 0), "x")
    run_alu(x, y, (1, 0, 0, 0, 1, 0), "y")
    result = run_alu(x, y, (0, 0, 0, 0, 1, 0), "x+y")
    run_alu(x, y, (0, 0, 0, 0, 0, 0), "x&y")
    run_alu(x, y, (0, 1, 0, 0, 1, 1), "x-y")

    print("\n8-bit register: load ALU sum, then hold")
    agenda = make_agenda()
    d = make_bus(8, "D")
    q = make_bus(8, "Q")
    clk = make_wire("CLK")
    load = make_wire("LOAD")
    n_bit_register(d, clk, q, load=load, agenda=agenda)

    set_bus_values(d, result)
    set_signal(load, 1)
    set_signal(clk, 0)
    propagate(agenda)
    set_signal(clk, 1)
    propagate(agenda)
    set_signal(clk, 0)
    propagate(agenda)
    print(f"  after load  Q={bus_to_int(q)}")

    set_bus_values(d, 0)
    set_signal(load, 0)
    set_signal(clk, 1)
    propagate(agenda)
    set_signal(clk, 0)
    propagate(agenda)
    print(f"  after hold  Q={bus_to_int(q)}")


if __name__ == "__main__":
    main()
