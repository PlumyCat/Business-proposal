# Infrastructure Réelle - Configuration

## Blob Storage

**Storage Account:** `mywordmcpacrstorage`
**Resource Group:** `my-word-mcp-rg`

### Containers

#### 1. word-templates
Structure des dossiers :
```
word-templates/
├── general/                    # Templates généraux
│   ├── template MW.docx
│   ├── template-placeholders.docx
│   ├── template-text.docx
│   ├── template.docx
│   ├── test-propal-final.docx
│   └── test-template-from-blob.docx
│
└── {DisplayName}/              # Dossiers utilisateurs
    └── Eric FER/
        └── .keep
```

**Usage:**
- `/general/` : Templates généraux accessibles à tous
- `/{DisplayName}/` : Dossiers personnels (ex: "Eric FER")
  - Ancien devis uploadés
  - Fichiers de travail (temp_working.docx)

#### 2. word-documents
Propositions générées finales (Word + PDF)

```
word-documents/
└── {DisplayName}/
    ├── proposition_20251017_1430.docx
    └── proposition_20251017_1430.pdf
```

---

## Dataverse

### Table: crb02_offrebeclouds

**Mapping des colonnes:**

| Colonne Dataverse | Type | Description | Code attendu |
|-------------------|------|-------------|--------------|
| `crb02_offrebecloudid` | GUID | ID unique | `offreId` |
| `crb02_offrebecloud1` | Text | Nom de l'offre | `name` |
| `crb02_description` | Text | Description | `description` |
| `crb02_prixht` | Decimal | Prix HT | `priceHT` |
| `crb02_prixttc` | Decimal | Prix TTC | `priceTTC` |
| `crb02_service` | Choice | Catégorie service | `category` |
| `statuscode` | Int | Code statut (1=actif) | `statusCode` |
| `statecode` | Int | État (0=actif) | `state` |

**Valeurs crb02_service (catégories):**
- `480810000` - Téléphonie (Teams Calling)
- `480810003` - Microsoft 365 / Bureautique
- `480810004` - Services Be-Cloud / IA

**Exemples d'offres:**
- SharePoint Plan 1 (5€ HT) - Service 480810004
- Power Apps Premium (19€ HT) - Service 480810004
- Microsoft 365 E3 (39€ HT) - Service 480810003
- Teams Phone Standard (8€ HT) - Service 480810000

---

## Variables d'Environnement

### .env (local)
```bash
# Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=mywordmcpacrstorage;...
AZURE_STORAGE_ACCOUNT_NAME=mywordmcpacrstorage
AZURE_TEMPLATES_CONTAINER_NAME=word-templates
AZURE_DOCUMENTS_CONTAINER_NAME=word-documents

# Dataverse
DATAVERSE_URL=https://{org}.crm.dynamics.com
DATAVERSE_CLIENT_ID={client-id}
DATAVERSE_CLIENT_SECRET={client-secret}
DATAVERSE_TENANT_ID={tenant-id}
DATAVERSE_TABLE_OFFERS=crb02_offrebeclouds

# SharePoint (conversion PDF)
SHAREPOINT_SITE_URL=https://{tenant}.sharepoint.com/sites/{site}
SHAREPOINT_TEMP_LIBRARY=TempConversions
```

### local.settings.json (Azure Functions)
```json
{
  "Values": {
    "BLOB_STORAGE_CONNECTION_STRING": "...",
    "BLOB_CONTAINER_TEMPLATES": "word-templates",
    "BLOB_CONTAINER_DOCUMENTS": "word-documents",

    "DATAVERSE_URL": "https://{org}.crm.dynamics.com",
    "DATAVERSE_CLIENT_ID": "{client-id}",
    "DATAVERSE_CLIENT_SECRET": "{client-secret}",
    "DATAVERSE_TENANT_ID": "{tenant-id}",
    "DATAVERSE_TABLE_OFFERS": "crb02_offrebeclouds",

    "SHAREPOINT_SITE_URL": "https://{tenant}.sharepoint.com/sites/{site}",
    "SHAREPOINT_TEMP_LIBRARY": "TempConversions"
  }
}
```

---

## Mapping Code vs Réalité

### Ancienne Configuration (code actuel)
```python
# ❌ Ancien
container = "devis-sources"
table = "cr_offres"
columns = ["cr_name", "cr_description", "cr_unit_price"]
```

### Nouvelle Configuration (infrastructure réelle)
```python
# ✅ Nouveau
container_templates = "word-templates"
container_documents = "word-documents"
table = "crb02_offrebeclouds"
columns = ["crb02_offrebecloud1", "crb02_description", "crb02_prixht"]
```

---

## Actions Requises

### ✅ Modifier le Code

**fichiers à adapter:**
1. `functions/shared/blob_client.py` - Noms containers
2. `functions/shared/dataverse_client.py` - Nom table + colonnes
3. `functions/DocumentProcessor/clean_quote.py` - Container templates
4. `functions/ProposalGenerator/prepare_template.py` - Container templates
5. `functions/ProposalGenerator/generate_simple.py` - Containers templates + documents
6. `local.settings.json` - Variables environnement

### ✅ Tester

**Test 1 - Lister les offres:**
```python
# Query Dataverse
table = "crb02_offrebeclouds"
filter = "statecode eq 0 and statuscode eq 1"  # Actives seulement
select = "crb02_offrebecloudid,crb02_offrebecloud1,crb02_description,crb02_prixht"
```

**Test 2 - Charger un template:**
```python
# Blob Storage
container = "word-templates"
blob_path = "general/template.docx"
```

**Test 3 - Sauvegarder proposition:**
```python
# Blob Storage
container = "word-documents"
blob_path = "Eric FER/proposition_20251017_1430.docx"
```

---

**Dernière mise à jour:** 2025-10-17
**Vérifié avec:** `check_blob_structure.py` + export CSV Dataverse
