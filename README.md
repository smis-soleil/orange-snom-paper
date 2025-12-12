# orange-snom paper data and workflows

Here we provide the data and corresponding [pySNOM](https://github.com/Quasars/pySNOM) scripts for each example in the first paper describing the [orange-snom](https://github.com/Quasars/orange-snom) add-on to [Quasar](https://quasar.codes/).

### Reproduce the calculations

We provide the example scripts as Jupyter notebooks for each workflow described in our paper. The goal is to demonstrate how to use pySNOM to achieve similar result then in Quasar. It is important to not, that not everything can be done. For example to define and use masks with a UI is only available in Quasar.

The Jupyter notebooks contain useful tips and descriptions to undertand and reproduce the functionality. The example data used in the script is available in this repository and free to play with, but we ecourige the user to experiment with their own.

To be able to run all the script, you need the packages installed described in `requirements.txt`. We suggest to create your environment using:

    conda myenv create -f environment.yml

### Standalone app

`browser.py` represent a GUI application created from Quasar widgets. Using the codebase of Quasar and Orange one can build a standalone UI consisting of Quasar widgets. The presented application allows to browse files with a treeview browser and the data is passed to the widgets for further processing and visualization.

### Cite us:

TODO: add citation here - first arXiv, then published paper.
