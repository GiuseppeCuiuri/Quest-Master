from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from ..config.llm_config import llm_config
from ..models.quest_data import SimpleQuestData


def _format_goal(quest_data: SimpleQuestData) -> str:
    """Formatta il goal in testo leggibile"""
    goal = f"The hero must reach {quest_data.destination}"

    if quest_data.required_item:
        goal += f" with the {quest_data.required_item}"

    goal += f" and {quest_data.success_condition}"

    return goal


class NarrativeGenerator:
    def __init__(self):
        self.llm = OllamaLLM(
            model=llm_config.NARRATIVE_MODEL,
            temperature=llm_config.NARRATIVE_TEMP,
            num_predict=llm_config.NARRATIVE_MAX_TOKENS
        )

    def generate(self, quest_data: SimpleQuestData) -> str:
        """Genera una narrativa basata sui dati della quest"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a creative storyteller. Generate an engaging narrative "
                       "about overcoming obstacles and achieving goals in a fantasy quest."),
            ("user", "Goal: {goal}\nObstacle: {obstacle}\n\nGenerate a compelling story:")
        ])

        goal_text = _format_goal(quest_data)

        formatted = prompt.invoke({
            "goal": goal_text,
            "obstacle": quest_data.obstacle
        })

        return self.llm.invoke(formatted)

    