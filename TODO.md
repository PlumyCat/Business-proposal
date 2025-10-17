# TODO - Business Proposal Generator

> **Note:** Pour le plan d'action détaillé EPCT (Explore-Plan-Code-Test), consulter `EPCT.md`

## Architecture Validée ✅

**Stack Technique:**
- Backend: Azure Functions (Python 3.11 - recommandé)
- Interface: Copilot Studio + Teams App
- **Upload Fichiers**: SharePoint Library + Power Automate → Blob Storage (workaround limitation Copilot)
- Stockage: Azure Blob Storage
- Base de données: Dataverse
- Format entrée: Word (.docx)
- Format sortie: Word (.docx) + PDF
- Authentification: Azure AD (Entra ID)

**Note Importante:** Copilot Studio ne gère pas nativement les pièces jointes. Le workflow d'upload utilise SharePoint comme zone de dépôt temporaire.

**Timeline Estimé:** 6-7 semaines

---

## Méthodologie EPCT

### ✅ EXPLORE (Complété)
- Analyse codebase et requirements
- Identification dépendances Azure/Copilot
- Revue contraintes et limitations

### ✅ PLAN (Complété)
- Architecture détaillée dans `EPCT.md`
- Schémas API et Dataverse
- Workflows Copilot Studio
- Timeline et ressources

### 🔄 CODE (En cours)
- Implémentation incrémentale
- Standards de code
- Gestion erreurs
- Documentation inline

### ⏳ TEST (À venir)
- Tests unitaires (80%+ couverture)
- Tests intégration
- Tests performance
- Validation utilisateurs

---

## Phase 1: Infrastructure Azure & Setup Projet (Semaine 1)

### 1.1 Ressources Azure à Provisionner (Jour 1-2)

**EPCT Référence:** `EPCT.md` - Phase 1, Semaine 1, Jour 1-2

- [ ] **Azure Resource Group**
  - Créer resource groups: `rg-proposals-dev`, `rg-proposals-test`, `rg-proposals-prod`
  - Location: choisir région Azure

- [ ] **Azure Storage Account**
  - Nom: `stproposalsXXXX` (XXXX = suffix unique)
  - Containers: `templates`, `devis-sources`, `propositions-generated`
  - Configuration CORS pour Copilot Studio
  - Lifecycle management: suppression après 90 jours (devis-sources)
  - Redundancy: LRS (dev), GRS (prod)

- [ ] **Azure Function App**
  - Nom: `func-proposals-XXXX`
  - Runtime: **Python 3.11** (recommandé)
  - Plan: Consumption (peut passer Premium si besoin)
  - Application Insights: activé
  - Variables env: connexions Dataverse, Blob Storage, Key Vault

- [ ] **Azure Key Vault**
  - Nom: `kv-proposals-XXXX`
  - Secrets à stocker:
    - `DataverseUrl`
    - `DataverseClientId`
    - `DataverseClientSecret`
    - `BlobStorageConnectionString`

- [ ] **Azure AD App Registration**
  - Nom: `app-proposals-functions`
  - API Permissions:
    - Dataverse (user_impersonation)
    - Storage Blob Data Contributor
  - Client Secret créé et stocké dans Key Vault

### 1.2 Dataverse Setup (Jour 3-4)

**EPCT Référence:** `EPCT.md` - Phase 1, Semaine 1, Jour 3-4

- [ ] **Environnement Power Platform**
  - Créer environnement: `Proposals - Dev`
  - Type: Sandbox avec Dataverse
  - Région: même que Azure

- [ ] **Table: cr_offres**
  - Créer table avec schéma défini dans `EPCT.md`
  - Colonnes: nom, description, catégorie, prix, éléments_inclus, actif
  - Forms et vues configurées

- [ ] **Table: cr_propositions**
  - Créer table avec schéma défini dans `EPCT.md`
  - Colonnes: nom_client, statut, offres_incluses, liens docx/pdf, notes, créé_par
  - Relations: lookup vers cr_offres (N:N)

- [ ] **Table: cr_templates**
  - Créer table avec schéma défini dans `EPCT.md`
  - Colonnes: nom, description, blob_url, version, actif

