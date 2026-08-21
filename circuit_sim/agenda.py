"""
Functional Agenda and Event-Driven Simulation Engine (SICP Section 3.3.4).

An Agenda is a time-ordered schedule of actions (callbacks) to be executed.
It consists of:
- current_time: Current simulation time (integer).
- segments: A collection of time segments, ordered by simulation time. Each
  time segment contains a timestamp and a FIFO queue of action procedures scheduled
  for that time.

Key operations:
- make_agenda()               : Constructs an agenda instance.
- empty_agenda(agenda)        : True if no actions remain scheduled.
- current_time(agenda)        : Returns current simulation time.
- add_to_agenda(time, action) : Enqueues an action at a future timestamp.
- first_agenda_item(agenda)   : Peeks at next procedure and advances current_time.
- remove_first_agenda_item(a) : Pops the completed procedure.
- after_delay(delay, action)  : Schedules action at current_time + delay.
- propagate(agenda)           : Runs scheduled events until the agenda is empty.
"""

from bisect import bisect_left
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

from circuit_sim.queue import (
    delete_queue,
    empty_queue,
    front_queue,
    insert_queue,
    make_queue,
)


@dataclass
class TimeSegment:
    """A time segment associating a discrete timestamp with an action queue."""
    time: int
    queue: Callable[..., Any]

    def __repr__(self) -> str:
        return f"TimeSegment(time={self.time}, queue={self.queue})"


def make_time_segment(time: int, queue: Optional[Callable[..., Any]] = None) -> TimeSegment:
    """Creates a new time segment (SICP make-time-segment)."""
    if queue is None:
        queue = make_queue()
    return TimeSegment(time=time, queue=queue)


def segment_time(segment: TimeSegment) -> int:
    """Extracts timestamp from a time segment (SICP segment-time)."""
    return segment.time


def segment_queue(segment: TimeSegment) -> Callable[..., Any]:
    """Extracts action queue from a time segment (SICP segment-queue)."""
    return segment.queue


def make_agenda() -> Callable[..., Any]:
    """
    Constructs a new Agenda simulation engine closure with message passing dispatch.
    
    Supported messages:
    - 'empty?' / 'is_empty'           : Returns True if agenda has no scheduled items.
    - 'current_time' / 'get_current_time': Returns current simulation time.
    - 'set_current_time!'             : Sets current simulation time.
    - 'time_segments'                 : Returns list of time segments.
    - 'add_to_agenda!'                : Enqueues (time, action).
    - 'first_item'                    : Returns front action and updates current time.
    - 'remove_first_item!'            : Pops front action.
    - 'after_delay'                   : Schedules action after delay.
    - 'propagate'                     : Runs simulation until empty.
    """
    sim_time: int = 0
    segments: List[TimeSegment] = []

    def is_empty() -> bool:
        return len(segments) == 0

    def get_current_time() -> int:
        return sim_time

    def set_current_time_fn(time: int) -> None:
        nonlocal sim_time
        sim_time = time

    def add_to_agenda_fn(time: int, action: Callable[[], Any]) -> str:
        if not callable(action):
            raise TypeError("Action must be callable")
        if time < sim_time:
            raise ValueError(f"Cannot schedule action in the past: {time} < current_time ({sim_time})")

        # Find existing segment with matching time using binary search
        times = [seg.time for seg in segments]
        idx = bisect_left(times, time)

        if idx < len(segments) and segments[idx].time == time:
            # Append to existing time segment queue
            insert_queue(segments[idx].queue, action)
        else:
            # Create a new time segment and insert in sorted position
            new_q = make_queue()
            insert_queue(new_q, action)
            new_seg = make_time_segment(time, new_q)
            segments.insert(idx, new_seg)
        return "done"

    def first_item() -> Callable[[], Any]:
        nonlocal sim_time
        if is_empty():
            raise IndexError("Agenda is empty -- FIRST-AGENDA-ITEM")
        first_seg = segments[0]
        sim_time = first_seg.time
        return front_queue(first_seg.queue)

    def remove_first_item() -> None:
        if is_empty():
            raise IndexError("Agenda is empty -- REMOVE-FIRST-AGENDA-ITEM!")
        first_seg = segments[0]
        delete_queue(first_seg.queue)
        if empty_queue(first_seg.queue):
            segments.pop(0)

    def after_delay_fn(delay: int, action: Callable[[], Any]) -> str:
        return add_to_agenda_fn(sim_time + delay, action)

    def propagate_fn(step_limit: Optional[int] = None) -> str:
        steps = 0
        while not is_empty():
            if step_limit is not None and steps >= step_limit:
                break
            item = first_item()
            item()
            remove_first_item()
            steps += 1
        return "done"

    def dispatch(message: str, *args: Any) -> Any:
        if message in ("empty?", "is_empty"):
            return is_empty()
        elif message in ("current_time", "get_current_time", "current-time"):
            return get_current_time()
        elif message in ("set_current_time!", "set-current-time!"):
            if len(args) == 0:
                return set_current_time_fn
            set_current_time_fn(args[0])
            return "done"
        elif message in ("time_segments", "segments"):
            return list(segments)
        elif message in ("add_to_agenda!", "add-to-agenda!", "add_to_agenda"):
            if len(args) == 0:
                return add_to_agenda_fn
            return add_to_agenda_fn(args[0], args[1])
        elif message in ("first_item", "first-item"):
            return first_item()
        elif message in ("remove_first_item!", "remove-first-item!"):
            return remove_first_item()
        elif message == "after_delay":
            if len(args) == 0:
                return after_delay_fn
            return after_delay_fn(args[0], args[1])
        elif message == "propagate":
            step_limit = args[0] if len(args) > 0 else None
            return propagate_fn(step_limit)
        else:
            raise ValueError(f"Unknown operation -- AGENDA: {message}")

    # Attach convenience methods
    dispatch.is_empty = is_empty
    dispatch.get_current_time = get_current_time
    dispatch.current_time = get_current_time
    dispatch.set_current_time = set_current_time_fn
    dispatch.add_to_agenda = add_to_agenda_fn
    dispatch.first_item = first_item
    dispatch.remove_first_item = remove_first_item
    dispatch.after_delay = after_delay_fn
    dispatch.propagate = propagate_fn
    dispatch.segments = lambda: list(segments)
    dispatch.__repr__ = lambda: f"Agenda(current_time={sim_time}, pending_segments={len(segments)})"

    return dispatch


