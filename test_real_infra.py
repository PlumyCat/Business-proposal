#!/usr/bin/env python3
"""
Script de test pour vérifier l'infrastructure réelle
- Connexion Blob Storage
- Liste des templates disponibles
- Test de chargement d'un template
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le path des functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions'))

from shared.blob_client import get_blob_client
from shared.config import (
    CONTAINER_TEMPLATES,
    CONTAINER_DOCUMENTS,
    TABLE_OFFERS,
    get_template_path,
    get_user_file_path
)

# Charger .env
load_dotenv()

print("=" * 80)
print("TEST INFRASTRUCTURE RÉELLE")
print("=" * 80)

# 1. Test Blob Storage
print("\n📦 TEST BLOB STORAGE")
print("-" * 80)

try:
    blob_client = get_blob_client()
    print(f"✅ Connexion Blob Storage réussie")
    print(f"   Account: {blob_client.blob_service_client.account_name}")
except Exception as e:
    print(f"❌ Erreur connexion Blob Storage: {str(e)}")
    sys.exit(1)

# 2. Lister les templates dans general/
print(f"\n📄 TEMPLATES DISPONIBLES (container: {CONTAINER_TEMPLATES})")
print("-" * 80)

try:
    blobs = blob_client.list_blobs(CONTAINER_TEMPLATES, "general/")
    templates = [b.replace("general/", "") for b in blobs if b.endswith(".docx")]

    if templates:
        print(f"Trouvé {len(templates)} template(s):")
        for t in templates:
            print(f"  - {t}")
            template_path = get_template_path(t)
            print(f"    Path complet: {template_path}")
    else:
        print("⚠️  Aucun template trouvé dans general/")
except Exception as e:
    print(f"❌ Erreur listing templates: {str(e)}")

# 3. Test dossier utilisateur
print(f"\n👤 TEST DOSSIER UTILISATEUR")
print("-" * 80)

user_display_name = "Eric FER"
print(f"DisplayName: {user_display_name}")

try:
    user_blobs = blob_client.list_blobs(CONTAINER_TEMPLATES, f"{user_display_name}/")
    print(f"Fichiers dans {user_display_name}/:")
    if user_blobs:
        for b in user_blobs:
            print(f"  - {b}")
    else:
        print(f"  (vide)")

    # Test path helper
    test_file_path = get_user_file_path(user_display_name, "test.docx")
    print(f"\nTest path helper: {test_file_path}")

except Exception as e:
    print(f"❌ Erreur: {str(e)}")

# 4. Afficher configuration
print(f"\n⚙️  CONFIGURATION")
print("-" * 80)
print(f"CONTAINER_TEMPLATES: {CONTAINER_TEMPLATES}")
print(f"CONTAINER_DOCUMENTS: {CONTAINER_DOCUMENTS}")
print(f"TABLE_OFFERS: {TABLE_OFFERS}")

# 5. Test chargement d'un template (si disponible)
if templates:
    print(f"\n📥 TEST CHARGEMENT TEMPLATE")
    print("-" * 80)

    test_template = templates[0]
    template_path = get_template_path(test_template)

    try:
        template_bytes = blob_client.download_blob(CONTAINER_TEMPLATES, template_path)
        size_kb = len(template_bytes) / 1024
        print(f"✅ Template chargé: {test_template}")
        print(f"   Taille: {size_kb:.2f} KB")
    except Exception as e:
        print(f"❌ Erreur chargement template: {str(e)}")

print("\n" + "=" * 80)
print("FIN DES TESTS")
print("=" * 80)
