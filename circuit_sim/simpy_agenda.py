"""
SimPy-Powered Simulation Engine and Discrete-Event Extensions.

This module integrates the Python SimPy library (Discrete-Event Simulation)
with the SICP circuit simulator architecture, providing:
- SimPyAgenda: A drop-in replacement for SICP Agenda backed by simpy.Environment.
- RealtimeAgenda: Wall-clock paced simulation using simpy.rt.RealtimeEnvironment.
- ClockGenerator: Process-based periodic clock signal generator.
- PulseGenerator / SignalGenerator: Patterned stimulus generators for testbenches.
- Simulation runners with duration limits.
"""

from typing import Any, Callable, List, Optional, Sequence, Tuple, Union

try:
    import simpy
    import simpy.rt
    SIMPY_AVAILABLE = True
except ImportError:
    SIMPY_AVAILABLE = False

from circuit_sim.wire import get_signal, set_signal


class SimPyAgenda:
    """
    Agenda simulation engine backed by a SimPy Environment.
    
    Provides the same procedural interface and message-passing dispatch
    as the native SICP Agenda while leveraging SimPy's optimized priority heap
    and process generator capabilities.
    """

    def __init__(self, env: Optional["simpy.Environment"] = None):
        if not SIMPY_AVAILABLE:
            raise ImportError("The 'simpy' library is required to use SimPyAgenda. Install via 'pip install simpy'.")
        self.env: simpy.Environment = env if env is not None else simpy.Environment()

    def is_empty(self) -> bool:
        """Returns True if there are no pending events in the SimPy schedule."""
        return len(self.env._queue) == 0

    def get_current_time(self) -> int:
        """Returns the current simulation time as an integer."""
        return int(self.env.now)

    def current_time(self) -> int:
        """Alias for get_current_time."""
        return self.get_current_time()

    def after_delay(self, delay: int, action: Callable[[], Any]) -> str:
        """
        Schedules an action procedure to run after a delay.
        
        Uses a SimPy timeout event with an attached completion callback.
        """
        if delay < 0:
            raise ValueError(f"Delay cannot be negative: {delay}")

        timeout_event = self.env.timeout(delay)
        timeout_event.callbacks.append(lambda _: action())
        return "done"

    def add_to_agenda(self, time: int, action: Callable[[], Any]) -> str:
        """
        Schedules an action procedure at a specific future simulation time.
        """
        delay = time - self.env.now
        if delay < 0:
            raise ValueError(f"Cannot schedule action in the past: {time} < current_time ({self.env.now})")
        return self.after_delay(int(delay), action)

    def propagate(self, step_limit: Optional[int] = None) -> str:
        """
        Runs the simulation until all events are processed or step_limit is reached.
        """
        if step_limit is not None:
            for _ in range(step_limit):
                if not self.is_empty():
                    try:
                        self.env.step()
                    except simpy.core.EmptySchedule:
                        break
                else:
                    break
        else:
            self.env.run()
        return "done"

    def run_until(self, until_time: Union[int, float]) -> str:
        """Runs the simulation until the specified timestamp."""
        self.env.run(until=until_time)
        return "done"

    def process(self, generator_func: Any) -> "simpy.Process":
        """Starts a SimPy process generator inside this agenda's environment."""
        return self.env.process(generator_func)

    def __call__(self, message: str, *args: Any) -> Any:
        """SICP Message passing dispatch."""
        if message in ("empty?", "is_empty"):
            return self.is_empty()
        elif message in ("current_time", "get_current_time", "current-time"):
            return self.get_current_time()
        elif message in ("add_to_agenda!", "add-to-agenda!", "add_to_agenda"):
            if len(args) == 0:
                return self.add_to_agenda
            return self.add_to_agenda(args[0], args[1])
        elif message == "after_delay":
            if len(args) == 0:
                return self.after_delay
            return self.after_delay(args[0], args[1])
        elif message == "propagate":
            step_limit = args[0] if len(args) > 0 else None
            return self.propagate(step_limit)
        elif message == "env":
            return self.env
        else:
            raise ValueError(f"Unknown operation -- SIMPY_AGENDA: {message}")

    def __repr__(self) -> str:
        return f"SimPyAgenda(now={self.env.now}, pending_events={len(self.env._queue)})"


