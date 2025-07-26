from quest_master.langgraph_workflow import run_flow
from pathlib import Path
import json

if __name__ == "__main__":
    # Percorso predefinito al file lore e alla cartella di output
    lore_path = "lore_document.txt"
    output_path = Path("examples/output")

    # Esegui il flusso LangGraph
    result = run_flow("lore_document.txt", "examples/output")

    # Stampa riepilogo esecuzione
    print("✅ LangGraph flow completed.")

    # Gestisci sia il caso di oggetto GraphState che di dizionario
    if hasattr(result, 'success'):
        # result è un oggetto GraphState
        success = result.success
        iterations = result.iterations
        result_dict = result.__dict__
    else:
        # result è un dizionario
        success = result.get('success', False)
        iterations = result.get('iterations', 0)
        result_dict = result

    print("Status:", "SUCCESS" if success else "FAILURE")
    print("Iterations:", iterations)

    # (Facoltativo) Salva lo stato finale completo per debug
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "final_state.json", "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2, default=str)
