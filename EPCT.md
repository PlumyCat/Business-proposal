# EPCT - Explore Plan Code Test

Plan d'action systématique pour le développement du Business Proposal Generator.

---

## EXPLORE - Analyse ✅

### Projet Existant
- Requirements documentés dans `projet.md` (français)
- Architecture validée: Azure Functions + Copilot Studio
- Plan global en 7 phases dans `TODO.md`

### Stack Technique Identifié

**Backend:**
- Azure Functions (Python recommandé)
- HTTP Triggers pour exposition API
- Azure Blob Storage (3 containers)
- Azure Key Vault (gestion secrets)

**Database:**
- Dataverse (Power Platform)
- 3 Tables: Offres, Propositions, Templates
- Authentification via Azure AD

**Frontend:**
- Copilot Studio
- Teams App integration
- Adaptive Cards pour UI

**Upload Documents (Workaround limitation Copilot Studio):**
- **IMPORTANT**: Copilot Studio ne gère pas les pièces jointes nativement
- **Solution**: SharePoint Library + Power Automate connector Blob Storage
- User upload fichier → SharePoint → Power Automate → Blob Storage
- Copilot récupère file_id après upload

**Traitement Documents:**
- Input: Word (.docx)
- Output: Word (.docx) + PDF
- Extraction: `python-docx`
- Nettoyage: logique custom
- Génération: `python-docx` + template engine

### Dépendances Critiques

**Python Packages:**
```
azure-functions
azure-storage-blob
azure-identity
azure-keyvault-secrets
python-docx
requests
pandas (pour tableaux)
```

**Copilot Studio:**
- Custom Actions pour appeler Azure Functions
- Power Automate pour workflows complexes
- Dataverse connector natif

**Contraintes:**
- Authentification Azure AD obligatoire
- CORS config pour Copilot Studio
- Taille max fichiers Blob Storage
- Timeout Azure Functions (5-10 min max)
- Limites API Dataverse (appels/jour)

---

## PLAN - Architecture Détaillée

### Architecture Globale

```
┌──────────────────────────────────────────────────────────┐
│                   USER (Teams)                            │
└───────┬──────────────────────────────────┬───────────────┘
        │                                  │
        │ Upload fichier                   │ Chat avec bot
        ▼                                  ▼
┌──────────────────┐              ┌─────────────────┐
│   SharePoint     │              │ Copilot Studio  │
│   Library        │              │  (Power VA)     │
│  (drop zone)     │              └────────┬────────┘
└────────┬─────────┘                       │
         │                                 │ API calls
         │ Trigger                         ▼
         ▼                        ┌─────────────────────────┐
┌──────────────────┐              │   Azure Functions       │
│ Power Automate   │◄─────────────│   (HTTP Triggers)       │
│  - File Monitor  │  Callback    │                         │
│  - Copy to Blob  │              │  ┌────────────────┐     │
│  - Notify Bot    │              │  │ DocumentProc   │     │
└────────┬─────────┘              │  ├────────────────┤     │
         │                        │  │ OfferManager   │     │
         │ Upload                 │  ├────────────────┤     │
         ▼                        │  │ ProposalGen    │     │
┌──────────────────┐              │  └────────────────┘     │
│  Blob Storage    │◄─────────────┴─────────────────────────┘
│  - templates     │                       │         │
│  - devis-sources │                       │         │
│  - propositions  │                       ▼         ▼
└──────────────────┘              ┌───────────┐  ┌──────────┐
                                  │ Dataverse │  │Key Vault │
                                  └───────────┘  └──────────┘

WORKFLOW UPLOAD:
1. User upload .docx → SharePoint Library
2. Power Automate détecte nouveau fichier
3. Flow copie fichier → Blob Storage (container: devis-sources)
4. Flow génère file_id unique
5. Flow envoie notification à Copilot (ou update Dataverse variable)
6. User communique file_id au Copilot ou Copilot récupère automatiquement
7. Copilot continue workflow avec file_id
```

### Structure du Projet

