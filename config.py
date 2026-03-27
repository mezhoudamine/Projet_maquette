"""
Configuration globale du projet Maquette Tactile 3D
Tous les paramètres modifiables en un seul endroit
"""

# ============================================================================
# PROJECTION GÉOGRAPHIQUE
# ============================================================================
CRS_SOURCE = "EPSG:4326"      # WGS84 (lat/lon en degrés)
CRS_TARGET = "EPSG:2154"      # Lambert 93 (France métropolitaine, en mètres)



# ============================================================================
# BÂTIMENTS (IMMEUBLES)
# ============================================================================
INCLUDE_BUILDINGS = True       # Inclure les bâtiments
BUILDING_HEIGHT = 40.0         # Hauteur fixe des bâtiments (en mm)
# ============================================================================
# ÉCHELLES
# ============================================================================
SCALE_HORIZONTAL = 1000        # 1:1000 (1m réel = 1mm sur maquette)
SCALE_VERTICAL = 800           # 1:800 (exagération verticale)
EXAGGERATION_RATIO = SCALE_HORIZONTAL / SCALE_VERTICAL  # = 1.25

# ============================================================================
# DIMENSIONS MAQUETTE (en millimètres)
# ============================================================================
BASE_THICKNESS = 2.5           # Épaisseur de la plaque de base
BASE_MARGIN = 5.0              # Marge autour des routes
ROAD_HEIGHT = 2.5              # Hauteur des traits en relief positif

# ============================================================================
# LARGEURS DES ROUTES PAR TYPE (en millimètres)
# ============================================================================
ROAD_WIDTH_DEFAULT = 1.5

ROAD_WIDTHS = {
    "motorway": 3.0,
    "trunk": 2.8,
    "primary": 2.5,
    "secondary": 2.0,
    "tertiary": 1.5,
    "unclassified": 1.2,
    "residential": 1.2,
    "living_street": 1.0,
    "service": 0.8,
    "pedestrian": 1.0,
    "footway": 0.6,
    "cycleway": 0.6,
    "path": 0.5,
    "steps": 0.5,
    "default": 1.0
}

# ============================================================================
# PROFIL DES ROUTES
# ============================================================================
ROAD_PROFILE = "rounded_rect"  # Options: "rectangle", "rounded_rect", "half_cylinder"
CORNER_RADIUS = 0.3            # Rayon des coins arrondis (mm)
MESH_RESOLUTION = 16           # Nombre de segments pour les arrondis (8-32)

# ============================================================================
# FILTRAGE DES TYPES DE VOIES
# ============================================================================
INCLUDE_FOOTWAYS = True        # Inclure les chemins piétons
INCLUDE_CYCLEWAYS = True       # Inclure les pistes cyclables
INCLUDE_STEPS = False          # Inclure les escaliers
INCLUDE_SERVICE = True         # Inclure les voies de service

# Types de voies à exclure (liste noire)
EXCLUDE_TYPES = []
if not INCLUDE_FOOTWAYS:
    EXCLUDE_TYPES.append("footway")
if not INCLUDE_CYCLEWAYS:
    EXCLUDE_TYPES.append("cycleway")
if not INCLUDE_STEPS:
    EXCLUDE_TYPES.append("steps")
if not INCLUDE_SERVICE:
    EXCLUDE_TYPES.append("service")

# ============================================================================
# SIMPLIFICATION (optionnel, pour réduire la complexité)
# ============================================================================
SIMPLIFY_GEOMETRY = False      # Activer la simplification
SIMPLIFY_TOLERANCE = 0.2       # Tolérance en mm
MIN_SEGMENT_LENGTH = 0.5       # Longueur minimum d'un segment (mm)

# ============================================================================
# EXPORT STL
# ============================================================================
STL_BINARY = True              # True = binaire (plus compact), False = ASCII
STL_PRECISION = 6              # Nombre de décimales pour ASCII

