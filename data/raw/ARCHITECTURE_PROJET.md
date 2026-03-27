# ARCHITECTURE DU PROJET - MAQUETTE TACTILE 3D
## Pipeline complet : GeoJSON → Visualisation → STL → Impression

---

## 📊 SCHÉMA GÉNÉRAL DU WORKFLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: PRÉPARATION DONNÉES                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌───────────────────────────────────────────────────────┐
    │  export.geojson (OpenStreetMap)                       │
    │  • 395 segments de voirie                             │
    │  • Coordonnées WGS84 (lat/lon en degrés)             │
    │  • Propriétés: highway type, name, etc.              │
    └───────────────────────────────────────────────────────┘
                                    ↓
    ┌───────────────────────────────────────────────────────┐
    │  MODULE 1: data_processor.py                          │
    │  ─────────────────────────────────────────────────    │
    │  ✓ Lecture GeoJSON                                    │
    │  ✓ Projection WGS84 → Lambert 93 (pyproj)           │
    │  ✓ Centrage sur origine (0,0)                        │
    │  ✓ Application échelle 1:1000                        │
    │  ✓ Filtrage des types de voies (optionnel)          │
    │  ✓ Export: processed_data.json                       │
    └───────────────────────────────────────────────────────┘
                                    ↓
                    processed_data.json (coordonnées en mm)

┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE 2: VISUALISATION 2D                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌───────────────────────────────────────────────────────┐
    │  MODULE 2: visualize_2d.py                            │
    │  ─────────────────────────────────────────────────    │
    │  ✓ Lecture processed_data.json                        │
    │  ✓ Affichage matplotlib (coordonnées en mm)          │
    │  ✓ Différenciation types de routes (couleur/épaisseur)│
    │  ✓ Export PNG haute résolution                        │
    │  ✓ Vérification dimensions et échelle                │
    └───────────────────────────────────────────────────────┘
                                    ↓
                        preview_2d.png (validation visuelle)

┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: GÉNÉRATION 3D                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌───────────────────────────────────────────────────────┐
    │  MODULE 3: generate_3d_model.py                       │
    │  ─────────────────────────────────────────────────    │
    │  INPUT: processed_data.json                           │
    │                                                        │
    │  ÉTAPES:                                              │
    │  1. Création base plane (plaque)                     │
    │     • Dimensions: bbox + marges                       │
    │     • Épaisseur: 2-3 mm                              │
    │                                                        │
    │  2. Pour chaque segment de route:                    │
    │     • Créer extrusion (profil → volume)              │
    │     • Hauteur: 2-3 mm (relief positif)               │
    │     • Largeur: 1-2 mm                                │
    │     • Section: rectangulaire ou arrondie              │
    │                                                        │
    │  3. Fusion géométries:                               │
    │     • Union booléenne des segments                    │
    │     • Jonctions aux intersections                     │
    │                                                        │
    │  4. Export STL                                        │
    │                                                        │
    │  OUTPUT: maquette_voirie.stl                         │
    └───────────────────────────────────────────────────────┘
                                    ↓
                        maquette_voirie.stl

┌─────────────────────────────────────────────────────────────────────────┐
│                   PHASE 4: VISUALISATION 3D INTERACTIVE                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌───────────────────────────────────────────────────────┐
    │  MODULE 4: viewer_3d.html (Three.js)                  │
    │  ─────────────────────────────────────────────────    │
    │  ✓ Chargement STL dans navigateur                     │
    │  ✓ Contrôles orbit (rotation, zoom, pan)             │
    │  ✓ Éclairage réaliste                                │
    │  ✓ Mesures et dimensions                             │
    │  ✓ Export captures d'écran                           │
    │                                                        │
    │  Alternative: trimesh/matplotlib 3D (Python)          │
    └───────────────────────────────────────────────────────┘
                                    ↓
                    Validation visuelle 3D interactive

┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 5: PRÉPARATION IMPRESSION                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
    ┌───────────────────────────────────────────────────────┐
    │  MODULE 5: prepare_for_print.py                       │
    │  ─────────────────────────────────────────────────    │
    │  ✓ Validation du STL (manifold, normales, etc.)     │
    │  ✓ Réparation automatique (si nécessaire)            │
    │  ✓ Orientation optimale pour impression              │
    │  ✓ Ajout supports (si besoin)                        │
    │  ✓ Export formats multiples (STL, OBJ, 3MF)         │
    │  ✓ Génération rapport technique                      │
    └───────────────────────────────────────────────────────┘
                                    ↓
                    maquette_voirie_final.stl
                    (prêt pour slicer → imprimante 3D)
