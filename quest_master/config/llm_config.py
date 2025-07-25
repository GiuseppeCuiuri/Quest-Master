from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configurazione centralizzata per i modelli LLM"""
    # Lore parser config
    LORE_PARSER_MODEL: str = "llama3:8b"
    LORE_PARSER_TEMP: float = 0.1
    LORE_PARSER_MAX_TOKENS: int = 512

    # Quest parser config
    PARSER_MODEL: str = "llama3:8b"
    PARSER_TEMP: float = 0.2
    PARSER_MAX_TOKENS: int = 256

    # Narrative config
    NARRATIVE_MODEL: str = "llama3:8b"
    NARRATIVE_TEMP: float = 0.8
    NARRATIVE_MAX_TOKENS: int = 1024

    # Reflection agent config
    REFLECTION_MODEL: str = "llama3:8b"
    REFLECTION_TEMP: float = 0.3
    REFLECTION_MAX_TOKENS: int = 256

    # Domain generator config
    DOMAIN_MODEL: str = "llama3:8b"
    DOMAIN_TEMP: float = 0.3
    DOMAIN_MAX_TOKENS: int = 1024


    HTML_MODEL = "tngtech/deepseek-r1t2-chimera:free"
    HTML_TEMP = 0.2
    HTML_MAX_TOKENS = 4096
    OPENROUTER_API_KEY: str = "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"  # Replace with your actual OpenRouter API key


# Singleton instance
llm_config = LLMConfig()