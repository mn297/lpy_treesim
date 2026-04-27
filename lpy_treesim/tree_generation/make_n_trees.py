#! /usr/bin/env python3
import argparse
import numpy as np
from pathlib import Path
import secrets


import logging
import lpy_treesim.utils.logging_conf
from lpy_treesim.tree_generation.tree_builder import TreeNamingConfig, TreeBuilder
import lpy_mesh_utils as lmu

logger = logging.getLogger(__name__)

MAX_TREES = 99_999


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and save multiple L-Py trees.")
    parser.add_argument("--num-trees", type=int, default=1, help="Number of trees to generate")
    parser.add_argument("--output-dir", type=Path, default=Path("dataset/"), help="Directory for outputs")
    parser.add_argument("--tree-name", type=str, default="ufo", help="Tree family to generate (UFO/Envy/etc.)")
    parser.add_argument("--verbose", action="store_true", help="Print progress details")
    parser.add_argument(
        "--dataset-seed", type=int, default=None, help="Optional deterministic seed for dataset generation"
    )
    parser.add_argument("--namespace", type=str, default="lpy", help="Prefix namespace for output filenames")
    parser.add_argument("--semantic-label", action="store_true", help="Enable semantic labeling")
    parser.add_argument("--instance-label", action="store_true", help="Enable instance labeling")
    parser.add_argument("--per-cylinder-label", action="store_true", help="Enable per-cylinder labeling")
    args = parser.parse_args()
    if args.num_trees > (MAX_TREES + 1) or args.num_trees < 1:
        raise ValueError(f"num_trees={args.num_trees} is not in the range [1, {MAX_TREES + 1}].")
    if args.dataset_seed is None:
        args.dataset_seed = secrets.randbits(32)
    return args


def main():
    logger.info("Starting tree generation...")
    args = _parse_args()

    naming = TreeNamingConfig(namespace=args.namespace, tree_type=args.tree_name)
    # ensure_output_dir(args.output_dir)

    # Generate trees
    tree_rng: np.random.Generator = np.random.default_rng(seed=args.dataset_seed)
    for index in range(args.num_trees):
        tree_seed = tree_rng.integers(low=0, high=1_000_000)
        lsb = TreeBuilder(
            tree_name=args.tree_name,
            seed_value=tree_seed,
            semantic_label=args.semantic_label,
            instance_label=args.instance_label,
            per_cylinder_label=args.per_cylinder_label,
        )

        if args.verbose:
            print(f"INFO: Generating {args.tree_name} tree #{index:03d}")
        logging.info(f"Generating {args.tree_name} tree #{index:03d} with seed {tree_seed}")

        lstring, scene = lsb.generate_tree()
        # PLY
        mesh_path = args.output_dir / naming.mesh_filename(index)
        lmu.write(str(mesh_path), scene)
        # Metadata
        metadata_path = args.output_dir / naming.metadata_filename(index)
        lsb.export_metadata(ply_filepath=str(mesh_path), metadata_path=str(metadata_path))

        logger.info(f"Wrote mesh to {mesh_path} and metadata to {metadata_path}")
        del scene
        del lstring
        del lsb
    logger.info("Tree generation complete.")
    return


if __name__ == "__main__":
    main()