```

---

## 🔧 OUTILS ET BIBLIOTHÈQUES

### **Python (Backend - Traitement des données)**

```yaml
Bibliothèques essentielles:
  - pyproj: "Projection géographique WGS84 → Lambert 93"
  - json: "Lecture/écriture GeoJSON (standard library)"
  - numpy: "Calculs numériques, transformations"
  - trimesh: "⭐ RECOMMANDÉ - Génération et manipulation de mesh 3D"
  - shapely: "Géométrie 2D (optionnel, pour simplification)"

Bibliothèques alternatives 3D:
  - pyvista: "Visualisation 3D scientifique (option)"
  - cadquery: "CAO paramétrique (trop complexe pour ce projet)"
  - solidpython: "Interface Python → OpenSCAD (détour inutile)"

Visualisation 2D:
  - matplotlib: "Déjà utilisé, parfait pour preview 2D"

Validation/Réparation STL:
  - trimesh: "Déjà inclus, fonctions repair()"
  - pymeshfix: "Réparation avancée (backup)"
```

### **JavaScript (Frontend - Visualisation interactive)**

```yaml
Bibliothèque 3D:
  - Three.js: "⭐ RECOMMANDÉ - Standard pour 3D web"
  
Chargeurs STL:
  - STLLoader: "Intégré dans Three.js"
  
Contrôles:
  - OrbitControls: "Navigation 3D intuitive"
```

---

## 📁 STRUCTURE DES FICHIERS DU PROJET

```
project_maquette_havre/
│
├── data/
│   ├── raw/
│   │   └── export.geojson                    # Données brutes OSM
│   ├── processed/
│   │   └── processed_data.json               # Coordonnées projetées (mm)
│   └── output/
│       ├── maquette_voirie.stl               # Modèle 3D final
│       ├── maquette_voirie.obj               # Format alternatif
│       └── preview_2d.png                    # Aperçu 2D
│
├── src/
│   ├── 01_data_processor.py                  # MODULE 1
│   ├── 02_visualize_2d.py                    # MODULE 2
│   ├── 03_generate_3d_model.py               # MODULE 3
│   ├── 04_prepare_for_print.py               # MODULE 5
│   └── utils/
│       ├── config.py                          # Paramètres globaux
│       └── geometry_helpers.py                # Fonctions géométriques
│
├── viewer/
│   ├── index.html                             # Visualiseur Three.js
│   ├── viewer_3d.js                           # Logic Three.js
│   └── styles.css                             # Styles interface
│
├── docs/
│   └── ARCHITECTURE_PROJET.md                 # Ce document
│
├── requirements.txt                           # Dépendances Python
└── README.md                                  # Guide utilisation
```

---

## ⚙️ PARAMÈTRES DE CONFIGURATION

```python
# config.py - Tous les paramètres en un seul endroit

# PROJECTION
CRS_SOURCE = "EPSG:4326"      # WGS84
CRS_TARGET = "EPSG:2154"      # Lambert 93 (France métropolitaine)

# ÉCHELLE
SCALE_HORIZONTAL = 1000        # 1:1000 (1m réel = 1mm maquette)
SCALE_VERTICAL = 800           # 1:800 (exagération selon projet Genève)
EXAGGERATION_RATIO = SCALE_HORIZONTAL / SCALE_VERTICAL  # 1.25

# DIMENSIONS MAQUETTE (mm)
BASE_THICKNESS = 2.5           # Épaisseur plaque de base
BASE_MARGIN = 5.0              # Marge autour des routes

# RELIEF DES ROUTES
ROAD_HEIGHT = 2.5              # Hauteur des traits (relief positif)
ROAD_WIDTH_DEFAULT = 1.5       # Largeur par défaut

# Largeurs différenciées par type (optionnel)
ROAD_WIDTHS = {
    "primary": 2.5,
    "secondary": 2.0,
    "tertiary": 1.5,
    "residential": 1.2,
    "service": 0.8,
    "footway": 0.6,
    "default": 1.0
}

# SECTION DES TRAITS
ROAD_PROFILE = "rounded_rect"  # Options: "rectangle", "rounded_rect", "half_cylinder"
CORNER_RADIUS = 0.3            # Pour profil arrondi

# SIMPLIFICATION (optionnel)
SIMPLIFY_TOLERANCE = 0.1       # mm, réduction de points
MIN_SEGMENT_LENGTH = 0.5       # mm, suppression segments trop courts