- [ ] **Sécurité Dataverse**
  - Créer rôle personnalisé: `Proposal Generator User`
  - Permissions: CRUD sur 3 tables
  - Assigner utilisateurs test

- [ ] **Table: cr_uploads_temp** (Workaround upload SharePoint)
  - file_id (Text, unique)
  - original_filename (Text, 255)
  - blob_url (URL)
  - upload_date (DateTime)
  - status (Choice: Uploaded, Processing, Completed, Error)
  - processed_by (Lookup user)

- [ ] **Données Initiales**
  - Importer 5-10 offres exemple
  - Créer 2-3 templates test

### 1.3 SharePoint & Power Automate Setup (Jour 5)

**IMPORTANT: Workaround limitation Copilot Studio (pas de support pièces jointes)**

- [ ] **SharePoint Library**
  - Créer site SharePoint: "Proposal Generator"
  - Créer document library: "Devis Sources"
  - Permissions: Département entier (Contribute)
  - Versionning activé (optionnel)

- [ ] **Power Automate Flow: File Upload Handler**
  - Nom: "Upload Devis to Blob Storage"
  - Trigger: "When a file is created" (SharePoint - Devis Sources)
  - Actions:
    1. Get file content
    2. Generate unique file_id (GUID)
    3. Upload to Blob Storage (container: devis-sources, name: {file_id}.docx)
    4. Create record in Dataverse cr_uploads_temp
    5. Optionnel: Teams notification
  - Test avec fichier .docx

### 1.4 Structure du Projet Local (Jour 5 bis)

**EPCT Référence:** `EPCT.md` - Phase 1, Semaine 1, Jour 5

- [ ] **Git Repository**
  - `git init`
  - Créer repo distant (GitHub/Azure DevOps)
  - Premier commit avec structure

- [ ] **Structure de Dossiers**
  ```
  business-proposal-generator/
  ├── functions/
  │   ├── DocumentProcessor/
  │   ├── OfferManager/
  │   ├── ProposalGenerator/
  │   └── shared/
  ├── copilot/
  ├── dataverse/
  ├── infrastructure/
  ├── tests/
  └── docs/
  ```

- [ ] **Fichiers Configuration**
  - `requirements.txt` (Python packages)
  - `host.json` (Azure Functions config)
  - `local.settings.json` (variables locales - NOT in git)
  - `.gitignore` (secrets, local settings, __pycache__, etc.)
  - `README.md` (guide démarrage)
  - `.env.example` (template variables env)

- [ ] **Setup Développement Local**
  - Installer Azure Functions Core Tools v4
  - Installer Python 3.11
  - Créer virtual environment: `python -m venv .venv`
  - Activer venv et installer packages: `pip install -r requirements.txt`
  - Configurer VS Code (extensions recommandées)

---

## Phase 2: Développement Azure Functions (Semaines 2-3)

**EPCT Référence:** `EPCT.md` - Phase 2, Semaines 2-3

### 2.1 Function: DocumentProcessor (HTTP Trigger) - Semaine 2

- [ ] **Endpoint: UploadDocument**
  - Recevoir fichier .docx depuis Copilot Studio
  - Valider le format et la taille
  - Upload vers Blob Storage
  - Retourner blob URL

- [ ] **Endpoint: ExtractContent**
  - Lire le fichier .docx depuis Blob Storage
  - Utiliser `python-docx` (Python) ou `mammoth` (TypeScript)
  - Extraire le texte structuré
  - Détecter et extraire les tableaux
  - Retourner JSON structuré

- [ ] **Endpoint: CleanDocument**
  - Recevoir le contenu extrait
  - Appliquer règles de nettoyage:
    - Supprimer anciennes données renseignées
    - Normaliser les tableaux
    - Conserver la structure du template
  - Retourner document nettoyé

### 2.2 Function: OfferManager (HTTP Trigger) - Semaine 3

- [ ] **Endpoint: GetOffers**
  - Connexion à Dataverse
  - Récupérer la liste des offres disponibles
  - Filtrage et recherche (optionnel)
  - Retourner liste formatée pour Copilot Studio

