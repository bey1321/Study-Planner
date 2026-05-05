from student_model import ALL_ACTIONS, heuristic, is_goal, risk_score
from search import a_star_search, greedy_search, uniform_cost_search

_ALGO_KEYS = {
    "A* Search":           "astar",
    "Greedy Best-First":   "greedy",
    "Uniform Cost Search": "ucs",
}


def run_single_algorithm(start, algo_name, actions=None):
    if actions is None:
        actions = ALL_ACTIONS
    if is_goal(start):
        return _ALGO_KEYS[algo_name], {"already_safe": True}
    if algo_name == "A* Search":
        path, cost, final, met = a_star_search(start, actions, heuristic, is_goal)
    elif algo_name == "Greedy Best-First":
        path, cost, final, met = greedy_search(start, actions, heuristic, is_goal)
    else:
        path, cost, final, met = uniform_cost_search(start, actions, heuristic, is_goal)
    return _ALGO_KEYS[algo_name], {"path": path, "cost": cost, "final": final, "metrics": met}


def run_all_algorithms(start, actions=None):
    if actions is None:
        actions = ALL_ACTIONS
    if is_goal(start):
        return {"already_safe": True}
    path_a, cost_a, final_a, met_a = a_star_search(start, actions, heuristic, is_goal)
    path_g, cost_g, final_g, met_g = greedy_search(start, actions, heuristic, is_goal)
    path_u, cost_u, final_u, met_u = uniform_cost_search(start, actions, heuristic, is_goal)
    return {
        "astar":  {"path": path_a, "cost": cost_a, "final": final_a, "metrics": met_a},
        "greedy": {"path": path_g, "cost": cost_g, "final": final_g, "metrics": met_g},
        "ucs":    {"path": path_u, "cost": cost_u, "final": final_u, "metrics": met_u},
    }