```
business-proposal-generator/
├── functions/
│   ├── DocumentProcessor/
│   │   ├── __init__.py
│   │   ├── function.json
│   │   ├── upload_handler.py
│   │   ├── extract_handler.py
│   │   └── clean_handler.py
│   ├── OfferManager/
│   │   ├── __init__.py
│   │   ├── function.json
│   │   ├── get_offers.py
│   │   └── get_offer_details.py
│   ├── ProposalGenerator/
│   │   ├── __init__.py
│   │   ├── function.json
│   │   ├── generate_handler.py
│   │   ├── pdf_converter.py
│   │   └── save_handler.py
│   └── shared/
│       ├── blob_client.py
│       ├── dataverse_client.py
│       ├── auth_helper.py
│       ├── validators.py
│       └── logger.py
├── copilot/
│   ├── topics/
│   │   ├── nouvelle_proposition.yaml
│   │   ├── traitement_document.yaml
│   │   ├── selection_offres.yaml
│   │   ├── generation_finale.yaml
│   │   └── consulter_historique.yaml
│   ├── actions/
│   │   └── azure_functions_actions.json
│   └── flows/
│       ├── email_notification.yaml
│       └── archivage_auto.yaml
├── dataverse/
│   ├── schemas/
│   │   ├── table_offres.json
│   │   ├── table_propositions.json
│   │   └── table_templates.json
│   └── security/
│       └── roles_permissions.json
├── infrastructure/
│   ├── bicep/
│   │   ├── main.bicep
│   │   ├── storage.bicep
│   │   ├── function_app.bicep
│   │   ├── keyvault.bicep
│   │   └── app_registration.bicep
│   └── scripts/
│       ├── deploy_dev.sh
│       ├── deploy_prod.sh
│       └── setup_dataverse.ps1
├── tests/
│   ├── unit/
│   │   ├── test_document_processor.py
│   │   ├── test_offer_manager.py
│   │   └── test_proposal_generator.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   └── test_copilot_integration.py
│   └── fixtures/
│       ├── sample_devis.docx
│       └── sample_template.docx
├── docs/
│   ├── api_documentation.md
│   ├── user_guide.md
│   └── deployment_guide.md
├── .gitignore
├── requirements.txt
├── host.json
├── local.settings.json
├── README.md
├── CLAUDE.md
├── TODO.md
└── EPCT.md (ce fichier)
```

### API Endpoints Design

#### 1. DocumentProcessor

**NOTE**: L'upload est géré par Power Automate + SharePoint → Blob Storage
L'Azure Function ne gère plus l'upload initial.

**POST /api/extract-content**
```json
Request:
{
  "file_id": "abc123"
}

Response:
{
  "text": "Contenu extrait...",
  "tables": [
    {
      "headers": ["Article", "Prix", "Quantité"],
      "rows": [...]
    }
  ],
  "structure": {
    "sections": [...]
  }
}
```

**POST /api/clean-document**
```json
Request:
{
  "extracted_content": {...},
  "cleaning_rules": ["remove_filled_data", "normalize_tables"]
}

Response:
{
  "cleaned_content": {...},
  "removed_items": ["old_data_1", "old_data_2"]
}
```

#### 2. OfferManager

**GET /api/offers?category={cat}&active=true**
```json
Response:
{
  "offers": [
    {
      "id": "offer_001",
      "name": "Pack Standard",
      "category": "Services",
      "price": 1200.00,
      "currency": "EUR",
      "active": true
    }
  ]
}
```

**GET /api/offers/{offer_id}**
```json
Response:
{
  "id": "offer_001",
  "name": "Pack Standard",
  "description": "Description complète...",
  "price": 1200.00,
  "elements": [
    "Élément 1",
    "Élément 2"
  ]
}
```

#### 3. ProposalGenerator

