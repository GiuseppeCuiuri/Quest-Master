import json
from pathlib import Path
from quest_master.parsers.lore_parser import LoreParser


def test_extract_informations(monkeypatch, tmp_path):
    fake_response = {
        "response": "Some text before {\n  \"quest_description\": \"Find the relic\", \n  \"branching_factor\": {\"min\": 1, \"max\": 2},\n  \"depth_constraints\": {\"min\": 1, \"max\": 3}\n} trailing"
    }
    monkeypatch.setattr("ollama.generate", lambda **_: fake_response)
    file = tmp_path / "lore.txt"
    file.write_text("dummy")
    parser = LoreParser()
    data = parser.extract_informations(file)
    assert data["quest_description"] == "Find the relic"
    assert data["branching_factor"]["max"] == 2
