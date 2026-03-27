
import argparse
import json
import sys

try:
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
except ImportError:
    print("Error: matplotlib module not found. Install with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def visualize_roads(geojson_file: str, save_file: str = None, dpi: int = 150):
    """
    Create a simple 2D plot of roads with white background.
    
    Args:
        geojson_file: Path to input GeoJSON file
        save_file: Optional output file path (PNG, SVG, PDF supported)
        dpi: Resolution for output image
    """
    # Read GeoJSON
    try:
        with open(geojson_file, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{geojson_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{geojson_file}' is not a valid JSON file.", file=sys.stderr)
        sys.exit(1)
    
    features = geojson_data.get("features", [])
    
    if not features:
        print("Warning: No features found in GeoJSON file.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded {len(features)} features from {geojson_file}")
    
    # Color and width mapping for highway types
    style_map = {
        "primary": {"color": "#000000", "linewidth": 3.0},      # black, thick
        "secondary": {"color": "#333333", "linewidth": 2.5},    # dark gray, medium-thick
        "tertiary": {"color": "#666666", "linewidth": 2.0},     # gray, medium
        "residential": {"color": "#999999", "linewidth": 1.5},  # light gray, thin
        "default": {"color": "#AAAAAA", "linewidth": 1.0}       # very light gray, very thin
    }
    
    # Create figure with white background
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='white')
    ax.set_facecolor('white')
    
    # Group roads by type for proper rendering order (thicker roads first)
    roads_by_type = {
        "primary": [],
        "secondary": [],
        "tertiary": [],
        "residential": [],
        "other": []
    }
    
    # Extract all road geometries
    for feature in features:
        coords = feature["geometry"]["coordinates"]
        highway_type = feature["properties"].get("highway", "default")
        
        # Convert coords to list of (lon, lat) tuples
        line_coords = [(c[0], c[1]) for c in coords]
        
        # Group by type
        if highway_type in roads_by_type:
            roads_by_type[highway_type].append(line_coords)
        else:
            roads_by_type["other"].append(line_coords)
    
    # Draw roads in order (primary first = bottom layer, residential last = top layer)
    draw_order = ["primary", "secondary", "tertiary", "residential", "other"]
    
    for road_type in draw_order:
        if roads_by_type[road_type]:
            style = style_map.get(road_type, style_map["default"])
            
            lc = LineCollection(
                roads_by_type[road_type],
                colors=style["color"],
                linewidths=style["linewidth"],
                capstyle='round',
                joinstyle='round'
            )
            ax.add_collection(lc)
            
            print(f"  {road_type}: {len(roads_by_type[road_type])} roads")
    
    # Set equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Auto-scale to fit all roads
    ax.autoscale()
    
    # Tight layout
    plt.tight_layout(pad=0)
    
    # Save or show
    if save_file:
        plt.savefig(save_file, dpi=dpi, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        print(f"\nImage saved to: {save_file}")
    else:
        print("\nDisplaying interactive plot... Close window to exit.")
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize GeoJSON roads as simple 2D plot with white background",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "geojson",
        help="Input GeoJSON file path"
    )
    
    parser.add_argument(
        "--save",
        help="Save to file (PNG, SVG, PDF supported) instead of displaying"
    )
    
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolution for output image (default: 300)"
    )
    
    args = parser.parse_args()
    
    visualize_roads(args.geojson, args.save, args.dpi)


if __name__ == "__main__":
    main()