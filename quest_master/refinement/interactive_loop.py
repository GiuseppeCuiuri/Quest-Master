from typing import Dict
from quest_master.refinement.reflection_agent import ReflectionAgent
from quest_master.validators.pddl_validator import PDDLValidator


class InteractiveRefinementLoop:
    """Chat interattiva libera per refinement di PDDL"""

    def __init__(self, validator: PDDLValidator):
        self.validator = validator
        self.reflection_agent = ReflectionAgent(validator)
        self.max_iterations = 3

    def run(self, domain_content: str, problem_content: str,
            quest_description: str) -> Dict:

        current_domain = domain_content
        current_problem = problem_content
        iteration = 0

        print("\n=== Benvenuto nella chat di refinement PDDL ===")

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n🌀 Iterazione {iteration}...")

            is_valid, error = self.validator.validate(current_domain, current_problem)

            if is_valid:
                print("✅ Validazione riuscita! Il PDDL è valido.")
                return {
                    'success': True,
                    'final_domain': current_domain,
                    'final_problem': current_problem,
                    'iterations': iteration
                }

            print(f"❌ Errore trovato: {error}")

            refinement = self.reflection_agent.analyze_and_refine(
                current_domain, current_problem, error, quest_description
            )

            print("\n🤖 ANALISI:")
            print(refinement['analysis'])

            print("\n🛠️  FIX PROPOSTI:")
            for i, suggestion in enumerate(refinement['suggestions'], 1):
                print(f"{i}. {suggestion}")

            # Chat libera
            user_choice = self._free_chat_loop(refinement['analysis'], refinement['suggestions'])

            if user_choice == 'apply':
                current_domain = refinement['refined_domain']
                current_problem = refinement['refined_problem']
                print("🟢 Fix applicati.")
            elif user_choice == 'manual':
                print("✏️ Puoi modificare i file manualmente e riprovare.")
                return {
                    'success': False,
                    'final_domain': current_domain,
                    'final_problem': current_problem,
                    'iterations': iteration,
                    'reason': 'Manual editing requested'
                }
            elif user_choice == 'skip':
                print("⏭️ Iterazione saltata.")

        print(f"\n❌ Numero massimo di iterazioni ({self.max_iterations}) raggiunto.")
        return {
            'success': False,
            'final_domain': current_domain,
            'final_problem': current_problem,
            'iterations': iteration,
            'reason': 'Max iterations reached'
        }

    def _free_chat_loop(self, analysis: str, suggestions: list) -> str:
        """
        Loop di chat libero senza if su input.
        L'LLM deve restituire stringhe speciali 'apply', 'manual', 'skip' per uscire.
        """
        print("\n💬 Scrivi liberamente cosa vuoi chiedere o dire.")
        print("Il sistema risponderà e aspetterà la tua decisione finale (es. applica, modifica, salta).")

        while True:
            user_input = input("\n🧑 Tu: ").strip()

            # Passa la conversazione al reflection agent che interpreta e risponde
            response, action = self.reflection_agent.chat_with_action(user_input, analysis, suggestions)

            print(f"\n🤖 {response}")

            # action è la decisione dell'agente: None o 'apply' o 'manual' o 'skip'
            if action in ('apply', 'manual', 'skip'):
                return action


if __name__ == "__main__":
    # Example usage
    domain_content = """
;; Quest Domain - Auto-generated
(define (domain quest-domain)
  (:requirements :strips :typing)

  (:types
    agent location item obstacle - object
  )

  (:predicates
    (at ?a - agent ?l - location)         ; agent is at location
    (has ?a - agent ?i - item)            ; agent has item
    (connected ?l1 ?l2 - location)        ; locations are connected
    (guarded_by ?l - location ?o - obstacle) ; location guarded by obstacle
    (alive ?a - agent)                    ; agent is alive
    (defeated ?o - obstacle)              ; obstacle is defeated
    (blocked ?from ?to - location)        ; path is blocked between two locations
  )

  (:action move
:parameters (?a - agent ?from ?to - location)
:precondition (and
  (at ?a ?from)
  (connected ?from ?to)
  (not (blocked ?from ?to))
  (alive ?a)
)
:effect (and
  (not (at ?a ?from))
  (at ?a ?to)
)
)
  (:action take
:parameters (?a - agent ?i - item ?l - location)
:precondition (and
  (at ?a ?l)
  (at ?i ?l)
  (alive ?a)
)
:effect (and
  (has ?a ?i)
  (not (at ?i ?l))
)
)
  (:action defeat_obstacle
:parameters (?a - agent ?o - obstacle ?l - location)
:precondition (and
  (at ?a ?l)
  (guarded_by ?l ?o)
  (alive ?a)
  (not (defeated ?o))
)
:effect (and
  (defeated ?o)
  (not (guarded_by ?l ?o))
)
)
)
    """
    problem_content = """
    ;; Quest Problem - Auto-generated
(define (problem quest-problem)
  (:domain quest-domain)

  (:objects
    hero - agent
    start - location
    crystal_caverns - location
  )

  (:init
    (at hero start)
    (alive hero)
    (connected start crystal_caverns)
    (connected crystal_caverns start)
    (guarded_by crystal_caverns golem)
  )

  (:goal
    (and
          (at hero crystal_caverns)
          (defeated golem)
    )
  )
)
    """
    quest_description = """
    The brave knight must journey to the Crystal Caverns carrying the Flame of Eternity and shatter the Dark Crystal. The entrance is sealed by an ancient golem that awakens when intruders approach.
    """

    validator = PDDLValidator()
    loop = InteractiveRefinementLoop(validator)
    result = loop.run(domain_content, problem_content, quest_description)

    print("\n=== Refinement Loop Result ===")
    print(result)