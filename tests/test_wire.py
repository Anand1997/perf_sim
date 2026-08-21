"""Tests for the functional wire module."""

import pytest
from circuit_sim.wire import (
    Wire,
    add_action,
    call_each,
    get_bus_values,
    get_signal,
    get_wire_name,
    make_bus,
    make_wire,
    set_bus_values,
    set_signal,
)


def test_wire_initial_state():
    w = make_wire("w1")
    assert get_signal(w) == 0
    assert w.get_signal() == 0
    assert get_wire_name(w) == "w1"
    assert w.name == "w1"
    assert w("get_signal") == 0


def test_wire_set_signal():
    w = make_wire("w1")
    set_signal(w, 1)
    assert get_signal(w) == 1
    set_signal(w, 0)
    assert get_signal(w) == 0


def test_wire_invalid_signal():
    w = make_wire()
    with pytest.raises(ValueError, match="Invalid signal value"):
        set_signal(w, 2)
    with pytest.raises(ValueError, match="Invalid signal value"):
        set_signal(w, -1)


def test_action_procedure_invocation():
    w = make_wire("test_wire")
    calls = []

    def action():
        calls.append(get_signal(w))

    # Adding action must trigger it immediately (SICP rule)
    add_action(w, action)
    assert calls == [0]

    # Changing signal triggers action again
    set_signal(w, 1)
    assert calls == [0, 1]

    # Setting to same value does NOT trigger action
    set_signal(w, 1)
    assert calls == [0, 1]

    # Changing signal again triggers action
    set_signal(w, 0)
    assert calls == [0, 1, 0]


def test_call_each_higher_order_procedure():
    records = []
    procs = [
        lambda: records.append("p1"),
        lambda: records.append("p2"),
        lambda: records.append("p3"),
    ]
    call_each(procs)
    assert records == ["p1", "p2", "p3"]


def test_message_passing_wire():
    w = make_wire("my_wire")
    assert w("name") == "my_wire"
    assert w("get_signal") == 0
    w("set_signal!", 1)
    assert w("get_signal") == 1

    events = []
    w("add_action!", lambda: events.append(w("get_signal")))
    assert events == [1]

    with pytest.raises(ValueError, match="Unknown operation -- WIRE"):
        w("invalid_op")


def test_wire_bus_utilities():
    bus = make_bus(4, prefix="data")
    assert len(bus) == 4
    assert [w.name for w in bus] == ["data[0]", "data[1]", "data[2]", "data[3]"]
    assert get_bus_values(bus) == [0, 0, 0, 0]

    # Set using integer (e.g. 11 = binary 1011 -> LSB [1, 1, 0, 1])
    set_bus_values(bus, 11)
    assert get_bus_values(bus) == [1, 1, 0, 1]

    # Set using explicit bit list
    set_bus_values(bus, [0, 1, 1, 0])
    assert get_bus_values(bus) == [0, 1, 1, 0]

    with pytest.raises(ValueError, match="Values length"):
        set_bus_values(bus, [1, 0])
