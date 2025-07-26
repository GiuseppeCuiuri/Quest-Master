import os
import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from langchain_community.chat_models import ChatOpenAI
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
        ### EXAMPLE 0
        Metadata: {
          "quest_data": {
            "locations": [
              "start",
              "loc_1",
              "loc_2",
              "loc_3",
              "crystal_caverns",
              "start_branch1",
              "start_branch2",
              "start_branch3",
              "loc_1_branch1",
              "loc_2_branch1",
              "loc_3_branch1",
              "loc_3_branch2"
            ],
            "items": [],
            "obstacles": {
              "crystal_caverns": "golem"
            },
            "connections": [
              [
                "start",
                "loc_1"
              ],
              [
                "start",
                "start_branch1"
              ],
              [
                "start",
                "start_branch2"
              ],
              [
                "start",
                "start_branch3"
              ],
              [
                "loc_1",
                "loc_2"
              ],
              [
                "loc_1",
                "loc_1_branch1"
              ],
              [
                "loc_2",
                "loc_3"
              ],
              [
                "loc_2",
                "loc_2_branch1"
              ],
              [
                "loc_3",
                "crystal_caverns"
              ],
              [
                "loc_3",
                "loc_3_branch1"
              ],
              [
                "loc_3",
                "loc_3_branch2"
              ],
              [
                "loc_1",
                "start"
              ],
              [
                "start_branch1",
                "start"
              ],
              [
                "start_branch2",
                "start"
              ],
              [
                "start_branch3",
                "start"
              ],
              [
                "loc_2",
                "loc_1"
              ],
              [
                "loc_1_branch1",
                "loc_1"
              ],
              [
                "loc_3",
                "loc_2"
              ],
              [
                "loc_2_branch1",
                "loc_2"
              ],
              [
                "crystal_caverns",
                "loc_3"
              ],
              [
                "loc_3_branch1",
                "loc_3"
              ],
              [
                "loc_3_branch2",
                "loc_3"
              ]
            ],
            "initial_location": "start",
            "goal_conditions": [
              "at hero crystal_caverns",
              "defeated golem"
            ],
            "branching_factor": {
              "min": 2,
              "max": 4
            },
            "depth_constraints": {
              "min": 3,
              "max": 4
            }
          },
          "branching_factor": {
            "min": 2,
            "max": 4
          },
          "depth_constraints": {
            "min": 3,
            "max": 8
          },
          "iterations": 0,
          "status": "success",
          "validation_error": null
        }
        Narrative generated from: "The brave knight must journey to the Crystal Caverns carrying the Flame of Eternity and shatter the Dark Crystal. The entrance is sealed by an ancient golem that awakens when intruders approach."
        Output:
        

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Eira's Quest</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel" data-presets="react">
    const { useState } = React;

    function App() {
      const quest = {
        locations: [
          "start", "loc_1", "loc_2", "loc_3", "loc_4", "loc_5", "loc_6", "loc_7",
          "crystal_caverns", "start_branch1", "start_branch2", "start_branch3",
          "loc_1_branch1", "loc_1_branch2", "loc_1_branch3", "loc_2_branch1",
          "loc_3_branch1", "loc_4_branch1", "loc_5_branch1", "loc_5_branch2",
          "loc_6_branch1", "loc_6_branch2", "loc_6_branch3", "loc_7_branch1",
          "loc_7_branch2"
        ],
        obstacles: { "crystal_caverns": "golem" },
        connections: [
          ["start", "loc_1"], ["start", "start_branch1"], ["start", "start_branch2"], ["start", "start_branch3"],
          ["loc_1", "loc_2"], ["loc_1", "loc_1_branch1"], ["loc_1", "loc_1_branch2"], ["loc_1", "loc_1_branch3"],
          ["loc_2", "loc_3"], ["loc_2", "loc_2_branch1"], ["loc_3", "loc_4"], ["loc_3", "loc_3_branch1"],
          ["loc_4", "loc_5"], ["loc_4", "loc_4_branch1"], ["loc_5", "loc_6"], ["loc_5", "loc_5_branch1"], ["loc_5", "loc_5_branch2"],
          ["loc_6", "loc_7"], ["loc_6", "loc_6_branch1"], ["loc_6", "loc_6_branch2"], ["loc_6", "loc_6_branch3"],
          ["loc_7", "crystal_caverns"], ["loc_7", "loc_7_branch1"], ["loc_7", "loc_7_branch2"],
          // Reverse connections
          ["loc_1", "start"], ["start_branch1", "start"], ["start_branch2", "start"], ["start_branch3", "start"],
          ["loc_2", "loc_1"], ["loc_1_branch1", "loc_1"], ["loc_1_branch2", "loc_1"], ["loc_1_branch3", "loc_1"],
          ["loc_3", "loc_2"], ["loc_2_branch1", "loc_2"], ["loc_4", "loc_3"], ["loc_3_branch1", "loc_3"],
          ["loc_5", "loc_4"], ["loc_4_branch1", "loc_4"], ["loc_6", "loc_5"], ["loc_5_branch1", "loc_5"], ["loc_5_branch2", "loc_5"],
          ["loc_7", "loc_6"], ["loc_6_branch1", "loc_6"], ["loc_6_branch2", "loc_6"], ["loc_6_branch3", "loc_6"],
          ["crystal_caverns", "loc_7"], ["loc_7_branch1", "loc_7"], ["loc_7_branch2", "loc_7"]
        ],
        initial_location: "start"
      };

      const [currentLocation, setCurrentLocation] = useState(quest.initial_location);
      const [defeatedObstacles, setDefeatedObstacles] = useState([]);

      const getConnectedLocations = () => {
        return quest.connections
          .filter(([from]) => from === currentLocation)
          .map(([, to]) => to);
      };

      const handleMove = (location) => {
        setCurrentLocation(location);
      };

      const handleDefeat = () => {
        setDefeatedObstacles([...defeatedObstacles, "golem"]);
      };

      const isGoalAchieved = currentLocation === "crystal_caverns" && defeatedObstacles.includes("golem");

      return (
        <div className="p-8 max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">Eira's Quest</h1>

          <div className="mb-6 prose">
            <p>In the realm of Eridoria, where the sun dipped into the horizon and painted the sky with hues of crimson and gold, the village of Brindlemark lay nestled between the rolling hills. It was here that our hero, Eira Shadowglow, dwelled. A skilled warrior-mage with a heart full of determination and a spirit unbroken by adversity.</p>
            {/* ... truncated for brevity ... */}
            <p>The journey was far from over, but Eira's determination and unyielding spirit had overcome the first great obstacle on her path to shattering the Dark Crystal and bringing hope back to the people of Eridoria.</p>
          </div>

          <div className="mb-4 p-4 bg-gray-100 rounded">
            <h2 className="text-xl font-semibold mb-2">Current Location: {currentLocation.replace(/_/g, ' ')}</h2>

            {quest.obstacles[currentLocation] && !defeatedObstacles.includes(quest.obstacles[currentLocation]) ? (
              <div className="mt-4">
                <p className="mb-2">A massive stone golem blocks your path!</p>
                <button
                  onClick={handleDefeat}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  Defeat Golem
                </button>
              </div>
            ) : (
              <div>
                <h3 className="font-medium mb-2">Available Paths:</h3>
                <div className="flex flex-wrap gap-2">
                  {getConnectedLocations().map(location => (
                    <button
                      key={location}
                      onClick={() => handleMove(location)}
                      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                    >
                      Go to {location.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {isGoalAchieved && (
            <div className="mt-6 p-4 bg-green-100 rounded text-green-800">
              <h2 className="text-2xl font-bold">Victory!</h2>
              <p>You've reached the Crystal Caverns and defeated the golem!</p>
            </div>
          )}
        </div>
      );
    }

    ReactDOM.render(<App />, document.getElementById('root'));
  </script>
</body>
</html>
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
'''
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
'''