- [ ] **Endpoint: GetOfferDetails**
  - Récupérer détails d'une offre spécifique
  - Inclure description, tarifs, éléments

### 2.3 Function: ProposalGenerator (HTTP Trigger) - Semaine 3

- [ ] **Endpoint: GenerateProposal**
  - Recevoir:
    - Document nettoyé
    - Liste des offres sélectionnées
    - Template à utiliser
  - Charger le template depuis Blob Storage
  - Insérer les éléments sélectionnés
  - Générer Word (.docx) avec `python-docx` ou `docxtemplater`
  - Sauvegarder vers Blob Storage

- [ ] **Endpoint: ConvertToPDF**
  - Convertir .docx vers PDF
  - Options:
    - LibreOffice headless
    - Azure Logic Apps (Word Online connector)
    - Service tiers (CloudConvert, etc.)
  - Sauvegarder PDF vers Blob Storage

- [ ] **Endpoint: SaveProposal**
  - Enregistrer métadonnées dans Dataverse
  - Lien vers fichiers Blob Storage
  - Historique et traçabilité

### 2.4 Code Partagé

- [ ] Module de connexion Dataverse
- [ ] Module de connexion Blob Storage
- [ ] Utilitaires de validation
- [ ] Gestion des erreurs et logging
- [ ] Authentication helpers

---

---

## Phase 3: Copilot Studio (Semaine 4)

**EPCT Référence:** `EPCT.md` - Phase 3, Semaine 4

### 3.1 Configuration Copilot (Jour 1-2)

- [ ] **Créer Copilot**
  - Nouveau Copilot dans Power Virtual Agents
  - Nom: "Proposal Generator Assistant"
  - Description et instructions système

- [ ] **Authentification**
  - Configurer Azure AD authentication
  - Permissions utilisateurs
  - Test connexion

- [ ] **Connexion Dataverse**
  - Connecter à environnement Dataverse
  - Vérifier accès tables cr_offres, cr_propositions, cr_templates
  - Test queries

- [ ] **Déploiement Teams**
  - Publier sur Microsoft Teams
  - Configuration icône et description
  - Test dans Teams

### 3.2 Custom Actions (Jour 3-4)

- [ ] ~~**Action: UploadDocument**~~ (NON NÉCESSAIRE - Power Automate gère)

- [ ] **Action: GetUploadedFile**
  - Query Dataverse table cr_uploads_temp
  - Input: filename OU user_id (dernier upload)
  - Output: file_id, blob_url, original_filename
  - Test et debug

- [ ] **Action: ExtractContent**
  - Input: file_id
  - Output: extracted_content (JSON)
  - Gestion erreurs et timeout

- [ ] **Action: CleanDocument**
  - Input: extracted_content
  - Output: cleaned_content
  - Test avec différents formats

- [ ] **Action: GetOffers**
  - Input: filters (optionnel)
  - Output: offers_list
  - Pagination si nécessaire

- [ ] **Action: GetOfferDetails**
  - Input: offer_id
  - Output: offer_details
  - Gestion offre inexistante

- [ ] **Action: GenerateProposal**
  - Input: cleaned_content, selected_offers, template_id
  - Output: proposal_id, docx_url, pdf_url
  - Gestion timeout (peut être long)

### 3.3 Topics/Conversations (Jour 5)

- [ ] **Topic: Nouvelle Proposition**
  - Trigger phrases
  - Message: Instructions upload SharePoint
  - Adaptive Card: Lien vers SharePoint Library + bouton "Ouvrir"
  - Attendre notification ou polling Dataverse (cr_uploads_temp)
  - Appel GetUploadedFile (récupération file_id)
  - Messages confirmation avec filename
  - Redirection vers Traitement

- [ ] **Topic: Traitement du Document**
  - Appel ExtractContent
  - Appel CleanDocument
  - Affichage aperçu
  - Validation utilisateur
  - Redirection vers Sélection

- [ ] **Topic: Sélection des Offres**
  - Appel GetOffers
  - Affichage Adaptive Cards (liste)
  - Sélection multiple
  - Détails à la demande
  - Confirmation sélection
  - Redirection vers Génération

