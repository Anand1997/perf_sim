"""Tests for the functional queue module."""

import pytest
from circuit_sim.queue import (
    Queue,
    delete_queue,
    empty_queue,
    front_queue,
    insert_queue,
    make_queue,
)


def test_queue_initial_state():
    q = make_queue()
    assert empty_queue(q) is True
    assert q.is_empty() is True
    assert len(q) == 0
    assert q("empty?") is True


def test_queue_insert_and_front():
    q = make_queue()
    insert_queue(q, "a")
    assert empty_queue(q) is False
    assert front_queue(q) == "a"
    assert len(q) == 1

    insert_queue(q, "b")
    assert front_queue(q) == "a"
    assert len(q) == 2


def test_queue_delete_fifo_order():
    q = make_queue()
    insert_queue(q, 10)
    insert_queue(q, 20)
    insert_queue(q, 30)

    assert delete_queue(q) == 10
    assert front_queue(q) == 20
    assert delete_queue(q) == 20
    assert front_queue(q) == 30
    assert delete_queue(q) == 30
    assert empty_queue(q) is True


def test_empty_queue_errors():
    q = make_queue()
    with pytest.raises(IndexError, match="FRONT called on an empty queue"):
        front_queue(q)
    with pytest.raises(IndexError, match="DELETE! called on an empty queue"):
        delete_queue(q)


def test_message_passing_interface():
    q = make_queue()
    assert q("empty?") is True
    q("insert!", "item1")
    q("insert!", "item2")
    assert q("size") == 2
    assert q("front") == "item1"
    assert q("items") == ["item1", "item2"]
    assert q("delete!") == "item1"
    assert q("delete!") == "item2"
    assert q("empty?") is True

    with pytest.raises(ValueError, match="Unknown operation -- QUEUE"):
        q("unknown_msg")


def test_queue_class_alias():
    q = Queue()
    q.insert(100)
    assert q.front() == 100
    assert q.delete() == 100
    assert q.is_empty()
