#!/bin/python3

## AUTHOR: Mahboob Karimian
## COPYRIGHT: 2023

import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def gen_random_num_nodes_per_layer(m, n, min_val, max_val, nfl, accurate):
        """
        Generate n random integers between min_val and max_val whose sum equals to m.
        "nfl": the first number in the list
        """
        # Check if it's possible to generate n random numbers whose sum equals to m
        if n * min_val > m or n * max_val < m:
            print("Cannot generate n random numbers between min_val and max_val whose sum equals to m.")
            return []

        numbers = []
        cnt = 0
        max_try = 500000
        if not accurate:
            while True:
                cnt += 1
                # Generate n-1 random numbers between min_val and max_val
                numbers = [random.randint(min_val, max_val) for _ in range(n-1)]
                # Calculate the last number to ensure that the sum equals to m
                numbers.append(m - sum(numbers))
                if numbers[-1] >= min_val:
                    break
                # Avoid infinite loop
                if cnt > max_try:
                    return []
        else:
            # Generate n-2 random numbers between min_val and max_val
            print("went2while")
            while True:
                cnt += 1
                numbers = [random.randint(min_val, max_val) for _ in range(n-2)]
                numbers.insert(0, nfl)
                # Calculate the last number to ensure that the sum equals to m
                numbers.append(m - sum(numbers))
                print("numbers: ", numbers[-1], cnt)
                if (numbers[-1] >= min_val and numbers[-1] <= max_val):
                    break
                # Avoid infinite loop
                if cnt > max_try:
                    return []

        # Check the first number to ensure it is the specified value
        diff = 0
        if numbers[0] > nfl:
            diff = numbers[0] - nfl
            numbers[0] = nfl
        
        #print("diff: ", diff)
        new_numbers = []
        if diff > 0:
            new_numbers.append(numbers[0])
            # Distribute the difference to the other numbers
            k = len(numbers) - 1
            additin_list = np.random.multinomial(diff, np.ones(k)/k)
            i = 1
            while i < len(numbers):
                new_numbers.append(numbers[i] + additin_list[i-1])
                i += 1
        else:
            new_numbers = numbers
        #print("numbers: ", numbers, "new_numbers: ", new_numbers)
        if max(new_numbers) > max_val:
            print("The maximum value of nodes per layer exceeded the max.", max(new_numbers), max_val)
        return new_numbers

def random_dag(num_nodes, num_layers, min_num_nodes_per_layer, max_num_nodes_per_layer,
                num_first_layer, max_outgoing_edges, accurate=False):
    """
    Generate a random DAG graph based on the provided arguments.
    "accurate": if True then the number of nodes per layer must not excced the max_num_nodes_per_layer
    """
    nodes = []
    edges = []
    node_count = 1
    virtual_num_nodes = num_nodes - 1
    random_integers = gen_random_num_nodes_per_layer(virtual_num_nodes, num_layers, min_num_nodes_per_layer,
                                                      max_num_nodes_per_layer,num_first_layer, accurate)

    if len(random_integers) == 0:
        return [], []
    # Create the nodes
    for i in range(num_layers):
        layer_nodes = []
        npl = random_integers[i]
        for j in range(npl):
            node = node_count
            layer_nodes.append(node)
            nodes.append(node)
            node_count += 1

        # Connect the nodes to the previous layer
        if i > 0:
            for node in layer_nodes:
                # Randomly select outgoing edges for this node
                num_outgoing_edges = random.randint(1, max_outgoing_edges)
                if num_outgoing_edges > len(prev_layer_nodes):
                    num_outgoing_edges = len(prev_layer_nodes)
                #print("num_outgoing_edges: ", num_outgoing_edges, "prev_layer_nodes: ", prev_layer_nodes)
                outgoing_edges = random.sample(prev_layer_nodes, num_outgoing_edges)
                for edge in outgoing_edges:
                    edges.append((edge, node))

        prev_layer_nodes = layer_nodes
    
    nodes.insert(0, 0)
    for j in range(num_first_layer):
        edges.append((0, j+1))
    return nodes, edges


# Plot the graph
def draw_graph(nodes, edges):
    # Create a directed graph
    G = nx.DiGraph()

    # Add the nodes to the graph
    for node in nodes:
        G.add_node(node)

    # Add the edges to the graph
    for edge in edges:
        G.add_edge(edge[0], edge[1])

    # Plot the graph
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    nx.draw(G, pos, with_labels=True)
    plt.show()

# Test
# Generate the random DAG
def test():
    for i in range(1):
        nodes, edges = random_dag(600, 20, 12, 35, 4 , 5, 1)

    draw_graph(nodes, edges)

#test()



