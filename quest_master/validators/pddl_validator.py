import re
import subprocess
import tempfile
import platform
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
                # Se non stai usando WSL, questo validatore ora supporta solo WSL
                return False, "This validator only supports WSL on Windows", None
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
    def __init__(self, fd_path: str | None = None, wsl_distro: str = "Ubuntu", wsl_user: str = "giuseppe",
                 output_dir: str = "examples/output"):
        """Initialize Fast Downward validator with optional WSL support."""
        self.use_wsl = platform.system() == "Windows"
        self.wsl_distro = wsl_distro
        self.wsl_user = wsl_user
        self.output_dir = Path(output_dir)

        # Crea la cartella di output se non esiste
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if fd_path:
            self.fd_path = fd_path
        else:
            self.fd_path = f"/home/{wsl_user}/downward" if self.use_wsl else "/usr/local/bin"

        if self.use_wsl:
            self._check_wsl()
            print(f"Fast Downward WSL path: {self.fd_path}")
        else:
            self.fd_executable = Path(self.fd_path) / "fast-downward.py"

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

    def _wsl_to_windows_path(self, wsl_path: str) -> str:
        """Converte un path WSL in path Windows"""
        if wsl_path.startswith('/mnt/'):
            # Path formato /mnt/c/... -> C:\...
            parts = wsl_path.split('/')
            if len(parts) >= 3:
                drive = parts[2].upper()
                rest_path = '/'.join(parts[3:]) if len(parts) > 3 else ''
                return f"{drive}:\\{rest_path.replace('/', chr(92))}"
        return wsl_path

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

    def _copy_plan_from_wsl(self, wsl_working_dir: str) -> Optional[str]:
        """Copia il piano da WSL alla cartella di output"""
        try:
            # Controlla se esiste sas_plan nella directory di lavoro WSL
            check_plan_cmd = f"test -f {wsl_working_dir}/sas_plan && echo 'PLAN_EXISTS'"
            result = self._run_wsl_command(check_plan_cmd)

            if "PLAN_EXISTS" not in result.stdout:
                return None

            # Leggi il contenuto del piano
            read_plan_cmd = f"cat {wsl_working_dir}/sas_plan"
            result = self._run_wsl_command(read_plan_cmd)

            if result.returncode == 0 and result.stdout.strip():
                # Salva il piano nella cartella di output
                plan_filename = f"problem_plan.txt"
                plan_path = self.output_dir / plan_filename

                with open(plan_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)

                print(f"Piano salvato in: {plan_path}")
                return str(plan_path)

        except Exception as e:
            print(f"Errore durante la copia del piano: {e}")

        return None

    def validate(self, domain_content: str, problem_content: str) -> Tuple[
        bool, Optional[str], Optional[str]]:
        """Validate domain and problem using Fast Downward. Returns (success, error_message, plan_path)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            domain_file = Path(tmpdir) / "domain.pddl"
            problem_file = Path(tmpdir) / "problem.pddl"
            domain_file.write_text(domain_content, encoding="utf-8")
            problem_file.write_text(problem_content, encoding="utf-8")

            try:
                if self.use_wsl:
                    wsl_domain = self._windows_to_wsl_path(str(domain_file))
                    wsl_problem = self._windows_to_wsl_path(str(problem_file))
                    wsl_tmpdir = self._windows_to_wsl_path(tmpdir)

                    command = (
                        f"cd {wsl_tmpdir} && python3 {self.fd_path}/fast-downward.py {wsl_domain} {wsl_problem} "
                        f"--evaluator 'eval=hmax()' --search 'lazy_greedy([eval])'"
                    )
                    result = subprocess.run(
                        ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", command],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                # Combine stdout and stderr for analysis
                full_output = result.stdout + "\n" + result.stderr

                print("=== Fast Downward output ===")
                print(full_output)
                print("============================")

                if result.returncode == 0:
                    if "Solution found!" in full_output:
                        # Copia il piano da WSL
                        wsl_tmpdir = self._windows_to_wsl_path(tmpdir)
                        plan_path = self._copy_plan_from_wsl(wsl_tmpdir)

                        return True, None, plan_path
                    elif "Search stopped without finding a solution." in full_output:
                        return False, "No solution found - goal might be unreachable", None
                    elif "Completely explored state space -- no solution!" in full_output:
                        return False, "Goal is provably unreachable from initial state", None
                    else:
                        return False, "Unknown outcome despite successful execution", None
                else:
                    error_msg = extract_error_block(full_output)
                    return False, f"Fast Downward error:\n{error_msg}", None

            except subprocess.TimeoutExpired:
                return False, "Validation timeout - problem might be too complex", None
            except FileNotFoundError:
                return False, "Fast Downward executable not found", None
            except Exception as e:
                return False, f"Validation error: {str(e)}", None

    def check_fast_downward_installation(self) -> bool:
        """Verify Fast Downward installation in WSL."""
        try:
            check_cmd = f"test -d {self.fd_path} && echo 'EXISTS'"
            result = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", check_cmd],
                capture_output=True,
                text=True,
            )
            if "EXISTS" not in result.stdout:
                return False
            check_script = f"test -f {self.fd_path}/fast-downward.py && echo 'SCRIPT_EXISTS'"
            result = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "--user", self.wsl_user, "bash", "-c", check_script],
                capture_output=True,
                text=True,
            )
            return "SCRIPT_EXISTS" in result.stdout
        except Exception:
            return False