**POST /api/generate-proposal**
```json
Request:
{
  "template_id": "template_001",
  "cleaned_content": {...},
  "selected_offers": ["offer_001", "offer_002"],
  "metadata": {
    "client_name": "Client ABC",
    "created_by": "user@domain.com"
  }
}

Response:
{
  "proposal_id": "prop_123",
  "docx_url": "https://storage/proposals/prop_123.docx",
  "pdf_url": "https://storage/proposals/prop_123.pdf",
  "status": "generated"
}
```

### Dataverse Schema

#### Table: Uploads Temp (Workaround SharePoint upload)
```
cr_uploads_temp
├── cr_upload_id (Primary Key, GUID)
├── cr_file_id (Text, 50 chars, unique) - ID généré par Power Automate
├── cr_original_filename (Text, 255 chars)
├── cr_blob_url (URL)
├── cr_upload_date (DateTime)
├── cr_status (Choice: Uploaded, Processing, Completed, Error)
├── cr_processed_by (Lookup → systemuser, optionnel)
└── cr_error_message (Multiline Text, optionnel)

Note: Cette table est temporaire. Les enregistrements peuvent être supprimés après 7 jours.
```

#### Table: Offres
```
cr_offres
├── cr_offre_id (Primary Key, GUID)
├── cr_nom (Text, 100 chars)
├── cr_description (Multiline Text)
├── cr_categorie (Choice: Services, Produits, Consulting)
├── cr_prix (Currency, EUR)
├── cr_elements_inclus (Multiline Text, JSON)
├── cr_actif (Yes/No)
├── createdon (DateTime)
└── modifiedon (DateTime)
```

#### Table: Propositions
```
cr_propositions
├── cr_proposition_id (Primary Key, GUID)
├── cr_nom_client (Text, 200 chars)
├── cr_statut (Choice: Brouillon, Envoyé, Accepté, Refusé)
├── cr_offres_incluses (Lookup Multiple → cr_offres)
├── cr_lien_docx (URL)
├── cr_lien_pdf (URL)
├── cr_notes (Multiline Text)
├── cr_cree_par (Lookup → systemuser)
├── createdon (DateTime)
└── modifiedon (DateTime)
```

#### Table: Templates
```
cr_templates
├── cr_template_id (Primary Key, GUID)
├── cr_nom (Text, 100 chars)
├── cr_description (Multiline Text)
├── cr_blob_url (URL)
├── cr_version (Text, 10 chars)
├── cr_actif (Yes/No)
├── createdon (DateTime)
└── modifiedon (DateTime)
```

### Copilot Studio - Topics Flow

#### Topic: Nouvelle Proposition

```yaml
trigger:
  - "nouvelle proposition"
  - "créer proposition"
  - "générer devis"

flow:
  1. Message: "Je vais vous aider à créer une proposition commerciale."
  2. Message: "📁 Pour commencer, uploadez votre devis source (.docx) dans le dossier SharePoint:"
     - Afficher Adaptive Card avec:
       * Lien vers SharePoint Library (devis-sources)
       * Instructions: "Déposez votre fichier .docx dans ce dossier"
       * Bouton: "Ouvrir SharePoint"
  3. Message: "Une fois le fichier uploadé, je serai notifié automatiquement."
  4. Attendre notification Power Automate (ou polling Dataverse)
  5. Récupérer file_id depuis Dataverse table temporaire
  6. Variable: file_id, filename
  7. Message: "✅ Document '{filename}' reçu! (ID: {file_id})"
  8. Rediriger vers: Topic TraitementDocument

Alternative (si l'utilisateur donne le file_id manuellement):
  1. Message: "Avez-vous déjà uploadé votre fichier dans SharePoint?"
  2. Si Oui:
     - Question: "Quel est le nom du fichier?"
     - Rechercher dans Dataverse par filename
     - Récupérer file_id
  3. Si Non:
     - Workflow normal ci-dessus
```

#### Topic: Traitement du Document

```yaml
flow:
  1. Appeler Action: ExtractContent(file_id)
  2. Variable: extracted_content
  3. Appeler Action: CleanDocument(extracted_content)
  4. Variable: cleaned_content
  5. Message: "Aperçu du contenu nettoyé:" + preview
  6. Question: "Voulez-vous continuer?"
     - Oui → Rediriger vers: Topic SélectionOffres
     - Non → Fin
```

