# Guide de Déploiement Azure Functions

Ce guide explique comment déployer les Azure Functions sur Azure dans le resource group `my-word-mcp-rg`.

## 📋 Prérequis

- Azure CLI installé et configuré
- Connexion à la souscription Azure active
- Resource Group: `my-word-mcp-rg` (France Central)
- Storage Account: `mywordmcpacrstorage` (déjà créé)

## 🚀 Étapes de Déploiement

### 1. Créer l'Azure Function App

```bash
# Variables
RESOURCE_GROUP="my-word-mcp-rg"
LOCATION="francecentral"
STORAGE_ACCOUNT="mywordmcpacrstorage"
FUNCTION_APP_NAME="business-proposal-functions"  # Choisir un nom unique
PYTHON_VERSION="3.11"

# Créer le Function App (Plan Consumption)
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP_NAME \
  --storage-account $STORAGE_ACCOUNT \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version $PYTHON_VERSION \
  --functions-version 4 \
  --os-type Linux
```

### 2. Configurer les Variables d'Environnement

```bash
# Blob Storage (utilise le storage account existant)
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "AZURE_STORAGE_CONNECTION_STRING=<CONNECTION_STRING>" \
    "BLOB_CONTAINER_TEMPLATES=word-templates" \
    "BLOB_CONTAINER_DOCUMENTS=word-documents"

# Dataverse
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "DATAVERSE_ENVIRONMENT_URL=https://YOUR_ORG.crm4.dynamics.com" \
    "DATAVERSE_CLIENT_ID=<CLIENT_ID>" \
    "DATAVERSE_CLIENT_SECRET=<CLIENT_SECRET>" \
    "DATAVERSE_TENANT_ID=<TENANT_ID>" \
    "DATAVERSE_TABLE_OFFERS=crb02_offrebeclouds"

# SharePoint
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "SHAREPOINT_SITE_URL=https://YOUR_TENANT.sharepoint.com/sites/YOUR_SITE" \
    "SHAREPOINT_CLIENT_ID=<CLIENT_ID>" \
    "SHAREPOINT_CLIENT_SECRET=<CLIENT_SECRET>" \
    "SHAREPOINT_TENANT_ID=<TENANT_ID>" \
    "SHAREPOINT_LIBRARY_NAME=Documents"
```

### 3. Activer Application Insights (Recommandé)

```bash
# Créer Application Insights
az monitor app-insights component create \
  --app business-proposal-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Récupérer l'instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app business-proposal-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

# Configurer
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY"
```

### 4. Déployer le Code

#### Option A: Déploiement via Azure CLI (Recommandé)

```bash
# Depuis la racine du projet
func azure functionapp publish $FUNCTION_APP_NAME --python
```

#### Option B: Déploiement via GitHub Actions

Voir `.github/workflows/deploy.yml` (à créer si besoin)

#### Option C: Déploiement via VS Code

1. Installer l'extension Azure Functions
2. Clic droit sur le Function App
3. "Deploy to Function App..."

### 5. Vérifier le Déploiement

```bash
# Lister les functions déployées
az functionapp function list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Obtenir les URLs des endpoints
az functionapp function show \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --function-name clean-quote \
  --query invokeUrlTemplate -o tsv
```

### 6. Récupérer la Function Key

⚠️ **IMPORTANT**: Les endpoints sont protégés par function key (`authLevel: "function"`).

```bash
# Récupérer la default host key (fonctionne pour tous les endpoints)
FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv)

echo "Function Key: $FUNCTION_KEY"
```

💡 **Voir `FUNCTION_KEYS.md` pour le guide complet d'utilisation des keys**

### 7. Tester les Endpoints

```bash
# URL de base
FUNCTION_URL="https://$FUNCTION_APP_NAME.azurewebsites.net"

# Récupérer la function key (si pas déjà fait)
FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv)

# Test clean-quote (AVEC FUNCTION KEY)
curl -X POST "$FUNCTION_URL/api/document/clean-quote?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "blob_path": "Eric FER/test.docx",
    "user_folder": "Eric FER"
  }'

# Test prepare-template (AVEC FUNCTION KEY)
curl -X POST "$FUNCTION_URL/api/proposal/prepare-template?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "template.docx",
    "customer_success": {
      "name": "Jean Dupont",
      "tel": "06 12 34 56 78",
      "email": "jean.dupont@company.com"
    },
    "user_folder": "Eric FER"
  }'

# Test generate (AVEC FUNCTION KEY - nécessite des GUIDs réels d'offres)
curl -X POST "$FUNCTION_URL/api/proposal/generate?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "working_file": "Eric FER/temp_working.docx",
    "offer_ids": ["guid1", "guid2"],
    "user_folder": "Eric FER"
  }'
```

## 🔒 Sécurité

### Activer l'Authentification (Optionnel)

Si vous souhaitez sécuriser les endpoints avec Azure AD :

```bash
az functionapp auth update \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --enabled true \
  --action LoginWithAzureActiveDirectory
```

### CORS Configuration

```bash
# Autoriser Copilot Studio à appeler les Functions
az functionapp cors add \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "https://copilotstudio.microsoft.com"
```

## 📊 Monitoring

### Logs en temps réel

```bash
# Suivre les logs
az functionapp log tail \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### Application Insights

Accéder aux logs détaillés via le portail Azure :
- Aller sur Application Insights
- Live Metrics pour voir l'activité en temps réel
- Logs pour requêtes détaillées

## 🔄 Mise à Jour

Pour déployer une nouvelle version :

```bash
# Depuis la racine du projet
func azure functionapp publish $FUNCTION_APP_NAME --python
```

## ⚠️ Points d'Attention

1. **Timeout**: Le `host.json` configure un timeout de 10 minutes. Ajuster si nécessaire pour les gros documents.

2. **Taille des fichiers**: Les Functions Consumption Plan ont une limite de ~100MB par requête. Pour des documents plus gros, passer à Premium Plan.

3. **Cold Start**: Le plan Consumption peut avoir un démarrage lent (~5-10s). Pour une latence constante, utiliser Premium ou Dedicated Plan.

4. **Connexions Dataverse**: S'assurer que l'App Registration a les permissions `user_impersonation` sur Dynamics CRM.

## 🎯 URLs des Endpoints (après déploiement)

Une fois déployé, vos endpoints seront accessibles à (⚠️ AVEC FUNCTION KEY):

- **clean-quote**: `https://$FUNCTION_APP_NAME.azurewebsites.net/api/document/clean-quote?code=FUNCTION_KEY`
- **prepare-template**: `https://$FUNCTION_APP_NAME.azurewebsites.net/api/proposal/prepare-template?code=FUNCTION_KEY`
- **generate**: `https://$FUNCTION_APP_NAME.azurewebsites.net/api/proposal/generate?code=FUNCTION_KEY`

**Important pour Copilot Studio**:
- Dans la configuration de l'action, utiliser l'URL sans `?code=...`
- Configurer l'authentification avec **API Key** (parameter name: `code`, location: Query)
- Voir `FUNCTION_KEYS.md` pour le guide complet

## 📝 Checklist Finale

- [ ] Function App créée
- [ ] Variables d'environnement configurées
- [ ] Application Insights activé
- [ ] Code déployé
- [ ] Function key récupérée (`az functionapp keys list`)
- [ ] Tests des 3 endpoints réussis (avec function key)
- [ ] CORS configuré pour Copilot Studio
- [ ] URLs et function key documentées pour la configuration Copilot
