# Schémas Dataverse - Business Proposal Generator

## ⚠️ IMPORTANT: Code Langue 1033 (Anglais)

**Limitation MCP Microsoft:**
- Le MCP Microsoft ne supporte que le code langue **1033 (Anglais US)**
- Il faut activer la langue anglaise dans l'environnement Dataverse avant de créer les tables
- Les noms logiques et Display Names doivent être en anglais pour le MCP

**Configuration préalable:**
1. Accéder à Power Platform Admin Center
2. Sélectionner l'environnement
3. Settings > Languages
4. Activer "English (United States)" (1033)
5. Attendre la provisioning (peut prendre 10-15 minutes)

---

## Table 1: cr_offres (Offers)

**Description:** Catalogue des offres/services disponibles pour inclusion dans les propositions.

**Note:** Cette table est gérée par un autre bot Copilot. Notre bot a uniquement accès en **lecture**.

### Colonnes

| Display Name | Logical Name | Type | Required | Max Length | Description |
|--------------|--------------|------|----------|------------|-------------|
| Name | cr_name | Single Line of Text | ✅ Yes | 255 | Nom de l'offre |
| Description | cr_description | Multiple Lines of Text | ❌ No | 4000 | Description détaillée de l'offre |
| Category | cr_category | Choice | ✅ Yes | - | Catégorie de l'offre |
| Unit Price | cr_unit_price | Currency | ✅ Yes | - | Prix unitaire (€) |
| Unit | cr_unit | Choice | ✅ Yes | - | Unité de tarification |
| Reference | cr_reference | Single Line of Text | ❌ No | 100 | Référence/Code produit |
| Included Elements | cr_included_elements | Multiple Lines of Text | ❌ No | 4000 | Liste des éléments inclus |
| Active | cr_active | Two Options (Yes/No) | ✅ Yes | - | Offre active/disponible |

### Choices (Picklists)

**cr_category:**
- `consulting` - Consulting Services
- `development` - Development
- `infrastructure` - Infrastructure
- `support` - Support & Maintenance
- `training` - Training
- `other` - Other

**cr_unit:**
- `hour` - Hour
- `day` - Day
- `month` - Month
- `year` - Year
- `unit` - Unit
- `package` - Package

### Permissions

- **Lecture:** ✅ Proposal Generator Bot (via Copilot Studio Dataverse connector)
- **Écriture:** ❌ Géré par autre bot (OfferManager)

---

## Table 2: cr_propositions (Proposals)

**Description:** Métadonnées des propositions générées (liens vers fichiers Word/PDF, client, offres incluses).

### Colonnes

| Display Name | Logical Name | Type | Required | Max Length | Description |
|--------------|--------------|------|----------|------------|-------------|
| Proposal Number | cr_proposal_number | Single Line of Text | ✅ Yes | 100 | Numéro unique (PROP-YYYYMMDD-XXXXX) |
| Client Name | cr_client_name | Single Line of Text | ✅ Yes | 255 | Nom du client |
| Client Contact | cr_client_contact | Single Line of Text | ✅ Yes | 255 | Nom du contact client |
| Client Email | cr_client_email | Email | ✅ Yes | 255 | Email du contact |
| Status | cr_status | Choice | ✅ Yes | - | Statut de la proposition |
| Word Document URL | cr_word_url | URL | ✅ Yes | 2000 | Lien Blob Storage .docx |
| PDF Document URL | cr_pdf_url | URL | ❌ No | 2000 | Lien Blob Storage .pdf |
| Word Blob Name | cr_word_blob_name | Single Line of Text | ✅ Yes | 500 | Nom du blob Word |
| PDF Blob Name | cr_pdf_blob_name | Single Line of Text | ❌ No | 500 | Nom du blob PDF |
| Offer IDs | cr_offer_ids | Multiple Lines of Text | ✅ Yes | 4000 | JSON array des GUIDs offres |
| Offer Count | cr_offer_count | Whole Number | ✅ Yes | - | Nombre d'offres incluses |
| Template Used | cr_template_used | Single Line of Text | ✅ Yes | 255 | Nom du template utilisé |
| Generated Date | cr_generated_date | Date and Time | ✅ Yes | - | Date de génération |
| Notes | cr_notes | Multiple Lines of Text | ❌ No | 4000 | Notes internes |

