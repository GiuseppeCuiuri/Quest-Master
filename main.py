from __future__ import annotations
import json
from pathlib import Path
import argparse

from quest_master.parsers.lore_parser import LoreParser
from quest_master.pipeline import QuestPipeline
from quest_master.langgraph_workflow import run_flow


def legacy_run(lore_file: Path, output_dir: Path):
    parser = LoreParser()
    info = parser.extract_informations(lore_file)
    quest_description = info["quest_description"]
    branching_factor = info.get("branching_factor")
    depth_constraints = info.get("depth_constraints")

    pipeline = QuestPipeline(output_dir=output_dir)
    results = pipeline.process(
        quest_description,
        branching_factor=branching_factor,
        depth_constraints=depth_constraints,
    )
    print(json.dumps(results["validation"], indent=2))


def main():
    argp = argparse.ArgumentParser(description="QuestMaster runner")
    argp.add_argument("--lore", default="lore_document.txt", help="Lore document path")
    argp.add_argument("--output", default="examples/output", help="Output directory")
    argp.add_argument("--langgraph", action="store_true", help="Use LangGraph workflow")
    args = argp.parse_args()

    lore_path = Path(args.lore)
    out_dir = Path(args.output)

    if args.langgraph:
        result = run_flow(str(lore_path), str(out_dir))
        summary = {"status": "success" if result.success else "failure", "iterations": result.iterations}
        print(json.dumps(summary, indent=2))
    else:
        legacy_run(lore_path, out_dir)


if __name__ == "__main__":
    main()
