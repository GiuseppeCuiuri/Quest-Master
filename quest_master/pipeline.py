import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from .parsers.quest_parser import QuestParser
from .generators.pddl_domain import PDDLDomainGenerator
from .generators.pddl_problem import PDDLProblemGenerator
from .generators.narrative import NarrativeGenerator
from .validators.pddl_validator import PDDLValidator
from .refinement.interactive_loop import InteractiveRefinementLoop


class QuestPipeline:
    def __init__(self, output_dir: Path = Path("output")):
        self.parser = QuestParser()
        self.domain_generator = PDDLDomainGenerator()
        self.narrative_generator = NarrativeGenerator()
        self.validator = PDDLValidator()
        self.output_dir = output_dir

    def process(
        self,
        quest_description: str,
        branching_factor: Optional[Dict[str, int]] = None,
        depth_constraints: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """Process an input quest and generate all outputs."""

        print("Parsing quest description...")
        simple_quest = self.parser.parse_simple(quest_description)
        enhanced_quest = self.parser.enhance_quest_data(
            simple_quest,
            branching_factor=branching_factor,
            depth_constraints=depth_constraints,
        )

        print("Generating PDDL domain and problem...")
        domain_pddl = self.domain_generator.generate(enhanced_quest)
        problem_pddl = PDDLProblemGenerator(enhanced_quest).generate()

        print("Writing temporary PDDL files for validation...")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            domain_path = tmpdir_path / "domain.pddl"
            problem_path = tmpdir_path / "problem.pddl"
            domain_path.write_text(domain_pddl, encoding="utf-8")
            problem_path.write_text(problem_pddl, encoding="utf-8")

            print("Validating PDDL...")
            is_valid, error_msg, plan_path = self.validator.validate(
                domain_path.read_text(encoding="utf-8"),
                problem_path.read_text(encoding="utf-8"),
            )

            if not is_valid:
                print("Validation failed, starting refinement loop...")
                loop = InteractiveRefinementLoop(self.validator)
                result = loop.run(domain_pddl, problem_pddl, quest_description)
                domain_pddl = result["final_domain"]
                problem_pddl = result["final_problem"]
                is_valid, error_msg, plan_path = self.validator.validate(domain_pddl, problem_pddl)

                domain_path.write_text(domain_pddl, encoding="utf-8")
                problem_path.write_text(problem_pddl, encoding="utf-8")

            print(f"Saving validated PDDL files to {self.output_dir}...")
            self.output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(domain_path, self.output_dir / "domain.pddl")
            shutil.copy(problem_path, self.output_dir / "problem.pddl")

        print("Generating narrative...")
        narrative = self.narrative_generator.generate(simple_quest)
        (self.output_dir / "narrative.txt").write_text(narrative, encoding="utf-8")

        lore_content = (
            f"Quest Description:\n{quest_description}\n\n"
            f"Branching Factor: {branching_factor}\n"
            f"Depth Constraints: {depth_constraints}\n"
        )
        (self.output_dir / "lore.txt").write_text(lore_content, encoding="utf-8")

        metadata = {
            "quest_data": enhanced_quest.model_dump(),
            "branching_factor": branching_factor,
            "depth_constraints": depth_constraints,
            "validation": {"is_valid": is_valid, "error": error_msg},
        }
        (self.output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return {
            "quest_data": enhanced_quest.model_dump(),
            "branching_factor": branching_factor,
            "depth_constraints": depth_constraints,
            "domain_pddl": domain_pddl,
            "problem_pddl": problem_pddl,
            "narrative": narrative,
            "validation": {"is_valid": is_valid, "error": error_msg},
        }
