import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import random
import sys

from openalea.lpy import Lsystem

from lpy_treesim.lpy_treesim import ColorManager
from lpy_treesim.tree_generation.helpers import write
from lpy_treesim.tree_generation.mesh_to_cylinders import add_cylinder_params_to_json

BASE_LPY_PATH = Path(__file__).resolve().parents[1] / "base_lpy.lpy"

# Ensure repository root is discoverable for prototype imports
sys.path.insert(0, str(BASE_LPY_PATH.parents[0]))


MAX_TREES = 99_999


@dataclass
class TreeNamingConfig:
    namespace: str
    tree_type: str

    def _prefix(self, index: int) -> str:
        if index > MAX_TREES:
            raise ValueError(f"Tree index {index} exceeds maximum supported value {MAX_TREES}.")
        return f"{self.namespace}_{self.tree_type}_{index:05d}"

    def mesh_filename(self, index: int) -> str:
        return f"{self._prefix(index)}.ply"

    def color_map_filename(self, index: int) -> str:
        return f"{self._prefix(index)}_colors.json"


def build_lsystem(tree_name: str) -> tuple[Lsystem, ColorManager]:
    color_manager = ColorManager()
    extern_vars = {
        "prototype_dict_path": f"examples.{tree_name}.{tree_name}_prototypes.basicwood_prototypes",
        "trunk_class_path": f"examples.{tree_name}.{tree_name}_prototypes.Trunk",
        "simulation_config_class_path": f"examples.{tree_name}.{tree_name}_simulation.{tree_name}SimulationConfig",
        "simulation_class_path": f"examples.{tree_name}.{tree_name}_simulation.{tree_name}Simulation",
        "color_manager": color_manager,
        "axiom_pitch": 0.0,
        "axiom_yaw": 0.0,
    }
    lsystem = Lsystem(str(BASE_LPY_PATH), extern_vars)
    return lsystem, color_manager


def generate_tree(lsystem: Lsystem, rng_seed: int, verbose: bool):
    random.seed(rng_seed)
    if verbose:
        print(f"INFO: RNG seed {rng_seed}")
    lstring = lsystem.axiom
    for iteration in range(lsystem.derivationLength):
        lstring = lsystem.derive(lstring, iteration, 1)
        lsystem.plot(lstring)
        # input("Press Enter to continue...")
    return lstring, lsystem.sceneInterpretation(lstring)


def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Generate and save multiple L-Py trees.")
    parser.add_argument('--num_trees', type=int, default=1, help='Number of trees to generate')
    parser.add_argument('--output_dir', type=Path, default=Path('dataset/'), help='Directory for outputs')
    parser.add_argument('--tree_name', type=str, default='UFO', help='Tree family to generate (UFO/Envy/etc.)')
    parser.add_argument('--verbose', action='store_true', help='Print progress details')
    parser.add_argument('--rng-seed', type=int, default=None, help='Optional deterministic seed')
    parser.add_argument('--namespace', type=str, default='lpy', help='Prefix namespace for output filenames')
    args = parser.parse_args()

    if args.num_trees > (MAX_TREES + 1):
        raise ValueError(f"num_trees={args.num_trees} exceeds supported maximum of {MAX_TREES + 1}.")

    naming = TreeNamingConfig(namespace=args.namespace, tree_type=args.tree_name)
    ensure_output_dir(args.output_dir)

    rng = random.Random(args.rng_seed)
    for index in range(args.num_trees):
        print(f"Generating tree {index + 1} of {args.num_trees}...")
        lsystem, color_manager = build_lsystem(args.tree_name)
        print(f"Generating tree {index + 1} of {args.num_trees}...")
        seed_value = rng.randint(0, 1_000_000)
        if args.verbose:
            print(f"INFO: Generating {args.tree_name} tree #{index:03d}")
        print(f"Generating tree {index + 1} of {args.num_trees}...")
        lstring, scene = generate_tree(lsystem, seed_value, args.verbose)
        mesh_path = args.output_dir / naming.mesh_filename(index)
        color_path = args.output_dir / naming.color_map_filename(index)
        write(str(mesh_path), scene)
        color_manager.export_mapping(str(color_path))
        if args.verbose:
            print(f"INFO: Wrote {mesh_path} and {color_path}")
        if lsystem.simulation_config.per_cylinder_label:
            add_cylinder_params_to_json(str(mesh_path), str(color_path))
        del scene
        del lstring
        del lsystem


if __name__ == "__main__":
    main()