- [ ] **Topic: Génération Finale**
  - Récapitulatif
  - Choix template
  - Appel GenerateProposal
  - Affichage liens téléchargement
  - Proposition nouvelle génération

- [ ] **Topic: Consulter Historique**
  - Query Dataverse propositions
  - Affichage liste
  - Téléchargement fichiers existants

### 3.4 Power Automate Flows (Optionnel)

- [ ] **Flow: Email Notification**
  - Trigger: nouvelle proposition générée
  - Action: envoyer email avec liens
  - Test

- [ ] **Flow: Archivage Auto**
  - Trigger: planifié (quotidien)
  - Condition: propositions > 90 jours
  - Action: déplacer Blob Storage archive

---

## Phase 4: Tests & Documentation (Semaine 5)

**EPCT Référence:** `EPCT.md` - Phase 4-5, Semaine 5

### 4.1 Tests Unitaires

- [ ] Tests DocumentProcessor (upload, extract, clean)
- [ ] Tests OfferManager (get offers, get details)
- [ ] Tests ProposalGenerator (generate, convert PDF)
- [ ] Tests shared modules (blob, dataverse, auth)
- [ ] Couverture > 80%

### 4.2 Tests Intégration

- [ ] Test workflow complet end-to-end
- [ ] Test avec différents formats devis
- [ ] Test avec différentes combinaisons offres
- [ ] Test génération PDF
- [ ] Test Copilot integration

### 4.3 Tests Performance

- [ ] Temps traitement < 30 sec end-to-end
- [ ] Support fichiers jusqu'à 25 MB
- [ ] Test charge (10 utilisateurs simultanés)

### 4.4 Tests Utilisateurs

- [ ] Identifier 3-5 utilisateurs pilotes
- [ ] Session test guidée
- [ ] Collecte feedback
- [ ] Ajustements UX

### 4.5 Documentation

- [ ] Guide utilisateur (avec screenshots)
- [ ] Documentation technique API
- [ ] Guide déploiement
- [ ] Procédures maintenance
- [ ] Troubleshooting guide

---

## Phase 5: Déploiement Production (Semaine 6)

### 5.1 Préparation Prod

- [ ] Créer ressources Azure prod
- [ ] Créer environnement Dataverse prod
- [ ] Migrer données (offres, templates)
- [ ] Configuration secrets Key Vault prod
- [ ] Tests smoke prod

### 5.2 Déploiement

- [ ] Déployer Azure Functions prod
- [ ] Publier Copilot Studio prod
- [ ] Déployer Teams App prod
- [ ] Configuration monitoring Application Insights
- [ ] Alertes configurées

### 5.3 Formation & Lancement

- [ ] Session formation utilisateurs
- [ ] Documentation distribuée
- [ ] Support contact établi
- [ ] Annonce lancement

---

## Phase 6: Améliorations Futures (Backlog)

**À prioriser après phase de stabilisation (2-4 semaines post-lancement)**

- [ ] Suggestions automatiques offres par IA (Azure OpenAI)
- [ ] Support format PDF en entrée (Azure Document Intelligence)
- [ ] Templates multiples et personnalisables
- [ ] Analytics et reporting (Power BI)
- [ ] Intégration CRM (Dynamics 365)
- [ ] Export Excel pour budgets
- [ ] Comparaison propositions côte-à-côte
- [ ] Workflow approbation multi-niveaux
- [ ] Versioning propositions
- [ ] Signature électronique

---

## ANNEXE: Ancienne Phase 3 (référence Dataverse - déjà couverte Phase 1.2)

~~## Phase 3: Configuration Dataverse~~

### 3.1 Table: Offres

- [ ] Créer table `Offres` avec colonnes:
  - Nom de l'offre (texte)
  - Description (multiligne)
  - Catégorie (choix)
  - Prix (devise)
  - Éléments inclus (multiligne)
  - Actif (oui/non)
  - Date création/modification

- [ ] Importer données initiales des offres

### 3.2 Table: Propositions

- [ ] Créer table `Propositions` avec colonnes:
  - Nom du client
  - Date de création
  - Créé par (lookup user)
  - Statut (brouillon/envoyé/accepté/refusé)
  - Offres incluses (lookup multiple)
  - Lien document Word (URL)
  - Lien document PDF (URL)
  - Notes

