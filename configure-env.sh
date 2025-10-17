#!/bin/bash

# Script de configuration des variables d'environnement
# Usage: ./configure-env.sh [FUNCTION_APP_NAME]

set -e

# Couleurs
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

RESOURCE_GROUP="my-word-mcp-rg"
FUNCTION_APP_NAME="${1:-business-proposal-functions}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Configuration Variables d'Environnement                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Function App: $FUNCTION_APP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo ""

# Récupérer la connection string du Storage Account
echo -e "${YELLOW}📦 Récupération de la connection string Blob Storage...${NC}"
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name mywordmcpacrstorage \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)
echo -e "${GREEN}✅ Connection string récupérée${NC}"

# Configuration Blob Storage
echo -e "${YELLOW}💾 Configuration Blob Storage...${NC}"
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION_STRING" \
    "BLOB_CONTAINER_TEMPLATES=word-templates" \
    "BLOB_CONTAINER_DOCUMENTS=word-documents" \
  --output none
echo -e "${GREEN}✅ Blob Storage configuré${NC}"

# Configuration Dataverse (interactif)
echo ""
echo -e "${YELLOW}🔧 Configuration Dataverse${NC}"
echo "Vous avez besoin de:"
echo "  - DATAVERSE_ENVIRONMENT_URL (ex: https://org.crm4.dynamics.com)"
echo "  - DATAVERSE_CLIENT_ID"
echo "  - DATAVERSE_CLIENT_SECRET"
echo "  - DATAVERSE_TENANT_ID"
echo ""
read -p "Voulez-vous configurer Dataverse maintenant? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "DATAVERSE_ENVIRONMENT_URL: " DATAVERSE_URL
    read -p "DATAVERSE_CLIENT_ID: " DATAVERSE_CLIENT_ID
    read -s -p "DATAVERSE_CLIENT_SECRET: " DATAVERSE_CLIENT_SECRET
    echo
    read -p "DATAVERSE_TENANT_ID: " DATAVERSE_TENANT_ID
    
    az functionapp config appsettings set \
      --name $FUNCTION_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --settings \
        "DATAVERSE_ENVIRONMENT_URL=$DATAVERSE_URL" \
        "DATAVERSE_CLIENT_ID=$DATAVERSE_CLIENT_ID" \
        "DATAVERSE_CLIENT_SECRET=$DATAVERSE_CLIENT_SECRET" \
        "DATAVERSE_TENANT_ID=$DATAVERSE_TENANT_ID" \
        "DATAVERSE_TABLE_OFFERS=crb02_offrebeclouds" \
      --output none
    echo -e "${GREEN}✅ Dataverse configuré${NC}"
else
    echo "Dataverse non configuré (à faire plus tard)"
fi

# Configuration SharePoint (interactif)
echo ""
echo -e "${YELLOW}📄 Configuration SharePoint${NC}"
echo "Vous avez besoin de:"
echo "  - SHAREPOINT_SITE_URL"
echo "  - SHAREPOINT_CLIENT_ID"
echo "  - SHAREPOINT_CLIENT_SECRET"
echo "  - SHAREPOINT_TENANT_ID"
echo ""
read -p "Voulez-vous configurer SharePoint maintenant? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "SHAREPOINT_SITE_URL: " SHAREPOINT_URL
    read -p "SHAREPOINT_CLIENT_ID: " SHAREPOINT_CLIENT_ID
    read -s -p "SHAREPOINT_CLIENT_SECRET: " SHAREPOINT_CLIENT_SECRET
    echo
    read -p "SHAREPOINT_TENANT_ID: " SHAREPOINT_TENANT_ID
    read -p "SHAREPOINT_LIBRARY_NAME (default: Documents): " SHAREPOINT_LIBRARY
    SHAREPOINT_LIBRARY=${SHAREPOINT_LIBRARY:-Documents}
    
    az functionapp config appsettings set \
      --name $FUNCTION_APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --settings \
        "SHAREPOINT_SITE_URL=$SHAREPOINT_URL" \
        "SHAREPOINT_CLIENT_ID=$SHAREPOINT_CLIENT_ID" \
        "SHAREPOINT_CLIENT_SECRET=$SHAREPOINT_CLIENT_SECRET" \
        "SHAREPOINT_TENANT_ID=$SHAREPOINT_TENANT_ID" \
        "SHAREPOINT_LIBRARY_NAME=$SHAREPOINT_LIBRARY" \
      --output none
    echo -e "${GREEN}✅ SharePoint configuré${NC}"
else
    echo "SharePoint non configuré (à faire plus tard)"
fi

# Application Insights
echo ""
echo -e "${YELLOW}📊 Configuration Application Insights...${NC}"
if az monitor app-insights component show \
  --app business-proposal-insights \
  --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Application Insights existe déjà"
else
    echo "Création d'Application Insights..."
    az monitor app-insights component create \
      --app business-proposal-insights \
      --location francecentral \
      --resource-group $RESOURCE_GROUP \
      --output none
fi

INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app business-proposal-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey -o tsv)

az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY" \
  --output none
echo -e "${GREEN}✅ Application Insights configuré${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            ✅ CONFIGURATION TERMINÉE !                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Vous pouvez maintenant tester les endpoints."
