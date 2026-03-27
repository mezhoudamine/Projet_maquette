

import json
import argparse
import sys
from pathlib import Path

try:
    import numpy as np
    from pyproj import Transformer
except ImportError as e:
    print(f"Erreur: module manquant - {e}")
    print("Installation: pip install numpy pyproj")
    sys.exit(1)

import config


class DataProcessor:
    """Processeur de données géographiques pour maquette 3D"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        
        # Créer le transformateur de projection
        self.transformer = Transformer.from_crs(
            config.CRS_SOURCE, 
            config.CRS_TARGET, 
            always_xy=True
        )
        
        self.roads_data = []
        self.bbox_wgs84 = None
        self.bbox_lambert = None
        self.bbox_mm = None
        
    def log(self, message):
        """Affiche un message si verbose est activé"""
        if self.verbose:
            print(message)
    
    def load_geojson(self, filepath):
        """
        Charge un fichier GeoJSON
        
        Args:
            filepath: Chemin vers le fichier GeoJSON
            
        Returns:
            dict: Données GeoJSON parsées
        """
        self.log(f"Lecture du fichier: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier introuvable: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Fichier JSON invalide: {filepath}")
        
        features = data.get("features", [])
        self.log(f"✓ {len(features)} features chargées")
        
        return data
    
    def calculate_bbox_wgs84(self, features):
        """
        Calcule la bounding box en WGS84
        
        Args:
            features: Liste des features GeoJSON
            
        Returns:
            dict: {min_lon, max_lon, min_lat, max_lat}
        """
        all_lons = []
        all_lats = []
        
        for feature in features:
            coords = feature['geometry']['coordinates']
            for coord in coords:
                all_lons.append(coord[0])
                all_lats.append(coord[1])
        
        bbox = {
            'min_lon': min(all_lons),
            'max_lon': max(all_lons),
            'min_lat': min(all_lats),
            'max_lat': max(all_lats)
        }
        
        self.bbox_wgs84 = bbox
        
        self.log(f"\nBounding Box WGS84:")
        self.log(f"  Longitude: {bbox['min_lon']:.6f}° → {bbox['max_lon']:.6f}°")
        self.log(f"  Latitude:  {bbox['min_lat']:.6f}° → {bbox['max_lat']:.6f}°")
        self.log(f"  Delta: {bbox['max_lon']-bbox['min_lon']:.6f}° × {bbox['max_lat']-bbox['min_lat']:.6f}°")
        
        return bbox
    
    def project_coordinates(self, lon, lat):
        """
        Projette une coordonnée WGS84 vers Lambert 93
        
        Args:
            lon: Longitude en degrés
            lat: Latitude en degrés
            
        Returns:
            tuple: (x, y) en mètres
        """
        x, y = self.transformer.transform(lon, lat)
        return x, y
    
    def project_feature(self, feature):
        """
        Projette toutes les coordonnées d'une feature
        
        Args:
            feature: Feature GeoJSON
            
        Returns:
            list: Liste de coordonnées projetées [[x, y], ...]
        """
        coords_wgs84 = feature['geometry']['coordinates']
        coords_lambert = []
        
        for coord in coords_wgs84:
            lon, lat = coord[0], coord[1]
            x, y = self.project_coordinates(lon, lat)
            coords_lambert.append([x, y])
        
        return coords_lambert
    
    def process_features(self, features):
        """
        Traite toutes les features: projection + filtrage
        
        Args:
            features: Liste des features GeoJSON
            
        Returns:
            list: Liste des routes traitées
        """
        self.log("\nProjection des coordonnées...")
        
        roads = []
        excluded_count = 0
        
        for i, feature in enumerate(features):
            props = feature['properties']
            highway_type = props.get('highway', 'unknown')
            
            # Filtrer selon la configuration
            if not config.should_include_road(highway_type):
                excluded_count += 1
                continue
            
            # Projeter les coordonnées
            coords_lambert = self.project_feature(feature)
            
            # Calculer la longueur du segment
            length_m = self._calculate_length(coords_lambert)
            
            road = {
                'id': feature.get('id', f'road_{i}'),
                'name': props.get('name', ''),
                'type': highway_type,
                'coordinates_lambert': coords_lambert,
                'length_m': length_m,
                'properties': props
            }
            
            roads.append(road)
        
        self.log(f"✓ {len(roads)} routes conservées, {excluded_count} exclues")
        
        return roads
    
    def _calculate_length(self, coords):
        """Calcule la longueur totale d'un LineString en mètres"""
        length = 0.0
        for i in range(len(coords) - 1):
            p1 = np.array(coords[i])
            p2 = np.array(coords[i + 1])
            length += np.linalg.norm(p2 - p1)
        return length
    
    def calculate_bbox_lambert(self, roads):
        """
        Calcule la bounding box en Lambert 93
        
        Args:
            roads: Liste des routes avec coordonnées Lambert
            
        Returns:
            dict: {min_x, max_x, min_y, max_y} en mètres
        """
        all_x = []
        all_y = []
        
        for road in roads:
            for coord in road['coordinates_lambert']:
                all_x.append(coord[0])
                all_y.append(coord[1])
        
        bbox = {
            'min_x': min(all_x),
            'max_x': max(all_x),
            'min_y': min(all_y),
            'max_y': max(all_y)
        }
        
        width_m = bbox['max_x'] - bbox['min_x']
        height_m = bbox['max_y'] - bbox['min_y']
        
        self.bbox_lambert = bbox
        
        self.log(f"\nBounding Box Lambert 93:")
        self.log(f"  X: {bbox['min_x']:.2f}m → {bbox['max_x']:.2f}m")
        self.log(f"  Y: {bbox['min_y']:.2f}m → {bbox['max_y']:.2f}m")
        self.log(f"  Dimensions: {width_m:.2f}m × {height_m:.2f}m")
        
        return bbox
    
    def center_and_scale(self, roads):
        """
        Centre les coordonnées sur (0, 0) et applique l'échelle
        
        Args:
            roads: Liste des routes avec coordonnées Lambert
            
        Returns:
            list: Routes avec coordonnées en millimètres, centrées
        """
        self.log(f"\nApplication de l'échelle 1:{config.SCALE_HORIZONTAL}...")
        
        bbox = self.bbox_lambert
        
        # Point central de la bounding box
        center_x = (bbox['min_x'] + bbox['max_x']) / 2
        center_y = (bbox['min_y'] + bbox['max_y']) / 2
        
        self.log(f"Centre Lambert: ({center_x:.2f}, {center_y:.2f})")
        
        # Traiter chaque route
        for road in roads:
            coords_mm = []
            
            for coord in road['coordinates_lambert']:
                # Centrer
                x_centered = coord[0] - center_x
                y_centered = coord[1] - center_y
                
                # Convertir en millimètres (échelle 1:1000)
                x_mm = x_centered * 1000 / config.SCALE_HORIZONTAL
                y_mm = y_centered * 1000 / config.SCALE_HORIZONTAL
                
                coords_mm.append([x_mm, y_mm])
            
            road['coordinates_mm'] = coords_mm
            
            # Calculer longueur en mm
            road['length_mm'] = road['length_m'] * 1000 / config.SCALE_HORIZONTAL
        
        # Calculer bounding box finale en mm
        all_x_mm = []
        all_y_mm = []
        
        for road in roads:
            for coord in road['coordinates_mm']:
                all_x_mm.append(coord[0])
                all_y_mm.append(coord[1])
        
        self.bbox_mm = {
            'min_x': min(all_x_mm),
            'max_x': max(all_x_mm),
            'min_y': min(all_y_mm),
            'max_y': max(all_y_mm),
            'width': max(all_x_mm) - min(all_x_mm),
            'height': max(all_y_mm) - min(all_y_mm)
        }
        
        self.log(f"\nDimensions finales de la maquette:")
        self.log(f"  Largeur:  {self.bbox_mm['width']:.1f} mm")
        self.log(f"  Hauteur:  {self.bbox_mm['height']:.1f} mm")
        self.log(f"  Zone: [{self.bbox_mm['min_x']:.1f}, {self.bbox_mm['min_y']:.1f}] → "
                 f"[{self.bbox_mm['max_x']:.1f}, {self.bbox_mm['max_y']:.1f}]")
        
        return roads
    
    def export_processed_data(self, roads, output_path):
        """
        Exporte les données traitées en JSON
        
        Args:
            roads: Liste des routes traitées
            output_path: Chemin du fichier de sortie
        """
        # Préparer les statistiques
        stats = {
            'total_roads': len(roads),
            'total_length_m': sum(r['length_m'] for r in roads),
            'total_length_mm': sum(r['length_mm'] for r in roads),
            'road_types': {}
        }
        
        for road in roads:
            road_type = road['type']
            stats['road_types'][road_type] = stats['road_types'].get(road_type, 0) + 1
        
        # Structure de sortie
        output_data = {
            'metadata': {
                'projection_source': config.CRS_SOURCE,
                'projection_target': config.CRS_TARGET,
                'scale_horizontal': config.SCALE_HORIZONTAL,
                'scale_vertical': config.SCALE_VERTICAL,
                'units': 'millimeters',
                'bbox_mm': self.bbox_mm,
                'statistics': stats
            },
            'roads': []
        }
        
        # Ajouter chaque route (seulement coordonnées en mm)
        for road in roads:
            output_data['roads'].append({
                'id': road['id'],
                'name': road['name'],
                'type': road['type'],
                'coordinates': road['coordinates_mm'],  # Coordonnées finales
                'length_mm': road['length_mm'],
                'width_mm': config.get_road_width(road['type'])
            })
        
        # Sauvegarder
        self.log(f"\nExport vers: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"✓ Fichier sauvegardé ({Path(output_path).stat().st_size / 1024:.1f} Ko)")
        
        # Afficher les statistiques
        self.log("\nStatistiques:")
        self.log(f"  Total: {stats['total_roads']} routes")
        self.log(f"  Longueur totale: {stats['total_length_m']:.1f}m "
                 f"({stats['total_length_mm']:.1f}mm sur maquette)")
        self.log(f"\nRépartition par type:")
        for road_type, count in sorted(stats['road_types'].items(), 
                                       key=lambda x: x[1], reverse=True):
            self.log(f"    {road_type:20s}: {count:3d}")
    
    def process(self, input_path, output_path):
        """
        Pipeline complet de traitement
        
        Args:
            input_path: Chemin du fichier GeoJSON d'entrée
            output_path: Chemin du fichier JSON de sortie
        """
        print("=" * 70)
        print("MODULE 1: DATA PROCESSOR")
        print("=" * 70)
        
        # 1. Charger les données
        geojson_data = self.load_geojson(input_path)
        features = geojson_data['features']
        
        # 2. Calculer bbox WGS84
        self.calculate_bbox_wgs84(features)
        
        # 3. Projeter et filtrer
        roads = self.process_features(features)
        
        # 4. Calculer bbox Lambert
        self.calculate_bbox_lambert(roads)
        
        # 5. Centrer et mettre à l'échelle
        self.center_and_scale(roads)
        
        # 6. Exporter
        self.export_processed_data(roads, output_path)
        
        print("=" * 70)
        print("✓ TRAITEMENT TERMINÉ")
        print("=" * 70)
        
        return output_path


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Traitement des données GeoJSON pour maquette 3D tactile",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input',
        default=config.DEFAULT_INPUT_GEOJSON,
        help='Fichier GeoJSON d\'entrée (défaut: data/raw/exportvlocan.geojson)'
    )
    
    parser.add_argument(
        '--output',
        default=config.DEFAULT_PROCESSED_JSON,
        help='Fichier JSON de sortie (défaut: data/processed/processed_data2.json)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Mode silencieux (pas de messages détaillés)'
    )
    
    args = parser.parse_args()
    
    # Créer le processeur
    processor = DataProcessor(verbose=not args.quiet)
    
    try:
        # Lancer le traitement
        output_file = processor.process(args.input, args.output)
        print(f"\n✓ Données traitées sauvegardées: {output_file}")
        
    except Exception as e:
        print(f"\n✗ Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
