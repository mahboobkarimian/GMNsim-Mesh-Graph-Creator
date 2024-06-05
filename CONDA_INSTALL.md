# Install with Conda

We use a venv with python 3.10.

## Installation


1. Create a new Conda environment with Python 3.10:
```
conda create -n gmnsim python=3.10
```

2. Activate the environment:
```
conda activate gmnsim
```


3. Install the required dependencies:
```
conda install -c conda-forge dbus-python
conda install matplotlib
conda install scikit-learn
conda install networkx
conda install pygraphviz
```


## Usage

To run GMNsim, simply activate the Conda environment and execute the main script:
```
conda activate gmnsim
python main.py
```