# Global default agenda management (SICP the-agenda)
_default_agenda: Optional[Callable[..., Any]] = None


def get_default_agenda() -> Callable[..., Any]:
    """Returns the global default agenda, instantiating it if necessary."""
    global _default_agenda
    if _default_agenda is None:
        _default_agenda = make_agenda()
    return _default_agenda


def set_default_agenda(agenda: Callable[..., Any]) -> None:
    """Sets the global default agenda."""
    global _default_agenda
    _default_agenda = agenda


def reset_default_agenda() -> Callable[..., Any]:
    """Resets the global default agenda to a fresh instance."""
    global _default_agenda
    _default_agenda = make_agenda()
    return _default_agenda


# Procedural interface (SICP style)
def empty_agenda(agenda: Optional[Callable[..., Any]] = None) -> bool:
    """Checks if the agenda is empty (SICP empty-agenda?)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "is_empty"):
        return ag.is_empty()
    return ag("empty?")


def current_time(agenda: Optional[Callable[..., Any]] = None) -> int:
    """Returns the current simulation time (SICP current-time)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "get_current_time"):
        return ag.get_current_time()
    return ag("current_time")


get_current_time = current_time


def set_current_time(agenda: Callable[..., Any], time: int) -> None:
    """Sets the simulation time of the agenda."""
    if hasattr(agenda, "set_current_time"):
        agenda.set_current_time(time)
    else:
        agenda("set_current_time!", time)


def add_to_agenda(time: int, action: Callable[[], Any], agenda: Optional[Callable[..., Any]] = None) -> str:
    """Enqueues an action at a specific future time (SICP add-to-agenda!)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "add_to_agenda"):
        return ag.add_to_agenda(time, action)
    return ag("add_to_agenda!", time, action)


def first_agenda_item(agenda: Optional[Callable[..., Any]] = None) -> Callable[[], Any]:
    """Returns the first scheduled procedure and advances current time (SICP first-agenda-item)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "first_item"):
        return ag.first_item()
    return ag("first_item")


def remove_first_agenda_item(agenda: Optional[Callable[..., Any]] = None) -> None:
    """Pops the first procedure from the agenda (SICP remove-first-agenda-item!)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "remove_first_item"):
        ag.remove_first_item()
    else:
        ag("remove_first_item!")


def after_delay(delay: int, action: Callable[[], Any], agenda: Optional[Callable[..., Any]] = None) -> str:
    """Schedules an action to run after a delay (SICP after-delay)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "after_delay"):
        return ag.after_delay(delay, action)
    return ag("after_delay", delay, action)


def propagate(agenda: Optional[Callable[..., Any]] = None, step_limit: Optional[int] = None) -> str:
    """Runs simulation events until the agenda is empty (SICP propagate)."""
    ag = agenda if agenda is not None else get_default_agenda()
    if hasattr(ag, "propagate"):
        return ag.propagate(step_limit)
    return ag("propagate", step_limit)


# Alias for class diagram / object-oriented style compatibility
Agenda = make_agenda
