Installation
==============

This document provides instructions on how to install `lpy_treesim` and its dependencies.

Prerequisites
-------------

- **Python 3.x**: Make sure you have a working Python 3 installation.
- **Conda**: `lpy_treesim` relies on the Conda package manager to handle its environment and dependencies. If you don't have Conda, you can install it by following the official documentation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/

Installing L-Py
---------------

`lpy_treesim` is built on top of L-Py, a Python-based L-system simulator. To install L-Py, follow these steps:

1.  **Create a Conda Environment**: Open your terminal and create a new Conda environment named `lpy`:

    .. code-block:: bash

        conda create -n lpy openalea.lpy -c fredboudon -c conda-forge

2.  **Activate the Environment**: Activate the newly created environment:

    .. code-block:: bash

        conda activate lpy

3.  **Run L-Py**: You can now run L-Py to ensure it's installed correctly:

    .. code-block:: bash

        lpy

For more detailed information and troubleshooting, refer to the official L-Py documentation: https://lpy.readthedocs.io/en/latest/user/installing.html

Installing `lpy_treesim`
------------------------

Once you have L-Py set up, you can install `lpy_treesim`:

1.  **Clone the Repository**: Clone this repository to your local machine:

    .. code-block:: bash

        git clone https://github.com/your-username/lpy_treesim.git
        cd lpy_treesim

2.  **Install Dependencies**: The required Python packages are listed in the `requirements.txt` file. You can install them using pip:

    .. code-block:: bash

        pip install -r requirements.txt

Running the Examples
--------------------

The `examples` directory contains several examples that demonstrate how to use `lpy_treesim`. To run an example, navigate to the `examples` directory and run the desired script:

.. code-block:: bash

    cd examples
    python example_script.py

Replace `example_script.py` with the actual name of the example you want to run.