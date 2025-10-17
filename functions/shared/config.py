"""
Configuration centralisée pour l'infrastructure réelle
Mapping entre les noms logiques du code et les noms réels dans Azure
"""

import os

# Blob Storage Containers
CONTAINER_TEMPLATES = os.environ.get("BLOB_CONTAINER_TEMPLATES", "word-templates")
CONTAINER_DOCUMENTS = os.environ.get("BLOB_CONTAINER_DOCUMENTS", "word-documents")

# Pour compatibilité avec ancien code
BLOB_CONTAINER_DEVIS = CONTAINER_TEMPLATES  # Ancien nom
BLOB_CONTAINER_PROPOSALS = CONTAINER_DOCUMENTS  # Ancien nom

# Dataverse Table Names
TABLE_OFFERS = os.environ.get("DATAVERSE_TABLE_OFFERS", "crb02_offrebeclouds")

# Mapping colonnes Dataverse: nom logique → nom réel
DATAVERSE_COLUMNS_MAPPING = {
    # Mapping pour cr_offres → crb02_offrebeclouds
    "offres": {
        "id": "crb02_offrebecloudid",
        "name": "crb02_offrebecloud1",
        "description": "crb02_description",
        "price_ht": "crb02_prixht",
        "price_ttc": "crb02_prixttc",
        "category": "crb02_service",
        "status_code": "statuscode",
        "state": "statecode"
    }
}

# Catégories de services (valeurs choicelist crb02_service)
SERVICE_CATEGORIES = {
    480810000: "Téléphonie / Teams Calling",
    480810003: "Microsoft 365 / Bureautique",
    480810004: "Services Be-Cloud / IA"
}

# Chemins dans Blob Storage
PATH_TEMPLATES_GENERAL = "general"  # Dossier templates généraux

def get_user_folder(display_name: str) -> str:
    """
    Retourne le chemin du dossier utilisateur dans Blob Storage

    Args:
        display_name: DisplayName de l'utilisateur Teams (ex: "Eric FER")

    Returns:
        Chemin du dossier (ex: "Eric FER")
    """
    return display_name

def get_template_path(template_name: str) -> str:
    """
    Retourne le chemin complet d'un template

    Args:
        template_name: Nom du fichier template (ex: "template.docx")

    Returns:
        Chemin complet (ex: "general/template.docx")
    """
    return f"{PATH_TEMPLATES_GENERAL}/{template_name}"

def get_user_file_path(display_name: str, filename: str) -> str:
    """
    Retourne le chemin complet d'un fichier utilisateur

    Args:
        display_name: DisplayName utilisateur
        filename: Nom du fichier

    Returns:
        Chemin complet (ex: "Eric FER/ancien_devis.docx")
    """
    return f"{display_name}/{filename}"

def map_dataverse_columns(data: dict, entity_type: str, reverse: bool = False) -> dict:
    """
    Convertit les noms de colonnes entre format logique et format Dataverse

    Args:
        data: Dictionnaire avec données
        entity_type: Type d'entité ("offres", etc.)
        reverse: Si True, convertit Dataverse → logique (au lieu de logique → Dataverse)

    Returns:
        Dictionnaire avec colonnes mappées
    """
    if entity_type not in DATAVERSE_COLUMNS_MAPPING:
        return data

    mapping = DATAVERSE_COLUMNS_MAPPING[entity_type]

    if reverse:
        # Dataverse → logique
        mapping = {v: k for k, v in mapping.items()}

    mapped_data = {}
    for key, value in data.items():
        mapped_key = mapping.get(key, key)
        mapped_data[mapped_key] = value

    return mapped_data
