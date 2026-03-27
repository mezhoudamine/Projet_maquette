#!/usr/bin/env python3
"""
VISUALISATION 2D MINIMALISTE - Version Ultra-Propre
====================================================
Routes carrossables uniquement, sans axes ni légende
Style épuré pour impression ou présentation

Usage:
    python visualisation_minimaliste.py processed_data.json

Sortie:
    maquette_minimaliste.png
"""

import json
import sys
import matplotlib.pyplot as plt


def visualiser_minimaliste(fichier_input, fichier_output="maquette_minimaliste.png"):
    """
    Visualisation ultra-minimaliste : juste les routes, rien d'autre
    """
    
    print("=" * 70)
    print("VISUALISATION MINIMALISTE - Routes Carrossables")
    print("=" * 70)
    
    # 1. CHARGER
    print(f"\nChargement : {fichier_input}")
    
    with open(fichier_input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    routes_toutes = data['roads']
    metadata = data['metadata']
    
    # 2. FILTRER
    types_gardes = {'secondary', 'tertiary', 'residential', 'unclassified', 'living_street'}
    
    routes_filtrees = [r for r in routes_toutes if r['type'] in types_gardes]
    
    print(f"✓ {len(routes_filtrees)} routes filtrées (sur {len(routes_toutes)})")
    
    # 3. CRÉER FIGURE
    largeur_mm = metadata['bbox_mm']['width']
    hauteur_mm = metadata['bbox_mm']['height']
    ratio = hauteur_mm / largeur_mm
    
    fig, ax = plt.subplots(figsize=(14, 14 * ratio), facecolor='white')
    ax.set_facecolor('white')
    ax.set_aspect('equal')
    
    # 4. STYLES (Noir et gris uniquement)
    styles = {
        'secondary':      {'color': '#000000', 'width': 3.5},
        'tertiary':       {'color': '#2a2a2a', 'width': 2.5},
        'residential':    {'color': '#555555', 'width': 1.8},
        'unclassified':   {'color': '#777777', 'width': 1.5},
        'living_street':  {'color': '#999999', 'width': 1.3}
    }
    
    # 5. DESSINER
    print("Dessin en cours...")
    
    ordre = ['residential', 'unclassified', 'living_street', 'tertiary', 'secondary']
    
    for route_type in ordre:
        for route in [r for r in routes_filtrees if r['type'] == route_type]:
            coords = route['coordinates']
            x = [c[0] for c in coords]
            y = [c[1] for c in coords]
            
            style = styles.get(route_type, {'color': '#666666', 'width': 1.5})
            
            ax.plot(x, y,
                   color=style['color'],
                   linewidth=style['width'],
                   solid_capstyle='round',
                   solid_joinstyle='round',
                   alpha=0.95)
    
    print(f"✓ Routes dessinées")
    
    # 6. CONFIGURATION MINIMALISTE
    bbox = metadata['bbox_mm']
    marge = 10
    
    ax.set_xlim(bbox['min_x'] - marge, bbox['max_x'] + marge)
    ax.set_ylim(bbox['min_y'] - marge, bbox['max_y'] + marge)
    
    # SUPPRIMER TOUT (axes, ticks, labels, bordures)
    ax.axis('off')
    
    # 7. SAUVEGARDER
    print(f"\nSauvegarde : {fichier_output}")
    
    plt.tight_layout(pad=0)
    plt.savefig(fichier_output,
               dpi=300,
               bbox_inches='tight',
               facecolor='white',
               edgecolor='none',
               pad_inches=0)
    
    import os
    taille = os.path.getsize(fichier_output) / 1024
    print(f"✓ Image sauvegardée ({taille:.1f} Ko)")
    
    plt.close()
    
    print("\n" + "=" * 70)
    print("✓ TERMINÉ - Version ultra-propre générée")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualisation_minimaliste.py <fichier_json> [sortie]")
        sys.exit(1)
    
    fichier_input = sys.argv[1]
    fichier_output = sys.argv[2] if len(sys.argv) >= 3 else "maquette_minimaliste.png"
    
    try:
        visualiser_minimaliste(fichier_input, fichier_output)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
