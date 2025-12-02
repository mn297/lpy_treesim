"""
Color management utilities for L-Py tree simulation system.

This module provides utilities for assigning unique colors to tree segments
for visualization and labeling purposes.
"""

import itertools
import json


class ColorManager:
    """Manages assignment of unique colors to named entities."""
    
    def __init__(self):
        self.color_to_name = {}
        self.name_to_color = {}
        # Permute all possible colors to make a list
        self.all_colors = list(itertools.product(range(256), repeat=3))  # 0-255 inclusive
        self.color_pointer = 0

    def get_unique_color(self, name, if_exists=True):
        """Get a unique RGB color tuple for the given name."""
        if name in self.name_to_color and if_exists:
            return self.name_to_color[name]
        
        if self.color_pointer >= len(self.all_colors):
            raise ValueError("Ran out of unique colors!")
        
        unique_color = self.all_colors[self.color_pointer]
        self.color_pointer += 1

        # Assign and save mapping
        self.name_to_color[name] = unique_color
        self.color_to_name[unique_color] = name

        return unique_color

    def export_mapping(self, filename):
        """Export color -> name mapping to JSON"""
        export_dict = {}
        for color, name in self.color_to_name.items():
            export_dict[str(color)] = {"part_name": name}

        with open(filename, "w") as f:
            json.dump(export_dict, f, indent=4)

        print(f"Exported color mappings to {filename}")

    def set_unique_color(self, color, name):
        """Set a specific color for a given name."""
        self.name_to_color[name] = color
        self.color_to_name[color] = name