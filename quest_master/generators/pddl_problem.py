from ..models.quest_data import EnhancedQuestData


class PDDLProblemGenerator:
    def __init__(self, quest_data: EnhancedQuestData):
        self.quest = quest_data
        self.problem_name = "quest-problem"

    def generate(self) -> str:
        """Genera il problem PDDL completo"""
        return f""";; Quest Problem - Auto-generated
(define (problem {self.problem_name})
  (:domain quest-domain)

  (:objects
{self._generate_objects()}
  )

  (:init
{self._generate_init()}
  )

  (:goal
{self._generate_goal()}
  )
)"""

    def _generate_objects(self) -> str:
        """Genera la sezione objects"""
        objects = ["    hero - agent"]

        # Agent

        # Locations
        for loc in self.quest.locations:
            objects.append(f"    {loc} - location")

        # Items
        for item in self.quest.items:
            objects.append(f"    {item} - item")

        # Obstacles
        for obstacle in set(self.quest.obstacles.values()):
            objects.append(f"    {obstacle} - obstacle")

        return "\n".join(objects)

    def _generate_init(self) -> str:
        """Genera lo stato iniziale"""
        init_facts = [f"    (at hero {self.quest.initial_location})", "    (alive hero)"]

        # Inizializza funzioni per profondità e branching
        max_depth = 0
        if self.quest.depth_constraints and "max" in self.quest.depth_constraints:
            max_depth = self.quest.depth_constraints["max"]
        else:
            max_depth = len(self.quest.locations)
        init_facts.append(f"    (= (current-step) 0)")
        init_facts.append(f"    (= (max-depth) {max_depth})")

        branch_limit = None
        if self.quest.branching_factor and "max" in self.quest.branching_factor:
            branch_limit = self.quest.branching_factor["max"]
        for loc in self.quest.locations:
            if branch_limit is not None:
                init_facts.append(f"    (= (branch-limit {loc}) {branch_limit})")
            else:
                init_facts.append(f"    (= (branch-limit {loc}) {len(self.quest.connections)})")
            init_facts.append(f"    (= (actions-used {loc}) 0)")

        # Hero position and state

        # Item positions (all at destination initially)
        for item in self.quest.items:
            init_facts.append(f"    (at {item} {self.quest.locations[-1]})")

        # Connections
        for loc1, loc2 in self.quest.connections:
            init_facts.append(f"    (connected {loc1} {loc2})")
            init_facts.append(f"    (connected {loc2} {loc1})")  # bidirectional

        # Obstacles
        for location, obstacle in self.quest.obstacles.items():
            init_facts.append(f"    (guarded_by {location} {obstacle})")

        return "\n".join(init_facts)

    def _generate_goal(self) -> str:
        """Genera le condizioni di goal"""
        goal_facts = []

        # Build goal from conditions
        for condition in self.quest.goal_conditions:
            goal_facts.append(f"    ({condition})")

        if len(goal_facts) == 1:
            return goal_facts[0]
        else:
            return "    (and\n" + "\n".join(f"      {fact}" for fact in goal_facts) + "\n    )"