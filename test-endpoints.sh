#!/bin/bash

# Script de test des endpoints Azure Functions
# Usage: ./test-endpoints.sh [FUNCTION_APP_NAME]

set -e

# Couleurs
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

FUNCTION_APP_NAME="${1:-business-proposal-functions}"
RESOURCE_GROUP="my-word-mcp-rg"
BASE_URL="https://$FUNCTION_APP_NAME.azurewebsites.net"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Test des Endpoints Azure Functions               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Function App: $FUNCTION_APP_NAME"
echo "Base URL: $BASE_URL"
echo ""

# Récupérer la function key
echo -e "${YELLOW}🔑 Récupération de la function key...${NC}"
if command -v az &> /dev/null; then
    FUNCTION_KEY=$(az functionapp keys list \
      --name $FUNCTION_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --query "functionKeys.default" -o tsv 2>/dev/null)

    if [ -z "$FUNCTION_KEY" ]; then
        echo -e "${RED}❌ Impossible de récupérer la function key${NC}"
        echo "   Utilisez: az functionapp keys list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
        exit 1
    fi
    echo -e "${GREEN}✅ Function key récupérée${NC}"
    echo "   Key: ${FUNCTION_KEY:0:10}..."
else
    echo -e "${YELLOW}⚠️  Azure CLI non installé, veuillez entrer la function key manuellement${NC}"
    read -p "Function Key: " FUNCTION_KEY
    if [ -z "$FUNCTION_KEY" ]; then
        echo -e "${RED}❌ Function key requise${NC}"
        exit 1
    fi
fi
echo ""

# Test 1: Clean Quote
echo -e "${YELLOW}📋 Test 1: Clean Quote${NC}"
echo "Endpoint: POST $BASE_URL/api/document/clean-quote?code=***"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/document/clean-quote?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "blob_path": "Eric FER/test.docx",
    "user_folder": "Eric FER"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${GREEN}✅ Endpoint accessible (HTTP $HTTP_CODE)${NC}"
    echo "Response: $BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}❌ Erreur (HTTP $HTTP_CODE)${NC}"
    echo "Response: $BODY"
fi
echo ""

# Test 2: Prepare Template
echo -e "${YELLOW}📄 Test 2: Prepare Template${NC}"
echo "Endpoint: POST $BASE_URL/api/proposal/prepare-template?code=***"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/proposal/prepare-template?code=$FUNCTION_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "template.docx",
    "customer_success": {
      "name": "Jean Dupont",
      "tel": "06 12 34 56 78",
      "email": "jean.dupont@company.com"
    },
    "user_folder": "Eric FER"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 404 ]; then
    echo -e "${GREEN}✅ Endpoint accessible (HTTP $HTTP_CODE)${NC}"
    echo "Response: $BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}❌ Erreur (HTTP $HTTP_CODE)${NC}"
    echo "Response: $BODY"
fi
echo ""

# Test 3: Generate (nécessite des IDs réels)
echo -e "${YELLOW}🎨 Test 3: Generate${NC}"
echo "Endpoint: POST $BASE_URL/api/proposal/generate"
echo "(Skipped - nécessite des GUIDs d'offres réels)"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Tests terminés                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "💡 Notes importantes:"
echo "   - Tous les appels utilisent la function key récupérée"
echo "   - Pour Copilot Studio, configurer l'authentification API Key (parameter: code)"
echo "   - Voir FUNCTION_KEYS.md pour le guide complet"
echo ""
echo "🔑 Function key utilisée: ${FUNCTION_KEY:0:10}..."
