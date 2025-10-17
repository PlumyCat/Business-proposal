# Workflows Simplifiés - Business Proposal Generator

## Architecture Ultra-Simplifiée ✅

### Tables Dataverse
- **cr_offres** uniquement (existe déjà, accès lecture) ✅
- ~~cr_uploads_temp~~ ❌ Supprimé (upload direct Blob via connecteur Copilot)
- ~~cr_propositions~~ ❌ Supprimé (pas de traçabilité demandée)
- ~~cr_templates~~ ❌ Supprimé (templates hardcodés)

### Structure Blob Storage

```
blob-storage/
├── general/                     # Templates généraux
│   ├── template_standard.docx
│   └── template_premium.docx
│
└── users/                       # Dossiers utilisateurs
    ├── {DisplayName 1}/
    │   ├── ancien_devis.docx
    │   ├── temp_working.docx
    │   └── proposition_20251017_1430.docx
    └── {DisplayName 2}/
        └── ...
```

---

## Workflow 1 : Partir d'un Template Général 📄

### Étapes Copilot Studio

```
1️⃣ Copilot: "Voulez-vous partir d'un template ou d'un ancien devis ?"
   User: "Template"

2️⃣ Copilot: "Quel template ?"
   Options: template_standard.docx | template_premium.docx
   User: Sélectionne "template_standard.docx"

3️⃣ Copilot: "Nom du customer success ?"
   User: "Jean Dupont"

4️⃣ Copilot: "Téléphone ?"
   User: "06 12 34 56 78"

5️⃣ Copilot: "Email ?"
   User: "jean.dupont@company.com"

6️⃣ Copilot → Appel Azure Function: prepare-template
   ↓
   📝 Template chargé et placeholders remplacés
   ↓
   💾 Sauvegardé dans users/{DisplayName}/temp_working.docx

7️⃣ Copilot: "Quelles offres voulez-vous inclure ?"
   → Query Dataverse cr_offres (connecteur natif)
   → Affichage Adaptive Cards avec liste offres
   User: Sélectionne 3 offres

8️⃣ Copilot → Appel Azure Function: generate
   ↓
   📊 Offres ajoutées dans tableaux
   ↓
   💾 Sauvegardé: users/{DisplayName}/proposition_20251017_1430.docx
   ↓
   📄 Converti en PDF via SharePoint
   ↓
   💾 Sauvegardé: users/{DisplayName}/proposition_20251017_1430.pdf

9️⃣ Copilot: Affiche liens téléchargement Word + PDF
```

### Appels API

**Étape 6 - Préparer le template**

```http
POST /api/proposal/prepare-template

Request:
{
  "template_name": "template_standard.docx",
  "customer_success": {
    "name": "Jean Dupont",
    "tel": "06 12 34 56 78",
    "email": "jean.dupont@company.com"
  },
  "user_folder": "Marie Martin"  // displayName de l'utilisateur Teams
}

Response:
{
  "success": true,
  "working_file": "users/Marie Martin/temp_working.docx",
  "blob_url": "https://...",
  "template_used": "template_standard.docx"
}
```

**Étape 8 - Générer la proposition**

```http
POST /api/proposal/generate

Request:
{
  "working_file": "users/Marie Martin/temp_working.docx",
  "offer_ids": ["guid1", "guid2", "guid3"],
  "user_folder": "Marie Martin"
}

Response:
{
  "success": true,
  "word_file": "users/Marie Martin/proposition_20251017_1430.docx",
  "word_url": "https://...",
  "pdf_file": "users/Marie Martin/proposition_20251017_1430.pdf",
  "pdf_url": "https://...",
  "offers_added": 3
}
```

---

## Workflow 2 : Partir d'un Ancien Devis 📋

### Étapes Copilot Studio

```
1️⃣ Copilot: "Voulez-vous partir d'un template ou d'un ancien devis ?"
   User: "Ancien devis"

2️⃣ Copilot: "Uploadez votre fichier .docx"
   → Utilise connecteur Blob Storage
   User: Upload fichier
   ↓
   💾 Sauvegardé: users/{DisplayName}/ancien_devis.docx

3️⃣ Copilot → Appel Azure Function: clean-quote
   ↓
   🧹 Tableaux vidés (garde headers + nom/tel/email customer success)
   ↓
   💾 Sauvegardé: users/{DisplayName}/temp_working.docx

4️⃣ Copilot: "Quelles offres voulez-vous inclure ?"
   → Query Dataverse cr_offres (connecteur natif)
   → Affichage Adaptive Cards avec liste offres
   User: Sélectionne 3 offres

5️⃣ Copilot → Appel Azure Function: generate
   (Identique à Workflow 1, étape 8)
   ↓
   📊 Offres ajoutées dans tableaux
   ↓
   💾 Sauvegardé: users/{DisplayName}/proposition_20251017_1430.docx + PDF

6️⃣ Copilot: Affiche liens téléchargement Word + PDF
```

### Appels API

**Étape 3 - Nettoyer l'ancien devis**

```http
POST /api/document/clean-quote

Request:
{
  "blob_path": "users/Jean Dupont/ancien_devis.docx",
  "user_folder": "Jean Dupont"
}

Response:
{
  "success": true,
  "working_file": "users/Jean Dupont/temp_working.docx",
  "blob_url": "https://...",
  "tables_found": 3,
  "rows_emptied": 15
}
```

**Étape 5 - Générer la proposition**

(Identique à Workflow 1, étape 8)

---

## Endpoints Azure Functions - Résumé

### DocumentProcessor