# FILTRAGE TYPES DE VOIES
INCLUDE_FOOTWAYS = False       # Inclure chemins piétons ?
INCLUDE_CYCLEWAYS = False      # Inclure pistes cyclables ?
INCLUDE_STEPS = False          # Inclure escaliers ?

# EXPORT STL
STL_ASCII = False              # False = binaire (plus compact)
MESH_RESOLUTION = 32           # Segments pour arrondis (8-64)

# VISUALISATION 3D
CAMERA_DISTANCE = 300          # mm
LIGHT_INTENSITY = 1.5
BACKGROUND_COLOR = "#f0f0f0"
```

---

## 🎯 DÉCISIONS TECHNIQUES CLÉS

### **1. Pourquoi Trimesh ? (vs autres outils)**

| Critère | Trimesh | PyVista | CadQuery | SolidPython |
|---------|---------|---------|----------|-------------|
| **Facilité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Export STL** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Opérations booléennes** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Légèreté** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Validation mesh** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

**VERDICT: Trimesh** - Parfait équilibre simplicité/puissance

### **2. Profil des routes : Quelle section ?**

```
┌─────────────────────────────────────────────────────────┐
│ OPTION A: Rectangle simple                              │
│ ▬▬▬▬▬▬▬▬▬                                               │
│ • Avantages: Simple, angles vifs = tactile clair       │
│ • Inconvénients: Risque de casse sur bords fins        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ OPTION B: Rectangle arrondi (RECOMMANDÉ)                │
│ ╭─────────╮                                             │
│ • Avantages: Robuste, tactile agréable                 │
│ • Inconvénients: Légèrement plus complexe              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ OPTION C: Demi-cylindre                                 │
│    ╭───╮                                                │
│ ───╯   ╰───                                            │
│ • Avantages: Tactile optimal, naturel                  │
│ • Inconvénients: Plus de triangles = fichier plus gros │
└─────────────────────────────────────────────────────────┘
```

**RECOMMANDATION: Option B (rectangle arrondi)**
- Compromis idéal robustesse/tactilité
- Bon pour impression FDM et résine

### **3. Gestion des intersections**

```python
# Problème: Routes qui se croisent
#
#     Route A
#        |
#        |
# ───────┼───────  Route B
#        |
#        |

# Solution 1: Union simple (rapide mais imparfait)
mesh_final = trimesh.util.concatenate(all_road_meshes)

# Solution 2: Union booléenne (propre mais lent)
mesh_final = trimesh.boolean.union(all_road_meshes, engine='blender')

# Solution 3: Sphères aux jonctions (RECOMMANDÉ)
for intersection_point in intersections:
    sphere = trimesh.creation.icosphere(radius=road_width/2)
    sphere.apply_translation(intersection_point)
    mesh_final += sphere
```

**RECOMMANDATION: Solution 3**
- Intersections propres et lisses
- Pas besoin d'opérations booléennes coûteuses

---

## 🚀 MODULES DÉTAILLÉS

### **MODULE 1: data_processor.py**

```python
"""
Transformation GeoJSON → Coordonnées projetées

INPUT:  export.geojson (WGS84)
OUTPUT: processed_data.json (Lambert 93, mm, centré)
"""

Fonctions principales:
├── load_geojson(filepath)
│   └── Lecture et parsing JSON
│
├── project_coordinates(features, crs_source, crs_target)
│   ├── Projection pyproj
│   └── Conversion en tableaux numpy
│
├── center_and_scale(coords, scale)
│   ├── Calcul bounding box
│   ├── Centrage sur (0, 0)
│   └── Application facteur échelle
│
├── filter_road_types(features, include_types)
│   └── Sélection types de voies
│
└── export_processed_data(data, output_path)
    └── Sauvegarde JSON structuré
```

**Format de sortie:**
```json
{
  "metadata": {
    "projection": "EPSG:2154",
    "scale": 1000,
    "bbox_mm": [0, 0, 150.5, 180.2],
    "units": "millimeters"
  },
  "roads": [
    {
      "id": "way/4995409",
      "name": "Rue Philippe Lebon",
      "type": "residential",
      "coordinates": [[10.5, 25.3], [15.2, 30.1], ...],
      "length_mm": 45.2
    },
    ...
  ]
}
```

---

### **MODULE 2: visualize_2d.py**

```python
"""
Visualisation 2D pour validation

INPUT:  processed_data.json
OUTPUT: preview_2d.png
"""

