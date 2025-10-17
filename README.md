# Business Proposal Generator

Système de génération automatisée de propositions commerciales basé sur Azure Functions et Copilot Studio.

## Architecture

- **Backend**: Azure Functions (Python 3.11)
- **Interface**: Copilot Studio + Microsoft Teams
- **Upload**: SharePoint Library + Power Automate → Blob Storage
- **Stockage**: Azure Blob Storage
- **Base de données**: Dataverse
- **Authentification**: Azure AD (Entra ID)

## Prérequis

### Logiciels Requis

- Python 3.11+
- Azure Functions Core Tools v4
- Git
- VS Code (recommandé)
- Azure CLI (pour déploiement)

### Accès Cloud Requis

- Subscription Azure (rôle Contributor)
- Environnement Power Platform avec Dataverse
- SharePoint Online
- Microsoft Teams

## Installation Locale

### 1. Cloner le Repository

```bash
git clone <repository-url>
cd business_proposal
```

### 2. Créer Environnement Virtuel Python

```bash
python -m venv .venv

# Activation (Linux/Mac)
source .venv/bin/activate

# Activation (Windows)
.venv\Scripts\activate
```

### 3. Installer Dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration Locale

Copier le template de configuration:

```bash
cp local.settings.json local.settings.json.local
```

Éditer `local.settings.json` et remplir les valeurs:

```json
{
  "Values": {
    "BLOB_STORAGE_CONNECTION_STRING": "<votre-connection-string>",
    "DATAVERSE_URL": "https://<org>.crm.dynamics.com",
    "DATAVERSE_CLIENT_ID": "<client-id>",
    "DATAVERSE_CLIENT_SECRET": "<client-secret>",
    "DATAVERSE_TENANT_ID": "<tenant-id>"
  }
}
```

### 5. Lancer Localement

```bash
func start
```

Les endpoints seront disponibles sur `http://localhost:7071/api/`

## Structure du Projet

```
business-proposal-generator/
├── functions/               # Azure Functions
│   ├── DocumentProcessor/   # Extraction et nettoyage documents
│   ├── OfferManager/        # Gestion offres Dataverse
│   ├── ProposalGenerator/   # Génération propositions
│   └── shared/              # Code partagé
├── copilot/                 # Configuration Copilot Studio
├── dataverse/               # Schémas Dataverse
├── infrastructure/          # IaC (Bicep)
├── tests/                   # Tests unitaires et intégration
└── docs/                    # Documentation
```

## Workflow Utilisateur

1. User upload fichier .docx → SharePoint Library "Devis Sources"
2. Power Automate détecte et copie vers Blob Storage
3. User démarre conversation avec Copilot sur Teams
4. Copilot récupère le fichier uploadé
5. Extraction et nettoyage du document
6. Sélection des offres à inclure
7. Génération proposition (.docx + PDF)
8. Téléchargement des fichiers générés

## Azure Functions Endpoints

### DocumentProcessor

- `POST /api/extract-content` - Extraction contenu document
- `POST /api/clean-document` - Nettoyage document

### OfferManager

- `GET /api/offers` - Liste des offres disponibles
- `GET /api/offers/{id}` - Détails d'une offre

### ProposalGenerator

- `POST /api/generate-proposal` - Génération proposition
- `POST /api/convert-to-pdf` - Conversion PDF
- `POST /api/save-proposal` - Sauvegarde métadonnées

## Développement

### Lancer Tests

```bash
# Tests unitaires
pytest tests/unit/

# Tests intégration
pytest tests/integration/

# Coverage
pytest --cov=functions tests/
```

### Linter & Formatage

```bash
# Black (formatage)
black functions/

# Flake8 (linting)
flake8 functions/

# Type checking
mypy functions/
```

## Déploiement

### Déploiement Dev

```bash
cd infrastructure/scripts
./deploy_dev.sh
```

### Déploiement Production

```bash
cd infrastructure/scripts
./deploy_prod.sh
```

## Documentation

- [EPCT.md](EPCT.md) - Plan d'action EPCT détaillé (Explore-Plan-Code-Test)
- [TODO.md](TODO.md) - Suivi des tâches par phase
- [CLAUDE.md](CLAUDE.md) - Documentation pour Claude Code
- [docs/api_documentation.md](docs/api_documentation.md) - Documentation API complète

## Support

Pour toute question ou problème:
1. Consulter la documentation dans `/docs`
2. Vérifier les issues GitHub
3. Contacter l'équipe de support

## Licence

Propriétaire - Tous droits réservés
