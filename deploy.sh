#!/bin/bash

# Script de déploiement Azure Functions
# Usage: ./deploy.sh

set -e  # Exit on error

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        Déploiement Business Proposal Azure Functions          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Variables
RESOURCE_GROUP="my-word-mcp-rg"
LOCATION="francecentral"
STORAGE_ACCOUNT="mywordmcpacrstorage"
FUNCTION_APP_NAME="${1:-business-proposal-functions}"  # Utilise le premier argument ou valeur par défaut

echo -e "${YELLOW}Configuration:${NC}"
echo "  Resource Group:   $RESOURCE_GROUP"
echo "  Location:         $LOCATION"
echo "  Storage Account:  $STORAGE_ACCOUNT"
echo "  Function App:     $FUNCTION_APP_NAME"
echo ""

# Vérifier que Azure CLI est installé
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI n'est pas installé${NC}"
    echo "   Installer: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Vérifier que func est installé
if ! command -v func &> /dev/null; then
    echo -e "${RED}❌ Azure Functions Core Tools n'est pas installé${NC}"
    echo "   Installer: npm install -g azure-functions-core-tools@4"
    exit 1
fi

# Vérifier la connexion Azure
echo -e "${YELLOW}🔐 Vérification de la connexion Azure...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Non connecté à Azure${NC}"
    echo "   Exécutez: az login"
    exit 1
fi
echo -e "${GREEN}✅ Connecté à Azure${NC}"
echo ""

# Vérifier que le Resource Group existe
echo -e "${YELLOW}📦 Vérification du Resource Group...${NC}"
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}❌ Resource Group $RESOURCE_GROUP n'existe pas${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Resource Group trouvé${NC}"
echo ""

# Vérifier que le Storage Account existe
echo -e "${YELLOW}💾 Vérification du Storage Account...${NC}"
if ! az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}❌ Storage Account $STORAGE_ACCOUNT n'existe pas${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Storage Account trouvé${NC}"
echo ""

# Demander confirmation
echo -e "${YELLOW}⚠️  Cette action va:${NC}"
echo "  1. Créer (ou mettre à jour) le Function App: $FUNCTION_APP_NAME"
echo "  2. Déployer les Azure Functions"
echo ""
read -p "Continuer? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Déploiement annulé."
    exit 0
fi
echo ""

# Créer ou mettre à jour le Function App
echo -e "${YELLOW}🚀 Création/Mise à jour du Function App...${NC}"
if az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${YELLOW}   Function App existe déjà, mise à jour...${NC}"
else
    echo -e "${YELLOW}   Création du Function App...${NC}"
    az functionapp create \
      --resource-group $RESOURCE_GROUP \
      --name $FUNCTION_APP_NAME \
      --storage-account $STORAGE_ACCOUNT \
      --consumption-plan-location $LOCATION \
      --runtime python \
      --runtime-version 3.11 \
      --functions-version 4 \
      --os-type Linux
fi
echo -e "${GREEN}✅ Function App prêt${NC}"
echo ""

# Déployer le code
echo -e "${YELLOW}📤 Déploiement du code...${NC}"
func azure functionapp publish $FUNCTION_APP_NAME --python

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 ✅ DÉPLOIEMENT RÉUSSI !                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Prochaines étapes:${NC}"
echo ""
echo "1. Configurer les variables d'environnement:"
echo "   Voir DEPLOYMENT.md section 'Configurer les Variables d'Environnement'"
echo ""
echo "2. Tester les endpoints:"
echo "   https://$FUNCTION_APP_NAME.azurewebsites.net/api/document/clean-quote"
echo "   https://$FUNCTION_APP_NAME.azurewebsites.net/api/proposal/prepare-template"
echo "   https://$FUNCTION_APP_NAME.azurewebsites.net/api/proposal/generate"
echo ""
echo "3. Configurer CORS pour Copilot Studio:"
echo "   az functionapp cors add --name $FUNCTION_APP_NAME \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --allowed-origins \"https://copilotstudio.microsoft.com\""
echo ""
