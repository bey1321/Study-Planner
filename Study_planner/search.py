import heapq
import itertools
import time
import warnings


def _state_id(state):
    """Hashable identity for a state. Rounds floats to avoid drift."""
    return (round(state.attendance, 2), state.missing, state.score,
            round(state.lms, 2), state.study_hours, state.days, state.fatigue)


def _reconstruct_path(parent, goal_id):
    """Walk the parent map backwards from goal to start, then reverse."""
    path, sid = [], goal_id
    while parent[sid][0] is not None:
        _, action_name, state = parent[sid]
        path.append((action_name, state))
        sid = parent[sid][0]
    return list(reversed(path))


def _search(start_state, actions, is_goal, priority_fn,
            heuristic=None, max_nodes=None):
    """
    General search framework shared by A*, Greedy, and UCS.

    Parameters:
        start_state  : initial State object
        actions      : list of functions, each takes a state and returns
                       (new_state, cost) or None
        is_goal      : function returning True when a state is the goal
        priority_fn  : function(g, state) -> heap priority
                       A*     -> g + h(state)
                       Greedy -> h(state)
                       UCS    -> g
        heuristic    : if provided, consistency is checked at runtime and a
                       warning is raised once if violated (A* only)
        max_nodes    : if set, search stops after expanding this many nodes
                       and returns (None, None, None, metrics)

    Returns:
        path        : list of (action_name, resulting_state)
        total_cost  : total path cost (g at goal)
        final_state : the goal State reached
        metrics     : dict with 'expanded_nodes' and 'runtime'
    """
    start_time = time.time()
    expanded_nodes = 0
    counter = itertools.count()
    inconsistency_warned = False

    start_id = _state_id(start_state)

    # Heap entries: (priority, g, tie_breaker, state_id)
    # State objects are stored in `parent` — never in the heap — so heap
    # entries are plain tuples of numbers and are always comparable.
    open_set = [(priority_fn(0, start_state), 0, next(counter), start_id)]

    # state_id -> (parent_state_id, action_name, state_object)
    parent = {start_id: (None, None, start_state)}

    # Best known g-cost per state; uses strict > so equal-cost alternative
    # paths are not discarded (allows finding all optimal paths if needed).
    best_g = {start_id: 0}

    visited = set()

    while open_set:
        _, g, _, current_id = heapq.heappop(open_set)

        if current_id in visited:
            continue
        visited.add(current_id)
        expanded_nodes += 1

        if max_nodes is not None and expanded_nodes > max_nodes:
            runtime = time.time() - start_time
            metrics = {'expanded_nodes': expanded_nodes, 'runtime': runtime}
            warnings.warn(
                f"Search stopped: node expansion limit of {max_nodes} reached "
                f"without finding a goal. Returning no solution.",
                RuntimeWarning, stacklevel=3
            )
            return None, None, None, metrics

        current = parent[current_id][2] #retrieve the state object for the current state_id

        if is_goal(current):
            runtime = time.time() - start_time
            metrics = {'expanded_nodes': expanded_nodes, 'runtime': runtime}
            return _reconstruct_path(parent, current_id), g, current, metrics

        for action in actions:
            result = action(current)
            if result is None:
                continue

            successor, cost = result
            new_g = g + cost
            successor_id = _state_id(successor)

            if successor_id in visited:
                continue
            if new_g > best_g.get(successor_id, float('inf')):
                continue

            # Runtime consistency check: h(n) <= cost(n, n') + h(n').
            # A consistent heuristic implies admissibility. Warn once if violated.
            if heuristic is not None and not inconsistency_warned:
                if heuristic(current) > cost + heuristic(successor):
                    warnings.warn(
                        "Heuristic is inconsistent: h(current) > cost + h(successor). "
                        "A* is no longer guaranteed to find the optimal path.",
                        UserWarning, stacklevel=3
                    )
                    inconsistency_warned = True

            best_g[successor_id] = new_g
            parent[successor_id] = (current_id, action.__name__, successor)
            heapq.heappush(open_set,
                           (priority_fn(new_g, successor), new_g,
                            next(counter), successor_id))

    runtime = time.time() - start_time
    metrics = {'expanded_nodes': expanded_nodes, 'runtime': runtime}
    return None, None, None, metrics


def a_star_search(start_state, actions, heuristic, is_goal, max_nodes=None):
    """
    A* search: priority = g(n) + h(n).
    Optimal when the heuristic is admissible (never overestimates).
    Warns at runtime if the heuristic is found to be inconsistent.

    Parameters:
        max_nodes : optional int — stops search after this many expansions

    Returns:
        path, total_cost, final_state, metrics
    """
    return _search(start_state, actions, is_goal,
                   priority_fn=lambda g, state: g + heuristic(state),
                   heuristic=heuristic,
                   max_nodes=max_nodes)


def greedy_search(start_state, actions, heuristic, is_goal, max_nodes=None):
    """
    Greedy Best-First Search: priority = h(n).
    Fast but not guaranteed to find the optimal path.
    The heuristic is used only for ordering — no consistency check is performed
    because Greedy does not guarantee optimality regardless.

    Parameters:
        max_nodes : optional int — stops search after this many expansions

    Returns:
        path, total_cost, final_state, metrics
    """
    return _search(start_state, actions, is_goal,
                   priority_fn=lambda _, state: heuristic(state),
                   max_nodes=max_nodes)


def uniform_cost_search(start_state, actions, _heuristic, is_goal, max_nodes=None):
    """
    Uniform Cost Search: priority = g(n).
    Optimal but explores more nodes than A* (heuristic is intentionally ignored).
    The _heuristic parameter is accepted only to keep a uniform call signature
    with a_star_search and greedy_search.

    Parameters:
        max_nodes : optional int — stops search after this many expansions

    Returns:
        path, total_cost, final_state, metrics
    """
    return _search(start_state, actions, is_goal,
                   priority_fn=lambda g, _: g,
                   max_nodes=max_nodes)
