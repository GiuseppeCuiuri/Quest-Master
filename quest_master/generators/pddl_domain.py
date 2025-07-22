from ..models.quest_data import EnhancedQuestData


def _generate_predicates() -> str:
    """Genera i predicati base"""
    predicates = [
        "    (at ?a - agent ?l - location)         ; agent is at location",
        "    (has ?a - agent ?i - item)            ; agent has item",
        "    (connected ?l1 ?l2 - location)        ; locations are connected",
        "    (guarded_by ?l - location ?o - obstacle) ; location guarded by obstacle",
        "    (alive ?a - agent)                    ; agent is alive",
        "    (defeated ?o - obstacle)              ; obstacle is defeated",
        "    (blocked ?from ?to - location)        ; path is blocked between two locations"
    ]
    return "\n".join(predicates)


def _generate_functions() -> str:
    """Genera le funzioni numeric-fluents"""
    funcs = [
        "    (current-step)",
        "    (max-depth)",
        "    (actions-used ?l - location)",
        "    (branch-limit ?l - location)",
    ]
    return "\n".join(funcs)


def _move_action() -> str:
    return """  (:action move
:parameters (?a - agent ?from ?to - location)
:precondition (and
  (at ?a ?from)
  (connected ?from ?to)
  (not (blocked ?from ?to))
  (alive ?a)
  (< (current-step) (max-depth))
  (< (actions-used ?from) (branch-limit ?from))
)
:effect (and
  (not (at ?a ?from))
  (at ?a ?to)
  (increase (current-step) 1)
  (increase (actions-used ?from) 1)
)
)"""


def _take_action() -> str:
    return """  (:action take
:parameters (?a - agent ?i - item ?l - location)
:precondition (and
  (at ?a ?l)
  (at ?i ?l)
  (alive ?a)
  (< (current-step) (max-depth))
  (< (actions-used ?l) (branch-limit ?l))
)
:effect (and
  (has ?a ?i)
  (not (at ?i ?l))
  (increase (current-step) 1)
  (increase (actions-used ?l) 1)
)
)"""


def _defeat_obstacle_action() -> str:
    return """  (:action defeat_obstacle
:parameters (?a - agent ?o - obstacle ?l - location)
:precondition (and
  (at ?a ?l)
  (guarded_by ?l ?o)
  (alive ?a)
  (not (defeated ?o))
  (< (current-step) (max-depth))
  (< (actions-used ?l) (branch-limit ?l))
)
:effect (and
  (defeated ?o)
  (not (guarded_by ?l ?o))
  (increase (current-step) 1)
  (increase (actions-used ?l) 1)
)
)"""


def _generate_actions() -> str:
    """Genera le azioni base"""
    actions = [
        _move_action(),
        _take_action(),
        _defeat_obstacle_action()
    ]
    return "\n".join(actions)


class PDDLDomainGenerator:
    def __init__(self):
        self.domain_name = "quest-domain"

    def generate(self, quest_data: EnhancedQuestData) -> str:
        """Genera il domain PDDL completo"""
        return f""";; Quest Domain - Auto-generated
(define (domain {self.domain_name})
  (:requirements :strips :typing :numeric-fluents)

  (:types
    agent location item obstacle - object
  )

  (:predicates
{_generate_predicates()}
  )

  (:functions
{_generate_functions()}
  )

{_generate_actions()}
)"""