### 3.3 Table: Templates

- [ ] Créer table `Templates` avec colonnes:
  - Nom du template
  - Description
  - Lien Blob Storage
  - Version
  - Actif (oui/non)

### 3.4 Sécurité Dataverse

- [ ] Configurer rôles de sécurité
- [ ] Permissions par département
- [ ] Audit activé

---

## Phase 4: Copilot Studio

### 4.1 Configuration du Copilot

- [ ] Créer nouveau Copilot dans Power Virtual Agents
- [ ] Configurer l'authentification (Azure AD)
- [ ] Connecter à Dataverse
- [ ] Déployer sur Teams

### 4.2 Topics (Conversations)

- [ ] **Topic: Nouvelle Proposition**
  - Salutation et explication du processus
  - Demander upload du devis source
  - Appeler Function `UploadDocument`
  - Afficher confirmation

- [ ] **Topic: Traitement du Document**
  - Appeler Function `ExtractContent`
  - Appeler Function `CleanDocument`
  - Afficher aperçu du contenu nettoyé
  - Demander validation utilisateur

- [ ] **Topic: Sélection des Offres**
  - Appeler Function `GetOffers`
  - Afficher liste des offres (Adaptive Cards)
  - Permettre sélection multiple
  - Afficher détails sur demande (`GetOfferDetails`)

- [ ] **Topic: Génération Finale**
  - Récapitulatif des sélections
  - Choix du template
  - Appeler Function `GenerateProposal`
  - Appeler Function `ConvertToPDF`
  - Appeler Function `SaveProposal`
  - Fournir liens de téléchargement

- [ ] **Topic: Consulter Historique**
  - Rechercher dans Dataverse table `Propositions`
  - Afficher propositions précédentes
  - Télécharger documents existants

### 4.3 Custom Actions

- [ ] Action pour appeler chaque Azure Function
- [ ] Gestion des erreurs et retry logic
- [ ] Timeout configuration

### 4.4 Power Automate Flows (si nécessaire)

- [ ] Flow: Notification email après génération
- [ ] Flow: Archivage automatique après X jours
- [ ] Flow: Workflow d'approbation (optionnel)

---

## Phase 5: Tests & Validation

### 5.1 Tests Unitaires

- [ ] Tests des fonctions d'extraction
- [ ] Tests des fonctions de génération
- [ ] Tests des connexions Dataverse
- [ ] Tests des opérations Blob Storage

### 5.2 Tests d'Intégration

- [ ] Test du workflow complet end-to-end
- [ ] Test avec différents formats de devis
- [ ] Test avec différentes combinaisons d'offres
- [ ] Test de génération PDF

### 5.3 Tests Utilisateurs

- [ ] Test avec utilisateurs pilotes
- [ ] Collecte de feedback
- [ ] Ajustements UI/UX dans Copilot Studio

### 5.4 Tests de Performance

- [ ] Test de montée en charge
- [ ] Temps de traitement des documents
- [ ] Optimisation si nécessaire

---

## Phase 6: Déploiement & Documentation

### 6.1 Déploiement

- [ ] Déploiement Azure Functions en prod
- [ ] Publication Copilot Studio
- [ ] Déploiement Teams App
- [ ] Configuration monitoring et alertes

### 6.2 Documentation

- [ ] Guide utilisateur (avec captures d'écran)
- [ ] Documentation technique (architecture, API)
- [ ] Procédures de maintenance
- [ ] Guide de troubleshooting

### 6.3 Formation

- [ ] Session de formation utilisateurs
- [ ] Documentation vidéo (optionnel)
- [ ] Support contact et escalation

---

## Phase 7: Améliorations Futures (Backlog)

- [ ] Suggestions automatiques d'offres par IA
- [ ] Support d'autres formats d'entrée (PDF)
- [ ] Templates multiples et personnalisables
- [ ] Analytics et reporting
- [ ] Intégration CRM
- [ ] Export Excel pour budgets
- [ ] Comparaison de propositions

---

**🚀 PROCHAINE ÉTAPE: Commencer Phase 1 - Provisionner les ressources Azure**
