import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any
from .parsers.quest_parser import QuestParser
from .generators.pddl_domain import PDDLDomainGenerator
from .generators.pddl_problem import PDDLProblemGenerator
from .generators.narrative import NarrativeGenerator
from .validators.pddl_validator import PDDLValidator


class QuestPipeline:
    def __init__(self, output_dir: Path = Path("output")):
        self.parser = QuestParser()
        self.domain_generator = PDDLDomainGenerator()
        self.narrative_generator = NarrativeGenerator()
        self.validator = PDDLValidator()
        self.output_dir = output_dir

    def process(self, quest_description: str) -> Dict[str, Any]:
        """Processa una descrizione di quest e genera tutti gli output"""

        # 1. Parse della quest
        print("Parsing quest description...")
        simple_quest = self.parser.parse_simple(quest_description)
        enhanced_quest = self.parser.enhance_quest_data(simple_quest)

        # 2. Genera PDDL in memoria
        print("Generating PDDL domain and problem...")
        domain_pddl = self.domain_generator.generate(enhanced_quest)
        problem_generator = PDDLProblemGenerator(enhanced_quest)
        problem_pddl = problem_generator.generate()

        # 3. Salvataggio temporaneo per validazione
        print("Writing temporary PDDL files for validation...")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domain_path = tmpdir_path / "domain.pddl"
            problem_path = tmpdir_path / "problem.pddl"

            domain_path.write_text(domain_pddl, encoding='utf-8')
            problem_path.write_text(problem_pddl, encoding='utf-8')

            print("Validating PDDL...")
            is_valid, error_msg = self.validator.validate(
                domain_path.read_text(encoding='utf-8'),
                problem_path.read_text(encoding='utf-8')
            )

            # 4. Se validazione avvenuta, copia in output dir
            print(f"Saving validated PDDL files to {self.output_dir}...")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(domain_path, self.output_dir / "domain.pddl")
            shutil.copy(problem_path, self.output_dir / "problem.pddl")

        # 5. Genera narrativa
        print("Generating narrative...")
        narrative = self.narrative_generator.generate(simple_quest)

        # 6. Scrive narrativa e metadata
        (self.output_dir / "narrative.txt").write_text(narrative, encoding='utf-8')
        metadata = {
            "quest_data": enhanced_quest.model_dump(),
            "validation": {
                "is_valid": is_valid,
                "error": error_msg
            }
        }
        (self.output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding='utf-8')

        return {
            "quest_data": enhanced_quest.model_dump(),
            "domain_pddl": domain_pddl,
            "problem_pddl": problem_pddl,
            "narrative": narrative,
            "validation": {
                "is_valid": is_valid,
                "error": error_msg
            }
        }
