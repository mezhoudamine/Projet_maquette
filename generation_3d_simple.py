#!/usr/bin/env python3
"""
ÉTAPE 3 : Génération 3D Simple (Version Pavés)
==============================================
Génère un fichier STL à partir du fichier processed_data.json
Les routes sont générées sous forme de pavés rectangulaires.

Usage:
    python generation_3d_simple.py processed_data.json
"""

import json
import sys
import numpy as np
import os

try:
    import trimesh
    import trimesh.transformations as tf
except ImportError:
    print(" ERREUR : trimesh n'est pas installé")
    print("Installation : pip install trimesh")
    sys.exit(1)


def generer_3d(fichier_input, fichier_output="maquette_3d.stl"):
    """
    Génère un modèle 3D STL simple avec des routes pavées
    """
    
    print("=" * 70)
    print("GÉNÉRATION 3D - Maquette Tactile (Style Pavé)")
    print("=" * 70)
    
    # PARAMÈTRES
    EPAISSEUR_BASE = 2.5      # mm
    HAUTEUR_ROUTE = 2.5       # mm (Hauteur du pavé par rapport à la base)
    MARGE = 5.0               # mm
    
    # 1. CHARGER
    print(f"\n[1/6] Chargement : {fichier_input}")
    
    with open(fichier_input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    routes_toutes = data['roads']
    metadata = data['metadata']
    
    print(f"✓ {len(routes_toutes)} routes chargées")
    
    # 2. FILTRER (routes carrossables uniquement)
    print("\n[2/6] Filtrage des routes...")
    
    types_gardes = {'secondary', 'tertiary', 'residential', 'unclassified', 'living_street'}
    
    routes = [r for r in routes_toutes if r['type'] in types_gardes]
    
    print(f"✓ {len(routes)} routes filtrées (routes carrossables uniquement)")
    print(f"  {len(routes_toutes) - len(routes)} routes exclues (service, footway, etc.)")
    
    # 3. CRÉER LA BASE
    print("\n[3/6] Création de la plaque de base...")
    
    bbox = metadata['bbox_mm']
    
    largeur = bbox['width'] + 2 * MARGE
    hauteur = bbox['height'] + 2 * MARGE
    
    centre_x = (bbox['min_x'] + bbox['max_x']) / 2
    centre_y = (bbox['min_y'] + bbox['max_y']) / 2
    
    print(f"  Dimensions : {largeur:.1f} × {hauteur:.1f} × {EPAISSEUR_BASE} mm")
    
    # Créer la base
    base = trimesh.creation.box(
        extents=[largeur, hauteur, EPAISSEUR_BASE]
    )
    base.apply_translation([centre_x, centre_y, EPAISSEUR_BASE / 2])
    
    print(f"✓ Base créée")
    
    # 4. CRÉER LES ROUTES
    print(f"\n[4/6] Génération des routes ({len(routes)} routes)...")
    
    # Largeurs par type
    largeurs = {
        'secondary': 4.0,       # Un peu plus large pour bien voir
        'tertiary': 3.5,
        'residential': 3.0,
        'unclassified': 2.5,
        'living_street': 2.5
    }
    
    meshes_routes = []
    compteur = 0
    
    for route in routes:
        coords = route['coordinates']
        route_type = route['type']
        largeur_route = largeurs.get(route_type, 2.5)
        
        # Pour chaque segment de route
        for i in range(len(coords) - 1):
            p1 = np.array([coords[i][0], coords[i][1], EPAISSEUR_BASE])
            p2 = np.array([coords[i+1][0], coords[i+1][1], EPAISSEUR_BASE])
            
            # Calculer vecteur direction
            direction = p2 - p1
            longueur = np.linalg.norm(direction)
            
            if longueur < 0.1:  # Ignorer les segments trop courts
                continue
            
            # --- MODIFICATION ICI : CRÉATION DE PAVÉ (BOÎTE) ---
            
            try:
                # On crée une boîte.
                # Par défaut, trimesh crée une boite centrée en 0,0,0
                # Dimensions: [Longueur (X), Largeur (Y), Hauteur (Z)]
                box = trimesh.creation.box(
                    extents=[longueur, largeur_route, HAUTEUR_ROUTE]
                )
                
                # 1. Rotation
                # On calcule l'angle dans le plan 2D (X, Y)
                angle_z = np.arctan2(direction[1], direction[0])
                
                # Matrice de rotation autour de l'axe Z
                rotation = tf.rotation_matrix(angle_z, [0, 0, 1])
                box.apply_transform(rotation)
                
                # 2. Positionnement
                # On place le centre de la boîte au milieu du segment
                centre_segment = (p1 + p2) / 2
                
                # Ajustement Z : Base + moitié de la hauteur de la route
                centre_segment[2] = EPAISSEUR_BASE + (HAUTEUR_ROUTE / 2)
                
                box.apply_translation(centre_segment)
                
                meshes_routes.append(box)
                compteur += 1
                
            except Exception as e:
                print(f"  Avertissement : segment ignoré ({e})")
                continue
        
        # Afficher progression
        if (routes.index(route) + 1) % 50 == 0:
            print(f"  {routes.index(route) + 1}/{len(routes)} routes traitées...")
    
    print(f"✓ {compteur} segments de routes créés")
    
    # 5. FUSIONNER
    print(f"\n[5/6] Fusion des géométries...")
    
    if not meshes_routes:
        print("ATTENTION: Aucune route générée !")
        mesh_final = base
    else:
        print(f"  Base : 1 mesh")
        print(f"  Routes : {len(meshes_routes)} meshes")
        
        # Combiner tous les meshes
        # Note: concaténer est rapide, mais ne fait pas d'union booléenne parfaite.
        # Pour l'impression 3D, la plupart des slicers gèrent très bien les objets qui s'interpénètrent.
        tous_meshes = [base] + meshes_routes
        mesh_final = trimesh.util.concatenate(tous_meshes)
    
    print(f"✓ Mesh final : {len(mesh_final.vertices)} vertices, {len(mesh_final.faces)} faces")
    
    # 6. SAUVEGARDER
    print(f"\n[6/6] Export STL : {fichier_output}")
    
    # Exporter en STL
    mesh_final.export(fichier_output)
    
    # Taille du fichier
    taille_mo = os.path.getsize(fichier_output) / (1024 * 1024)
    
    print(f"✓ Fichier sauvegardé ({taille_mo:.2f} Mo)")
    
    # Dimensions finales
    bounds = mesh_final.bounds
    dims = bounds[1] - bounds[0]
    
    print(f"\nDimensions du modèle :")
    print(f"  Largeur (X) : {dims[0]:.1f} mm")
    print(f"  Profondeur (Y) : {dims[1]:.1f} mm")
    print(f"  Hauteur (Z) : {dims[2]:.1f} mm")
    
    print("\n" + "=" * 70)
    print("✓ GÉNÉRATION TERMINÉE")
    print("=" * 70)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generation_3d_simple.py <fichier_json> [fichier_stl]")
        sys.exit(1)
    
    fichier_input = sys.argv[1]
    fichier_output = sys.argv[2] if len(sys.argv) >= 3 else "maquette_3d.stl"
    
    try:
        generer_3d(fichier_input, fichier_output)
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()