### Choices (Picklists)

**cr_status:**
- `draft` - Draft
- `sent` - Sent to Client
- `accepted` - Accepted
- `rejected` - Rejected
- `expired` - Expired

### Relations

- **Created By:** System field (Owner)
- **Modified By:** System field

### Permissions

- **Lecture:** ✅ Tous les utilisateurs autorisés
- **Écriture:** ✅ Proposal Generator Function (via service principal)
- **Suppression:** ❌ Administrateurs uniquement

---

## Table 3: cr_templates (Document Templates)

**Description:** Templates Word (.docx) utilisés pour générer les propositions.

### Colonnes

| Display Name | Logical Name | Type | Required | Max Length | Description |
|--------------|--------------|------|----------|------------|-------------|
| Template Name | cr_template_name | Single Line of Text | ✅ Yes | 255 | Nom du template |
| Description | cr_description | Multiple Lines of Text | ❌ No | 2000 | Description du template |
| Blob URL | cr_blob_url | URL | ✅ Yes | 2000 | URL Blob Storage du .docx |
| Blob Name | cr_blob_name | Single Line of Text | ✅ Yes | 500 | Nom du fichier blob |
| Version | cr_version | Single Line of Text | ✅ Yes | 50 | Version (ex: 1.0, 1.1) |
| Active | cr_active | Two Options (Yes/No) | ✅ Yes | - | Template actif/disponible |
| Language | cr_language | Choice | ✅ Yes | - | Langue du template |
| Last Updated | cr_last_updated | Date and Time | ✅ Yes | - | Date dernière mise à jour |

### Choices (Picklists)

**cr_language:**
- `fr` - French
- `en` - English
- `de` - German
- `es` - Spanish

### Permissions

- **Lecture:** ✅ Tous les utilisateurs autorisés
- **Écriture:** ✅ Administrateurs uniquement
- **Suppression:** ❌ Administrateurs uniquement

### Données Initiales

Créer au moins 1 template par défaut:
- **Name:** "Default Proposal Template"
- **Version:** "1.0"
- **Active:** Yes
- **Language:** fr
- **Blob Name:** "default_template.docx"
- **Blob URL:** (à remplir après upload dans Blob Storage)

---

## Table 4: cr_uploads_temp (Temporary Upload Tracking)

**Description:** Table temporaire pour tracker les fichiers uploadés via SharePoint → Power Automate → Blob Storage.

**Workflow:**
1. User upload .docx → SharePoint Library "Devis Sources"
2. Power Automate détecte nouveau fichier
3. Power Automate crée record dans cr_uploads_temp avec file_id
4. Power Automate upload vers Blob Storage
5. Copilot query cette table pour récupérer le file_id du dernier upload

### Colonnes

| Display Name | Logical Name | Type | Required | Max Length | Description |
|--------------|--------------|------|----------|------------|-------------|
| File ID | cr_file_id | Single Line of Text | ✅ Yes | 100 | GUID unique du fichier |
| Original Filename | cr_original_filename | Single Line of Text | ✅ Yes | 255 | Nom du fichier original |
| Blob URL | cr_blob_url | URL | ✅ Yes | 2000 | URL dans Blob Storage |
| Blob Name | cr_blob_name | Single Line of Text | ✅ Yes | 500 | Nom du blob (file_id.docx) |
| Upload Date | cr_upload_date | Date and Time | ✅ Yes | - | Date d'upload |
| Status | cr_status | Choice | ✅ Yes | - | Statut du traitement |
| Uploaded By | cr_uploaded_by | Lookup (User) | ✅ Yes | - | Utilisateur ayant uploadé |
| Processed Date | cr_processed_date | Date and Time | ❌ No | - | Date de traitement |

### Choices (Picklists)

**cr_status:**
- `uploaded` - Uploaded to Blob Storage
- `processing` - Being Processed
- `completed` - Processing Completed
- `error` - Error Occurred

### Relations

- **Uploaded By:** Lookup to System User table

### Permissions

- **Lecture:** ✅ Tous les utilisateurs autorisés
- **Écriture:** ✅ Power Automate Flow (service account)
- **Suppression:** ✅ Auto-cleanup après 7 jours (via Power Automate)

