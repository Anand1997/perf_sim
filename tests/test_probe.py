"""Tests for the probe monitoring module."""

from circuit_sim.agenda import make_agenda, propagate
from circuit_sim.probe import make_probe_recorder, probe
from circuit_sim.wire import make_wire, set_signal


def test_probe_output_and_recorder():
    agenda = make_agenda()
    w = make_wire("signal_alpha")
    recorder = make_probe_recorder()

    probe("alpha", w, agenda=agenda, callback=recorder.callback)

    # Initial probe registration captures t=0, val=0
    assert len(recorder) == 1
    assert recorder.latest.name == "alpha"
    assert recorder.latest.time == 0
    assert recorder.latest.value == 0
    assert "alpha 0  New-value = 0" in recorder.latest.message

    # Transition to 1
    set_signal(w, 1)
    assert len(recorder) == 2
    assert recorder.latest.time == 0
    assert recorder.latest.value == 1

    # Setting to 1 again should not trigger probe
    set_signal(w, 1)
    assert len(recorder) == 2


def test_probe_stdout_default(capsys):
    agenda = make_agenda()
    w = make_wire("test_w")
    probe("test_w", w, agenda=agenda)

    captured = capsys.readouterr()
    assert "test_w 0  New-value = 0" in captured.out

    set_signal(w, 1)
    captured = capsys.readouterr()
    assert "test_w 0  New-value = 1" in captured.out
