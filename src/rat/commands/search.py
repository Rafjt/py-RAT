# Commande de recherche de fichiers sur le système de fichiers local.
# Elle parcourt récursivement un dossier et retourne les fichiers
# dont le nom correspond à un motif donné.

import os


class SearchCommand:

    # Nom utilisé par le registry pour appeler la commande
    name = "search"

    def execute(self, args: str) -> str:

        # Découpe des arguments :
        # pattern = nom ou motif recherché
        # root = dossier de départ (optionnel)
        parts = args.split()

        # Vérifie qu’un motif de recherche est fourni
        if not parts:
            return "Usage: search <pattern> [path]"

        pattern = parts[0]

        # Dossier racine de recherche (par défaut : dossier courant)
        if len(parts) > 1:
            root = parts[1]
        else:
            root = os.getcwd()

        # Vérifie que le chemin existe
        if not os.path.exists(root):
            return "Path not found"

        matches = []

        try:
            # Parcours récursif de l’arborescence
            for dirpath, dirnames, filenames in os.walk(root):

                for name in filenames:

                    # Recherche insensible à la casse dans le nom du fichier
                    if pattern.lower() in name.lower():

                        full_path = os.path.join(dirpath, name)

                        matches.append(full_path)

        except Exception as e:
            return f"Search error: {e}"

        # Aucun résultat trouvé
        if not matches:
            return "No files found"

        # Retour des résultats (1 fichier par ligne)
        return "\n".join(matches)
