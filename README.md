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
  - ⚠️ **IMPORTANT:** Langue anglaise (code 1033) doit être activée pour MCP Microsoft
  - Voir [dataverse/LIMITATIONS.md](dataverse/LIMITATIONS.md) pour détails
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
    "DATAVERSE_TENANT_ID": "<tenant-id>",
    "SHAREPOINT_SITE_URL": "https://<tenant>.sharepoint.com/sites/<site-name>",
    "SHAREPOINT_TEMP_LIBRARY": "TempConversions"
  }
}
```

**Configuration SharePoint:**
- Créer une bibliothèque SharePoint nommée "TempConversions" sur le site configuré
- Cette bibliothèque est utilisée temporairement pour la conversion Word → PDF
- Les fichiers sont automatiquement supprimés après conversion

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
│   ├── ProposalGenerator/   # Génération propositions
│   └── shared/              # Code partagé
│       ├── blob_client.py       # Client Azure Blob Storage
│       ├── dataverse_client.py  # Client Dataverse
│       ├── sharepoint_client.py # Client SharePoint (conversion PDF)
│       ├── auth_helper.py       # Authentification Azure AD
│       ├── logger.py            # Configuration logging
│       └── validators.py        # Validation des données
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

- `POST /api/document/extract-content` - Extraction contenu document
- `POST /api/document/clean-document` - Nettoyage document

### ProposalGenerator

- `POST /api/proposal/generate` - Génération proposition Word/PDF
- `POST /api/proposal/save` - Sauvegarde métadonnées Dataverse

**Note:** Les offres sont gérées directement par Copilot Studio via son connecteur Dataverse natif (pas besoin d'Azure Function)

## Conversion Word → PDF

La conversion des propositions Word (.docx) en PDF utilise SharePoint Online:

1. Le fichier Word est uploadé temporairement vers une bibliothèque SharePoint
2. SharePoint convertit automatiquement le fichier en PDF via son API native
3. Le PDF est téléchargé et stocké dans Blob Storage
4. Le fichier temporaire est supprimé de SharePoint

**Avantages:**
- Aucun service tiers requis (LibreOffice, CloudConvert, etc.)
- Conversion native Microsoft avec haute fidélité
- Déjà intégré dans l'écosystème Microsoft 365
- Authentification unifiée via Azure AD

**Prérequis:**
- Site SharePoint Online accessible
- Bibliothèque "TempConversions" créée sur le site
- Permissions de lecture/écriture/suppression sur la bibliothèque

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
- [dataverse/schemas.md](dataverse/schemas.md) - Schémas des tables Dataverse
- [dataverse/LIMITATIONS.md](dataverse/LIMITATIONS.md) - Limitations connues et workarounds
- [docs/api_documentation.md](docs/api_documentation.md) - Documentation API complète

## Support

Pour toute question ou problème:
1. Consulter la documentation dans `/docs`
2. Vérifier les issues GitHub
3. Contacter l'équipe de support

## Licence

Propriétaire - Tous droits réservés
