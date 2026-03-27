#!/usr/bin/env python3
"""
MODULE 3: Générateur de Modèle 3D
==================================
Génération du modèle 3D STL à partir des données traitées

Pipeline:
1. Création de la plaque de base
2. Génération des segments de routes (extrusion)
3. Ajout de sphères aux intersections
4. Fusion de toutes les géométries
5. Validation et réparation
6. Export STL

Entrée:  processed_data.json
Sortie:  maquette_voirie.stl
"""

import json
import argparse
import sys
from pathlib import Path
import time

try:
    import numpy as np
    import trimesh
    from tqdm import tqdm
except ImportError as e:
    print(f"Erreur: module manquant - {e}")
    print("Installation: pip install numpy trimesh tqdm")
    sys.exit(1)

import config


class MeshGenerator3D:
    """Générateur de modèle 3D pour maquette tactile"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.data = None
        self.base_mesh = None
        self.road_meshes = []
        self.intersection_meshes = []
        self.final_mesh = None
        
    def log(self, message):
        """Affiche un message si verbose est activé"""
        if self.verbose:
            print(message)
    
    def load_processed_data(self, filepath):
        """
        Charge les données traitées
        
        Args:
            filepath: Chemin vers processed_data.json
            
        Returns:
            dict: Données chargées
        """
        self.log(f"Lecture du fichier: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier introuvable: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Fichier JSON invalide: {filepath}")
        
        self.data = data
        
        self.log(f"✓ {len(data['roads'])} routes chargées")
        
        return data
    
    def create_base_plate(self):
        """
        Crée la plaque de base rectangulaire
        
        Returns:
            trimesh.Trimesh: Plaque de base
        """
        self.log("\nCréation de la plaque de base...")
        
        bbox = self.data['metadata']['bbox_mm']
        margin = config.BASE_MARGIN
        thickness = config.BASE_THICKNESS
        
        # Dimensions de la plaque
        width = bbox['width'] + 2 * margin
        height = bbox['height'] + 2 * margin
        
        # Centre de la plaque
        center_x = (bbox['min_x'] + bbox['max_x']) / 2
        center_y = (bbox['min_y'] + bbox['max_y']) / 2
        
        self.log(f"  Dimensions: {width:.1f} × {height:.1f} × {thickness:.1f} mm")
        
        # Créer une boîte
        base = trimesh.creation.box(
            extents=[width, height, thickness]
        )
        
        # Positionner la base
        # Le centre de la boîte est à l'origine, on la translate
        base.apply_translation([center_x, center_y, thickness / 2])
        
        self.base_mesh = base
        
        return base
    
    def create_rounded_rectangle_profile(self, width, height, radius):
        """
        Crée un profil de rectangle arrondi (section transversale)
        
        Args:
            width: Largeur du rectangle
            height: Hauteur du rectangle
            radius: Rayon des coins arrondis
            
        Returns:
            np.array: Points du profil 2D
        """
        # Limiter le rayon
        max_radius = min(width, height) / 2
        radius = min(radius, max_radius)
        
        # Nombre de segments pour les coins
        segments_per_corner = config.MESH_RESOLUTION // 4
        
        profile_points = []
        
        # Coin inférieur gauche (quart de cercle)
        angles = np.linspace(np.pi, 3*np.pi/2, segments_per_corner)
        for angle in angles:
            x = -width/2 + radius + radius * np.cos(angle)
            y = radius + radius * np.sin(angle)
            profile_points.append([x, y])
        
        # Coin inférieur droit
        angles = np.linspace(3*np.pi/2, 2*np.pi, segments_per_corner)
        for angle in angles:
            x = width/2 - radius + radius * np.cos(angle)
            y = radius + radius * np.sin(angle)
            profile_points.append([x, y])
        
        # Coin supérieur droit
        angles = np.linspace(0, np.pi/2, segments_per_corner)
        for angle in angles:
            x = width/2 - radius + radius * np.cos(angle)
            y = height - radius + radius * np.sin(angle)
            profile_points.append([x, y])
        
        # Coin supérieur gauche
        angles = np.linspace(np.pi/2, np.pi, segments_per_corner)
        for angle in angles:
            x = -width/2 + radius + radius * np.cos(angle)
            y = height - radius + radius * np.sin(angle)
            profile_points.append([x, y])
        
        return np.array(profile_points)
    
    def create_rectangle_profile(self, width, height):
        """
        Crée un profil rectangulaire simple
        
        Args:
            width: Largeur
            height: Hauteur
            
        Returns:
            np.array: Points du profil 2D
        """
        return np.array([
            [-width/2, 0],
            [width/2, 0],
            [width/2, height],
            [-width/2, height]
        ])
    
    def extrude_profile_along_path(self, profile_2d, path_3d):
        """
        Extrude un profil 2D le long d'un chemin 3D
        
        Args:
            profile_2d: Points du profil 2D (N, 2)
            path_3d: Points du chemin 3D (M, 3)
            
        Returns:
            trimesh.Trimesh: Mesh extrudé
        """
        # Utiliser trimesh pour créer l'extrusion
        # On crée un path 3D à partir du profil 2D
        
        # Nombre de points sur le profil et le chemin
        n_profile = len(profile_2d)
        n_path = len(path_3d)
        
        # Créer les vertices (position de chaque point du profil à chaque position du chemin)
        vertices = []
        
        for i, path_point in enumerate(path_3d):
            # Calculer la direction et la normale
            if i == 0:
                direction = path_3d[1] - path_3d[0]
            elif i == n_path - 1:
                direction = path_3d[i] - path_3d[i-1]
            else:
                direction = path_3d[i+1] - path_3d[i-1]
            
            direction = direction / (np.linalg.norm(direction) + 1e-10)
            
            # Vecteur perpendiculaire (dans le plan XY)
            perpendicular = np.array([-direction[1], direction[0], 0])
            perpendicular = perpendicular / (np.linalg.norm(perpendicular) + 1e-10)
            
            # Vecteur vertical
            up = np.array([0, 0, 1])
            
            # Pour chaque point du profil
            for profile_point in profile_2d:
                # Transformer le point 2D en 3D
                offset = profile_point[0] * perpendicular + profile_point[1] * up
                vertex = path_point + offset
                vertices.append(vertex)
        
        vertices = np.array(vertices)
        
        # Créer les faces
        faces = []
        
        for i in range(n_path - 1):
            for j in range(n_profile):
                # Indices des 4 coins du quad
                idx1 = i * n_profile + j
                idx2 = i * n_profile + (j + 1) % n_profile
                idx3 = (i + 1) * n_profile + (j + 1) % n_profile
                idx4 = (i + 1) * n_profile + j
                
                # Créer deux triangles
                faces.append([idx1, idx2, idx3])
                faces.append([idx1, idx3, idx4])
        
        # Ajouter les caps (début et fin)
        # Cap au début
        center_start = np.mean(vertices[:n_profile], axis=0)
        center_start_idx = len(vertices)
        vertices = np.vstack([vertices, center_start])
        
        for j in range(n_profile):
            idx1 = j
            idx2 = (j + 1) % n_profile
            faces.append([center_start_idx, idx2, idx1])
        
        # Cap à la fin
        center_end = np.mean(vertices[-(n_profile+1):-1], axis=0)
        center_end_idx = len(vertices)
        vertices = np.vstack([vertices, center_end])
        
        base_idx = (n_path - 1) * n_profile
        for j in range(n_profile):
            idx1 = base_idx + j
            idx2 = base_idx + (j + 1) % n_profile
            faces.append([center_end_idx, idx1, idx2])
        
        faces = np.array(faces)
        
        # Créer le mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        return mesh
    
    def create_road_segment(self, road):
        """
        Crée un segment de route en 3D
        
        Args:
            road: Dictionnaire contenant les données de la route
            
        Returns:
            trimesh.Trimesh: Mesh de la route
        """
        coords = road['coordinates']
        width = road['width_mm']
        height = config.ROAD_HEIGHT
        
        # Convertir en 3D (z = hauteur de la base)
        path_3d = []
        for coord in coords:
            x, y = coord[0], coord[1]
            z = config.BASE_THICKNESS  # Commence au sommet de la base
            path_3d.append([x, y, z])
        
        path_3d = np.array(path_3d)
        
        # Créer le profil de la route
        if config.ROAD_PROFILE == "rounded_rect":
            profile_2d = self.create_rounded_rectangle_profile(
                width, height, config.CORNER_RADIUS
            )
        else:  # rectangle simple
            profile_2d = self.create_rectangle_profile(width, height)
        
        # Extruder le profil le long du chemin
        mesh = self.extrude_profile_along_path(profile_2d, path_3d)
        
        return mesh
    
    def find_intersections(self):
        """
        Trouve les points d'intersection approximatifs entre les routes
        
        Returns:
            list: Liste de points d'intersection [x, y, z]
        """
        self.log("\nRecherche des intersections...")
        
        # Méthode simple: chercher les points très proches entre différentes routes
        all_points = []
        road_ids = []
        
        for i, road in enumerate(self.data['roads']):
            for coord in road['coordinates']:
                all_points.append([coord[0], coord[1]])
                road_ids.append(i)
        
        all_points = np.array(all_points)
        
        # Trouver les points en double (à 1mm près)
        tolerance = 1.0  # mm
        intersections = []
        
        used_indices = set()
        
        for i in range(len(all_points)):
            if i in used_indices:
                continue
            
            point = all_points[i]
            
            # Chercher les points proches
            distances = np.linalg.norm(all_points - point, axis=1)
            close_indices = np.where((distances < tolerance) & (distances > 0))[0]
            
            # Vérifier qu'ils appartiennent à des routes différentes
            close_different_roads = [idx for idx in close_indices 
                                     if road_ids[idx] != road_ids[i]]
            
            if len(close_different_roads) > 0:
                # Intersection trouvée
                intersections.append([
                    point[0], 
                    point[1], 
                    config.BASE_THICKNESS + config.ROAD_HEIGHT / 2
                ])
                
                used_indices.add(i)
                used_indices.update(close_indices)
        
        self.log(f"✓ {len(intersections)} intersections trouvées")
        
        return intersections
    
    def create_intersection_sphere(self, point, radius):
        """
        Crée une sphère à une intersection
        
        Args:
            point: [x, y, z]
            radius: Rayon de la sphère
            
        Returns:
            trimesh.Trimesh: Sphère
        """
        sphere = trimesh.creation.icosphere(
            subdivisions=2,
            radius=radius
        )
        
        sphere.apply_translation(point)
        
        return sphere
    
    def generate_road_meshes(self):
        """Génère tous les mesh de routes"""
        self.log("\nGénération des routes...")
        
        roads = self.data['roads']
        
        if self.verbose:
            iterator = tqdm(roads, desc="Routes", unit="route")
        else:
            iterator = roads
        
        for road in iterator:
            try:
                mesh = self.create_road_segment(road)
                self.road_meshes.append(mesh)
            except Exception as e:
                self.log(f"  Erreur sur route {road['id']}: {e}")
        
        self.log(f"✓ {len(self.road_meshes)} mesh de routes créés")
    
    def generate_intersection_meshes(self):
        """Génère les sphères aux intersections"""
        intersections = self.find_intersections()
        
        if not intersections:
            return
        
        self.log("\nGénération des sphères d'intersection...")
        
        # Rayon moyen des routes
        avg_width = np.mean([r['width_mm'] for r in self.data['roads']])
        radius = avg_width / 2
        
        for point in intersections:
            sphere = self.create_intersection_sphere(point, radius)
            self.intersection_meshes.append(sphere)
        
        self.log(f"✓ {len(self.intersection_meshes)} sphères créées")
    
    def merge_all_meshes(self):
        """Fusionne tous les mesh en un seul"""
        self.log("\nFusion de toutes les géométries...")
        
        all_meshes = [self.base_mesh] + self.road_meshes + self.intersection_meshes
        
        self.log(f"  Total: {len(all_meshes)} mesh à fusionner")
        
        # Concaténer tous les mesh
        self.final_mesh = trimesh.util.concatenate(all_meshes)
        
        self.log(f"✓ Mesh final: {len(self.final_mesh.vertices)} vertices, "
                 f"{len(self.final_mesh.faces)} faces")
        
        return self.final_mesh
    
    def validate_and_repair(self):
        """Valide et répare le mesh si nécessaire"""
        self.log("\nValidation du mesh...")
        
        # Vérifications
        is_watertight = self.final_mesh.is_watertight
        is_winding_consistent = self.final_mesh.is_winding_consistent
        
        self.log(f"  Étanche (watertight): {is_watertight}")
        self.log(f"  Normales cohérentes: {is_winding_consistent}")
        
        if config.REPAIR_MESH and (not is_watertight or not is_winding_consistent):
            self.log("  Réparation du mesh...")
            
            # Réparer les normales
            if not is_winding_consistent:
                self.final_mesh.fix_normals()
            
            # Fusionner les vertices proches
            self.final_mesh.merge_vertices()
            
            # Supprimer les faces dégénérées
            self.final_mesh.remove_degenerate_faces()
            
            # Remplir les trous (si possible)
            trimesh.repair.fill_holes(self.final_mesh)
            
            self.log("  ✓ Réparations appliquées")
        
        # Statistiques finales
        bounds = self.final_mesh.bounds
        dimensions = bounds[1] - bounds[0]
        
        self.log(f"\nDimensions finales du modèle:")
        self.log(f"  X: {dimensions[0]:.2f} mm")
        self.log(f"  Y: {dimensions[1]:.2f} mm")
        self.log(f"  Z: {dimensions[2]:.2f} mm")
        self.log(f"  Volume: {self.final_mesh.volume:.2f} mm³")
    
    def export_stl(self, output_path):
        """
        Exporte le mesh en STL
        
        Args:
            output_path: Chemin de sortie
        """
        self.log(f"\nExport STL: {output_path}")
        
        # Export
        self.final_mesh.export(
            output_path,
            file_type='stl_ascii' if not config.STL_BINARY else 'stl'
        )
        
        # Taille du fichier
        file_size = Path(output_path).stat().st_size / 1024
        self.log(f"✓ Fichier sauvegardé ({file_size:.1f} Ko)")
    
    def generate(self, input_path, output_path):
        """
        Pipeline complet de génération 3D
        
        Args:
            input_path: Chemin vers processed_data.json
            output_path: Chemin de sortie STL
        """
        print("=" * 70)
        print("MODULE 3: GÉNÉRATEUR DE MODÈLE 3D")
        print("=" * 70)
        
        start_time = time.time()
        
        # 1. Charger les données
        self.load_processed_data(input_path)
        
        # 2. Créer la base
        self.create_base_plate()
        
        # 3. Générer les routes
        self.generate_road_meshes()
        
        # 4. Générer les intersections
        self.generate_intersection_meshes()
        
        # 5. Fusionner
        self.merge_all_meshes()
        
        # 6. Valider et réparer
        self.validate_and_repair()
        
        # 7. Exporter
        self.export_stl(output_path)
        
        elapsed = time.time() - start_time
        
        print("=" * 70)
        print(f"✓ GÉNÉRATION TERMINÉE en {elapsed:.1f}s")
        print("=" * 70)
        
        return output_path


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Génération du modèle 3D STL",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input',
        default=config.DEFAULT_PROCESSED_JSON,
        help='Fichier JSON d\'entrée (défaut: data/processed/processed_data.json)'
    )
    
    parser.add_argument(
        '--output',
        default=config.DEFAULT_OUTPUT_STL,
        help='Fichier STL de sortie (défaut: data/output/maquette_voirie.stl)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Mode silencieux'
    )
    
    args = parser.parse_args()
    
    # Créer le générateur
    generator = MeshGenerator3D(verbose=not args.quiet)
    
    try:
        # Lancer la génération
        output_file = generator.generate(args.input, args.output)
        print(f"\n✓ Modèle 3D sauvegardé: {output_file}")
        print(f"\nVous pouvez maintenant:")
        print(f"  - Visualiser avec viewer/index.html")
        print(f"  - Importer dans un slicer (Cura, PrusaSlicer, etc.)")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