| Endpoint | Méthode | Description | Workflow |
|----------|---------|-------------|----------|
| `/api/document/clean-quote` | POST | Nettoie ancien devis (vide tableaux) | Workflow 2 |
| `/api/document/extract-content` | POST | Extraction contenu (legacy) | - |
| `/api/document/clean-document` | POST | Nettoyage avancé (legacy) | - |

### ProposalGenerator

| Endpoint | Méthode | Description | Workflow |
|----------|---------|-------------|----------|
| `/api/proposal/prepare-template` | POST | Prépare template avec infos CS | Workflow 1 |
| `/api/proposal/generate` | POST | Génère proposition finale (Word+PDF) | Les 2 |
| `/api/proposal/save` | POST | Sauvegarde métadonnées (optionnel) | - |

---

## Format des Tableaux dans les Documents

### Template Général

Les templates dans `/general/` doivent contenir :

**Placeholders pour Customer Success:**
- `{{CS_NAME}}` - Nom du customer success
- `{{CS_TEL}}` - Téléphone
- `{{CS_EMAIL}}` - Email

**Tableau Offres (minimum 1 tableau avec headers):**

| Description | Quantité | Prix Unitaire | Prix Total |
|-------------|----------|---------------|------------|
| (vide) | (vide) | (vide) | (vide) |

Les offres seront ajoutées automatiquement sous les headers.

### Ancien Devis

L'ancien devis uploadé par l'utilisateur doit contenir :
- Nom, téléphone, email du customer success ✅ (conservés)
- Tableaux avec headers ✅ (headers conservés, lignes vidées)

---

## Copilot Studio - Configuration Requise

### Connecteurs

1. **Dataverse** (natif)
   - Lecture cr_offres
   - Actions: List rows, Get row

2. **Blob Storage** (personnalisé)
   - Upload de fichiers .docx
   - Configuration: Connection string + container name

### Custom Actions

1. **PrepareTemplate**
   - URL: `https://{function-app}.azurewebsites.net/api/proposal/prepare-template`
   - Méthode: POST
   - Inputs: template_name, customer_success (object), user_folder
   - Outputs: success, working_file, blob_url

2. **CleanQuote**
   - URL: `https://{function-app}.azurewebsites.net/api/document/clean-quote`
   - Méthode: POST
   - Inputs: blob_path, user_folder
   - Outputs: success, working_file, tables_found, rows_emptied

3. **GenerateProposal**
   - URL: `https://{function-app}.azurewebsites.net/api/proposal/generate`
   - Méthode: POST
   - Inputs: working_file, offer_ids (array), user_folder
   - Outputs: success, word_url, pdf_url, offers_added

### Variables Globales Copilot

- `UserDisplayName` - Récupéré depuis Teams (displayName de l'utilisateur)
- `SelectedTemplate` - Template choisi par l'utilisateur
- `WorkingFile` - Chemin du fichier de travail
- `SelectedOfferIds` - Array des GUIDs offres sélectionnées

---

## Gestion du Dossier Utilisateur

Le **displayName** de l'utilisateur Teams est utilisé comme nom de dossier :

```
users/
├── Jean Dupont/
├── Marie Martin/
└── Pierre Durand/
```

**Copilot Studio peut récupérer le displayName via :**
```
System.User.DisplayName
```

---

## Points d'Attention pour Copilot Studio

### Simplicité = Performance

Copilot Studio peut être "bête à manger du foin" selon vos mots 😅

**Recommandations :**
1. **Variables simples** - Pas de structures imbriquées complexes
2. **Étapes linéaires** - Éviter les branches conditionnelles excessives
3. **Validation minimale** - Faire la validation côté Azure Functions
4. **Messages clairs** - Toujours donner feedback visuel à l'utilisateur
5. **Gestion erreurs** - Si Azure Function échoue, afficher message simple et proposer de recommencer

### Adaptive Cards Simplifiées

**Liste des offres :**
```json
{
  "type": "AdaptiveCard",
  "body": [
    {
      "type": "TextBlock",
      "text": "Sélectionnez les offres à inclure"
    },
    {
      "type": "Input.ChoiceSet",
      "id": "selectedOffers",
      "isMultiSelect": true,
      "choices": [
        {
          "title": "{offer.cr_name} - {offer.cr_unit_price}€/{offer.cr_unit}",
          "value": "{offer.cr_offreid}"
        }
      ]
    }
  ]
}
```

---

## Testing Rapide

### Test Workflow 1 (Template)

```bash
# 1. Upload template_standard.docx dans blob:general/
# 2. Appeler prepare-template
curl -X POST https://{function}.azurewebsites.net/api/proposal/prepare-template \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "template_standard.docx",
    "customer_success": {"name": "Test", "tel": "06", "email": "test@test.com"},
    "user_folder": "Test User"
  }'

# 3. Appeler generate avec 2 offres
curl -X POST https://{function}.azurewebsites.net/api/proposal/generate \
  -H "Content-Type: application/json" \
  -d '{
    "working_file": "users/Test User/temp_working.docx",
    "offer_ids": ["guid1", "guid2"],
    "user_folder": "Test User"
  }'
```

### Test Workflow 2 (Ancien Devis)

```bash
# 1. Upload ancien_devis.docx dans blob:users/Test User/
# 2. Appeler clean-quote
curl -X POST https://{function}.azurewebsites.net/api/document/clean-quote \
  -H "Content-Type: application/json" \
  -d '{
    "blob_path": "users/Test User/ancien_devis.docx",
    "user_folder": "Test User"
  }'

# 3. Appeler generate (même que workflow 1)
```

---

**Date dernière mise à jour:** 2025-10-17
**Version:** 2.0 Simplifiée