#### Topic: Sélection des Offres

```yaml
flow:
  1. Appeler Action: GetOffers()
  2. Variable: offers_list
  3. Afficher Adaptive Card avec liste multi-select
  4. Recueillir: selected_offers
  5. Pour chaque offre:
     - Bouton "Détails" → GetOfferDetails(offer_id)
  6. Question: "Voulez-vous ajouter d'autres offres?"
     - Oui → Retour étape 3
     - Non → Rediriger vers: Topic GénérationFinale
```

#### Topic: Génération Finale

```yaml
flow:
  1. Récapitulatif:
     - Fichier source: {filename}
     - Offres sélectionnées: {count}
  2. Question: "Choisissez le template:"
     - Template Standard
     - Template Premium
     - Template Custom
  3. Variable: selected_template
  4. Appeler Action: GenerateProposal(cleaned_content, selected_offers, selected_template)
  5. Variable: proposal_id, docx_url, pdf_url
  6. Appeler Action: SaveProposal(metadata)
  7. Message avec liens téléchargement:
     - "Votre proposition est prête!"
     - Bouton: Télécharger Word
     - Bouton: Télécharger PDF
  8. Question: "Souhaitez-vous créer une autre proposition?"
     - Oui → Rediriger: Topic NouvelleProposition
     - Non → Message remerciement + Fin
```

---

## CODE - Plan d'Implémentation

### Phase 1: Setup Infrastructure (Semaine 1)

**Jour 1-2: Azure Resources**
- [ ] Créer Resource Group (dev, test, prod)
- [ ] Provisionner Storage Account + containers
- [ ] Créer Function App (Python 3.11)
- [ ] Setup Key Vault
- [ ] Configurer App Registration (Azure AD)
- [ ] Setup Application Insights

**Jour 3-4: Dataverse Setup**
- [ ] Créer environnement Power Platform
- [ ] Créer table Offres avec colonnes
- [ ] Créer table Propositions avec colonnes
- [ ] Créer table Templates avec colonnes
- [ ] Configurer sécurité et rôles
- [ ] Importer données test

**Jour 5: SharePoint & Power Automate (Upload Workaround)**
- [ ] **SharePoint Library Setup**
  - Créer site SharePoint: "Proposal Generator"
  - Créer document library: "Devis Sources"
  - Permissions: Département entier (Contribute)
  - Activer versionning (optionnel)

- [ ] **Power Automate Flow: File Upload Handler**
  - Trigger: "When a file is created" (SharePoint)
  - Actions:
    1. Get file content (SharePoint)
    2. Generate unique file_id (GUID)
    3. Upload to Blob Storage (container: devis-sources)
       - Blob name: {file_id}.docx
    4. Create record in Dataverse (table: cr_uploads_temp)
       - Colonnes: file_id, original_filename, blob_url, upload_date, status
    5. Optionnel: Notify Copilot ou user via Teams
  - Test avec fichier .docx

- [ ] **Dataverse Table: cr_uploads_temp**
  - file_id (Primary Key, Text)
  - original_filename (Text, 255 chars)
  - blob_url (URL)
  - upload_date (DateTime)
  - status (Choice: Uploaded, Processing, Completed, Error)
  - processed_by_user (Lookup → systemuser)

**Jour 5 bis: Project Structure**
- [ ] Initialiser Git repository
- [ ] Créer structure de dossiers
- [ ] Setup requirements.txt
- [ ] Configurer host.json
- [ ] Créer local.settings.json
- [ ] Setup .gitignore

### Phase 2: Azure Functions Core (Semaines 2-3)

**Semaine 2: DocumentProcessor**
- [ ] Créer shared/blob_client.py
- [ ] Créer shared/auth_helper.py
- [ ] ~~Implémenter upload_handler.py~~ (NON NÉCESSAIRE - Power Automate gère upload)
- [ ] Implémenter extract_handler.py
  - Lecture .docx avec python-docx
  - Extraction texte et structure
  - Extraction tableaux
  - Retour JSON structuré
