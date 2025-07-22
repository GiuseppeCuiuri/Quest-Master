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
    NARRATIVE_MAX_TOKENS: int = 512

    # Reflection agent config
    REFLECTION_MODEL: str = "llama3:8b"
    REFLECTION_TEMP: float = 0.3
    REFLECTION_MAX_TOKENS: int = 256

    # Domain generator config
    DOMAIN_MODEL: str = "llama3:8b"
    DOMAIN_TEMP: float = 0.3
    DOMAIN_MAX_TOKENS: int = 1024


# Singleton instance
llm_config = LLMConfig()