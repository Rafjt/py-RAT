import subprocess
from .base_command import BaseCommand


# Commande permettant d'exécuter une commande système directement via le shell.
# Elle sert d'interface générale pour lancer des commandes OS (ls, dir, etc.).
class ShellCommand(BaseCommand):

    name = "shell"
    description = "Execute a shell command and return the output"

    def execute(self, args: str) -> str:

        # Vérifie qu'une commande a bien été fournie
        if not args.strip():
            return "Usage: shell <command>"

        try:
            # Exécution de la commande via le shell système.
            # shell=True permet d'utiliser les commandes natives du système
            # (ex: dir sous Windows, ls sous Linux/macOS, pipes, redirections, etc.)
            result = subprocess.run(
                args,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # protection contre les commandes bloquantes infinies
            )

            # Récupération de la sortie standard
            output = result.stdout

            # Ajout de la sortie d'erreur si elle existe
            if result.stderr:
                output += "\n" + result.stderr

            # Si rien n'a été retourné, on l'indique explicitement
            return output if output else "(no output)"

        except subprocess.TimeoutExpired:
            # Protection contre les commandes qui ne se terminent jamais
            return "shell error: command timed out (30s)"

        except Exception as e:
            # Gestion globale des erreurs inattendues (OS, permissions, etc.)
            return f"shell error: {e}"
