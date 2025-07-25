import os
import subprocess
import tempfile
import shutil
import re
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from quest_master.config.llm_config import llm_config

class HTMLGenerator:
    """
    Classe per generare file HTML/React a partire da metadata e narrative,
    usando Llama 3 8B in locale con LangChain, formattare il risultato con Prettier,
    post-processare per conformità HTML5 e rimuovere eventuali script di live reload.
    """
    def __init__(self,
                 model_name: llm_config.HTML_MODEL,
                 temperature: llm_config.HTML_TEMP,
                 max_tokens: llm_config.HTML_MAX_TOKENS):
        # Inizializza il modello Llama 3:8B locale via OllamaLLM
        self.llm = OllamaLLM(model=model_name, temperature=temperature, num_predict=max_tokens)

        # Few-shot example di index.html minimale (HTML5 void tag syntax)
        example_html = ("""<!DOCTYPE html>
<html lang=\"en\">"""
"""
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>QuestMaster Game</title>
    <link href=\"styles.css\" rel=\"stylesheet\">
</head>
<body>
    <div id=\"root\"></div>
    <script src=\"app.js\"></script>
</body>
</html>""")

        # Prompt template con few-shot example
        prompt_template = (
            "You are an assistant that generates a complete, valid HTML5 file (or React entrypoint) based on provided metadata and narrative. "
            "Always output well-formed HTML5, using HTML5 void tag syntax without self-closing slashes, and include DOCTYPE and required tags.\n"
            f"Example index.html:\n```html\n{example_html}\n```\n"
            "Now, generate the HTML for this quest:\n"
            "Metadata (JSON): {metadata_json}\n"
            "Narrative (text): {narrative_text}\n"
            "Provide only the HTML content without additional commentary."
        )

        self.prompt = PromptTemplate(
            input_variables=["metadata_json", "narrative_text"],
            template=prompt_template
        )
        # Costruisci la pipeline prompt → LLM
        self.pipeline = self.prompt | self.llm

    def generate_html(self, metadata_json: str, narrative_text: str) -> str:
        """
        Genera il file HTML, lo formatta con Prettier se disponibile, e post-processa per:
         - rimuovere self-closing slashes su void tags
         - rimuovere eventuali script di live reload appesi dopo </html>

        Returns:
            HTML pulito come stringa.
        """
        raw_html = self.pipeline.invoke({
            "metadata_json": metadata_json,
            "narrative_text": narrative_text
        })

        # Format con Prettier se disponibile
        html_content = raw_html
        if shutil.which("npx"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                tmp.write(raw_html.encode('utf-8'))
                tmp_path = tmp.name
            try:
                try:
                    subprocess.run(["npx", "prettier", "--parser", "html", "--write", tmp_path], check=True)
                    with open(tmp_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                except FileNotFoundError:
                    print("[Warning] Comando 'npx' non trovato durante run: salto formattazione.")
                except subprocess.CalledProcessError as e:
                    print(f"[Warning] Prettier ha restituito un errore ({e.returncode}), uso HTML non formattato.")
            finally:
                try: os.remove(tmp_path)
                except OSError: pass
        else:
            print("[Warning] 'npx' non trovato: salto formattazione con Prettier.")

        # Rimuovi self-closing slashes da void elements
        void_tags = ['meta', 'link', 'img', 'br', 'hr', 'input', 'col', 'embed', 'param', 'source', 'track', 'wbr']
        for tag in void_tags:
            html_content = re.sub(rf"<({tag})([^>]*)\s+/>", r"<\1\2>", html_content, flags=re.IGNORECASE)

        # Taglia via eventuali script live reload dopo </html>
        lower = html_content.lower()
        end_idx = lower.rfind("</html>")
        if end_idx != -1:
            end_idx += len("</html>")
            html_content = html_content[:end_idx] + "\n"

        return html_content

if __name__ == "__main__":
    generator = HTMLGenerator()
    base_path = os.path.join('..', 'examples', 'output')
    meta_path = os.path.join(base_path, 'metadata.json')
    narr_path = os.path.join(base_path, 'narrative.txt')
    with open(meta_path, 'r', encoding='utf-8') as m, open(narr_path, 'r', encoding='utf-8') as n:
        meta = m.read().strip()
        narr = n.read().strip()
    html = generator.generate_html(meta, narr)
    os.makedirs(base_path, exist_ok=True)
    output_file = os.path.join(base_path, 'index.html')
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(html)
    print(f"index.html generato in {output_file}")