# ============================================================================
# VISUALISATION 2D
# ============================================================================
FIGURE_SIZE = (14, 14)         # Taille de la figure matplotlib (inches)
DPI = 300                      # Résolution pour export PNG
BACKGROUND_COLOR = "white"
GRID_VISIBLE = True            # Afficher une grille en mm

# Couleurs par type de route (pour visualisation 2D)
ROAD_COLORS = {
    "motorway": "#e892a2",
    "trunk": "#f9b29c",
    "primary": "#fcd6a4",
    "secondary": "#f7fabf",
    "tertiary": "#ffffff",
    "unclassified": "#dcdcdc",
    "residential": "#dcdcdc",
    "living_street": "#c5c5c5",
    "service": "#cfcdca",
    "pedestrian": "#dddde8",
    "footway": "#fa8072",
    "cycleway": "#6495ed",
    "path": "#8b4513",
    "steps": "#a0522d",
    "default": "#888888"
}

# ============================================================================
# VISUALISATION 3D (Three.js)
# ============================================================================
CAMERA_DISTANCE = 300          # Distance initiale de la caméra (mm)
LIGHT_INTENSITY = 1.5
VIEWER_BACKGROUND = "#f0f0f0"

# ============================================================================
# VALIDATION ET DEBUG
# ============================================================================
VERBOSE = True                 # Afficher des messages détaillés
CHECK_GEOMETRY = True          # Vérifier la validité des géométries
REPAIR_MESH = True             # Réparer automatiquement les mesh invalides

# ============================================================================
# CHEMINS DES FICHIERS
# ============================================================================
import os

# Dossier racine du projet
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Dossiers de données
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# Créer les dossiers s'ils n'existent pas
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Fichiers par défaut
DEFAULT_INPUT_GEOJSON = os.path.join(RAW_DATA_DIR, "export.geojson")
DEFAULT_PROCESSED_JSON = os.path.join(PROCESSED_DATA_DIR, "processed_data.json")
DEFAULT_OUTPUT_STL = os.path.join(OUTPUT_DIR, "maquette_voirie.stl")
DEFAULT_PREVIEW_2D = os.path.join(OUTPUT_DIR, "preview_2d.png")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_road_width(highway_type):
    """Retourne la largeur d'une route selon son type"""
    return ROAD_WIDTHS.get(highway_type, ROAD_WIDTH_DEFAULT)

def get_road_color(highway_type):
    """Retourne la couleur d'une route selon son type"""
    return ROAD_COLORS.get(highway_type, ROAD_COLORS["default"])

def should_include_road(highway_type):
    """Détermine si un type de route doit être inclus"""
    return highway_type not in EXCLUDE_TYPES

def print_config():
    """Affiche la configuration actuelle"""
    print("=" * 70)
    print("CONFIGURATION DU PROJET")
    print("=" * 70)
    print(f"Projection: {CRS_SOURCE} → {CRS_TARGET}")
    print(f"Échelle horizontale: 1:{SCALE_HORIZONTAL}")
    print(f"Échelle verticale: 1:{SCALE_VERTICAL}")
    print(f"Exagération verticale: {EXAGGERATION_RATIO:.2f}x")
    print(f"\nDimensions maquette:")
    print(f"  - Base: {BASE_THICKNESS}mm d'épaisseur")
    print(f"  - Routes: {ROAD_HEIGHT}mm de hauteur")
    print(f"  - Marge: {BASE_MARGIN}mm")
    print(f"\nProfil des routes: {ROAD_PROFILE}")
    print(f"Résolution mesh: {MESH_RESOLUTION} segments")
    print(f"\nTypes de voies inclus:")
    print(f"  - Footways: {'Oui' if INCLUDE_FOOTWAYS else 'Non'}")
    print(f"  - Cycleways: {'Oui' if INCLUDE_CYCLEWAYS else 'Non'}")
    print(f"  - Steps: {'Oui' if INCLUDE_STEPS else 'Non'}")
    print(f"  - Service: {'Oui' if INCLUDE_SERVICE else 'Non'}")
    print("=" * 70)


if __name__ == "__main__":
    print_config()
