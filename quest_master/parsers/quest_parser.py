from typing import List, Dict
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from ..models.quest_data import SimpleQuestData, EnhancedQuestData
from ..config.llm_config import llm_config


def _normalize(text: str) -> str:
    """Normalizza il testo per PDDL"""
    return text.replace(' ', '_').replace('-', '_').lower()


class QuestParser:
    def __init__(self):
        self.llm = ChatOllama(
            model=llm_config.PARSER_MODEL,
            temperature=llm_config.PARSER_TEMP,
            num_predict=llm_config.PARSER_MAX_TOKENS
        )
        self.simple_parser = self.llm.with_structured_output(schema=SimpleQuestData)
        self.enhanced_parser = self.llm.with_structured_output(schema=EnhancedQuestData)

    def parse_simple(self, description: str) -> SimpleQuestData:
        """Parsing base della quest"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract quest components from the description."),
            MessagesPlaceholder("examples"),
            ("human", "{input}")
        ])

        formatted = prompt.invoke({
            "input": description,
            "examples": self._get_few_shot_examples()
        })

        return self.simple_parser.invoke(formatted)

    def _get_few_shot_examples(self) -> List:
        """Esempi per il parsing"""
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
            ))
        ]

    def enhance_quest_data(
        self,
        simple_data: SimpleQuestData,
        branching_factor: Dict[str, int] | None = None,
        depth_constraints: Dict[str, int] | None = None,
    ) -> EnhancedQuestData:
        """Arricchisce i dati per generare PDDL completo applicando i limiti"""

        # Calcola profondità minima richiesta
        depth = 1
        if depth_constraints and depth_constraints.get("min", 1) > 1:
            depth = depth_constraints["min"]
        # Calcola la profondità desiderata nel range [min, max]
        min_depth = 1
        max_depth = 1
        if depth_constraints:
            min_depth = max(1, depth_constraints.get("min", 1))
            max_depth = max(min_depth, depth_constraints.get("max", min_depth))
        depth = max_depth

        dest_norm = _normalize(simple_data.destination)

        # Genera percorso lineare con il numero di passi richiesto
        locations = ["start"]
        for i in range(1, depth):
            locations.append(f"loc_{i}")
        locations.append(dest_norm)

        # Estrai items
        items = []
        if simple_data.required_item:
            items.append(_normalize(simple_data.required_item))

        # Crea obstacles mapping
        obstacles = {
            dest_norm: _normalize(simple_data.obstacle_key)
        }

        # Definisci connections secondo la profondità calcolata
        connections = []
        for i in range(len(locations) - 1):
            current = locations[i]
            next_loc = locations[i + 1]
            connections.append((current, next_loc))

            # Crea rami aggiuntivi se richiesto
            if branching_factor and branching_factor.get("min", 1) > 1:
                extra = branching_factor["min"] - 1
            # Gestione branching factor
            if branching_factor:
                min_b = max(1, branching_factor.get("min", 1))
                max_b = max(min_b, branching_factor.get("max", min_b))

                base_actions = 1  # collegamento principale
                desired_actions = min_b
                if desired_actions > max_b:
                    desired_actions = max_b
                extra = max(0, min(desired_actions, max_b) - base_actions)
                for j in range(extra):
                    side_loc = f"{current}_b{j+1}"
                    locations.append(side_loc)
                    connections.append((current, side_loc))

        # Assicura che la destinazione sia l'ultima nella lista delle location
        locations = [loc for loc in locations if loc != dest_norm] + [dest_norm]

        # Goal conditions
        goal_conditions = [
            f"at hero {dest_norm}",
            f"defeated {_normalize(simple_data.obstacle_key)}"
        ]

        return EnhancedQuestData(
            locations=locations,
            items=items,
            obstacles=obstacles,
            connections=connections,
            initial_location="start",
            goal_conditions=goal_conditions,
            branching_factor=branching_factor,
            depth_constraints=depth_constraints
        )

