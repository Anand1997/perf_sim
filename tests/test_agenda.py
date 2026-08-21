"""Tests for the functional agenda module."""

import pytest
from circuit_sim.agenda import (
    Agenda,
    add_to_agenda,
    after_delay,
    current_time,
    empty_agenda,
    first_agenda_item,
    get_default_agenda,
    make_agenda,
    propagate,
    remove_first_agenda_item,
    reset_default_agenda,
    set_current_time,
)


def test_agenda_initial_state():
    agenda = make_agenda()
    assert empty_agenda(agenda) is True
    assert current_time(agenda) == 0
    assert agenda.is_empty() is True
    assert agenda.get_current_time() == 0


def test_agenda_schedule_and_propagate():
    agenda = make_agenda()
    order = []

    add_to_agenda(10, lambda: order.append(("task10", current_time(agenda))), agenda)
    add_to_agenda(5, lambda: order.append(("task5", current_time(agenda))), agenda)
    add_to_agenda(10, lambda: order.append(("task10_b", current_time(agenda))), agenda)

    assert empty_agenda(agenda) is False

    propagate(agenda)

    assert empty_agenda(agenda) is True
    assert current_time(agenda) == 10
    assert order == [
        ("task5", 5),
        ("task10", 10),
        ("task10_b", 10),
    ]


def test_after_delay():
    agenda = make_agenda()
    trace = []

    def task1():
        trace.append(("t1", current_time(agenda)))
        after_delay(4, lambda: trace.append(("t2", current_time(agenda))), agenda)

    after_delay(3, task1, agenda)
    propagate(agenda)

    assert trace == [
        ("t1", 3),
        ("t2", 7),
    ]
    assert current_time(agenda) == 7


def test_propagate_step_limit():
    agenda = make_agenda()
    trace = []

    add_to_agenda(1, lambda: trace.append(1), agenda)
    add_to_agenda(2, lambda: trace.append(2), agenda)
    add_to_agenda(3, lambda: trace.append(3), agenda)

    # Execute only 2 steps
    propagate(agenda, step_limit=2)
    assert trace == [1, 2]
    assert empty_agenda(agenda) is False

    # Execute remaining
    propagate(agenda)
    assert trace == [1, 2, 3]
    assert empty_agenda(agenda) is True


def test_agenda_past_time_error():
    agenda = make_agenda()
    set_current_time(agenda, 10)
    with pytest.raises(ValueError, match="Cannot schedule action in the past"):
        add_to_agenda(5, lambda: None, agenda)


def test_agenda_empty_pop_errors():
    agenda = make_agenda()
    with pytest.raises(IndexError, match="Agenda is empty"):
        first_agenda_item(agenda)
    with pytest.raises(IndexError, match="Agenda is empty"):
        remove_first_agenda_item(agenda)


def test_default_agenda_handling():
    reset_default_agenda()
    log = []

    after_delay(5, lambda: log.append("default_task"))
    assert not empty_agenda()
    propagate()
    assert log == ["default_task"]
    assert current_time() == 5
    assert empty_agenda()
