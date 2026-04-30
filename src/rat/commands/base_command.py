# Ce module définit la classe de base abstraite pour toutes les commandes.
# Chaque commande du système doit hériter de cette classe et implémenter
# la méthode `execute`, garantissant une interface uniforme.

from abc import ABC, abstractmethod


class BaseCommand(ABC):

    # Nom de la commande (utilisé pour l’enregistrement dans le registry)
    name = ""

    @abstractmethod
    def execute(self, args: str) -> str:
        pass
