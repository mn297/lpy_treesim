Files and Directory Structure
=============================

This document provides an overview of the important files and directories in the `lpy_treesim` project.

Top-Level Files
---------------

- **`README.rst`**: The main README file for the project.
- **`helper.py`**: Contains helper functions used by other scripts in the project.
- **`stochastic_tree.py`**: The core module for generating stochastic trees.
- **`.gitignore`**: A file that specifies which files and directories to ignore in a Git repository.

`docs/`
-------

This directory contains the documentation for the project.

- **`Makefile`**: A makefile with commands to build the documentation.
- **`source/`**: The source files for the documentation, written in reStructuredText.
    - **`conf.py`**: The configuration file for Sphinx, the documentation generator.
    - **`index.rst`**: The main entry point for the documentation.
    - **`installation.rst`**: Instructions on how to install the project.
    - **`usage.rst`**: An explanation of how to use the project.
    - **`files.rst`**: An overview of the important files and directories in the project.
    - **`resources.rst`**: A list of resources related to the project.
    - **`methods.rst`**: A description of the methods used in the project.
- **`_static/`**: Static files, such as images and videos, that are used in the documentation.

`examples/`
-----------

This directory contains example `.lpy` files that demonstrate how to use `lpy_treesim`.

- **`legacy/`**: Older example files.
- **`UFO/`**: Examples related to the UFO cherry tree architecture.

`modules_test/`
---------------

This directory contains test files for the modules in the project. The files in this folder use classes and functions defined in `stochastic_tree.py` and can be a good example of how to use the `BasicWood`, `Wire`, and `Support` classes.

`other_files/`
--------------

These files may or may not work. They were used in previous iterations of `lpy_treesim` and are kept for reference.

`tree_generation/`
------------------

This directory contains scripts for generating and converting tree models.