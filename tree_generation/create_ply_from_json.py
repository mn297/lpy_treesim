import argparse
import json
import numpy as np
from pathlib import Path
import math

def rotation_matrix_from_vectors(vec1, vec2):
    """Find the rotation matrix that aligns vec1 to vec2."""
    a, b = np.array(vec1), np.array(vec2)
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    if s == 0:
        return np.eye(3)
    v = v / s
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * ((1 - c) / (s ** 2))

def create_cylinder_vertices_faces(centroid, radius, length, orientation = [0, 0, 1], slices=16, stacks=1):
    """
    Create vertices and faces for a cylinder along the given orientation.
    """
    cx, cy, cz = centroid
    z_axis = np.array([0, 0, 1])
    orientation = np.array(orientation)
    rot_matrix = rotation_matrix_from_vectors(z_axis, orientation)
    
    vertices = []
    faces = []
    
    # Bottom circle at z=-length/2
    for i in range(slices):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = -length / 2
        point = np.array([x, y, z])
        rotated = rot_matrix @ point
        vertices.append((cx + rotated[0], cy + rotated[1], cz + rotated[2]))
    
    # Top circle at z=length/2
    for i in range(slices):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = length / 2
        point = np.array([x, y, z])
        rotated = rot_matrix @ point
        vertices.append((cx + rotated[0], cy + rotated[1], cz + rotated[2]))
    
    # Bottom face
    bottom_center = len(vertices)
    vertices.append((cx, cy, cz - length / 2))  # Approximate center, but should rotate too
    for i in range(slices):
        faces.append([bottom_center, i, (i + 1) % slices])
    
    # Top face
    top_center = len(vertices)
    vertices.append((cx, cy, cz + length / 2))
    offset = slices
    for i in range(slices):
        faces.append([top_center, offset + (i + 1) % slices, offset + i])
    
    # Side faces
    for i in range(slices):
        i1 = i
        i2 = (i + 1) % slices
        i3 = i2 + slices
        i4 = i1 + slices
        faces.append([i1, i2, i3, i4])
    
    return vertices, faces

def create_ply_from_json(json_path, ply_path):
    """
    Creates a PLY file from cylinder parameters in JSON.
    """
    # Load JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    for color_key, value in data.items():
        if isinstance(value, dict) and len(value.keys()) == 4:
            part_name = value.get("part_name")
            centroid = value.get("centroid")
            radius = value.get("radius")
            length = value.get("length")
            
            # Parse color from key, e.g., "(255, 0, 0)"
            color_str = color_key.strip('()')
            r, g, b = map(int, color_str.split(', '))
            
            vertices, faces = create_cylinder_vertices_faces(centroid, radius, length)
            
            # Add color to vertices
            colored_vertices = [(x, y, z, r, g, b) for x, y, z in vertices]
            all_vertices.extend(colored_vertices)
            
            # Offset faces
            offset_faces = [[vi + vertex_offset for vi in face] for face in faces]
            all_faces.extend(offset_faces)
            
            vertex_offset += len(vertices)
    
    # Write PLY
    with open(ply_path, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("comment Generated from JSON\n")
        f.write(f"element vertex {len(all_vertices)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar diffuse_red\n")
        f.write("property uchar diffuse_green\n")
        f.write("property uchar diffuse_blue\n")
        f.write(f"element face {len(all_faces)}\n")
        f.write("property list uchar int vertex_indices\n")
        f.write("end_header\n")
        
        for v in all_vertices:
            f.write(f"{v[0]} {v[1]} {v[2]} {v[3]} {v[4]} {v[5]}\n")
        
        for face in all_faces:
            f.write(f"{len(face)} {' '.join(map(str, face))}\n")
    
    print(f"Created PLY at {ply_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create PLY from cylinder JSON.")
    parser.add_argument('--json', type=str, required=True, help='Path to JSON file')
    parser.add_argument('--ply', type=str, required=True, help='Path to output PLY file')
    
    args = parser.parse_args()
    
    create_ply_from_json(args.json, args.ply)