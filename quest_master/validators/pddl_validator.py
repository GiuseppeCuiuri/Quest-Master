import re
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional


def extract_error_block(output: str) -> str:
    """Estrae il blocco di errore principale da stdout/stderr di Fast Downward"""
    if not output.strip():
        return "Unknown error (empty output)"

    lines = output.split('\n')

    # Prima cerca errori specifici più informativi
    specific_patterns = [
        r"Undefined object\s*Got:\s*(\w+)",  # Errore oggetto non definito
        r"Undefined predicate\s*Got:\s*(\w+)",  # Predicato non definito
        r"Syntax error.*",  # Errori di sintassi
        r"Parse error.*",  # Errori di parsing
    ]

    # Cerca errori specifici e cattura il contesto
    for i, line in enumerate(lines):
        for pattern in specific_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Cattura la riga dell'errore e quelle precedenti/successive per contesto
                start_idx = max(0, i - 1)
                end_idx = min(len(lines), i + 3)
                context_lines = []

                # Aggiungi righe con contenuto significativo
                for j in range(start_idx, end_idx):
                    line_content = lines[j].strip()
                    if line_content and not line_content.startswith('INFO'):
                        context_lines.append(line_content)

                if context_lines:
                    return '\n'.join(context_lines)
                else:
                    return line.strip()

    # Se non trova errori specifici, cerca "translate exit code" e trova l'errore correlato
    if re.search(r'translate exit code: (?!0\b)\d+', output):
        # Cerca indietro per trovare l'errore che ha causato l'exit code
        for i in reversed(range(len(lines))):
            line = lines[i].strip()
            # Cerca righe che sembrano errori ma non sono solo INFO
            if (line and
                    not line.startswith('INFO') and
                    not line.startswith('translate exit code') and
                    not line.startswith('Driver aborting') and
                    ('error' in line.lower() or 'undefined' in line.lower() or 'got:' in line.lower())):

                # Trova il contesto attorno a questa riga
                start_idx = max(0, i - 1)
                end_idx = min(len(lines), i + 3)
                context_lines = []

                for j in range(start_idx, end_idx):
                    context_line = lines[j].strip()
                    if (context_line and
                            not context_line.startswith('INFO') and
                            not context_line.startswith('translator')):
                        context_lines.append(context_line)

                if context_lines:
                    return '\n'.join(context_lines)

        # Se non trova niente di specifico, restituisce messaggio generico
        return "Translation failed - check PDDL syntax and object definitions"

    # Cerca altri tipi di errori
    error_keywords = ['error', 'failed', 'undefined', 'syntax']
    for line in lines:
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in error_keywords) and not line_lower.startswith('info'):
            return line.strip()

    # In ultima istanza, restituisce tutto l'output
    return output.strip()


