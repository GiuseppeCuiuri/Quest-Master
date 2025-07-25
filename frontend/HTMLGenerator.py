import os
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chat_models import ChatOpenAI
from quest_master.config.llm_config import llm_config

class HTMLGenerator:
    """
    Classe per generare file HTML/React a partire da metadata e narrative,
    usando DeepSeek Chimera via OpenRouter, formattare il risultato con Prettier,
    post-processare per conformità HTML5 e rimuovere eventuali script di live reload.
    """

    def __init__(
        self,
        model_name: str = llm_config.HTML_MODEL,
        temperature: float = llm_config.HTML_TEMP,
        max_tokens: int = llm_config.HTML_MAX_TOKENS,
    ):
        """Inizializza il modello DeepSeek Chimera via OpenAI-compatible API."""

        os.environ["OPENAI_API_KEY"] = llm_config.OPENROUTER_API_KEY  # <-- assicurati che ci sia
        self.llm = ChatOpenAI(
            model=model_name,  # es. "deepseek-chat", "deepseek-coder", "deepseek-chimera"
            temperature=temperature,
            max_tokens=max_tokens,
            base_url="https://openrouter.ai/api/v1",  # endpoint OpenRouter
        )

        # Prompt template con few-shot
        '''
        prompt_str = (
            "You are a developer assistant. Generate a complete HTML page with an interactive React interface"
            " for a fantasy quest game.\nUse the provided metadata and narrative to render a fixed narrative"
            " box and allow the user to navigate between available actions based on the current state.\n"
            "Display the current location, defeated enemies, and goal progress.\n"
            "Output only valid HTML with embedded React (via Babel).\n"
            "Metadata (JSON): {metadata_json}\n"
            "Narrative (text): {narrative_text}\n"
        )
        '''

        from langchain_core.prompts import PromptTemplate

        prompt_str = """
        You are a React/Babel HTML generator. Per ogni richiesta di seguito produci SOLO la pagina HTML, niente spiegazioni.

        {% raw %}
        ### EXAMPLE 1
        Metadata: {"initial_location":"start","connections":[],"obstacles":{}}
        Narrative: "Hello world"
        Output:
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8"/>
          <title>Example Quest</title>
          <script src="https://cdn.tailwindcss.com"></script>
          <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
          <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
          <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        </head>
        <body>
          <div id="root"></div>
          <script type="text/babel" data-presets="react">
            // framents supportati da Babel-standalone v7
            function App() {
              return <React.Fragment>
                <h1>Example Quest</h1>
                <p>Hello world</p>
              </React.Fragment>;
            }
            ReactDOM.render(<App/>, document.getElementById("root"));
          </script>
        </body>
        </html>

        ### EXAMPLE 2
        Metadata: {"initial_location":"home","connections":[["home","cave"]],"obstacles":{"cave":"goblin"}}
        Narrative: "Begin"
        Output:
        <!DOCTYPE html>
        <html>…stesso boilerplate di SCRIPT e PRESET…</html>
        {% endraw %}

        ### NOW YOU
        Metadata (JSON): {{ metadata_json }}
        Narrative (text): {{ narrative_text }}
        Output:
        """



        self.prompt = PromptTemplate(
            input_variables=["metadata_json", "narrative_text"],
            template=prompt_str,
            template_format="jinja2",
        )
        self.pipeline = self.prompt | self.llm

    def generate_html(self, metadata_json: str, narrative_text: str) -> str:
        """
        Genera il file HTML, lo formatta con Prettier se disponibile, e post-processa per:
         - rimuovere self-closing slashes su void tags
         - rimuovere eventuali script di live reload appesi dopo </html>
        """
        raw_html = self.pipeline.invoke({
            "metadata_json": metadata_json,
            "narrative_text": narrative_text,
        }).content

        html_content = raw_html
        if shutil.which("npx"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                tmp.write(raw_html.encode("utf-8"))
                tmp_path = tmp.name
            try:
                subprocess.run(["npx", "prettier", "--parser", "html", "--write", tmp_path], check=True)
                html_content = Path(tmp_path).read_text(encoding="utf-8")
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                print(f"[Warning] Prettier formatting skipped: {e}")
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
        else:
            print("[Warning] 'npx' non trovato: salto formattazione con Prettier.")

        void_tags = ['meta', 'link', 'img', 'br', 'hr', 'input', 'col', 'embed', 'param', 'source', 'track', 'wbr']
        for tag in void_tags:
            html_content = re.sub(rf"<({tag})([^>]*)\s+/>", r"<\1\2>", html_content, flags=re.IGNORECASE)

        lower = html_content.lower()
        end_idx = lower.rfind("</html>")
        if end_idx != -1:
            end_idx += len("</html>")
            html_content = html_content[:end_idx] + "\n"

        return html_content

if __name__ == "__main__":
    generator = HTMLGenerator()
    root = Path(__file__).resolve().parent.parent
    examples_path = root / "examples" / "output"
    meta_path = examples_path / "metadata.json"
    narr_path = examples_path / "narrative.txt"

    meta = meta_path.read_text(encoding="utf-8").strip()
    narr = narr_path.read_text(encoding="utf-8").strip()

    html = generator.generate_html(meta, narr)
    output_file = root / "frontend" / "index.html"
    output_file.write_text(html, encoding="utf-8")
    print(f"index.html generato in {output_file}")
