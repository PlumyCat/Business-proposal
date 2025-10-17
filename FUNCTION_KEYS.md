# Function Keys - Guide d'Utilisation

Les Azure Functions sont configurées avec le niveau d'authentification **`function`**, ce qui nécessite une clé (function key) pour chaque appel.

## ✅ Configuration Actuelle

Tous les endpoints sont protégés par function key:
- `authLevel: "function"` dans `functions/DocumentProcessor/function.json`
- `authLevel: "function"` dans `functions/ProposalGenerator/function.json`

## 🔑 Récupérer les Function Keys

### Option 1: Via Azure CLI

```bash
FUNCTION_APP_NAME="business-proposal-functions"
RESOURCE_GROUP="my-word-mcp-rg"

# Récupérer la default host key (fonctionne pour tous les endpoints)
az functionapp keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv

# Ou récupérer le master key (admin)
az functionapp keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "masterKey" -o tsv
```

### Option 2: Via le Portail Azure

1. Aller sur le Function App dans le portail Azure
2. Aller dans **"Functions"** → **"App keys"**
3. Copier la **"default"** key ou en créer une nouvelle

### Option 3: Pour une fonction spécifique

```bash
# Récupérer la key pour DocumentProcessor
az functionapp function keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --function-name DocumentProcessor \
  --query "default" -o tsv

# Récupérer la key pour ProposalGenerator
az functionapp function keys list \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --function-name ProposalGenerator \
  --query "default" -o tsv
```

## 📞 Utiliser les Keys dans les Appels

### Avec cURL

```bash
FUNCTION_KEY="YOUR_FUNCTION_KEY_HERE"
FUNCTION_URL="https://business-proposal-functions.azurewebsites.net"

# Option 1: Via query parameter (recommandé)
curl -X POST "$FUNCTION_URL/api/document/clean-quote?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "blob_path": "Eric FER/test.docx",
    "user_folder": "Eric FER"
  }'

# Option 2: Via header x-functions-key
curl -X POST "$FUNCTION_URL/api/document/clean-quote" \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $FUNCTION_KEY" \
  -d '{
    "blob_path": "Eric FER/test.docx",
    "user_folder": "Eric FER"
  }'
```

### Depuis Copilot Studio

Lors de la configuration de l'action personnalisée dans Copilot Studio:

1. **URL de l'endpoint**: `https://business-proposal-functions.azurewebsites.net/api/document/clean-quote`

2. **Authentification**: Choisir **"API Key"** avec:
   - **Parameter name**: `code`
   - **Location**: `Query`
   - **Value**: Votre function key

OU utiliser **"Custom Header"**:
   - **Header name**: `x-functions-key`
   - **Value**: Votre function key

### Depuis JavaScript/TypeScript

```typescript
const functionKey = "YOUR_FUNCTION_KEY_HERE";
const functionUrl = "https://business-proposal-functions.azurewebsites.net";

// Option 1: Query parameter
const response = await fetch(
  `${functionUrl}/api/document/clean-quote?code=${functionKey}`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      blob_path: "Eric FER/test.docx",
      user_folder: "Eric FER"
    })
  }
);

// Option 2: Header
const response = await fetch(
  `${functionUrl}/api/document/clean-quote`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-functions-key': functionKey
    },
    body: JSON.stringify({
      blob_path: "Eric FER/test.docx",
      user_folder: "Eric FER"
    })
  }
);
```

### Depuis Power Automate

Dans le connecteur HTTP:

1. **URI**: `https://business-proposal-functions.azurewebsites.net/api/document/clean-quote?code=YOUR_KEY`
2. **Method**: `POST`
3. **Headers**:
   - `Content-Type`: `application/json`
4. **Body**: Votre JSON

## 🔐 Sécurité des Keys

### Niveaux d'Authentification Disponibles

- **`anonymous`**: Aucune key requise (NON utilisé ici)
- **`function`**: Function key requise (✅ ACTUEL)
- **`admin`**: Master key requise (plus restrictif)

### Types de Keys

1. **Default Host Key**: Fonctionne pour TOUS les endpoints du Function App
2. **Master Key**: Accès admin complet (à ne pas partager)
3. **Function-specific Key**: Key spécifique à une seule fonction

### Bonnes Pratiques

1. ✅ Utiliser la **default host key** pour Copilot Studio
2. ✅ Stocker la key dans les **variables d'environnement** Copilot Studio (pas en dur dans le code)
3. ✅ Ne JAMAIS commiter les keys dans Git
4. ✅ Régénérer les keys si elles sont exposées
5. ✅ Utiliser des keys différentes pour dev/prod

### Régénérer une Key

Si une key est compromise:

```bash
# Régénérer la default key
az functionapp keys set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --key-type functionKeys \
  --key-name default \
  --key-value $(openssl rand -base64 32)
```

## 📋 Résumé pour Configuration Copilot Studio

Pour chaque action personnalisée dans Copilot Studio:

| Endpoint | URL | Authentification |
|----------|-----|------------------|
| clean-quote | `https://[APP].azurewebsites.net/api/document/clean-quote` | API Key: `code` (Query) |
| prepare-template | `https://[APP].azurewebsites.net/api/proposal/prepare-template` | API Key: `code` (Query) |
| generate | `https://[APP].azurewebsites.net/api/proposal/generate` | API Key: `code` (Query) |

**Value de la key**: Récupérer via `az functionapp keys list` (voir ci-dessus)

## 🚨 Erreur 401 Unauthorized

Si vous obtenez cette erreur:
- ✅ Vérifier que la key est bien passée (`?code=...` ou header `x-functions-key`)
- ✅ Vérifier que la key n'a pas de caractères spéciaux mal encodés
- ✅ Vérifier que c'est la bonne key pour le bon Function App
- ✅ Essayer de régénérer une nouvelle key
