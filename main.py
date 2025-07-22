from pathlib import Path

from quest_master.parsers.lore_parser import LoreParser
from quest_master.pipeline import QuestPipeline

def main():
    # Estrazione della quest description dal lore document
    lore_file = Path("../PythonProject1/lore_document.txt")

    parser = LoreParser()
    quest_description = parser.extract_informations(lore_file)["quest_description"]

    print("=== Quest Description Extracted ===")
    print(quest_description)

    # Directory dove salvare gli output
    output_dir = Path("../PythonProject1/examples/output")

    # Crea pipeline
    pipeline = QuestPipeline(output_dir=output_dir)

    # Processa la quest e salva gli output automaticamente
    results = pipeline.process(quest_description)

    # Stampa risultati
    print("\n=== Quest Processing Complete ===")
    print(f"Valid PDDL: {results['validation']['is_valid']}")
    if not results['validation']['is_valid']:
        print(f"Error: {results['validation']['error']}")

    print(f"\nFiles saved to: {output_dir}")

if __name__ == "__main__":
    main()
