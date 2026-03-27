#!/usr/bin/env python3
"""
VISUALISATION 2D FILTRÉE - Routes Carrossables Uniquement
==========================================================
Affiche uniquement les routes essentielles pour une maquette tactile claire

Types inclus : secondary, tertiary, residential, unclassified, living_street
Types exclus : service, footway, cycleway, path, pedestrian

Style : Hiérarchie visuelle claire avec couleurs propres

Usage:
    python visualisation_filtree.py processed_data.json

Sortie:
    maquette_filtree.png
"""

import json
import sys
import matplotlib.pyplot as plt


def visualiser_filtree(fichier_input, fichier_output="maquette_filtree.png"):
    """
    Crée une visualisation 2D des routes carrossables uniquement
    
    Args:
        fichier_input: Chemin vers processed_data.json
        fichier_output: Chemin de l'image de sortie
    """
    
    print("=" * 70)
    print("VISUALISATION 2D FILTRÉE - Routes Carrossables")
    print("=" * 70)
    
    # 1. CHARGER LES DONNÉES
    print(f"\n[1/5] Chargement : {fichier_input}")
    
    try:
        with open(fichier_input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERREUR : Fichier '{fichier_input}' introuvable")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ ERREUR : Fichier JSON invalide")
        sys.exit(1)
    
    routes_toutes = data['roads']
    metadata = data['metadata']
    
    print(f"✓ {len(routes_toutes)} routes chargées")
    
    # 2. FILTRER LES ROUTES
    print("\n[2/5] Filtrage des routes...")
    
    # Types à GARDER (routes carrossables uniquement)
    types_gardes = {
        'secondary',
        'tertiary',
        'residential',
        'unclassified',
        'living_street'
    }
    
    # Types à EXCLURE
    types_exclus = {
        'service',
        'footway',
        'cycleway',
        'path',
        'pedestrian',
        'steps'
    }
    
    routes_filtrees = []
    stats_avant = {}
    stats_apres = {}
    
    for route in routes_toutes:
        route_type = route['type']
        stats_avant[route_type] = stats_avant.get(route_type, 0) + 1
        
        if route_type in types_gardes:
            routes_filtrees.append(route)
            stats_apres[route_type] = stats_apres.get(route_type, 0) + 1
    
    print(f"✓ Filtrage terminé")
    print(f"  Avant : {len(routes_toutes)} routes")
    print(f"  Après : {len(routes_filtrees)} routes ({len(routes_filtrees)/len(routes_toutes)*100:.1f}%)")
    
    print(f"\n  Routes CONSERVÉES :")
    for route_type in sorted(types_gardes):
        if route_type in stats_apres:
            print(f"    ✓ {route_type:20s} : {stats_apres[route_type]:3d}")
    
    print(f"\n  Routes EXCLUES :")
    for route_type in sorted(types_exclus):
        if route_type in stats_avant:
            print(f"    ✗ {route_type:20s} : {stats_avant[route_type]:3d}")
    
    # 3. CRÉER LA FIGURE
    print("\n[3/5] Création de la figure...")
    
    # Dimensions
    largeur_mm = metadata['bbox_mm']['width']
    hauteur_mm = metadata['bbox_mm']['height']
    
    # Taille proportionnelle
    ratio = hauteur_mm / largeur_mm
    fig_width = 14
    fig_height = fig_width * ratio
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor='white')
    ax.set_facecolor('white')
    ax.set_aspect('equal')
    
    # 4. DÉFINIR LES STYLES (Couleurs propres et hiérarchisées)
    print("\n[4/5] Application des styles...")
    
    styles = {
        # Routes principales : NOIR (importance maximale)
        'secondary': {
            'color': '#000000',      # Noir pur
            'width': 3.0,
            'label': 'Routes secondaires (principales)',
            'zorder': 3
        },
        
        # Routes tertiaires : GRIS FONCÉ (structure)
        'tertiary': {
            'color': '#404040',      # Gris très foncé
            'width': 2.2,
            'label': 'Routes tertiaires',
            'zorder': 2
        },
        
        # Routes résidentielles : GRIS MOYEN (tissu urbain)
        'residential': {
            'color': '#707070',      # Gris moyen
            'width': 1.5,
            'label': 'Routes résidentielles',
            'zorder': 1
        },
        
        # Routes non classifiées : GRIS CLAIR
        'unclassified': {
            'color': '#909090',      # Gris clair
            'width': 1.3,
            'label': 'Routes non classifiées',
            'zorder': 1
        },
        
        # Zones partagées : GRIS TRÈS CLAIR
        'living_street': {
            'color': '#a0a0a0',      # Gris très clair
            'width': 1.2,
            'label': 'Zones partagées',
            'zorder': 1
        }
    }
    
    # 5. DESSINER LES ROUTES PAR ORDRE D'IMPORTANCE
    print("\n[5/5] Dessin des routes...")
    
    # Ordre de dessin : des plus larges aux plus fines
    ordre_dessin = ['residential', 'unclassified', 'living_street', 'tertiary', 'secondary']
    
    routes_dessinees = 0
    
    for route_type in ordre_dessin:
        if route_type not in styles:
            continue
        
        style = styles[route_type]
        
        # Filtrer les routes de ce type
        routes_type = [r for r in routes_filtrees if r['type'] == route_type]
        
        if not routes_type:
            continue
        
        for route in routes_type:
            coords = route['coordinates']
            
            # Extraire x et y
            x_coords = [c[0] for c in coords]
            y_coords = [c[1] for c in coords]
            
            # Dessiner
            ax.plot(
                x_coords, y_coords,
                color=style['color'],
                linewidth=style['width'],
                solid_capstyle='round',
                solid_joinstyle='round',
                zorder=style['zorder'],
                alpha=0.95  # Légère transparence pour les superpositions
            )
            
            routes_dessinees += 1
    
    print(f"✓ {routes_dessinees} routes dessinées")
    
    # 6. CONFIGURER LES AXES ET LÉGENDE
    bbox = metadata['bbox_mm']
    marge = 15  # mm
    
    ax.set_xlim(bbox['min_x'] - marge, bbox['max_x'] + marge)
    ax.set_ylim(bbox['min_y'] - marge, bbox['max_y'] + marge)
    
    # Titre propre
    ax.set_title(
        f"Maquette Tactile - Routes Carrossables\n{largeur_mm:.0f} × {hauteur_mm:.0f} mm (Échelle 1:1000)",
        fontsize=16,
        fontweight='bold',
        pad=20,
        color='#333333'
    )
    
    # Légende élégante
    from matplotlib.lines import Line2D
    
    legend_elements = []
    for route_type in ordre_dessin[::-1]:  # Ordre inverse pour la légende
        if route_type in styles and route_type in stats_apres:
            style = styles[route_type]
            legend_elements.append(
                Line2D([0], [0], 
                       color=style['color'], 
                       linewidth=style['width'],
                       label=f"{style['label']} ({stats_apres[route_type]})")
            )
    
    ax.legend(
        handles=legend_elements,
        loc='upper right',
        fontsize=10,
        framealpha=0.95,
        edgecolor='#cccccc',
        title='Types de routes',
        title_fontsize=11
    )
    
    # Axes propres (grille légère)
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5)
    ax.set_xlabel('X (mm)', fontsize=11, color='#666666')
    ax.set_ylabel('Y (mm)', fontsize=11, color='#666666')
    ax.tick_params(colors='#666666', labelsize=9)
    
    # Bordure propre
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')
        spine.set_linewidth(1)
    
    # 7. SAUVEGARDER
    print(f"\nSauvegarde : {fichier_output}")
    
    plt.tight_layout()
    
    plt.savefig(
        fichier_output,
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none'
    )
    
    print(f"✓ Image sauvegardée (300 DPI)")
    
    # Taille du fichier
    import os
    taille_ko = os.path.getsize(fichier_output) / 1024
    print(f"  Taille : {taille_ko:.1f} Ko")
    
    plt.close()
    
    # 8. RÉSUMÉ
    print("\n" + "=" * 70)
    print("✓ VISUALISATION TERMINÉE")
    print("=" * 70)
    print(f"\nFichier généré : {fichier_output}")
    print(f"\nRésumé :")
    print(f"  • {len(routes_filtrees)} routes carrossables affichées")
    print(f"  • {len(routes_toutes) - len(routes_filtrees)} routes exclues (chemins piétons, service)")
    print(f"  • Hiérarchie claire : noir (principal) → gris (secondaire)")
    print(f"  • Parfait pour maquette tactile 3D")
    print("=" * 70)


def main():
    """Point d'entrée principal"""
    
    if len(sys.argv) < 2:
        print("Usage: python visualisation_filtree.py <fichier_json> [fichier_sortie]")
        print("\nExemple:")
        print("  python visualisation_filtree.py processed_data.json")
        print("  python visualisation_filtree.py processed_data.json ma_carte.png")
        sys.exit(1)
    
    fichier_input = sys.argv[1]
    
    if len(sys.argv) >= 3:
        fichier_output = sys.argv[2]
    else:
        fichier_output = "maquette_filtree.png"
    
    try:
        visualiser_filtree(fichier_input, fichier_output)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
