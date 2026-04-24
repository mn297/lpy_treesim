#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
import os
import sys
from pathlib import Path
import random
from lpy_treesim import ColorManager
import json
from openalea.lpy import Lsystem
import lpy_treesim.tree_generation.lpy_mesh_utils as lmu
from lpy_treesim.tree_generation.mesh_to_cylinders import add_cylinder_params_to_json, get_cylinder_params
import numpy as np
import secrets

import logging
import lpy_treesim.utils.logging_conf

logger = logging.getLogger(__name__)

BASE_LPY_PATH = Path(__file__).resolve().parents[1] / "base_lpy.lpy"

# Ensure repository root is discoverable for prototype imports
sys.path.insert(0, str(BASE_LPY_PATH.parents[0]))


MAX_TREES = 99_999


@dataclass
class TreeNamingConfig:
    def __init__(self, namespace: str, tree_type: str):
        self.namespace = namespace.lower().strip()
        self.tree_type = tree_type.lower().strip()
        return

    def _prefix(self, index: int) -> str:
        if index > MAX_TREES:
            logging.error(f"Tree index {index} exceeds maximum supported value {MAX_TREES}.")
            raise ValueError(f"Tree index {index} exceeds maximum supported value {MAX_TREES}.")
        return f"{self.namespace}_{self.tree_type}_{index:05d}"

    def mesh_filename(self, index: int) -> str:
        return f"{self._prefix(index)}.ply"

    def usd_filename(self, index: int) -> str:
        return f"{self._prefix(index)}.usda"

    def metadata_filename(self, index: int) -> str:
        return f"{self._prefix(index)}_metadata.json"

    def hierarchy_filename(self, index: int) -> str:
        return f"{self._prefix(index)}_hierarchy.json"


class TreeBuilder:
    def __init__(
        self,
        tree_name: str,
        seed_value: int,
        semantic_label: bool = False,
        instance_label: bool = False,
        per_cylinder_label: bool = False,
    ):
        self.branch_hierarchy = {}
        self.color_manager = ColorManager()
        self.extern_vars = {
            "prototype_builder_path": f"lpy_treesim.examples.{tree_name}.{tree_name}_prototypes.build_basicwood_prototypes",
            "trunk_class_path": f"lpy_treesim.examples.{tree_name}.{tree_name}_prototypes.Trunk",
            "simulation_config_class_path": f"lpy_treesim.examples.{tree_name}.{tree_name}_simulation.{tree_name.upper()}SimulationConfig",
            "simulation_class_path": f"lpy_treesim.examples.{tree_name}.{tree_name}_simulation.{tree_name.upper()}Simulation",
            "color_manager": self.color_manager,
            "axiom_pitch": 0.0,
            "axiom_yaw": 0.0,
            "branch_hierarchy": self.branch_hierarchy,
            "semantic_label": semantic_label,
            "instance_label": instance_label,
            "per_cylinder_label": per_cylinder_label,
            "seed_value": seed_value,
        }
        self.__lsystem = Lsystem(str(BASE_LPY_PATH), self.extern_vars)
        return

    def lsystem(self) -> Lsystem:
        return self.__lsystem

    def generate_tree(self):
        lstring = self.__lsystem.axiom
        for iteration in range(self.__lsystem.derivationLength):
            lstring = self.__lsystem.derive(lstring, iteration, 1)
            self.__lsystem.plot(lstring)
            # input("Press Enter to continue...")
        return lstring, self.__lsystem.sceneInterpretation(lstring)
    
    def export_hierarchy_dict(self) -> dict:
        named_hierarchy = {}
        for key, branch in self.branch_hierarchy.items():
            key = key.lower().strip()
            named_hierarchy[key] = []
            for child in branch:
                named_hierarchy[key].append(child.name.lower().strip())
        return named_hierarchy

    @staticmethod
    def convert_vec3_to_tuple(vec3) -> tuple:
        return (float(vec3.x), float(vec3.y), float(vec3.z))
    
    def export_branch_location_dict(self) -> dict:
        named_hierarchy = {}
        for key, branch in self.branch_hierarchy.items():
            for child in branch:
                child_name = child.name.lower().strip()
                named_hierarchy[child_name] = {"start": self.convert_vec3_to_tuple(child.location.start), "end": self.convert_vec3_to_tuple(child.location.end)}
        return named_hierarchy
    
    def get_metadata(self, ply_filepath: str, metadata_path: str) -> None:
        """Export metadata based on label settings. Includes hierarchy and L-Py vars."""
        export_dict = {
            "seed_value": int(self.extern_vars["seed_value"]),
            "semantic_label": self.extern_vars["semantic_label"],
            "instance_label": self.extern_vars["instance_label"],
            "per_cylinder_label": self.extern_vars["per_cylinder_label"],
            "axiom_pitch": float(self.extern_vars["axiom_pitch"]),
            "axiom_yaw": float(self.extern_vars["axiom_yaw"]),
        }
        # Hierarchy
        export_dict["hierarchy"] = self.export_hierarchy_dict()
        export_dict["branch_locations"] = self.export_branch_location_dict()
        color_data = self.color_manager.export_mapping_dict()
        export_dict["color_mapping"] = color_data
        # Label data
        if self.extern_vars["semantic_label"]:
            ...
        if self.extern_vars["instance_label"]:
            ...
        if self.extern_vars["per_cylinder_label"]:
            export_dict["cylinder_data"] = get_cylinder_params(ply_path=ply_filepath, cylinder_metadata=color_data)
        return export_dict

    def export_metadata(self, ply_filepath: str, metadata_path: str) -> None:
        """Export metadata based on label settings. Includes hierarchy and L-Py vars."""
        logger.info(f"Exporting metadata to {metadata_path}...")
        export_dict = self.get_metadata(ply_filepath, metadata_path)
        with open(metadata_path, "w") as f:
            json.dump(export_dict, f, indent=4)
        return export_dict
