from typing import List, Dict
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from ..models.quest_data import SimpleQuestData, EnhancedQuestData
from ..config.llm_config import llm_config


def _normalize(text: str) -> str:
    """Normalize text for PDDL."""
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
        """Parse a simple quest description."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract quest components from the description."),
            MessagesPlaceholder("examples"),
            ("human", "{input}"),
        ])
        formatted = prompt.invoke({"input": description, "examples": self._get_few_shot_examples()})
        return self.simple_parser.invoke(formatted)

    def _get_few_shot_examples(self) -> List:
        """Examples for parsing."""
        return [
            HumanMessage(
                content="The hero must reach the Dark Tower with the Crystal Sword and defeat the Dragon. The bridge is guarded by trolls."),
            AIMessage(content=(
                "SimpleQuestData(\n"
                "  destination='Dark Tower',\n"
                "  required_item='Crystal Sword',\n"
                "  success_condition='defeat the Dragon',\n"
                "  obstacle='The bridge is guarded by trolls',\n"
                "  obstacle_key='trolls'\n)"
            )),
        ]

    def _compute_depth(self, constraints: Dict[str, int] | None) -> int:
        min_d = max(1, constraints.get("min", 1)) if constraints else 1
        max_d = max(min_d, constraints.get("max", min_d)) if constraints else min_d
        return max_d

    def _compute_branching(self, factor: Dict[str, int] | None) -> tuple[int, int]:
        min_b = max(1, factor.get("min", 1)) if factor else 1
        max_b = max(min_b, factor.get("max", min_b)) if factor else min_b
        return min_b, max_b

    def enhance_quest_data(
        self,
        simple_data: SimpleQuestData,
        branching_factor: Dict[str, int] | None = None,
        depth_constraints: Dict[str, int] | None = None,
    ) -> EnhancedQuestData:
        """Enhance parsed data with branching and depth limits."""
        depth = self._compute_depth(depth_constraints)
        dest_norm = _normalize(simple_data.destination)

        locations = ["start"] + [f"loc_{i}" for i in range(1, depth)] + [dest_norm]

        items = []
        if simple_data.required_item:
            items.append(_normalize(simple_data.required_item))

        obstacles = {dest_norm: _normalize(simple_data.obstacle_key)}

        connections = []
        min_b, max_b = self._compute_branching(branching_factor)
        for i in range(len(locations) - 1):
            current = locations[i]
            next_loc = locations[i + 1]
            connections.append((current, next_loc))
            extra = max(0, min(min_b, max_b) - 1)
            for j in range(extra):
                side_loc = f"{current}_b{j+1}"
                if side_loc not in locations:
                    locations.append(side_loc)
                connections.append((current, side_loc))

        locations = [loc for loc in locations if loc != dest_norm] + [dest_norm]

        goal_conditions = [
            f"at hero {dest_norm}",
            f"defeated {_normalize(simple_data.obstacle_key)}",
        ]

        return EnhancedQuestData(
            locations=locations,
            items=items,
            obstacles=obstacles,
            connections=connections,
            initial_location="start",
            goal_conditions=goal_conditions,
            branching_factor=branching_factor,
            depth_constraints=depth_constraints,
        )
