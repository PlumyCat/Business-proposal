# Limitations Connues - Dataverse & MCP

## ⚠️ CRITIQUE: Code Langue 1033 Requis

### Problème

Le **MCP (Model Context Protocol) Microsoft** utilisé par certains bots Copilot pour créer/gérer des tables Dataverse ne supporte **QUE** le code langue **1033 (Anglais US)**.

### Symptômes

- Erreur lors de la création de tables via MCP si la langue 1033 n'est pas activée
- Impossible d'utiliser le bot pour gérer Dataverse sans cette langue
- Les opérations CRUD via MCP échouent

### Solution

**1. Activer la langue anglaise dans Dataverse:**

1. Accéder à [Power Platform Admin Center](https://admin.powerplatform.microsoft.com/)
2. Sélectionner votre environnement
3. Cliquer sur **Settings** (en haut à droite)
4. Naviguer vers **Product** > **Languages**
5. Cocher **"English (United States)"** (code 1033)
6. Cliquer **Apply**
7. **Attendre 10-20 minutes** pour le provisioning

**2. Vérifier l'activation:**

1. Retourner dans Power Apps Maker Portal
2. Créer une nouvelle table test
3. Vérifier que la langue 1033 est disponible dans les paramètres

### Impact

- **Noms de colonnes:** Doivent avoir des Display Names en anglais pour le MCP
- **Labels:** Les labels en français peuvent être ajoutés **après** création via le portail
- **Documentation:** Utiliser noms anglais dans les schémas techniques, français dans l'UI

### Workaround

Si vous ne pouvez pas activer la langue 1033 :
- Créer les tables manuellement via Power Apps Maker Portal (https://make.powerapps.com)
- Utiliser l'API Dataverse directement (sans passer par le MCP)
- Utiliser des solutions Dataverse pré-configurées (.zip)

### Tables Affectées

Toutes les tables du projet:
- cr_offres
- cr_propositions
- cr_templates
- cr_uploads_temp

---

## Autres Limitations Dataverse

### Limite de Taille des Fichiers

- **Choice fields:** Maximum 100 options par liste
- **Text fields:** Maximum 4000 caractères pour Multiple Lines of Text
- **URL fields:** Maximum 2000 caractères
- **Attachments:** Non utilisés dans ce projet (on utilise Blob Storage à la place)

### Performances

- **Query complexity:** Éviter les requêtes avec plus de 3 niveaux de joins
- **Batch operations:** Maximum 1000 records par batch
- **API rate limits:**
  - 6000 requêtes par 5 minutes par utilisateur
  - 100,000 requêtes par 24h par environnement

### Sécurité

- **Row-level security:** Configurée via Business Units et Security Roles
- **Column-level security:** Possible mais complexe à maintenir
- **Service Principal:** Requiert App Registration Azure AD avec permissions Dataverse

---

## Limitations Copilot Studio

### Connecteur Dataverse Natif

**Avantages:**
- Lecture directe des tables sans Azure Function
- Filtrage et tri natifs
- Pas de coûts supplémentaires

**Limitations:**
- Pas de transactions complexes
- Pas de logique métier côté serveur
- Timeout après 2 minutes pour les requêtes lentes

### Pièces Jointes

**Limitation majeure:** Copilot Studio ne supporte **PAS** nativement l'upload de fichiers.

**Workaround implémenté:**
1. SharePoint Library comme zone de dépôt
2. Power Automate pour détecter et copier vers Blob Storage
3. Dataverse (cr_uploads_temp) pour tracking
4. Copilot query Dataverse pour récupérer le file_id

---

## Limitations Azure Functions

### Timeout

- **Consumption Plan:** Maximum 5 minutes (peut être étendu à 10 minutes)
- **Premium Plan:** Illimité (mais coûteux)

**Impact sur ce projet:**
- Conversion PDF via SharePoint peut prendre 1-2 minutes pour gros fichiers
- Génération de propositions complexes peut prendre 30-60 secondes

**Solution:** Utiliser Premium Plan si nécessaire, ou implémenter pattern async avec polling

### Cold Start

- **Consumption Plan:** 5-20 secondes de latence au premier appel après inactivité
- **Solution:** Premium Plan avec "Always On", ou accepter la latence

---

## Limitations SharePoint

### Conversion PDF

**Limitations:**
- Fichiers > 10 MB peuvent échouer à la conversion
- Conversion peut prendre 30-60 secondes pour fichiers complexes
- Certains formats Word avancés (macros, ActiveX) ne sont pas supportés

**Recommandations:**
- Garder les templates simples
- Limiter les images haute résolution
- Tester la conversion avec différents types de contenu

### API Rate Limits

- **SharePoint API:** 2000 requêtes par heure par utilisateur
- **Impact:** Faible (1 conversion = 3 appels API: upload, download, delete)

---

## Recommandations Générales

### 1. Gestion des Erreurs

Toujours implémenter retry logic pour:
- Appels API Dataverse (rate limiting)
- Conversion PDF SharePoint (timeout)
- Upload Blob Storage (réseau)

### 2. Monitoring

Configurer Application Insights pour tracker:
- Temps de réponse des fonctions
- Erreurs de conversion PDF
- Échecs d'authentification Dataverse

### 3. Documentation

Maintenir ce fichier à jour avec:
- Nouvelles limitations découvertes
- Workarounds implémentés
- Versions des services (API Dataverse, etc.)

---

**Dernière mise à jour:** 2025-10-17
**Version Dataverse API:** 9.2
**Version MCP Microsoft:** Actuelle
