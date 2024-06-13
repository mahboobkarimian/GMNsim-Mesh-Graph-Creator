# Automatic installation with Conda

Running `bash init_conda_env.sh` will install all the required dependencies.

# Manual installation with Conda

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

3. Automatically export D-Bus system bus required when WSBRD runs as root on conda env activation
```
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo 'export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/var/run/dbus/system_bus_socket' > $CONDA_PREFIX/etc/conda/activate.d/set_dbus_address.sh
```

4. Load previous change
conda deactivate
conda activate gmnsim

5. Install the required dependencies:
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