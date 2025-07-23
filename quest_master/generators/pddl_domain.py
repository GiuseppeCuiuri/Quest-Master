from ..models.quest_data import EnhancedQuestData


def _generate_predicates() -> list[str]:
    """Return predicate lines with comments."""
    return [
        "    (at ?a - agent ?l - location) ; agent is at location",
        "    (has ?a - agent ?i - item) ; agent has item",
        "    (connected ?l1 ?l2 - location) ; locations are connected",
        "    (guarded_by ?l - location ?o - obstacle) ; location guarded by obstacle",
        "    (alive ?a - agent) ; agent is alive",
        "    (defeated ?o - obstacle) ; obstacle is defeated",
        "    (blocked ?from ?to - location) ; path is blocked"
    ]


def _generate_functions() -> list[str]:
    """Return numeric fluent lines with comments."""
    return [
        "    (current-step) ; current planning step",
        "    (max-depth) ; maximum allowed depth",
        "    (actions-used ?l - location) ; actions used at location",
        "    (branch-limit ?l - location) ; branching limit per location",
    ]


def _move_action() -> list[str]:
    """Lines for the move action with comments."""
    return [
        "  (:action move ; move from one location to another",
        "   :parameters (?a - agent ?from ?to - location) ; agent and locations",
        "   :precondition (and ; requirements to move",
        "     (at ?a ?from) ; agent at starting location",
        "     (connected ?from ?to) ; locations are connected",
        "     (not (blocked ?from ?to)) ; path is not blocked",
        "     (alive ?a) ; agent must be alive",
        "     (< (current-step) (max-depth)) ; within depth limit",
        "     (< (actions-used ?from) (branch-limit ?from)) ; within branch limit",
        "   ) ; end precondition",
        "   :effect (and ; effects of moving",
        "     (not (at ?a ?from)) ; leave old location",
        "     (at ?a ?to) ; arrive at new location",
        "     (increase (current-step) 1) ; advance step",
        "     (increase (actions-used ?from) 1) ; count action",
        "   ) ; end effect",
        "  ) ; end action",
    ]


def _take_action() -> list[str]:
    """Lines for the take action with comments."""
    return [
        "  (:action take ; pick up an item",
        "   :parameters (?a - agent ?i - item ?l - location) ; agent, item, location",
        "   :precondition (and ; requirements to take",
        "     (at ?a ?l) ; agent at location",
        "     (at ?i ?l) ; item at same location",
        "     (alive ?a) ; agent alive",
        "     (< (current-step) (max-depth)) ; within depth",
        "     (< (actions-used ?l) (branch-limit ?l)) ; within branch limit",
        "   ) ; end precondition",
        "   :effect (and ; effects of taking",
        "     (has ?a ?i) ; agent now has item",
        "     (not (at ?i ?l)) ; item removed from location",
        "     (increase (current-step) 1) ; advance step",
        "     (increase (actions-used ?l) 1) ; count action",
        "   ) ; end effect",
        "  ) ; end action",
    ]


def _defeat_obstacle_action() -> list[str]:
    """Lines for defeating an obstacle with comments."""
    return [
        "  (:action defeat_obstacle ; defeat a guarding obstacle",
        "   :parameters (?a - agent ?o - obstacle ?l - location) ; agent, obstacle, location",
        "   :precondition (and ; requirements to defeat",
        "     (at ?a ?l) ; agent at location",
        "     (guarded_by ?l ?o) ; obstacle guards location",
        "     (alive ?a) ; agent alive",
        "     (not (defeated ?o)) ; obstacle not already defeated",
        "     (< (current-step) (max-depth)) ; within depth",
        "     (< (actions-used ?l) (branch-limit ?l)) ; within branch limit",
        "   ) ; end precondition",
        "   :effect (and ; effects of defeating",
        "     (defeated ?o) ; obstacle defeated",
        "     (not (guarded_by ?l ?o)) ; location unguarded",
        "     (increase (current-step) 1) ; advance step",
        "     (increase (actions-used ?l) 1) ; count action",
        "   ) ; end effect",
        "  ) ; end action",
    ]


def _generate_actions() -> list[str]:
    """Collect all action lines."""
    actions = []
    for action in (_move_action(), _take_action(), _defeat_obstacle_action()):
        actions.extend(action)
    return actions


class PDDLDomainGenerator:
    def __init__(self):
        self.domain_name = "quest-domain"

    def generate(self, quest_data: EnhancedQuestData) -> str:
        """Generate the full domain with comments on each line."""
        lines: list[str] = [
            ";; Quest Domain - Auto-generated",
            f"(define (domain {self.domain_name}) ; domain name",
            "  (:requirements :strips :typing :numeric-fluents) ; requirements",
            "",
            "  (:types ; type declarations",
            "    agent location item obstacle - object ; basic types",
            "  ) ; end types",
            "",
            "  (:predicates ; predicate declarations",
        ]
        lines.extend(_generate_predicates())
        lines.append("  ) ; end predicates")
        lines.append("")
        lines.append("  (:functions ; numeric fluents")
        lines.extend(_generate_functions())
        lines.append("  ) ; end functions")
        lines.append("")
        lines.extend(_generate_actions())
        lines.append(") ; end domain")
        return "\n".join(lines)