### Indexation

- Index sur `cr_uploaded_by` + `cr_upload_date` pour requêtes rapides "dernier fichier uploadé par user X"

---

## Sécurité & Rôles

### Rôle: Proposal Generator User

**Permissions:**

| Table | Create | Read | Write | Delete | Append | Append To |
|-------|--------|------|-------|--------|--------|-----------|
| cr_offres | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| cr_propositions | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| cr_templates | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| cr_uploads_temp | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |

### Service Principal (Azure Function)

**Permissions:**
- cr_propositions: Create, Read, Write
- cr_offres: Read
- cr_uploads_temp: Read
- cr_templates: Read

---

## Scripts de Création

### Option 1: Via Power Apps Maker Portal (Recommandé pour débutants)

1. Accéder à https://make.powerapps.com
2. Sélectionner l'environnement
3. Tables > + New table > Add columns and data
4. Créer chaque colonne selon les specs ci-dessus

### Option 2: Via MCP Microsoft (avec bot Copilot)

**IMPORTANT:** S'assurer que la langue 1033 (anglais) est activée !

Exemple de prompt pour le bot:
```
Create a Dataverse table with the following specifications:
- Table Name: cr_offres
- Display Name: Offers
- Primary Name Column: cr_name (max 255 characters)

Add the following columns:
1. cr_description - Multiple Lines of Text, max 4000 chars
2. cr_category - Choice with options: consulting, development, infrastructure, support, training, other
3. cr_unit_price - Currency
4. cr_unit - Choice with options: hour, day, month, year, unit, package
5. cr_reference - Single Line of Text, max 100 chars
6. cr_included_elements - Multiple Lines of Text, max 4000 chars
7. cr_active - Yes/No (default: Yes)
```

### Option 3: Via Solution Export/Import

Un fichier solution Dataverse (.zip) peut être créé une fois les tables configurées et réutilisé pour d'autres environnements.

---

## Nettoyage & Maintenance

### Auto-Cleanup cr_uploads_temp

**Power Automate Flow recommandé:**
- **Déclencheur:** Planifié - Quotidien à 2h00 AM
- **Condition:** cr_upload_date < (Today - 7 days) AND cr_status = "completed"
- **Action:** Delete records

### Archivage cr_propositions

Optionnel: Archiver les propositions > 1 an vers table cr_propositions_archive

---

## Tests Post-Création

### Test 1: cr_offres
```
1. Créer manuellement 3-5 offres exemple
2. Vérifier lecture via Copilot Studio Dataverse connector
3. Tester filtrage par cr_category
4. Tester filtrage cr_active = true
```

### Test 2: cr_propositions
```
1. Créer manuellement 1 proposition test
2. Vérifier les lookups fonctionnent
3. Tester query par cr_uploaded_by
4. Vérifier URL clickables
```

### Test 3: cr_templates
```
1. Créer template "Default Proposal Template"
2. Uploader default_template.docx vers Blob Storage
3. Copier URL et l'ajouter dans cr_blob_url
4. Vérifier cr_active = true
```

### Test 4: cr_uploads_temp
```
1. Créer record test manuellement
2. Simuler Power Automate flow
3. Query "dernier upload par user X"
4. Vérifier lookup vers User
```

---

## Checklist de Création

- [ ] Langue 1033 (Anglais) activée dans l'environnement
- [ ] Table cr_offres créée avec toutes les colonnes
- [ ] Table cr_propositions créée avec toutes les colonnes
- [ ] Table cr_templates créée avec toutes les colonnes
- [ ] Table cr_uploads_temp créée avec toutes les colonnes
- [ ] Tous les Choice fields configurés avec les bonnes options
- [ ] Relations/Lookups configurés
- [ ] Rôle "Proposal Generator User" créé
- [ ] Permissions configurées
- [ ] 3-5 offres exemple créées dans cr_offres
- [ ] 1 template par défaut créé dans cr_templates
- [ ] Tests de lecture via Copilot Studio effectués
- [ ] Service principal Azure Function configuré avec permissions

---

**Note:** Pour un déploiement reproductible, exporter les tables comme Solution Dataverse une fois configurées.
