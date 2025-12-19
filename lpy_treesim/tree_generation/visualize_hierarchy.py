"""
Visualize PLY mesh with hierarchy points overlaid using Open3D.

This script loads a PLY mesh file and its corresponding hierarchy JSON,
then visualizes the mesh with branch points overlaid as colored spheres.
"""

import json
import argparse
from pathlib import Path
import numpy as np
import open3d as o3d


def load_hierarchy_points(json_path):
    """
    Load branch points from hierarchy JSON.
    
    Args:
        json_path: Path to hierarchy JSON file
        
    Returns:
        List of tuples: [(branch_name, position, direction), ...]
        where position and direction are numpy arrays of shape (3,)
    """
    with open(json_path, 'r') as f:
        hierarchy = json.load(f)
    
    points = []
    for branch_name, children in hierarchy.items():
        if not children:
            continue
        
        for child in children:
            if not child:  # Skip empty entries
                continue
            
            if len(child) >= 3:
                child_name = child['name']
                start_position = np.array(child['start'], dtype=np.float64)
                end_position = np.array(child['end'], dtype=np.float64)
                
                points.append((child_name, start_position, end_position))
    
    return points


def create_sphere_at_point(position, radius=0.02, color=[1, 0, 0]):
    """
    Create a colored sphere mesh at the given position.
    
    Args:
        position: 3D position as numpy array
        radius: Sphere radius
        color: RGB color as [r, g, b] in range [0, 1]
        
    Returns:
        open3d.geometry.TriangleMesh sphere
    """
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
    sphere.translate(position)
    sphere.paint_uniform_color(color)
    sphere.compute_vertex_normals()
    return sphere


def visualize_mesh_with_hierarchy(ply_path, json_path, show_arrows=False, sphere_radius=0.02):
    """
    Visualize PLY mesh with hierarchy points overlaid.
    
    Args:
        ply_path: Path to PLY mesh file
        json_path: Path to hierarchy JSON file
        show_arrows: If True, show direction arrows at branch points
        sphere_radius: Radius of spheres marking branch points
    """
    # Load mesh
    print(f"Loading mesh from {ply_path}")
    mesh = o3d.io.read_triangle_mesh(str(ply_path))
    
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()
    
    # Set mesh color to a neutral gray
    mesh.paint_uniform_color([0.7, 0.7, 0.7])
    
    # Load hierarchy points
    print(f"Loading hierarchy from {json_path}")
    points = load_hierarchy_points(json_path)
    print(f"Found {len(points)} branch points")
    
    # Create geometries for visualization
    geometries = [mesh]
    
    # Color palette for different branch types
    color_map = {
        'Trunk': [0.8, 0.2, 0.2],    # Red
        'Branch': [0.2, 0.8, 0.2],   # Green
        'Spur': [0.2, 0.2, 0.8],     # Blue
        'NonTrunk': [0.8, 0.8, 0.2], # Yellow
    }
    
    # Group points by branch type (limit to 100 spheres total for performance)
    point_groups = {'Trunk': [], 'Branch': [], 'Spur': [], 'NonTrunk': []}
    arrow_meshes = []
    
    print("Processing branch points...")
    total_spheres = 0
    max_spheres = 100
    
    for branch_name, start, end in points:
        if total_spheres >= max_spheres:
            break

       
        # Determine branch type from name
        branch_type = branch_name.split('_')[0]
        # if branch_type != "Spur":
        #     continue
            
        if branch_type in point_groups:
            # Add both start and end positions
            point_groups[branch_type].append(start)
            point_groups[branch_type].append(end)
            total_spheres += 2
    
    
    # Create individual spheres for each branch type
    for branch_type, positions in point_groups.items():
        if not positions:
            continue
        
        color = color_map.get(branch_type, [0.5, 0.5, 0.5])
        
        # Create individual spheres 
        for pos in positions:
            sphere = create_sphere_at_point(np.array(pos), sphere_radius, color)
            geometries.append(sphere)
        
        print(f"  {branch_type}: {len(positions)} points")
    
    # Add arrows if enabled
    if show_arrows:
        geometries.extend(arrow_meshes)
        print(f"  Added {len(arrow_meshes)} direction arrows")
        
    
    # Create coordinate frame at origin for reference
    coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5, origin=[0, 0, 0])
    # geometries.append(coord_frame)
    
    # Visualize using more responsive visualizer
    print("Launching visualization...")
    print("Controls:")
    print("  - Mouse left: Rotate")
    print("  - Mouse right: Translate")
    print("  - Mouse wheel: Zoom")
    print("  - Q or ESC: Quit")
    
    # Create visualizer with better responsiveness
    vis = o3d.visualization.Visualizer()
    vis.create_window(
        window_name="Tree Mesh with Hierarchy",
        width=1280,
        height=720,
        left=50,
        top=50
    )
    
    # Add all geometries
    for geom in geometries:
        vis.add_geometry(geom)
    
    # Set render options for better quality
    render_opt = vis.get_render_option()
    render_opt.mesh_show_back_face = True
    render_opt.background_color = np.array([0.1, 0.1, 0.1])
    
    # Reset view to fit all geometry
    vis.reset_view_point(True)
    
    # Run visualization loop
    vis.run()
    vis.destroy_window()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize PLY tree mesh with hierarchy points overlaid"
    )
    parser.add_argument(
        '--ply',
        type=str,
        required=True,
        help='Path to PLY mesh file'
    )
    parser.add_argument(
        '--json',
        type=str,
        default=None,
        help='Path to hierarchy JSON file (default: inferred from PLY filename)'
    )
    parser.add_argument(
        '--no-arrows',
        action='store_true',
        help='Hide direction arrows (show only points)'
    )
    parser.add_argument(
        '--sphere-radius',
        type=float,
        default=0.02,
        help='Radius of spheres at branch points (default: 0.02)'
    )
    
    args = parser.parse_args()
    
    ply_path = Path(args.ply)
    if not ply_path.exists():
        print(f"Error: PLY file not found: {ply_path}")
        return
    
    # Infer JSON path if not provided
    if args.json is None:
        json_path = ply_path.with_name(ply_path.stem + '_hierarchy.json')
        if not json_path.exists():
            print(f"Error: Could not find hierarchy JSON at {json_path}")
            print("Please specify --json explicitly")
            return
    else:
        json_path = Path(args.json)
        if not json_path.exists():
            print(f"Error: JSON file not found: {json_path}")
            return
    
    visualize_mesh_with_hierarchy(
        ply_path,
        json_path,
        show_arrows=not args.no_arrows,
        sphere_radius=args.sphere_radius
    )


if __name__ == '__main__':
    main()