Fonctionnalités:
├── Affichage matplotlib haute résolution
├── Légende avec types de routes
├── Dimensions annotées (échelle)
├── Grille en mm (optionnel)
└── Export PNG/SVG/PDF
```

---

### **MODULE 3: generate_3d_model.py** ⭐ CŒUR DU PROJET

```python
"""
Génération du modèle 3D STL

INPUT:  processed_data.json
OUTPUT: maquette_voirie.stl
"""

Architecture:
├── create_base_plate(bbox, thickness, margin)
│   └── Plaque rectangulaire (base)
│
├── create_road_segment(start, end, width, height, profile)
│   ├── Calcul vecteur direction
│   ├── Génération profil 2D
│   ├── Extrusion le long du chemin
│   └── Retourne trimesh.Trimesh
│
├── create_intersection_sphere(point, radius)
│   └── Sphère aux jonctions
│
├── process_all_roads(roads_data, config)
│   ├── Boucle sur chaque route
│   ├── Création mesh par segment
│   ├── Détection intersections
│   └── Collection de tous les meshes
│
├── merge_meshes(base, roads, intersections)
│   └── Fusion en un seul mesh
│
├── validate_and_repair(mesh)
│   ├── Check manifold
│   ├── Réparation normales
│   └── Suppression dégénérés
│
└── export_stl(mesh, output_path)
    └── Sauvegarde binaire
```

**Algorithme détaillé de create_road_segment():**

```python
def create_road_segment(p1, p2, width, height, profile_type):
    """
    Créer un segment de route 3D
    
    Args:
        p1, p2: points début/fin [x, y] en mm
        width: largeur en mm
        height: hauteur relief en mm
        profile_type: "rectangle" ou "rounded_rect"
    
    Returns:
        trimesh.Trimesh object
    """
    
    # 1. Calcul vecteur direction et perpendiculaire
    direction = p2 - p1
    length = np.linalg.norm(direction)
    direction_norm = direction / length
    perpendicular = np.array([-direction_norm[1], direction_norm[0]])
    
    # 2. Génération du profil 2D (section transversale)
    if profile_type == "rectangle":
        # 4 coins du rectangle
        profile = [
            [-width/2, 0],
            [width/2, 0],
            [width/2, height],
            [-width/2, height]
        ]
    
    elif profile_type == "rounded_rect":
        # Rectangle avec coins arrondis
        profile = generate_rounded_rectangle(width, height, radius=0.3)
    
    # 3. Extrusion le long du segment
    path = [p1, p2]  # Chemin linéaire
    mesh = extrude_profile_along_path(profile, path, perpendicular)
    
    return mesh
```

---

### **MODULE 4: viewer_3d.html** (Three.js)

```javascript
/**
 * Visualiseur 3D interactif
 * 
 * Fonctionnalités:
 * - Chargement STL drag & drop
 * - Rotation, zoom, pan
 * - Mesures de dimensions
 * - Export captures PNG
 */

Structure:
├── scene (THREE.Scene)
├── camera (THREE.PerspectiveCamera)
├── renderer (THREE.WebGLRenderer)
├── controls (OrbitControls)
├── lights (DirectionalLight + AmbientLight)
└── loader (STLLoader)

Interactions:
- Souris gauche: Rotation
- Souris droite: Pan
- Molette: Zoom
- Double-clic: Centrer sur point
- Touche 'R': Reset vue
- Touche 'M': Afficher mesures
```

---

### **MODULE 5: prepare_for_print.py**

```python
"""
Validation et préparation finale

INPUT:  maquette_voirie.stl
OUTPUT: maquette_voirie_final.stl + rapport
"""

Vérifications:
├── is_watertight() - Mesh fermé ?
├── check_normals() - Normales cohérentes ?
├── check_degenerate() - Triangles dégénérés ?
├── check_dimensions() - Taille réaliste ?
└── suggest_orientation() - Orientation optimale impression

Réparations automatiques:
├── fill_holes()
├── fix_normals()
├── remove_duplicate_vertices()
└── merge_close_vertices()

Rapport généré:
- Dimensions (L x l x h)
- Volume (mm³)
- Surface (mm²)
- Nombre de triangles
- Temps d'impression estimé
- Quantité de filament estimée
```

---

## 📦 INSTALLATION

```bash
# 1. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Installer dépendances
pip install -r requirements.txt
```

**requirements.txt:**
```txt
# Projection géographique
pyproj>=3.6.0