- [ ] Implémenter clean_handler.py
  - Règles de nettoyage
  - Normalisation tableaux
  - Suppression données renseignées
- [ ] Tests unitaires DocumentProcessor

**Semaine 3: OfferManager + ProposalGenerator**
- [ ] Créer shared/dataverse_client.py
- [ ] Implémenter get_offers.py
  - Connexion Dataverse
  - Query table Offres
  - Filtrage et tri
- [ ] Implémenter get_offer_details.py
  - Récupération détails offre
- [ ] Implémenter generate_handler.py
  - Chargement template Blob
  - Insertion offres sélectionnées
  - Génération .docx
- [ ] Implémenter pdf_converter.py
  - Conversion .docx → PDF
  - Upload PDF Blob Storage
- [ ] Implémenter save_handler.py
  - Enregistrement Dataverse
  - Liaison Blob URLs
- [ ] Tests unitaires complets

### Phase 3: Copilot Studio (Semaine 4)

**Jour 1-2: Configuration**
- [ ] Créer Copilot dans Power Virtual Agents
- [ ] Configurer authentification Azure AD
- [ ] Connecter Dataverse
- [ ] Tester connexion

**Jour 3-4: Custom Actions**
- [ ] ~~Action: UploadDocument~~ (NON NÉCESSAIRE - Power Automate gère upload)
- [ ] Action: GetUploadedFile
  - Input: filename ou user_id (récupère dernier upload)
  - Query Dataverse table cr_uploads_temp
  - Output: file_id, blob_url, original_filename
- [ ] Action: ExtractContent
- [ ] Action: CleanDocument
- [ ] Action: GetOffers
- [ ] Action: GetOfferDetails
- [ ] Action: GenerateProposal
- [ ] Tester chaque action individuellement

**Jour 5: Topics Creation**
- [ ] Topic: Nouvelle Proposition
- [ ] Topic: Traitement du Document
- [ ] Topic: Sélection des Offres
- [ ] Topic: Génération Finale
- [ ] Topic: Consulter Historique
- [ ] Test end-to-end workflow

### Phase 4: Adaptive Cards & UX (Semaine 5)

- [ ] Design Adaptive Card: Liste offres
- [ ] Design Adaptive Card: Détails offre
- [ ] Design Adaptive Card: Récapitulatif
- [ ] Design Adaptive Card: Téléchargement
- [ ] Intégration dans Topics
- [ ] Tests utilisateurs pilotes
- [ ] Ajustements UX

### Phase 5: Power Automate Flows (Semaine 5)

- [ ] Flow: Email notification après génération
- [ ] Flow: Archivage automatique
- [ ] Flow: Workflow approbation (optionnel)
- [ ] Tests flows

---

## TEST - Stratégie de Validation

### Tests Unitaires

**DocumentProcessor:**
```python
# test_upload_handler.py
def test_upload_valid_docx():
    # Given: fichier .docx valide
    # When: appel upload_handler
    # Then: blob_url retourné, fichier dans storage

def test_upload_invalid_format():
    # Given: fichier .pdf
    # When: appel upload_handler
    # Then: erreur 400, message validation

# test_extract_handler.py
def test_extract_simple_document():
    # Given: document avec texte simple
    # When: appel extract_handler
    # Then: texte extrait correctement

def test_extract_document_with_tables():
    # Given: document avec tableaux
    # When: appel extract_handler
    # Then: tableaux détectés et structurés

# test_clean_handler.py
def test_clean_removes_filled_data():
    # Given: document avec données renseignées
    # When: appel clean_handler
    # Then: données supprimées, structure conservée
```

**OfferManager:**
```python
# test_get_offers.py
def test_get_all_offers():
    # Given: 10 offres actives dans Dataverse
    # When: GET /api/offers
    # Then: 10 offres retournées

def test_filter_by_category():
    # Given: offres mixtes
    # When: GET /api/offers?category=Services
    # Then: uniquement offres Services retournées
```

