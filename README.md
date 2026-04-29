# Startup Guide

## Prérequis

- Python 3.10+
- Poetry
- OpenSSL
- pip

---

## Installation du projet

```bash
git clone <repo_url>
cd py-RAT
```

---

## Configuration Poetry

```bash
poetry install
```

Activation du shell :

```bash
poetry shell
ou création de votre venv
```

---

## Dépendance audio (soundcard)

Si nécessaire sur votre machine :

```bash
pip install soundcard
```

Ou via Poetry :

```bash
poetry add soundcard
```

---

## Génération des certificats SSL

Créer le dossier :

```bash
mkdir -p certs
cd certs
```

Générer une clé privée :

```bash
openssl genrsa -out key.pem 2048
```

Générer un certificat auto-signé :

```bash
openssl req -new -x509 -key key.pem -out cert.pem -days 365
```

### Structure attendue

```
certs/
 ├── cert.pem
 └── key.pem
```

---

## Lancement du serveur

Depuis la racine du projet :

```bash
poetry run python -m rat.run_server
```

---

## Lancement du client

```bash
poetry run python -m rat.run_client
```

---

## Notes importantes

- Toujours lancer depuis la racine du projet
- Ne jamais exécuter les fichiers `.py` directement
- Toujours utiliser `poetry run` ou `python -m ...`
- Garder `src/` comme base de package (`rat`)
