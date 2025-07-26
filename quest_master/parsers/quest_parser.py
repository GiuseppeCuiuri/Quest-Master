from typing import List, Dict, Tuple
import random
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from ..models.quest_data import SimpleQuestData, EnhancedQuestData
from ..config.llm_config import llm_config


def _normalize(text: str) -> str:
    """Normalize text for PDDL identifiers."""
    return text.replace(" ", "_").replace("-", "_").lower()


class QuestParser:
    def __init__(self):
        self.llm = ChatOllama(
            model=llm_config.PARSER_MODEL,
            temperature=llm_config.PARSER_TEMP,
            num_predict=llm_config.PARSER_MAX_TOKENS,
        )
        self.simple_parser = self.llm.with_structured_output(schema=SimpleQuestData)
        self.enhanced_parser = self.llm.with_structured_output(schema=EnhancedQuestData)

    def parse_simple(self, description: str) -> SimpleQuestData:
        """Parse a simple quest description using few-shot prompts."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract quest components from the description."),
            MessagesPlaceholder("examples"),
            ("human", "{input}"),
        ])
        formatted = prompt.invoke({"input": description, "examples": self._get_few_shot_examples()})
        return self.simple_parser.invoke(formatted)

    def _get_few_shot_examples(self) -> List:
        """Provide examples for the LLM simple parser."""
        return [
            HumanMessage(
                content=(
                    "The hero must reach the Dark Tower with the Crystal Sword and defeat the Dragon."
                    " The bridge is guarded by trolls."
                )
            ),
            AIMessage(
                content=(
                    "SimpleQuestData(\n"
                    "  destination='Dark Tower',\n"
                    "  required_item='Crystal Sword',\n"
                    "  success_condition='defeat the Dragon',\n"
                    "  obstacle='The bridge is guarded by trolls',\n"
                    "  obstacle_key='trolls'\n)"
                )
            ),
        ]

    def _select_depth(self, constraints: Dict[str, int] | None) -> int:
        """Randomly select a depth value within the given constraints."""
        if constraints:
            min_d = max(1, constraints.get("min", 1))
            max_d = max(min_d, constraints.get("max", min_d))
        else:
            min_d = max_d = 1
        return random.randint(min_d, max_d)

    def _select_branching(self, factor: Dict[str, int] | None) -> Tuple[int, int]:
        """Determine the min and max branching factor."""
        if factor:
            min_b = max(1, factor.get("min", 1))
            max_b = max(min_b, factor.get("max", min_b))
        else:
            min_b = max_b = 1
        return min_b, max_b

    def enhance_quest_data(
            self,
            simple_data: SimpleQuestData,
            branching_factor: Dict[str, int] | None = None,
            depth_constraints: Dict[str, int] | None = None,
    ) -> EnhancedQuestData:
        """Enhance parsed quest data: select dynamic depth and branching, build graph, preserve solvability."""
        # Select random depth
        depth = self._select_depth(depth_constraints)

        # Normalize destination and item keys
        dest_norm = _normalize(simple_data.destination)
        item_norm = _normalize(simple_data.required_item) if simple_data.required_item else None
        obs_key = _normalize(simple_data.obstacle_key) if simple_data.obstacle_key else None

        # Build main path locations
        theme = simple_data.destination + " " + (simple_data.obstacle or "")
        main_path_names = self._generate_fantasy_location_names(depth - 1, theme)
        locations = ["start"] + [_normalize(name) for name in main_path_names] + [dest_norm]

        # Items and obstacles
        items = [item_norm] if item_norm else []
        obstacles = {dest_norm: obs_key} if obs_key else {}

        # Select branching
        min_b, max_b = self._select_branching(branching_factor)

        # Build connections: main edges plus random branches
        connections: List[Tuple[str, str]] = []
        for idx, loc in enumerate(locations[:-1]):
            # Ensure one main edge
            next_loc = locations[idx + 1]
            connections.append((loc, next_loc))

            # Determine total outgoing edges from this node
            total_out = random.randint(min_b, max_b)
            extra = max(0, total_out - 1)

            # Generate side branches
            for j in range(extra):
                side = f"{loc}_branch{j + 1}"
                if side not in locations:
                    locations.append(side)
                connections.append((loc, side))

        # Compose goal conditions
        goal_conditions = [f"at hero {dest_norm}"]
        if obs_key:
            goal_conditions.append(f"defeated {obs_key}")

        return EnhancedQuestData(
            locations=locations,
            items=items,
            obstacles=obstacles,
            connections=connections,
            initial_location="start",
            goal_conditions=goal_conditions,
            branching_factor=branching_factor,
            depth_constraints={"min": 1 if not depth_constraints else depth_constraints.get("min"),
                               "max": depth},
        )

    def _generate_fantasy_location_names(self, count: int, theme_hint: str) -> list[str]:
        prompt = f"""
    Generate {count} unique fantasy location names that could exist in a world where:
    "{theme_hint}"

    Rules:
    - Names must fit the tone (e.g. mystical, eerie, ancient).
    - Avoid real-world objects or modern references.
    - Output as a JSON list of strings.
        """
        response = self.llm.invoke(prompt)
        import json, re
        match = re.search(r'\[.*\]', response.content, re.DOTALL)
        return json.loads(match.group(0)) if match else [f"loc_{i + 1}" for i in range(count)]


