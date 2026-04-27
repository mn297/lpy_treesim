#!/usr/bin/env python3
"""
Script to verify that all colors present in a PLY file exist as keys in a corresponding JSON file.

Usage:
    python verify_colors.py --ply_file dataset/lpy_UFO_00000.ply --json_file dataset/lpy_UFO_00000_colors.json
"""

import argparse
import json
import os


def parse_ply_colors(ply_file_path):
    """
    Parse the PLY file and extract unique RGB color tuples from vertices.

    Assumes ASCII PLY format with properties: x y z diffuse_red diffuse_green diffuse_blue
    """
    colors = set()

    with open(ply_file_path, "r") as f:
        lines = f.readlines()

    # Find the start of vertex data
    vertex_start = None
    vertex_count = 0
    for i, line in enumerate(lines):
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        elif line.startswith("end_header"):
            vertex_start = i + 1
            break

    if vertex_start is None:
        raise ValueError("Could not find end_header in PLY file")

    # Read vertex data
    for i in range(vertex_start, vertex_start + vertex_count):
        parts = lines[i].strip().split()
        if len(parts) >= 6:
            # x y z r g b
            r, g, b = int(parts[3]), int(parts[4]), int(parts[5])
            colors.add((r, g, b))

    return colors


def load_json(json_file_path):
    """
    Load the JSON file and return the set of keys (color strings).
    """
    with open(json_file_path, "r") as f:
        data = json.load(f)

    return data


def main():
    parser = argparse.ArgumentParser(description="Verify PLY colors exist in JSON keys")
    parser.add_argument("--ply_file", required=True, help="Path to the PLY file")
    parser.add_argument("--json_file", required=True, help="Path to the JSON file")

    args = parser.parse_args()

    if not os.path.exists(args.ply_file):
        print(f"Error: PLY file {args.ply_file} does not exist")
        return

    if not os.path.exists(args.json_file):
        print(f"Error: JSON file {args.json_file} does not exist")
        return

    # Extract colors from PLY
    ply_colors = parse_ply_colors(args.ply_file)
    print(f"Found {len(ply_colors)} unique colors in PLY file")

    # Load JSON keys
    json_data = load_json(args.json_file)
    json_keys = set(json_data.keys())
    print(f"Found {len(json_keys)} keys in JSON file")

    # Check for missing colors
    missing_colors = []
    for color in ply_colors:
        color_str = str(color)
        if color_str not in json_keys:
            missing_colors.append(color_str)

    if missing_colors:
        print(f"Error: {len(missing_colors)} colors from PLY are missing in JSON:")
        # for color in missing_colors:
        #     print(f"  {color}")
    else:
        print("Success: All colors from PLY are present in JSON keys")

    # Check other way round
    extra_keys = []
    for key in json_keys:
        color_tuple = tuple(map(int, key.strip("()").split(", ")))
        if color_tuple not in ply_colors:
            extra_keys.append(key)
    print(f"Info: {len(extra_keys)} keys in JSON are not present in PLY colors.")
    # for key in extra_keys:
    #     print(f" Name: {json_data[key]} Color: {key}")


if __name__ == "__main__":
    main()
