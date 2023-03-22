# Mesh Graph Creator

Mesh Graph Creator is a tool that provides a simple graphical interface for drawing and generating custom or random graphs. It is primarily designed to create graphs that can be used with a mesh network simulator based on the Mbed OS.


## Drawing nodes and edges

The process of creating a graph is straightforward.

* Draw nodes on the blank canvas by **clicking** on it.

* Connect two nodes, simply **right-click** on one node and then the other.

* Delete a node and its connected edges by pressing **Ctrl + Click**.

* Move a node and its edges by **double-click** and holding it.

* Click the "Update" button. If you have deleted some nodes or resized the window, this button will update your graph accordingly.

## Simulator

The "Simulator" panel enables you to configure the simulation and logging options. By clicking on the "Export Config" button, you can export these settings along with the graph to a bash script. The bash script can be directly executed to deploy nodes in the mesh network and start the simulation.

Example: `bash run_22_10_31_20_n51.sh`

## Export Graph

Click the 'Export Graph' button to write your graph into text file, `model.txt`