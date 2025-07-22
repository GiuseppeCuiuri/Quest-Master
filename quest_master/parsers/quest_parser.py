from typing import List
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

    def enhance_quest_data(self, simple_data: SimpleQuestData) -> EnhancedQuestData:
        """Arricchisce i dati per generare PDDL completo"""
        # Estrai locations
        locations = ["start", _normalize(simple_data.destination)]

        # Estrai items
        items = []
        if simple_data.required_item:
            items.append(_normalize(simple_data.required_item))

        # Crea obstacles mapping
        obstacles = {
            _normalize(simple_data.destination): _normalize(simple_data.obstacle_key)
        }

        # Definisci connections (semplice: start -> destination)
        connections = [("start", _normalize(simple_data.destination))]

        # Goal conditions
        goal_conditions = [
            f"at hero {_normalize(simple_data.destination)}",
            f"defeated {_normalize(simple_data.obstacle_key)}"
        ]

        return EnhancedQuestData(
            locations=locations,
            items=items,
            obstacles=obstacles,
            connections=connections,
            initial_location="start",
            goal_conditions=goal_conditions
        )

