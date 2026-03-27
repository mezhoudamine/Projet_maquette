import json
import sys
import numpy as np
from pyproj import Transformer
import config

class DataProcessor:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.transformer = Transformer.from_crs(config.CRS_SOURCE, config.CRS_TARGET, always_xy=True)
        self.bbox_lambert = None
        self.bbox_mm = None

    def log(self, message):
        if self.verbose: print(message)

    def project_ring(self, ring):
        """Projette une liste de points [lon, lat] en [x, y]"""
        projected = []
        for point in ring:
            x, y = self.transformer.transform(point[0], point[1])
            projected.append([x, y])
        return projected

    def process_features(self, features):
        self.log("\nTraitement des géométries complexes...")
        
        roads = []
        buildings = []
        all_x, all_y = [], []

        for i, feature in enumerate(features):
            props = feature['properties']
            geom = feature['geometry']
            g_type = geom['type']
            
            # --- 1. TRAITEMENT DES ROUTES (Lignes) ---
            if 'highway' in props and g_type == 'LineString':
                coords = self.project_ring(geom['coordinates'])
                # Mise à jour bbox globale
                for p in coords:
                    all_x.append(p[0])
                    all_y.append(p[1])
                
                # Calcul longueur
                length = sum(np.linalg.norm(np.array(coords[k+1]) - np.array(coords[k])) for k in range(len(coords)-1))
                
                roads.append({
                    'id': feature.get('id', f'road_{i}'),
                    'type': props.get('highway', 'unknown'),
                    'coordinates_lambert': coords,
                    'length_m': length
                })

            # --- 2. TRAITEMENT DES BÂTIMENTS (Polygones complexes) ---
            elif 'building' in props and config.INCLUDE_BUILDINGS:
                # Structure standardisée : une liste de parties.
                # Chaque partie a 1 "shell" (contour) et N "holes" (trous)
                parts = []

                if g_type == 'Polygon':
                    # Polygon GeoJSON : [ [Shell], [Hole1], [Hole2]... ]
                    rings = geom['coordinates']
                    if len(rings) > 0:
                        shell = self.project_ring(rings[0])
                        holes = [self.project_ring(h) for h in rings[1:]]
                        parts.append({'shell': shell, 'holes': holes})

                elif g_type == 'MultiPolygon':
                    # MultiPolygon GeoJSON : [ [[Shell], [Holes]], [[Shell], [Holes]] ]
                    for poly in geom['coordinates']:
                        if len(poly) > 0:
                            shell = self.project_ring(poly[0])
                            holes = [self.project_ring(h) for h in poly[1:]]
                            parts.append({'shell': shell, 'holes': holes})

                if parts:
                    # Mise à jour bbox globale
                    for part in parts:
                        for p in part['shell']:
                            all_x.append(p[0])
                            all_y.append(p[1])

                    buildings.append({
                        'id': feature.get('id', f'bld_{i}'),
                        'type': 'building',
                        'parts_lambert': parts # On garde la structure complexe
                    })

        # Calcul BBox Lambert
        if not all_x: sys.exit("Aucune donnée valide trouvée.")
        
        self.bbox_lambert = {
            'min_x': min(all_x), 'max_x': max(all_x),
            'min_y': min(all_y), 'max_y': max(all_y)
        }
        
        self.log(f"✓ {len(roads)} routes, {len(buildings)} bâtiments (complexes inclus)")
        return roads, buildings

    def scale_point(self, point, center_x, center_y):
        """Applique l'échelle et le centrage sur un point (x, y)"""
        x = (point[0] - center_x) * 1000 / config.SCALE_HORIZONTAL
        y = (point[1] - center_y) * 1000 / config.SCALE_HORIZONTAL
        return [x, y]

    def process(self, input_path, output_path):
        data = self.load_geojson(input_path)
        roads, buildings = self.process_features(data['features'])
        
        # Centrage
        cx = (self.bbox_lambert['min_x'] + self.bbox_lambert['max_x']) / 2
        cy = (self.bbox_lambert['min_y'] + self.bbox_lambert['max_y']) / 2
        
        # Mise à l'échelle finale
        final_roads = []
        for r in roads:
            r['coordinates'] = [self.scale_point(p, cx, cy) for p in r['coordinates_lambert']]
            del r['coordinates_lambert']
            final_roads.append(r)
            
        final_buildings = []
        for b in buildings:
            final_parts = []
            for part in b['parts_lambert']:
                final_shell = [self.scale_point(p, cx, cy) for p in part['shell']]
                final_holes = [[self.scale_point(p, cx, cy) for p in h] for h in part['holes']]
                final_parts.append({'shell': final_shell, 'holes': final_holes})
            
            b['parts'] = final_parts
            del b['parts_lambert']
            final_buildings.append(b)

        # Calcul bbox MM pour export
        self.bbox_mm = {
            'width': (self.bbox_lambert['max_x'] - self.bbox_lambert['min_x']) * 1000 / config.SCALE_HORIZONTAL,
            'height': (self.bbox_lambert['max_y'] - self.bbox_lambert['min_y']) * 1000 / config.SCALE_HORIZONTAL,
            'min_x': -100, 'max_x': 100, 'min_y': -100, 'max_y': 100 # Valeurs fictives, l'important est width/height
        }

        output = {
            'metadata': {'bbox_mm': self.bbox_mm, 'scale': config.SCALE_HORIZONTAL},
            'roads': final_roads,
            'buildings': final_buildings
        }
        
        with open(output_path, 'w') as f: json.dump(output, f, indent=2)
        print(f"✓ Fichier traité généré : {output_path}")

    def load_geojson(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e: sys.exit(f"Erreur fichier: {e}")

if __name__ == "__main__":
    DataProcessor().process("test_volcan.geojson", "data/processed/volcantest_proceced.json")