# Calculs numériques
numpy>=1.24.0

# Génération 3D (⭐ essentiel)
trimesh>=4.0.0

# Dépendances trimesh
rtree>=1.0.0        # Accélération spatiale
networkx>=3.0       # Graphes pour topologie
scipy>=1.10.0       # Opérations mathématiques
pillow>=10.0.0      # Gestion images/textures

# Géométrie 2D (optionnel)
shapely>=2.0.0

# Visualisation 2D
matplotlib>=3.7.0

# Réparation mesh avancée (backup)
pymeshfix>=0.16.0

# Utilitaires
tqdm>=4.65.0        # Barres de progression
```

---

## 🎨 VARIANTES FUTURES (Carte 2, 3, 4, 5)

```
Carte 1: ✓ Relief positif simple (actuel)
         └─ Voirie uniquement

Carte 2: Relief négatif (creux)
         └─ Inverser: base pleine + routes en creux
         └─ Modification: height = -2.5 mm

Carte 3: Relief positif + bâtiments (hauteur uniforme)
         └─ Ajouter polygones OSM (building)
         └─ Hauteur constante: 5 mm

Carte 4: Carte 3 + repères tactiles
         └─ Plans d'eau: rainures horizontales
         └─ Espaces verts: petits cylindres (arbres)

Carte 5: Relief avec hauteurs réelles bâtiments
         └─ Utiliser building:levels (OSM)
         └─ Échelle verticale 1:800 (exagération 1.25x)
```

---

## ✅ VALIDATION AVANT CODE

**Questions à confirmer:**

1. **Quartier ciblé:** Volcan/Halles ou Saint-Roch ? (ou les deux ?)
2. **Dimensions souhaitées:** ~150mm x 180mm convient ?
3. **Types de voies:** Inclure footways/cycleways ?
4. **Profil routes:** Rectangle arrondi OK ?
5. **Hauteur relief:** 2.5mm perceptible ?
6. **Imprimante disponible:** FDM (Prusa, Ender) ou Résine (SLA) ?
7. **Matériau:** PLA, PETG, ABS ?

**Tests recommandés:**
- Imprimer d'abord une petite zone (50x50mm) pour valider
- Tester perception tactile avec différentes hauteurs (2mm, 3mm, 4mm)
- Vérifier robustesse des traits fins

---

## 🔄 WORKFLOW D'UTILISATION

```bash
# Étape 1: Traiter les données
python src/01_data_processor.py \
  --input data/raw/export.geojson \
  --output data/processed/processed_data.json \
  --scale 1000

# Étape 2: Preview 2D
python src/02_visualize_2d.py \
  --input data/processed/processed_data.json \
  --output data/output/preview_2d.png

# Étape 3: Générer modèle 3D
python src/03_generate_3d_model.py \
  --input data/processed/processed_data.json \
  --output data/output/maquette_voirie.stl \
  --profile rounded_rect \
  --height 2.5

# Étape 4: Visualiser 3D (navigateur)
# Ouvrir viewer/index.html dans Chrome/Firefox
# Glisser-déposer le fichier STL

# Étape 5: Préparer pour impression
python src/04_prepare_for_print.py \
  --input data/output/maquette_voirie.stl \
  --output data/output/maquette_voirie_final.stl \
  --report
```

---

## 📊 ESTIMATION PROJET

**Temps de développement:**
- Module 1 (data_processor): 2-3h
- Module 2 (visualize_2d): 1h
- Module 3 (generate_3d): 5-6h ⭐
- Module 4 (viewer_3d): 2-3h
- Module 5 (prepare_print): 1-2h
- Tests et ajustements: 3-4h
**TOTAL: 14-19 heures**

**Temps d'impression (estimé):**
- Zone 150x180mm, hauteur 5mm total
- FDM 0.2mm layer: ~3-4 heures
- Résine 0.05mm layer: ~1.5-2 heures

**Coût matériau:**
- Volume ~15-20 cm³
- PLA: ~0.30-0.50€
- Résine: ~2-3€

---

## 🎯 PRÊT POUR LA VALIDATION

**Ce qu'on a défini:**
✓ Pipeline complet 5 étapes
✓ Outils (Trimesh + Three.js)
✓ Structure fichiers
✓ Paramètres configurables
✓ Format de données intermédiaires
✓ Méthodes de génération 3D

**Prochaine étape:**
→ Validation de cette architecture
→ Puis génération du code module par module

**Des questions ? Des modifications ?**
