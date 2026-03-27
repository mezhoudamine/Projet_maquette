#!/usr/bin/env python3
"""
ÉTAPE 2 : Visualisation 2D Simple
==================================
Génère une image PNG simple des routes à partir du fichier processed_data.json

Style : Lignes noires/grises sur fond blanc (comme votre exemple)

Usage:
    python visualisation_2d_simple.py processed_data.json

Sortie:
    maquette_2d.png
"""

import json
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def visualiser_2d(fichier_input, fichier_output="maquette_2d.png"):
    """
    Crée une visualisation 2D simple des routes
    
    Args:
        fichier_input: Chemin vers processed_data.json
        fichier_output: Chemin de l'image de sortie
    """
    
    print("=" * 70)
    print("ÉTAPE 2 : VISUALISATION 2D")
    print("=" * 70)
    
    # 1. CHARGER LES DONNÉES
    print(f"\n[1/4] Chargement : {fichier_input}")
    
    try:
        with open(fichier_input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f" ERREUR : Fichier '{fichier_input}' introuvable")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f" ERREUR : Fichier JSON invalide")
        sys.exit(1)
    
    routes = data['roads']
    metadata = data['metadata']
    
    print(f"✓ {len(routes)} routes chargées")
    print(f"  Dimensions : {metadata['bbox_mm']['width']:.1f} × {metadata['bbox_mm']['height']:.1f} mm")
    
    # 2. CRÉER LA FIGURE
    print("\n[2/4] Création de la figure...")
    
    # Taille de la figure (proportionnelle aux dimensions)
    largeur_mm = metadata['bbox_mm']['width']
    hauteur_mm = metadata['bbox_mm']['height']
    
    # Taille en inches (1 inch = 25.4 mm)
    ratio = hauteur_mm / largeur_mm
    fig_width = 12  # inches
    fig_height = fig_width * ratio
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor='white')
    ax.set_facecolor('white')
    ax.set_aspect('equal')
    
    # 3. DESSINER LES ROUTES
    print("\n[3/4] Dessin des routes...")
    
    # Définir les épaisseurs et couleurs selon le type
    styles = {
        # Routes principales : plus épaisses et noires
        'motorway': {'color': '#000000', 'width': 3.0},
        'trunk': {'color': '#000000', 'width': 2.8},
        'primary': {'color': '#000000', 'width': 2.5},
        'secondary': {'color': '#000000', 'width': 2.0},
        'tertiary': {'color': '#333333', 'width': 1.8},
        
        # Routes secondaires : grises
        'unclassified': {'color': '#666666', 'width': 1.2},
        'residential': {'color': '#666666', 'width': 1.2},
        'living_street': {'color': '#888888', 'width': 1.0},
        
        # Service et petites routes : grises claires
        'service': {'color': '#999999', 'width': 0.8},
        'pedestrian': {'color': '#aaaaaa', 'width': 0.8},
        
        # Chemins piétons et cyclables : très fins
        'footway': {'color': '#bbbbbb', 'width': 0.5},
        'cycleway': {'color': '#bbbbbb', 'width': 0.5},
        'path': {'color': '#cccccc', 'width': 0.4},
        
        # Par défaut
        'default': {'color': '#888888', 'width': 1.0}
    }
    
    # Compter par type pour statistiques
    stats = {}
    
    # Dessiner chaque route
    for route in routes:
        coords = route['coordinates']
        route_type = route['type']
        
        # Statistiques
        stats[route_type] = stats.get(route_type, 0) + 1
        
        # Style
        style = styles.get(route_type, styles['default'])
        
        # Extraire x et y
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        
        # Dessiner la ligne
        ax.plot(
            x_coords, y_coords,
            color=style['color'],
            linewidth=style['width'],
            solid_capstyle='round',
            solid_joinstyle='round',
            zorder=10 - style['width']  # Routes larges en arrière-plan
        )
    
    print(f"✓ {len(routes)} routes dessinées")
    
    # Afficher stats
    print("\n  Répartition par type :")
    for route_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    {route_type:20s} : {count:3d}")
    
    # 4. CONFIGURER LES AXES
    print("\n[4/4] Configuration de l'image...")
    
    # Limites (avec petite marge)
    bbox = metadata['bbox_mm']
    marge = 10  # mm
    
    ax.set_xlim(bbox['min_x'] - marge, bbox['max_x'] + marge)
    ax.set_ylim(bbox['min_y'] - marge, bbox['max_y'] + marge)
    
    # Supprimer les axes (style épuré comme votre image)
    ax.axis('off')
    
    # Titre optionnel (commentez si vous ne voulez pas)
    # ax.set_title(
    #     f"Maquette Tactile - {largeur_mm:.0f} × {hauteur_mm:.0f} mm",
    #     fontsize=16, fontweight='bold', pad=20
    # )
    
    # 5. SAUVEGARDER
    print(f"\nSauvegarde : {fichier_output}")
    
    plt.tight_layout(pad=0.1)
    
    plt.savefig(
        fichier_output,
        dpi=300,  # Haute résolution
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none',
        pad_inches=0.05
    )
    
    print(f"✓ Image sauvegardée (300 DPI)")
    
    # Taille du fichier
    import os
    taille_ko = os.path.getsize(fichier_output) / 1024
    print(f"  Taille : {taille_ko:.1f} Ko")
    
    plt.close()
    
    print("\n" + "=" * 70)
    print("✓ VISUALISATION TERMINÉE")
    print("=" * 70)
    print(f"\nFichier généré : {fichier_output}")
    print("Ouvrez l'image pour voir votre maquette !")
    print("=" * 70)


def main():
    """Point d'entrée principal"""
    
    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("Usage: python visualisation_2d_simple.py <fichier_json>")
        print("\nExemple:")
        print("  python visualisation_2d_simple.py processed_data.json")
        sys.exit(1)
    
    fichier_input = sys.argv[1]
    
    # Fichier de sortie (optionnel)
    if len(sys.argv) >= 3:
        fichier_output = sys.argv[2]
    else:
        fichier_output = "maquette_2d.png"
    
    # Visualiser
    try:
        visualiser_2d(fichier_input, fichier_output)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
