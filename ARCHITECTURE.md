# Architecture Simplifiée

## Azure Functions (2 fonctions seulement)

### 1. DocumentProcessor
**Endpoints:**
- `POST /api/document/extract-content` - Extrait contenu .docx
- `POST /api/document/clean-document` - Nettoie document extrait

### 2. ProposalGenerator
**Endpoints:**
- `POST /api/proposal/generate` - Génère proposition Word/PDF
- `POST /api/proposal/save` - Sauvegarde métadonnées Dataverse

## ~~OfferManager~~ (SUPPRIMÉ)

**Raison:** Copilot Studio gère directement les offres via son **connecteur Dataverse natif**.

Pas besoin d'Azure Function pour:
- Lire la table `cr_offres`
- Filtrer les offres
- Récupérer détails d'une offre

→ Copilot Studio le fait nativement avec ses **Dataverse Actions**

## Workflow Simplifié

```
1. User upload .docx → SharePoint
2. Power Automate → Blob Storage + Dataverse cr_uploads_temp
3. Copilot récupère file_id (Dataverse query)
4. Copilot appelle DocumentProcessor/extract-content (Azure Function)
5. Copilot appelle DocumentProcessor/clean-document (Azure Function)
6. Copilot lit table cr_offres DIRECTEMENT (Dataverse connector)
7. User sélectionne offres dans Copilot
8. Copilot appelle ProposalGenerator/generate (Azure Function)
9. Copilot appelle ProposalGenerator/save (Azure Function → Dataverse)
10. Copilot affiche liens téléchargement
```

## Conversion PDF via SharePoint

**Solution adoptée:** Utilisation de SharePoint Online pour la conversion Word → PDF

**Workflow de conversion:**
```
1. Azure Function génère le document Word en mémoire
2. Upload temporaire vers SharePoint (bibliothèque "TempConversions")
3. Demande du fichier en format PDF via API SharePoint
4. SharePoint convertit automatiquement le .docx en PDF
5. Téléchargement du PDF généré
6. Suppression du fichier temporaire de SharePoint
7. Upload du PDF vers Blob Storage
```

**Avantages:**
- ✅ Conversion native Microsoft (haute fidélité)
- ✅ Pas de service tiers (LibreOffice, CloudConvert, etc.)
- ✅ Déjà dans l'écosystème Microsoft 365
- ✅ Authentification unifiée Azure AD
- ✅ Pas de conteneur Docker supplémentaire requis

**Implémentation:** `functions/shared/sharepoint_client.py`

## Avantages Architecture Globale

- ✅ Moins de code Azure Functions à maintenir
- ✅ Moins de coûts (moins de fonction calls)
- ✅ Utilise capacités natives Copilot Studio
- ✅ Performance: pas de round-trip via Azure Function pour lire offres
- ✅ Simplicité: connexion directe Copilot ↔ Dataverse
- ✅ Conversion PDF native sans services tiers