def make_simpy_agenda(env: Optional["simpy.Environment"] = None) -> SimPyAgenda:
    """Constructs a new SimPy-backed Agenda instance."""
    return SimPyAgenda(env=env)


def make_realtime_agenda(factor: float = 0.01, strict: bool = False) -> SimPyAgenda:
    """
    Constructs a real-time paced SimPy Agenda where simulation time correlates
    with wall-clock time (useful for animated/visual live simulations).
    
    Args:
        factor: Number of seconds per simulation time unit (default 0.01s = 10ms per tick).
        strict: If True, raises RuntimeError if processing takes longer than the real-time step.
    """
    if not SIMPY_AVAILABLE:
        raise ImportError("The 'simpy' library is required. Install via 'pip install simpy'.")
    rt_env = simpy.rt.RealtimeEnvironment(factor=factor, strict=strict)
    return SimPyAgenda(env=rt_env)


# Process-Based Generators & Stimulus Tools

def clock_generator(
    agenda_or_env: Union[SimPyAgenda, "simpy.Environment"],
    wire: Callable[..., Any],
    high_duration: int = 5,
    low_duration: int = 5,
    initial_value: int = 0,
    cycles: Optional[int] = None,
) -> Any:
    """
    Spawns a periodic clock generator process on a wire.
    
    Args:
        agenda_or_env: SimPyAgenda or simpy.Environment instance.
        wire: The Wire to drive clock pulses onto.
        high_duration: Duration of high phase (signal = 1).
        low_duration: Duration of low phase (signal = 0).
        initial_value: Initial signal state (0 or 1).
        cycles: Number of complete clock cycles (None for infinite).
        
    Returns:
        The running simpy.Process.
    """
    env = agenda_or_env.env if isinstance(agenda_or_env, SimPyAgenda) else agenda_or_env
    set_signal(wire, initial_value)

    def _clock_proc():
        val = initial_value
        count = 0
        while cycles is None or count < cycles:
            delay = high_duration if val == 1 else low_duration
            yield env.timeout(delay)
            val = 1 - val
            set_signal(wire, val)
            if val == initial_value:
                count += 1

    return env.process(_clock_proc())


def pulse_generator(
    agenda_or_env: Union[SimPyAgenda, "simpy.Environment"],
    wire: Callable[..., Any],
    sequence: Sequence[Tuple[int, int]],
    repeat: bool = False,
) -> Any:
    """
    Drives a custom timed sequence of signal values onto a wire.
    
    Args:
        agenda_or_env: SimPyAgenda or simpy.Environment instance.
        wire: The Wire to drive.
        sequence: List of (duration, value) pairs, e.g. [(10, 1), (5, 0), (20, 1)].
        repeat: Whether to loop through the sequence continuously.
        
    Returns:
        The running simpy.Process.
    """
    env = agenda_or_env.env if isinstance(agenda_or_env, SimPyAgenda) else agenda_or_env

    def _pulse_proc():
        while True:
            for duration, val in sequence:
                set_signal(wire, val)
                yield env.timeout(duration)
            if not repeat:
                break

    return env.process(_pulse_proc())


def signal_schedule(
    agenda_or_env: Union[SimPyAgenda, "simpy.Environment"],
    wire: Callable[..., Any],
    schedule: Sequence[Tuple[int, int]],
) -> Any:
    """
    Applies transitions at absolute timestamps: [(timestamp, value), ...].
    """
    env = agenda_or_env.env if isinstance(agenda_or_env, SimPyAgenda) else agenda_or_env

    def _schedule_proc():
        sorted_schedule = sorted(schedule, key=lambda p: p[0])
        last_t = env.now
        for abs_time, val in sorted_schedule:
            if abs_time < env.now:
                continue
            delta = abs_time - env.now
            if delta > 0:
                yield env.timeout(delta)
            set_signal(wire, val)

    return env.process(_schedule_proc())
