Methods
=======

This document describes the methods and algorithms used in the `lpy_treesim` project.

L-System for Tree Generation
----------------------------

`lpy_treesim` uses the L-Py language to define the growth rules of the trees. L-Py is a Python-based implementation of L-systems, which are a type of formal grammar that can be used to model the growth of plants and other biological systems.

The L-system used in `lpy_treesim` is defined in the `.lpy` files in the `examples` directory. These files contain the axiom and production rules that determine the structure of the tree.

- **Axiom**: The axiom is the initial state of the L-system. It is a string of symbols that represents the starting point of the tree.
- **Production Rules**: The production rules are a set of rules that specify how the symbols in the L-system are replaced over time. Each rule consists of a predecessor and a successor. The predecessor is a symbol that is replaced by the successor.

By iteratively applying the production rules to the axiom, the L-system generates a sequence of strings that represents the growth of the tree.

Pruning and Tying Algorithms
----------------------------

`lpy_treesim` includes algorithms for pruning and tying the branches of the tree. These algorithms are used to control the shape and size of the tree.

- **Pruning**: The pruning algorithm removes branches from the tree that are too long or that are growing in the wrong direction. This is done by defining a set of rules that specify which branches to remove.
- **Tying**: The tying algorithm connects branches of the tree together. This is done by defining a set of rules that specify which branches to connect and how to connect them.

The pruning and tying algorithms are implemented in the `stochastic_tree.py` module.

API Reference
-------------

.. automodule:: stochastic_tree
    :members: