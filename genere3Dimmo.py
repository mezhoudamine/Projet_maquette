#!/usr/bin/env python3
import json
import sys
import numpy as np
import config

try:
    import trimesh
    import trimesh.transformations as tf
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
except ImportError:
    sys.exit("ERREUR: Installez les modules -> pip install trimesh shapely numpy")

def generer_3d(fichier_input, fichier_output="maquette_3d.stl"):
    print("=" * 60)
    print("GÉNÉRATION 3D - Bâtiments Complexes")
    print("=" * 60)
    
    with open(fichier_input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    meshes = []
    
    # 1. BASE
    print("[1/3] Construction de la base...")
    bbox = data['metadata']['bbox_mm']
    w, h = bbox['width'] + 2*config.BASE_MARGIN, bbox['height'] + 2*config.BASE_MARGIN
    base = trimesh.creation.box(extents=[w, h, config.BASE_THICKNESS])
    base.apply_translation([0, 0, config.BASE_THICKNESS/2]) # Centré en 0,0
    meshes.append(base)
    
    # 2. ROUTES
    print(f"[2/3] Construction des routes ({len(data['roads'])})...")
    for r in data['roads']:
        pts = r['coordinates']
        if len(pts) < 2: continue
        
        width = config.get_road_width(r['type'])
        
        for i in range(len(pts)-1):
            p1, p2 = np.array(pts[i]), np.array(pts[i+1])
            vec = p2 - p1
            dist = np.linalg.norm(vec)
            if dist < 0.1: continue
            
            box = trimesh.creation.box(extents=[dist, width, config.ROAD_HEIGHT])
            angle = np.arctan2(vec[1], vec[0])
            box.apply_transform(tf.rotation_matrix(angle, [0,0,1]))
            mid = (p1+p2)/2
            box.apply_translation([mid[0], mid[1], config.BASE_THICKNESS + config.ROAD_HEIGHT/2])
            meshes.append(box)

    # 3. BÂTIMENTS COMPLEXES
    print(f"[3/3] Construction des bâtiments ({len(data['buildings'])})...")
    h_bat = getattr(config, 'BUILDING_HEIGHT', 10.0)
    
    for bat in data['buildings']:
        for part in bat['parts']:
            shell = part['shell']
            holes = part['holes']
            
            if len(shell) < 3: continue
            
            try:
                # Création du polygone Shapely avec trous
                poly = Polygon(shell=shell, holes=holes)
                
                # Nettoyage géométrique (indispensable pour les données OSM brutes)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                
                if poly.is_empty: continue

                # Extrusion via Trimesh
                # Trimesh gère nativement les polygones Shapely avec trous !
                mesh = trimesh.creation.extrude_polygon(poly, height=h_bat)
                
                # Positionnement sur la base
                mesh.apply_translation([0, 0, config.BASE_THICKNESS])
                meshes.append(mesh)
                
            except Exception as e:
                print(f"  ! Erreur sur bâtiment {bat['id']}: {e}")

    # EXPORT
    if meshes:
        print("\nFusion et Export...")
        final = trimesh.util.concatenate(meshes)
        final.export(fichier_output)
        print(f"✓ Fichier STL créé : {fichier_output}")
    else:
        print("Erreur: Rien à générer.")

if __name__ == "__main__":
    fichier_entree = "data/processed/volcantest_proceced.json"
    
    # Tu peux aussi choisir le nom du fichier STL de sortie ici (2ème argument)
    fichier_sortie = "maquette_testvolcan.stl"
    
    generer_3d(fichier_entree, fichier_sortie)