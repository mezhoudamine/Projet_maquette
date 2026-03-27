# Maquette Tactile 3D - Projet Le Havre

Pipeline complet de génération de maquettes tactiles 3D à partir de données OpenStreetMap.

## 📋 Description

Ce projet génère des maquettes en relief 3D destinées aux personnes déficientes visuelles. Il transforme des données géographiques (voirie) en modèles 3D imprimables.

**Caractéristiques:**
- Projection géographique précise (WGS84 → Lambert 93)
- Échelle 1:1000 (1m réel = 1mm sur maquette)
- Relief positif (traits en hauteur)
- Profils arrondis pour robustesse
- Export STL prêt pour impression 3D

## 🚀 Installation

### 1. Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 📁 Structure du projet

```
project/
├── config.py                    # Configuration globale
├── 01_data_processor.py         # Module 1: Traitement données
├── 02_visualize_2d.py          # Module 2: Visualisation 2D
├── 03_generate_3d_model.py     # Module 3: Génération 3D
├── requirements.txt            # Dépendances Python
│
├── data/
│   ├── raw/
│   │   └── export.geojson      # Données OpenStreetMap (input)
│   ├── processed/
│   │   └── processed_data.json # Données traitées (intermédiaire)
│   └── output/
│       ├── preview_2d.png      # Aperçu 2D
│       └── maquette_voirie.stl # Modèle 3D final
```

## 🎯 Utilisation

### Pipeline complet (3 étapes)

#### Étape 1: Traiter les données GeoJSON

```bash
python 01_data_processor.py --input data/raw/export.geojson
```

**Résultat:** `data/processed/processed_data.json`

Cette étape:
- Lit le fichier GeoJSON d'OpenStreetMap
- Projette les coordonnées (WGS84 → Lambert 93)
- Applique l'échelle 1:1000
- Centre les données sur (0, 0)
- Filtre les types de voies selon config.py

#### Étape 2: Visualiser en 2D (validation)

```bash
python 02_visualize_2d.py
```

**Résultat:** `data/output/preview_2d.png`

Cette étape:
- Crée un aperçu 2D pour vérification
- Affiche les dimensions
- Différencie les types de routes par couleur
- Permet de valider avant l'impression 3D

**Options:**
```bash
# Affichage interactif
python 02_visualize_2d.py --show

# Changer la résolution
python 02_visualize_2d.py --dpi 600
```

#### Étape 3: Générer le modèle 3D

```bash
python 03_generate_3d_model.py
```

**Résultat:** `data/output/maquette_voirie.stl`

Cette étape:
- Crée la plaque de base
- Génère les routes en relief (extrusion)
- Ajoute des sphères aux intersections
- Fusionne toutes les géométries
- Valide et répare le mesh
- Exporte en format STL

**Le fichier STL est prêt pour l'impression 3D!**

## ⚙️ Configuration

Tous les paramètres sont dans `config.py`:

```python
# Échelle
SCALE_HORIZONTAL = 1000        # 1:1000

# Dimensions (mm)
BASE_THICKNESS = 2.5           # Épaisseur de base
BASE_MARGIN = 5.0              # Marge autour
ROAD_HEIGHT = 2.5              # Hauteur du relief

# Profil des routes
ROAD_PROFILE = "rounded_rect"  # ou "rectangle"
CORNER_RADIUS = 0.3            # Rayon des coins

# Filtrage
INCLUDE_FOOTWAYS = True        # Chemins piétons
INCLUDE_CYCLEWAYS = True       # Pistes cyclables
INCLUDE_STEPS = False          # Escaliers
```

**Modifier selon vos besoins puis relancer le pipeline!**

## 🖨️ Impression 3D

### Paramètres recommandés (FDM)

- **Matériau:** PLA ou PETG
- **Hauteur de couche:** 0.2mm
- **Remplissage:** 20-30%
- **Supports:** Non nécessaires (modèle optimisé)
- **Adhésion:** Brim recommandé

### Paramètres recommandés (Résine SLA)

- **Hauteur de couche:** 0.05mm
- **Exposition:** Standard
- **Supports:** Légers si nécessaire

### Temps d'impression estimé

Pour une zone de ~150×180mm:
- **FDM (0.2mm):** 3-4 heures
- **Résine (0.05mm):** 1.5-2 heures

## 📊 Dimensions typiques

Pour les quartiers du Havre testés:

| Quartier | Dimensions réelles | Dimensions maquette |
|----------|-------------------|---------------------|
| Volcan/Halles | ~1800m × 1200m | ~180mm × 120mm |
| Saint-Roch | ~1500m × 1000m | ~150mm × 100mm |

## 🔍 Validation

Avant d'imprimer, vérifiez:

1. **Preview 2D:** Dimensions correctes ?
2. **Fichier STL:** Ouvrir dans un viewer 3D
   - Recommended: MeshLab, 3D Builder, PrusaSlicer
3. **Slicer:** Temps et coût réalistes ?

## 🐛 Résolution de problèmes

### Erreur: "module not found"

```bash
pip install -r requirements.txt
```

### Le mesh a des trous

Dans `config.py`, activer:
```python
REPAIR_MESH = True
```

### Routes trop fines/épaisses

Dans `config.py`, ajuster:
```python
ROAD_WIDTHS = {
    "residential": 1.5,  # Augmenter/diminuer
    ...
}
```

### Fichier STL trop gros

Dans `config.py`, réduire:
```python
MESH_RESOLUTION = 8  # Au lieu de 16
```

## 📝 Variantes futures

Le projet prévoit 5 types de cartes:

1. ✅ **Carte 1:** Relief positif (voirie uniquement) - **ACTUELLE**
2. **Carte 2:** Relief négatif (creux)
3. **Carte 3:** Relief + bâtiments (hauteur uniforme)
4. **Carte 4:** Carte 3 + repères tactiles (eau, végétation)
5. **Carte 5:** Relief + bâtiments à l'échelle réelle

## 📄 Licence

Données OpenStreetMap © Contributeurs OpenStreetMap
Disponible sous Open Database License (ODbL)

## 👥 Auteurs

Projet: Maquette en relief du Havre
Encadrants: Frédéric Serin, Antoine Dutot, Jean-Luc Ponty
Université du Havre

## 🤝 Contribution

Pour améliorer ce projet:
1. Testez avec différents quartiers
2. Ajustez les paramètres selon vos tests tactiles
3. Partagez vos résultats d'impression

## 📧 Support

Pour toute question, référez-vous à:
- Documentation du code (commentaires détaillés)
- `config.py` pour les paramètres
- OpenStreetMap pour les données sources
