Usage
=====

This section provides a guide on how to use `lpy_treesim` to generate and simulate tree growth.

Running Simulations
-------------------

To run a simulation, you need to have an L-Py file (`.lpy`) that defines the growth rules of the tree. You can find several examples in the `examples` directory.

1.  **Activate the Conda Environment**:

    .. code-block:: bash

        conda activate lpy

2.  **Launch L-Py**:

    .. code-block:: bash

        lpy

3.  **Open an L-Py File**: In the L-Py GUI, navigate to the desired `.lpy` file and open it.

4.  **Run the Simulation**:
    - Click the **Animate** button on the toolbar to start the simulation.
    - **Note**: The tying and pruning processes will only work when you use **Animate**, not **Run**.
    - **Warning**: There is a known bug where files may not run correctly on the first attempt. If this happens, click **Rewind** and then **Animate** again.

Defining Growth Rules
---------------------

Growth rules are defined using the L-Py language in `.lpy` files. These files typically contain:

- **Axiom**: The initial state of the L-system.
- **Productions**: A set of rules that define how the L-system evolves over time.

Here's a simple example of an L-Py file:

.. code-block:: python

    axiom: A(1)
    production:
    A(x) -> F(x) A(x+1)

This example defines a simple L-system that grows a branch of increasing length.

Visualizing the Results
-----------------------

L-Py provides a 3D viewer that allows you to visualize the tree as it grows. You can interact with the 3D model by rotating, panning, and zooming.

Key Modules in `lpy_treesim`
----------------------------

`lpy_treesim` is organized into several modules, each with a specific purpose:

- **`stochastic_tree.py`**: This module contains the core logic for generating stochastic trees. It uses random parameters to create variations in the tree structure.
- **`helper.py`**: This module provides a set of helper functions that are used throughout the package.
- **`tree_generation/`**: This directory contains scripts for generating and converting tree models.

To use these modules, you can import them into your L-Py files or other Python scripts. For example:

.. code-block:: python

    from stochastic_tree import generate_stochastic_tree

    # Generate a stochastic tree with custom parameters
    tree = generate_stochastic_tree(num_branches=10, branch_length=0.5)

For more detailed examples, please refer to the scripts in the `examples` directory.
