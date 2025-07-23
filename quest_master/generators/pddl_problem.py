from ..models.quest_data import EnhancedQuestData


class PDDLProblemGenerator:
    def __init__(self, quest_data: EnhancedQuestData):
        self.quest = quest_data
        self.problem_name = "quest-problem"

    def generate(self) -> str:
        """Generate the problem file with comments."""
        lines = [
            ";; Quest Problem - Auto-generated",
            f"(define (problem {self.problem_name}) ; problem name",
            "  (:domain quest-domain) ; associated domain",
            "",
            "  (:objects ; declare objects",
        ]
        lines.extend(self._generate_objects())
        lines.append("  ) ; end objects")
        lines.append("")
        lines.append("  (:init ; initial state")
        lines.extend(self._generate_init())
        lines.append("  ) ; end init")
        lines.append("")
        lines.append("  (:goal ; goal conditions")
        lines.extend(self._generate_goal())
        lines.append("  ) ; end goal")
        lines.append(") ; end problem")
        return "\n".join(lines)

    def _generate_objects(self) -> list[str]:
        """Objects section with comments."""
        objects = ["    hero - agent ; the hero"]
        for loc in self.quest.locations:
            objects.append(f"    {loc} - location ; location")
        for item in self.quest.items:
            objects.append(f"    {item} - item ; item")
        for obstacle in set(self.quest.obstacles.values()):
            objects.append(f"    {obstacle} - obstacle ; obstacle")
        return objects

    def _generate_init(self) -> list[str]:
        """Initial state facts with comments."""
        init_facts = [
            f"    (at hero {self.quest.initial_location}) ; hero starting position",
            "    (alive hero) ; hero is alive",
        ]
        max_depth = self.quest.depth_constraints.get("max", len(self.quest.locations)) if self.quest.depth_constraints else len(self.quest.locations)
        init_facts.append("    (= (current-step) 0) ; step counter start")
        init_facts.append(f"    (= (max-depth) {max_depth}) ; maximum depth")

        branch_limit = self.quest.branching_factor.get("max") if self.quest.branching_factor else None
        for loc in self.quest.locations:
            if branch_limit is not None:
                init_facts.append(f"    (= (branch-limit {loc}) {branch_limit}) ; branch limit")
            else:
                init_facts.append(f"    (= (branch-limit {loc}) {len(self.quest.connections)}) ; default branch limit")
            init_facts.append(f"    (= (actions-used {loc}) 0) ; actions used")

        for item in self.quest.items:
            init_facts.append(f"    (at {item} {self.quest.initial_location}) ; item starting location")

        for loc1, loc2 in self.quest.connections:
            init_facts.append(f"    (connected {loc1} {loc2}) ; connection forward")
            init_facts.append(f"    (connected {loc2} {loc1}) ; connection backward")

        for location, obstacle in self.quest.obstacles.items():
            init_facts.append(f"    (guarded_by {location} {obstacle}) ; obstacle guarding")

        return init_facts

    def _generate_goal(self) -> list[str]:
        """Goal conditions with comments."""
        goal_facts = []
        for condition in self.quest.goal_conditions:
            goal_facts.append(f"    ({condition}) ; goal condition")
        if len(goal_facts) <= 1:
            return goal_facts
        lines = ["    (and ; all goals"]
        lines.extend(goal_facts)
        lines.append("    ) ; end and")
        return lines
