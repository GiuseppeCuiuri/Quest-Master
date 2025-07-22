import ollama
from typing import Dict, List, Tuple, Optional
from ..config.llm_config import llm_config
from ..validators.pddl_validator import PDDLValidator


class ReflectionAgent:
    """Agent che analizza errori PDDL e propone refinements interattivi"""

    def __init__(self, validator: PDDLValidator):
        self.validator = validator
        self.model = llm_config.REFLECTION_MODEL
        self.temperature = llm_config.REFLECTION_TEMP
        self.max_tokens = llm_config.REFLECTION_MAX_TOKENS

    def analyze_and_refine(self, domain_content: str, problem_content: str,
                           validation_error: str, quest_description: str) -> Dict:
        """
        Analizza l'errore di validazione e propone refinements

        Returns:
            Dict con 'analysis', 'suggestions', 'refined_domain', 'refined_problem'
        """
        # 1. Analizza l'errore
        analysis = self._analyze_error(domain_content, problem_content,
                                       validation_error, quest_description)

        # 2. Genera suggestions
        suggestions = self._generate_suggestions(analysis, domain_content,
                                                 problem_content, quest_description)

        # 3. Applica refinements automatici
        refined_domain, refined_problem = self._apply_refinements(
            domain_content, problem_content, suggestions, quest_description
        )

        return {
            'analysis': analysis,
            'suggestions': suggestions,
            'refined_domain': refined_domain,
            'refined_problem': refined_problem
        }

    def _analyze_error(self, domain_content: str, problem_content: str,
                       validation_error: str, quest_description: str) -> str:
        """Analizza l'errore di validazione usando LLM"""

        prompt = f"""
Analyze this PDDL validation error and identify the root cause:

QUEST DESCRIPTION:
{quest_description}

VALIDATION ERROR:
{validation_error}

DOMAIN:
{domain_content}

PROBLEM:
{problem_content}

Identify:
1. What specific PDDL element is causing the error
2. Why this error prevents finding a solution
3. What narrative elements are missing or inconsistent

Provide a clear analysis in 3-4 sentences.
"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                'temperature': self.temperature,
                'num_predict': self.max_tokens
            }
        )

        return response['response'].strip()

    def _generate_suggestions(self, analysis: str, domain_content: str,
                              problem_content: str, quest_description: str) -> List[str]:
        """Genera suggestions specifiche per fix"""

        prompt = f"""
Based on this analysis, provide 3-4 specific suggestions to fix the PDDL:

ANALYSIS:
{analysis}

QUEST DESCRIPTION:
{quest_description}

Each suggestion should be:
- Specific and actionable
- Focused on PDDL structure (actions, predicates, objects)
- Aligned with the quest narrative

Format as numbered list:
1. [suggestion]
2. [suggestion]
etc.
"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                'temperature': self.temperature,
                'num_predict': self.max_tokens
            }
        )

        # Parse suggestions into list
        suggestions = []
        lines = response['response'].strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                suggestion = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                suggestions.append(suggestion)

        return suggestions

    def _apply_refinements(self, domain_content: str, problem_content: str,
                           suggestions: List[str], quest_description: str) -> Tuple[str, str]:
        """Applica i refinements automaticamente"""

        prompt = f"""
Apply these refinements to fix the PDDL files:

QUEST DESCRIPTION:
{quest_description}

SUGGESTIONS TO APPLY:
{chr(10).join(f"- {s}" for s in suggestions)}

ORIGINAL DOMAIN:
{domain_content}

ORIGINAL PROBLEM:
{problem_content}

Generate the corrected PDDL files. Return in this exact format:

REFINED DOMAIN:
[domain content]

REFINED PROBLEM:
[problem content]
"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                'temperature': 0.1,  # Low temperature for precision
                'num_predict': 1500
            }
        )

        # Parse refined files
        content = response['response']

        try:
            domain_start = content.find("REFINED DOMAIN:")
            problem_start = content.find("REFINED PROBLEM:")

            if domain_start == -1 or problem_start == -1:
                raise ValueError("Could not find refined sections in response")

            refined_domain = content[domain_start + len("REFINED DOMAIN:"):problem_start].strip()
            refined_problem = content[problem_start + len("REFINED PROBLEM:"):].strip()

            return refined_domain, refined_problem

        except Exception as e:
            print(f"Error parsing refined PDDL: {e}")
            return domain_content, problem_content  # Return originals as fallback

    def chat_with_action(self, user_input: str, analysis: str, suggestions: list) -> tuple[str, str | None]:
        """
        Chat libera con l'utente che interpreta un'azione opzionale.

        Args:
            user_input: testo libero dell'utente
            analysis: analisi corrente del problema PDDL
            suggestions: lista di fix suggeriti

        Returns:
            (response_text, action) dove action è 'apply', 'manual', 'skip' oppure None
        """
        prompt = f"""
Sei un assistente esperto di PDDL. Analizza il seguente contesto e rispondi all'utente.

CONTESTO:
Analisi errore:
{analysis}

Suggerimenti:
{chr(10).join(f"- {s}" for s in suggestions)}

DOMANDA UTENTE:
{user_input}

Istruzioni per la risposta:
- Fornisci una risposta chiara e utile.
- Se l'utente chiede di applicare i fix, scrivi alla fine "[ACTION: apply]"
- Se l'utente chiede di modificare manualmente, scrivi alla fine "[ACTION: manual]"
- Se l'utente vuole saltare l'iterazione, scrivi alla fine "[ACTION: skip]"
- Se non vuole terminare il processo, non scrivere tag ACTION.

Rispondi ora:
"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                'temperature': 0.7,
                'num_predict': 1000
            }
        )

        text = response['response'].strip()

        action = None
        # Cerca tag ACTION nel testo
        import re
        match = re.search(r'\[ACTION:\s*(apply|manual|skip)\]', text, re.IGNORECASE)
        if match:
            action = match.group(1).lower()
            # Rimuovi il tag dal testo prima di restituire
            text = re.sub(r'\[ACTION:\s*(apply|manual|skip)\]', '', text, flags=re.IGNORECASE).strip()

        return text, action