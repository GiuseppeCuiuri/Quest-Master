from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict

from langgraph.graph import StateGraph, END

from .parsers.lore_parser import LoreParser
from .parsers.quest_parser import QuestParser
from .generators.pddl_domain import PDDLDomainGenerator
from .generators.pddl_problem import PDDLProblemGenerator
from .generators.narrative import NarrativeGenerator
from .validators.pddl_validator import PDDLValidator
from .refinement.interactive_loop import InteractiveRefinementLoop
from frontend.HTMLGenerator import HTMLGenerator
from .models.quest_data import SimpleQuestData, EnhancedQuestData

@dataclass
class GraphState:
    """State shared across the LangGraph workflow."""
    lore_path: Path
    output_dir: Path = Path("output")
    quest_description: Optional[str] = None
    branching_factor: Optional[Dict[str, int]] = None
    depth_constraints: Optional[Dict[str, int]] = None
    simple_quest: Optional[SimpleQuestData] = None
    enhanced_quest: Optional[EnhancedQuestData] = None
    domain_pddl: Optional[str] = None
    problem_pddl: Optional[str] = None
    validation_error: Optional[str] = None
    iterations: int = 0
    narrative: Optional[str] = None
    html: Optional[str] = None
    success: bool = False

# ----- Node implementations -----

def lore_parser_node(state: GraphState) -> GraphState:
    parser = LoreParser()
    info = parser.extract_informations(state.lore_path)
    state.quest_description = info["quest_description"]
    state.branching_factor = info.get("branching_factor")
    state.depth_constraints = info.get("depth_constraints")
    print("[LoreParserNode] parsed lore")
    return state

def quest_parser_node(state: GraphState) -> GraphState:
    qp = QuestParser()
    simple = qp.parse_simple(state.quest_description)
    enhanced = qp.enhance_quest_data(
        simple,
        branching_factor=state.branching_factor,
        depth_constraints=state.depth_constraints,
    )
    state.simple_quest = simple
    state.enhanced_quest = enhanced
    print("[QuestParserNode] generated quest data")
    return state

def domain_generator_node(state: GraphState) -> GraphState:
    generator = PDDLDomainGenerator()
    state.domain_pddl = generator.generate(state.enhanced_quest)
    print("[DomainGeneratorNode] domain generated")
    return state

def problem_generator_node(state: GraphState) -> GraphState:
    generator = PDDLProblemGenerator(state.enhanced_quest)
    state.problem_pddl = generator.generate()
    print("[ProblemGeneratorNode] problem generated")
    return state

def pddl_validator_node(state: GraphState) -> GraphState:
    validator = PDDLValidator()
    ok, err, _ = validator.validate(state.domain_pddl, state.problem_pddl)
    state.success = ok
    state.validation_error = err
    print(f"[PDDLValidatorNode] valid={ok}")
    return state

def refinement_loop_node(state: GraphState) -> GraphState:
    loop = InteractiveRefinementLoop(PDDLValidator())
    result = loop.run(state.domain_pddl, state.problem_pddl, state.quest_description)
    state.domain_pddl = result["final_domain"]
    state.problem_pddl = result["final_problem"]
    state.iterations += result.get("iterations", 0)
    state.success = result.get("success", False)
    if state.success:
        state.validation_error = None
    else:
        state.validation_error = result.get("reason")
    print(f"[RefinementLoopNode] success={state.success} iterations={state.iterations}")
    return state

def narrative_generator_node(state: GraphState) -> GraphState:
    generator = NarrativeGenerator()
    state.narrative = generator.generate(state.simple_quest)
    print("[NarrativeGeneratorNode] narrative created")
    return state

def html_generator_node(state: GraphState) -> GraphState:
    generator = HTMLGenerator()
    metadata = {
        "quest_data": state.enhanced_quest.model_dump() if state.enhanced_quest else {},
        "branching_factor": state.branching_factor,
        "depth_constraints": state.depth_constraints,
    }
    state.html = generator.generate_html(json.dumps(metadata, indent=2), state.narrative or "")
    print("[HTMLGeneratorNode] HTML generated")
    return state

def file_writer_node(state: GraphState) -> GraphState:
    out = state.output_dir
    out.mkdir(parents=True, exist_ok=True)
    if state.domain_pddl:
        (out / "domain.pddl").write_text(state.domain_pddl, encoding="utf-8")
    if state.problem_pddl:
        (out / "problem.pddl").write_text(state.problem_pddl, encoding="utf-8")
    if state.narrative:
        (out / "narrative.txt").write_text(state.narrative, encoding="utf-8")
    if state.html:
        (out / "index.html").write_text(state.html, encoding="utf-8")
    meta = {
        "branching_factor": state.branching_factor,
        "depth_constraints": state.depth_constraints,
        "iterations": state.iterations,
        "status": "success" if state.success else "failure",
        "validation_error": state.validation_error,
    }
    (out / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("[FileWriterNode] files written")
    return state

# ----- Decision helpers -----

def validation_decider(state: GraphState) -> str:
    return "valid" if state.success else "invalid"

def refinement_decider(state: GraphState) -> str:
    return "retry" if state.success else "fail"

# ----- Flow builder -----

def build_quest_flow() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("lore_parser", lore_parser_node)
    graph.add_node("quest_parser", quest_parser_node)
    graph.add_node("domain_generator", domain_generator_node)
    graph.add_node("problem_generator", problem_generator_node)
    graph.add_node("pddl_validator", pddl_validator_node)
    graph.add_node("refinement_loop", refinement_loop_node)
    graph.add_node("narrative_generator", narrative_generator_node)
    graph.add_node("html_generator", html_generator_node)
    graph.add_node("file_writer", file_writer_node)
    graph.add_node("success", lambda s: s)
    graph.add_node("failure", lambda s: s)

    graph.set_entry_point("lore_parser")
    graph.add_edge("lore_parser", "quest_parser")
    graph.add_edge("quest_parser", "domain_generator")
    graph.add_edge("domain_generator", "problem_generator")
    graph.add_edge("problem_generator", "pddl_validator")
    graph.add_conditional_edges(
        "pddl_validator",
        validation_decider,
        {"valid": "narrative_generator", "invalid": "refinement_loop"},
    )
    graph.add_conditional_edges(
        "refinement_loop",
        refinement_decider,
        {"retry": "pddl_validator", "fail": "failure"},
    )
    graph.add_edge("narrative_generator", "html_generator")
    graph.add_edge("html_generator", "file_writer")
    graph.add_edge("file_writer", "success")

    return graph.compile()

def run_flow(lore_path: str, output_dir: str = "output") -> GraphState:
    flow = build_quest_flow()
    initial = GraphState(lore_path=Path(lore_path), output_dir=Path(output_dir))
    final_state: GraphState = flow.invoke(initial)  # type: ignore
    return final_state

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Quest Master LangGraph workflow")
    parser.add_argument("lore", help="Path to lore.txt")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    result = run_flow(args.lore, args.output)
    summary = {"status": "success" if result.success else "failure", "iterations": result.iterations}
    print(json.dumps(summary, indent=2))
