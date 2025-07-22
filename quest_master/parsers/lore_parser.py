import json

import ollama
from pathlib import Path
from ..config.llm_config import llm_config


class LoreParser:
    def __init__(self):
        self.model = llm_config.LORE_PARSER_MODEL
        self.temperature = llm_config.LORE_PARSER_TEMP
        self.max_tokens = llm_config.LORE_PARSER_MAX_TOKENS

    def extract_informations(self, file_path: Path) -> str:
        """Estrae la quest description dal lore document"""
        content = file_path.read_text(encoding='utf-8')

        prompt = f"""
        From this lore document, extract the following fields:
        - The quest description (a paragraph summarizing the goal, initial state, obstacles, and story context).
        - The branching factor (minimum and maximum number of actions available at each narrative state).
        - The depth constraints (minimum and maximum number of steps required to reach the goal).

        Document:
        {content}

        Return a JSON string object with the following structure:

        {{
          "quest_description": "<a textual description of the quest>",
          "branching_factor": {{
            "min": <minimum number of actions>,
            "max": <maximum number of actions>
          }},
          "depth_constraints": {{
            "min": <minimum number of steps>,
            "max": <maximum number of steps>
          }}
        }}
        """

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                'temperature': self.temperature,
                'num_predict': self.max_tokens
            }
        )

        result = response['response'].strip()

        start_index = result.find('{')
        result_json = result[start_index:].strip()

        return json.loads(result_json)