class PDDLValidator:
    def __init__(self, fd_path: str = None, wsl_distro: str = "Ubuntu", wsl_user: str = "giuseppe"):
        """
        Inizializza il validatore Fast Downward per WSL

        Args:
            fd_path: Path a Fast Downward in WSL (es. /home/user/downward)
            wsl_distro: Nome della distribuzione WSL (es. Ubuntu-22.04)
            wsl_user: Nome utente WSL (es. giuseppe)
        """
        self.wsl_distro = wsl_distro
        self.wsl_user = wsl_user

        if fd_path:
            self.fd_path = fd_path
        else:
            self.fd_path = f"/home/{wsl_user}/downward"

        self._check_wsl()
        print(f"Fast Downward WSL path: {self.fd_path}")

    # Modifica nelle chiamate a WSL
    def _run_wsl_command(self, command: str):
        """Esegue un comando in WSL con distro e utente specificati"""
        return subprocess.run(
            ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", command],
            capture_output=True,
            text=True
        )

    def _windows_to_wsl_path(self, windows_path: str) -> str:
        """Converte un path Windows in path WSL"""
        path = Path(windows_path).absolute()
        path_str = str(path).replace('\\', '/')
        if len(path_str) > 1 and path_str[1] == ':':
            drive = path_str[0].lower()
            path_str = f"/mnt/{drive}{path_str[2:]}"
        return path_str

    def _check_wsl(self):
        """Verifica che WSL sia installato e funzionante"""
        try:
            result = subprocess.run(
                ["wsl", "--list"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception("WSL not properly installed or configured")
        except FileNotFoundError:
            raise Exception("WSL not found. Please install WSL on Windows 10/11")

    def validate(self, domain_content: str, problem_content: str) -> Tuple[bool, Optional[str]]:
        """Valida domain e problem PDDL usando Fast Downward in WSL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            domain_file = Path(tmpdir) / "domain.pddl"
            problem_file = Path(tmpdir) / "problem.pddl"
            domain_file.write_text(domain_content, encoding='utf-8')
            problem_file.write_text(problem_content, encoding='utf-8')

            wsl_domain = self._windows_to_wsl_path(str(domain_file))
            wsl_problem = self._windows_to_wsl_path(str(problem_file))

            try:
                wsl_command = (
                    f"cd {self.fd_path} && "
                    f"python3 fast-downward.py {wsl_domain} {wsl_problem} "
                    f"--evaluator 'eval=hmax()' --search 'lazy_greedy([eval])'"
                )

                result = subprocess.run(
                    ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", wsl_command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Combina stdout e stderr per l'analisi completa
                full_output = result.stdout + "\n" + result.stderr

                print("=== Fast Downward output ===")
                print(full_output)
                print("============================")

                if result.returncode == 0:
                    if "Solution found!" in full_output:
                        return True, None
                    elif "Search stopped without finding a solution." in full_output:
                        return False, "No solution found - goal might be unreachable"
                    elif "Completely explored state space -- no solution!" in full_output:
                        return False, "Goal is provably unreachable from initial state"
                    else:
                        return False, "Unknown outcome despite successful execution"
                else:
                    # Usa extract_error_block sull'output completo per trovare l'errore
                    error_msg = extract_error_block(full_output)
                    return False, f"Fast Downward error:\n{error_msg}"

            except subprocess.TimeoutExpired:
                return False, "Validation timeout - problem might be too complex"
            except FileNotFoundError:
                return False, "WSL command not found - ensure WSL is properly installed"
            except Exception as e:
                return False, f"Validation error: {str(e)}"

    def check_fast_downward_installation(self) -> bool:
        """Verifica che Fast Downward sia installato correttamente in WSL"""
        try:
            check_cmd = f"test -d {self.fd_path} && echo 'EXISTS'"
            result = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", check_cmd],
                capture_output=True,
                text=True
            )

            if "EXISTS" not in result.stdout:
                print(f"Fast Downward not found at {self.fd_path}")
                print("To install Fast Downward in WSL:")
                print("1. Open WSL terminal")
                print("2. Run: cd ~")
                print("3. Run: git clone https://github.com/aibasel/downward.git")
                print("4. Run: cd downward")
                print("5. Run: ./build.py")
                return False

            check_script = f"test -f {self.fd_path}/fast-downward.py && echo 'SCRIPT_EXISTS'"
            result = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", check_script],
                capture_output=True,
                text=True
            )

            if "SCRIPT_EXISTS" in result.stdout:
                print("Fast Downward installation verified!")
                return True
            else:
                print(f"fast-downward.py not found in {self.fd_path}")
                return False
        except Exception as e:
            print(f"Error checking Fast Downward installation: {e}")
            return False


if __name__ == "__main__":
    domain_content = """(define (domain quest-domain)
      (:requirements :strips :typing)
      (:types
        agent location item obstacle - object
      )
      (:predicates
        (at ?a - agent ?l - location)
        (has ?a - agent ?i - item)
        (connected ?l1 ?l2 - location)
        (guarded_by ?l - location ?o - obstacle)
        (alive ?a - agent)
        (defeated ?o - obstacle)
      )
      (:action move
        :parameters (?a - agent ?from ?to - location)
        :precondition (and
          (at ?a ?from)
          (connected ?from ?to)
          (alive ?a)
        )
        :effect (and
          (not (at ?a ?from))
          (at ?a ?to)
        )
      )
      (:action take
        :parameters (?a - agent ?i - item ?l - location)
        :precondition (and
          (at ?a ?l)
          (at ?i ?l)
          (alive ?a)
        )
        :effect (and
          (has ?a ?i)
          (not (at ?i ?l))
        )
      )
      (:action defeat_obstacle
        :parameters (?a - agent ?o - obstacle ?l - location)
        :precondition (and
          (at ?a ?l)
          (guarded_by ?l ?o)
          (alive ?a)
          (not (defeated ?o))
        )
        :effect (and
          (defeated ?o)
          (not (guarded_by ?l ?o))
        )
      )
    )
    """

    problem_content = """(define (problem quest-problem)
      (:domain quest-domain)
      (:objects
        hero - agent
        start - location
        crystal_caverns - location
        golem - obstacle
      )
      (:init
        (at hero start)
        (alive hero)
        (connected start crystal_caverns)
        (connected crystal_caverns start)
        (guarded_by crystal_caverns golem)
      )
      (:goal
        (and
          (at hero crystal_caverns)
          (defeated golem)
        )
      )
    )
    """

    # Inserisci qui la tua distro e utente WSL
    validator = PDDLValidator(
        fd_path="/home/giuseppe/downward",
        wsl_distro="Ubuntu",
        wsl_user="giuseppe"
    )

    if validator.check_fast_downward_installation():
        print("\nValidating PDDL...")
        is_valid, error = validator.validate(domain_content, problem_content)
        print(f"Valid: {is_valid}")
        if error:
            print(f"Error: {error}")
    else:
        print("\nPlease install Fast Downward in WSL first!")