**ProposalGenerator:**
```python
# test_generate_handler.py
def test_generate_proposal_with_offers():
    # Given: template + 2 offres sélectionnées
    # When: appel generate_handler
    # Then: .docx généré avec offres insérées

def test_pdf_conversion():
    # Given: .docx généré
    # When: appel pdf_converter
    # Then: PDF créé, même contenu
```

### Tests d'Intégration

**End-to-End:**
```python
# test_end_to_end.py
def test_full_workflow():
    # 1. Upload devis source
    # 2. Extract content
    # 3. Clean document
    # 4. Get offers
    # 5. Select 2 offers
    # 6. Generate proposal
    # 7. Convert to PDF
    # 8. Save to Dataverse
    # 9. Verify all steps succeeded
    # 10. Verify files in Blob Storage
    # 11. Verify record in Dataverse
```

**Copilot Integration:**
```python
# test_copilot_integration.py
def test_custom_actions():
    # Test chaque custom action depuis Copilot
    # Vérifier réponses et gestion erreurs

def test_conversation_flow():
    # Simuler conversation utilisateur
    # Vérifier transitions entre topics
```

### Tests de Performance

```python
# test_performance.py
def test_document_processing_time():
    # Given: document 10 pages
    # When: extract + clean
    # Then: < 10 secondes

def test_concurrent_requests():
    # Given: 10 utilisateurs simultanés
    # When: chacun génère proposition
    # Then: toutes réussies, temps acceptable

def test_large_file_handling():
    # Given: .docx 50 MB
    # When: upload
    # Then: succès ou erreur explicite
```

### Critères de Succès

**Fonctionnels:**
- ✅ Upload document .docx réussi
- ✅ Extraction complète (texte + tableaux)
- ✅ Nettoyage conforme aux règles
- ✅ Récupération offres Dataverse
- ✅ Génération .docx avec offres
- ✅ Conversion PDF fonctionnelle
- ✅ Sauvegarde Dataverse complète
- ✅ Workflow Copilot fluide

**Non-Fonctionnels:**
- ✅ Temps traitement < 30 sec (end-to-end)
- ✅ Support fichiers jusqu'à 25 MB
- ✅ Disponibilité > 99%
- ✅ Authentification sécurisée
- ✅ Logging complet (Application Insights)
- ✅ Gestion erreurs gracieuse

**Qualité Code:**
- ✅ Couverture tests > 80%
- ✅ Pas de secrets en dur
- ✅ Documentation complète
- ✅ Code review passé

---

## Timeline Estimé

| Phase | Durée | Activités Principales |
|-------|-------|----------------------|
| **Phase 1: Infrastructure** | 1 semaine | Azure setup, Dataverse, Git |
| **Phase 2: Azure Functions** | 2 semaines | 3 functions + shared code |
| **Phase 3: Copilot Studio** | 1 semaine | Topics + Custom Actions |
| **Phase 4: UX/Adaptive Cards** | 1 semaine | Design + intégration |
| **Phase 5: Flows & Tests** | 1 semaine | Power Automate + tests complets |
| **Phase 6: Déploiement** | 3 jours | Prod deployment + monitoring |
| **Phase 7: Documentation** | 2 jours | Guides + formation |

**Total estimé: 6-7 semaines**

---

## Prochaines Actions Immédiates

1. **Choisir langage Azure Functions:**
   - Python 3.11 (recommandé) ou TypeScript/Node.js 18+

2. **Accès Azure:**
   - Vérifier accès Azure Portal
   - Permissions nécessaires (Contributor sur subscription)

3. **Accès Power Platform:**
   - Vérifier accès environnement Power Platform
   - Permissions Dataverse

4. **Setup local:**
   - Installer Azure Functions Core Tools
   - Installer Python 3.11 + pip
   - Installer VS Code + extensions
   - Installer Git

5. **Commencer Phase 1.2:**
   - Initialiser structure projet
   - Premier commit Git

---

**Statut: PLAN VALIDÉ - Prêt pour CODE**
