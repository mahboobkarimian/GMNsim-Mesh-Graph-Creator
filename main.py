#!/bin/python3

import json
import os
import subprocess
import tkinter as tk
from tkinter import filedialog as filedialog
import time
from tkinter import ttk
import dbus
from matplotlib import pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

from confgen import configure as SimConfGen
from assets import bs64_wisun_img as GetWisunImg
from daggen import random_mesh_graph_gen as RndMeshGen
from daggen import plot_dag_as_tree as MeshPlot
from daggen import get_pos_dag as RndGetPos
from daggen import get_graph_diameter as GrphDiameter
from managed_daggen import random_dag as MngRndMeshGen


_VERSION = "0.5b"
_BG = "#292929"
_FG = "#d9d9d9"
_EBG = "#444444"
_DBG = "#4e5552"

def get_sim_nodes():
    globalinfo.reset_connected_nodes()
    if not is_sim_running():
        return None, None
    bus = dbus.SessionBus()
    interface_name = 'com.silabs.Wisun.BorderRouter'
    object_path = '/com/silabs/Wisun/BorderRouter'
    property_name = 'Nodes'
    try:
        proxy_obj = bus.get_object(interface_name, object_path)
    except:
        print("Error: Could not connect to the border router")
        #tk.messagebox.showerror(title="D-BUS error", message="Could not connect to the border router. Is simulation running?")
        return None, None
    interface = dbus.Interface(proxy_obj, dbus_interface='org.freedesktop.DBus.Properties')
    try:
        nodes = interface.Get(interface_name, property_name)
    except:
        print("Error: too soon to read nodes property")
        #tk.messagebox.showerror(title="D-BUS error", message="too soon to read nodes property")
        return None, None
    #print(nodes)
    gedges = []
    gnodes = []
    for n in nodes:
        nname = ""
        pname = ""
        for i in range(0,8):
            nname = nname + str(int(n[0][i]))
        for i in range(0,8):
            pname = pname + str(int(n[1]['parent'][i]))
        gedges.append((nname,pname))
        gnodes.append(nname)
    globalinfo.set_connected_nodes(len(gnodes))
    globalinfo.set_ref_timestamp(time.time())
    globalinfo.set_nodes_timestamp(gnodes, time.time())
    return gnodes, gedges

def is_sim_running():
    process1_name = 'wssimserver'
    process2_name = 'wsbrd'
    pid = None
    try:
        pid = subprocess.check_output(['pgrep', process1_name])
        pid = pid.decode().strip()
        # dummy check also if border router is running
        _pid = subprocess.check_output(['pgrep', process2_name])
    except subprocess.CalledProcessError:
        print("No simulation running")
    return pid
############################################################
# Class: Global information
class GlobalInfo:
    def __init__(self):
        self.total_nodes = 0
        self.connected_nodes = 0
        self.sim_settings = dict()
        self.conn_timestamp = dict()
    
    def set_total_nodes(self, num_nodes):
        self.total_nodes = num_nodes

    def set_connected_nodes(self, num_nodes):
        self.connected_nodes = num_nodes

    def reset_total_nodes(self):
        self.total_nodes = 0

    def reset_connected_nodes(self):
        self.connected_nodes = 0

    def get_total_nodes(self):
        return self.total_nodes
    
    def get_connected_nodes(self):
        return self.connected_nodes
    
    def init_sim_settings(self):
        self.sim_settings = {'varTundev': tk.IntVar(value=1), 'varNano': tk.IntVar(value=1),
                'varRadio': tk.IntVar(value=1), 'varLog': "e.g: 1,5,6,50",
                'varCleartmp': tk.IntVar(value=1), 'varTunip': "fd12:3456::1/64",
                'sim_path': ""}
    
    def set_sim_settings(self, sw_config): 
        self.sim_settings['varTundev'].set(sw_config['varTundev'])
        self.sim_settings['varNano'].set(sw_config['varNano'])
        self.sim_settings['varRadio'].set(sw_config['varRadio'])
        self.sim_settings['varLog'] = sw_config['varLog']
        self.sim_settings['varCleartmp'].set(sw_config['varCleartmp'])
        self.sim_settings['varTunip'] = sw_config['varTunip']
        if 'sim_path' in sw_config.keys():
            self.sim_settings['sim_path'] = sw_config['sim_path']

    def set_sim_setting_element(self, element, value):
        self.sim_settings[element] = value

    def get_sim_settings(self):
        return self.sim_settings
    
    def set_ref_timestamp(self, timestamp):
        if 'ref' not in self.conn_timestamp.keys():
            self.conn_timestamp['ref'] = timestamp
    
    def set_nodes_timestamp(self, nodes, timestamp):
        for a_node in nodes:
            if a_node not in self.conn_timestamp.keys():
                self.conn_timestamp[a_node] = timestamp
    
    def get_all_timestamp(self):
        return self.conn_timestamp

    def del_node_timestamp(self, node):
        if node in self.conn_timestamp.keys():
            del self.conn_timestamp[node]
    
    def del_all_timestamp(self):
        self.conn_timestamp.clear()
############################################################
# Class: Theme
class Bt(tk.Button):
    def __init__ (self, *args, color=None, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self['bg'] = '#0078d4'
        self['fg'] = 'white'
        self['bd'] = 0
        self['activebackground'] = '#1092cb'
        self['activeforeground'] = "white"
        self['highlightbackground'] = _BG
        self['relief'] = tk.FLAT
        if color == 'green':
            self['bg'] = "#25a004"
            self['activebackground'] = '#3ca858'
        elif color == 'red':
            self['bg'] = "#A0042a"
            self['activebackground'] = '#c3042a'
        if self['image']:
            self['bg'] = _BG
            self['activebackground'] = _BG
            self['highlightbackground'] = _BG

class Rb(tk.Radiobutton):
    def __init__ (self, *args, color=None, **kwargs):
        tk.Radiobutton.__init__(self, *args, **kwargs)
        self['bg'] = _BG
        self['fg'] = _FG
        self['selectcolor'] = _EBG
        self['bd'] = 0
        self['activebackground'] = _BG
        self['activeforeground'] = _FG
        self['highlightbackground'] = _BG
        self['relief'] = tk.FLAT

class Lf(tk.LabelFrame):
    def __init__ (self, *args, **kwargs):
        tk.LabelFrame.__init__(self, *args, **kwargs)
        self['bg'] = _BG
        self['fg'] = _FG
        self['bd'] = 1
        self['relief'] = tk.GROOVE
        self['highlightbackground'] = _BG

class Cb(tk.Checkbutton):
    def __init__ (self, *args, **kwargs):
        tk.Checkbutton.__init__(self, *args, **kwargs)
        self['bg'] = _BG
        self['fg'] = _FG
        self['activebackground'] = _BG
        self['activeforeground'] = _FG
        self['highlightbackground'] = _BG
        self['selectcolor'] = _EBG
        self['bd'] = 0

class Lb(tk.Label):
    def __init__ (self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self['bg'] = _BG
        self['fg'] = _FG

class En(tk.Entry):
    def __init__ (self, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        self['bg'] = _EBG
        self['fg'] = _FG
        self['highlightbackground'] = _BG
        self['insertbackground'] = _FG
        self['disabledbackground'] = _DBG
        self['disabledforeground'] = _EBG
        self['bd'] = 0
        self['relief'] = tk.FLAT
############################################################
# Class: Node
class Node:

    def __init__(self, x, y, r, index, canvas_name):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        self.x = x
        self.y = y
        self.r = r
        self.index = index
        self.hidden = False
        self.canvas_name = canvas_name
        self.oval = canvas_name.create_oval(x0, y0, x1, y1,fill="gray49")
        self.text = canvas_name.create_text(x, y, text=str(index-1), font=(False, 10), fill="white")

    def clicked_down(self):
        self.canvas_name.itemconfig(self.oval, fill="green")

    def clicked_up(self):
        self.canvas_name.itemconfig(self.oval, fill="gray49")

    def double_clicked(self):
        self.canvas_name.itemconfig(self.oval, fill="black")

    def reset_click(self):
        self.canvas_name.itemconfig(self.oval, fill="gray49")

    def is_collide(self,x,y):
        # print("({0} - {2})^2 + ({1} - {3})^2) < {4}^2".format(x,y,self.x,self.y,self.r))
        if self.hidden:
            return False
        return ((x - self.x)**2 + (y - self.y)**2) < (self.r*2)**2

    def is_clicked(self,x,y):
        if self.hidden:
            return False
        return ((x - self.x)**2 + (y - self.y)**2) < self.r**2

    def print_node(self):
        print("X: {0} Y: {1} R: {2} Index:{3}".format(self.x, self.y, self.r,self.index))

    def get_index(self): return self.index

    def move_node(self,x,y):
        self.x = x
        self.y = y
        x0 = x - self.r
        y0 = y - self.r
        x1 = x + self.r
        y1 = y + self.r
        self.canvas_name.coords(self.oval, x0, y0, x1, y1)
        self.canvas_name.coords(self.text, x, y)

############################################################
# Class: GBuilder
class GBuilder:
    # TODO: Add DoubleClick event so the nodes can be moved
    # TODO: Add option the remove edge

    def __init__(self, root, width, height, bgc, status_bar):
        self.root = root
        self.status_bar = status_bar
        self.canvas = tk.Canvas(root, height=height, widt=width, bg=bgc)
        self.canvas['bd'] = 0
        self.canvas['highlightthickness'] = 0
        self.canvas['relief'] = tk.FLAT
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas_width = width
        self.canvas_height = height

        self.canvas.bind("<Button-1>", self.canvas_mouseClick)
        self.canvas.bind("<Button-3>", self.canvas_mouseRightClick)
        # bind double click event:
        self.canvas.bind("<Double-Button-1>", self.canvas_mouseDoubleClick)
        self.canvas.bind("<Control-Button-1>", self.canvas_ctrlMouseRightClick)
        dummy_node = Node(-10, -10, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.edges = []
        self.node_list_index = 0

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node
        self.id_textMode = 0 # 0: int node IDs, 1: hex node IDs

    def draw_line(self, x1, y1, x2, y2):
        line1 = self.canvas.create_line(x1, y1, x2, y2, arrow=None, fill="#222", width=2.5)
        line2 = self.canvas.create_line(x1, y1, x2, y2, arrow=None, fill="#222", width=2)
        self.canvas.tag_lower(line1)
        self.canvas.tag_lower(line2)
        return line1, line2

    def canvas_mouseClick(self, event):
        if self.connecting:
            return
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                lst = []
                for e in self.edges:
                    if n.get_index() in e and n.get_index() != e[1]:
                        lst.append(e[1]-1)
                self.status_bar.config(text=f"Node: {n.get_index()-1} connected to {len(lst)} nodes: {lst}")
        # 'Check for collision:
        for n in self.nodes:
            if n.is_collide(event.x, event.y):
                return
        # 'Add new node:
        self.node_list_index += 1
        new_node = Node(event.x, event.y, 15, self.node_list_index, self.canvas)
        #print(event.x, event.y)
        self.nodes.append(new_node)
        globalinfo.set_total_nodes(self.node_list_index)

    def canvas_mouseRightClick(self, event):
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                if self.connecting:
                    self.selectedNode.clicked_up()
                    if n is not self.selectedNode:
                        # 'Connecting two nodes:
                        line1, line2 = self.draw_line(self.selectedNode.x, self.selectedNode.y, n.x, n.y)
                        edge = [self.selectedNode.index,n.index, line1, line2]
                        self.edges.append(edge)
                    self.connecting = False
                else:
                    n.clicked_down()
                    self.selectedNode = n
                    self.connecting = True
    
    def canvas_mouseDoubleClick(self, event):
        # move node to new position
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                n.double_clicked()
                var = tk.StringVar()
                self.canvas.bind("<ButtonRelease-1>", lambda event, var=var: var.set("released"))
                self.canvas.wait_variable(var)
                # get new position of pointer in the canvas
                xy = self.canvas.winfo_pointerxy()
                x = xy[0] - self.canvas.winfo_rootx()
                y = xy[1] - self.canvas.winfo_rooty()
                #print("Moving to:", event.x, event.y, x, y)
                n.move_node(x,y)
                # move edges
                #print("Moving edges", self.edges)
                index = 0
                for e in self.edges:
                    index += 1
                    if e[0] == n.index or e[1] == n.index:
                        self.canvas.delete(e[2])
                        self.canvas.delete(e[3])
                        #for e in self.edges:
                        line1, line2 = self.draw_line(self.nodes[e[0]].x, self.nodes[e[0]].y, self.nodes[e[1]].x, self.nodes[e[1]].y)
                        e[2] = line1
                        e[3] = line2
                
                n.reset_click()

    def canvas_ctrlMouseRightClick(self, event):
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                n.double_clicked()
                # remove node
                self.canvas.delete(n.oval)
                self.canvas.delete(n.text)
                #self.nodes.remove(n)
                #self.node_list_index -= 1
                # Hack: instead of removing the node, we just hide it
                n.hidden = True
                # remove edges
                tmp_edges = []
                for e in self.edges:
                    if e[0] == n.index or e[1] == n.index:
                        self.canvas.delete(e[2])
                        self.canvas.delete(e[3])
                    else:
                        tmp_edges.append(e)
                #print(tmp_edges, "||||", self.edges)
                self.edges = tmp_edges
                break
        #self.reinddex_nodes_and_edges()

    def reinddex_nodes_and_edges(self):
        # Reindex nodes:
        tmp_nodes = []
        for n1 in self.nodes:
            if n1.hidden:
                idx = n1.index
                for n2 in self.nodes:
                    if n2.index > idx:
                        n2.index -= 1
                        self.canvas.delete(n2.text)
                        if not n2.hidden:
                            n2.text = self.canvas.create_text(n2.x, n2.y, text=str(n2.index-1), font=(False, 10), fill="black")
                for e in self.edges:
                    if e[0] > idx:
                        e[0] -= 1
                    if e[1] > idx:
                        e[1] -= 1
                self.node_list_index -= 1
            else:
                tmp_nodes.append(n1)
        self.nodes = tmp_nodes
        globalinfo.set_total_nodes(self.node_list_index)

        # check if window size is changed:
        if self.canvas.winfo_width() != self.canvas_width+2 or self.canvas.winfo_height() != self.canvas_height+39:
            print("size:", self.canvas.winfo_width(), self.canvas.winfo_height(), self.canvas_width, self.canvas_height)
            self.canvas_width = self.canvas.winfo_width()-2
            self.canvas_height = self.canvas.winfo_height()-39
            self.draw_graph_from_list(self.node_list_index, self.edges)


    def draw_graph_from_list(self, num_raw_nodes, edges):
        if edges == []:
            return
        # Make a backup of the edges list:
        edges_copy = edges.copy()
        # Clear the canvas:
        self.clear()

        # edges may have 0 elemnt which is considered as a dummy node here.
        # they must start from 1 in our case, so if it comes from rnd graph
        # we take 2 elements, if its from update function we take 4 elements
        for elmnt in edges_copy:
            if 0 in elmnt:
                if len(edges_copy[0]) > 2:
                    edges = [[x, y] for x, y, m, l in edges_copy]
                else:
                    edges = [[x+1, y+1] for x, y in edges_copy]
                break
        # Otherwise, we have a list of edges that starts from 1:
        if edges == []:
            edges = [[x, y] for x, y, m, l in edges_copy]

        nx_pos = RndGetPos(edges)
        pos = dict(sorted(nx_pos.items()))
        #print("pos:", pos)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        for n in pos:
            # Map pos to canvas size:
            x = pos[n][0] * canvas_width*0.5 + canvas_width/2 + 20
            y = pos[n][1] * canvas_height*0.47 + canvas_height/2
            new_node = (Node(x, y, 15, n, self.canvas))
            #print("x", x, "y", y, "c_w", canvas_width, "c_h", canvas_height)
            self.nodes.append(new_node)
            self.node_list_index += 1

        for e in edges:
            line1, line2 = self.draw_line(self.nodes[e[0]].x, self.nodes[e[0]].y, self.nodes[e[1]].x, self.nodes[e[1]].y)
            edge = [e[0],e[1], line1, line2]
            self.edges.append(edge)
        globalinfo.set_total_nodes(num_raw_nodes)
    

    def get_graph_diameter_from_edges(self):
        if len(self.edges) == 0:
            return 1
        edges = []
        if len(self.edges[0]) > 2:
            edges = [(x, y) for x, y, m, l in self.edges]
        else:
            edges =[(x, y) for x, y in self.edges]
        return GrphDiameter(edges)
    

    def change_labels_to_hex(self):
        if not self.id_textMode:
            self.id_textMode = 1
            for n in self.nodes:
                if not n.hidden:
                    self.canvas.delete(n.text)
                    n.text = self.canvas.create_text(n.x, n.y, text=str(hex(n.index-1))[2:], fill="White")
        else:
            self.id_textMode = 0
            for n in self.nodes:
                if not n.hidden:
                    self.canvas.delete(n.text)
                    n.text = self.canvas.create_text(n.x, n.y, text=str(n.index-1), font=(False, 10), fill="White")


    def clear(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()

        # 'Reset nodes:
        dummy_node = Node(-10, -10, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.node_list_index = 0

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node
        self.id_textMode = 0
        globalinfo.reset_total_nodes()

    def import_graph(self):
        num_nodes = 0
        name = filedialog.askopenfilename(filetypes=[('Graph files','*.graph')])
        if type(name) != str or name == "":
            return
        with open(name, "r") as f:
            lines = f.readlines()
            try:
                num_nodes = int(lines[0]) -1
            except:
                tk.messagebox.showerror("Error", "Invalid file format!")
                return
            if num_nodes < 1:
                "No nodes to import!"
                return
            self.clear()
            edges = []
            for i in range(1, len(lines)):
                if "---" in lines[i]:
                    break
                edges.append([int(lines[i].split(",")[0]), int(lines[i].split(",")[1])])
            self.draw_graph_from_list(num_nodes, edges)

    def export(self):
        if self.node_list_index < 1:
            return
        name = ["graph_" + str(time.strftime("%d_%H_%M_%S_n")) + str(self.node_list_index) + ".graph", 'last.graph']
        for filename in name:
            with open(filename, "w") as f:
                f.write(f"{self.node_list_index}\n")
                for e in self.edges:
                    f.write(f"{e[0]},{e[1]}\n")
                f.write("---")

############################################################
# Class: Config Window
class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, VarTundev, VarNano, VarRadio, VarLog, VarCleartmp, VarTunip):
        super().__init__(parent)

        self.title("Simulation configuration")
        self.configure(bg=_BG)
        self.resizable(False, False)
        self.varTundev = VarTundev
        self.varNano = VarNano
        self.varRadio = VarRadio
        self.varLog = VarLog
        self.varCleartmp = VarCleartmp
        self.varTunip = VarTunip

        sim_frame = tk.Frame(self, bg = _BG)
        sim_frame.pack(side=tk.TOP, padx=5, anchor=tk.NW)
        loglbl = Lb(sim_frame, text="Log:")
        loglbl.pack(padx=5, pady=10, side=tk.LEFT)
        self.log = En(sim_frame)
        self.log.insert(0, VarLog)
        self.log.pack(padx=5, pady=10, side=tk.LEFT)
        
        Nano = Cb(sim_frame, text="IP stack log", variable=self.varNano)
        Nano.pack(padx=1, pady=10, side=tk.LEFT)
        
        Radio = Cb(sim_frame, text="MAC/RF log", variable=self.varRadio, bg=_BG, fg=_FG)
        Radio.pack(padx=1, pady=10, side=tk.LEFT)
        
        Cleartmp = Cb(sim_frame, text="Clear /tmp logs", variable=self.varCleartmp, bg=_BG, fg=_FG)
        Cleartmp.pack(padx=1, pady=10, side=tk.LEFT)

        sim_frame1 = tk.Frame(self, bg = _BG)
        sim_frame1.pack(side=tk.TOP, padx=5, anchor=tk.NW)
        
        Tundev = Cb(sim_frame1, text="Create TUN interface", variable=self.varTundev, bg=_BG, fg=_FG)
        Tundev.pack(padx=1, pady=10, side=tk.LEFT)
        Tuniplbl = Lb(sim_frame1, text="TUN IP:")
        Tuniplbl.pack(padx=5, pady=10, side=tk.LEFT)
        self.Tunip = En(sim_frame1, width=35)
        self.Tunip.insert(0, self.varTunip)
        self.Tunip.pack(padx=5, pady=10, side=tk.LEFT)

        sim_frame2 = tk.Frame(self, bg = _BG)
        sim_frame2.pack(side=tk.TOP, padx=5, anchor=tk.NW)
        war_label = tk.Label(sim_frame2, text="Tip: Close this window to interact again with main window!", bg=_BG, fg="Red")
        war_label.pack(side=tk.LEFT)


        # create OK and Cancel buttons
        button_frame = tk.Frame(self, bg=_BG)
        button_frame.pack(side=tk.TOP, pady=10, padx=5, anchor=tk.SE)
        ok_button = Bt(button_frame, text="OK", command=self.ok)
        ok_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = Bt(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)

        reset_button = Bt(button_frame, text="Reset", command=self.reset)
        reset_button.pack(side=tk.RIGHT, padx=5)

        self.result = None

    def reset(self):
        self.varTundev.set(1)
        self.varNano.set(1)
        self.varRadio.set(1)
        self.varCleartmp.set(1)
        self.varLog = "e.g: 1,5,6,50"
        self.log.delete(0, tk.END)
        self.log.insert(0, self.varLog)
        self.varTunip = "fd12:3456::1/64"
        self.Tunip.delete(0, tk.END)
        self.Tunip.insert(0, self.varTunip)

    def ok(self):
        self.result = [str(self.Tunip.get()), str(self.log.get())]
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

############################################################
# Class: Plot window
class PlotDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Live Mesh")
        self.configure(bg='gray35')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Before making canvas, get some hints about size of the window
        # and fill gedges and gnodes
        self.gedges = []
        self.gnodes = []
        pos, CVS_W, CVS_H = self.get_pos_w_h()
        if pos is None:
            """ tk.messagebox.showwarning("Error", "No nodes found!")
            self.destroy()
            return """
            CVS_W = 200
            CVS_H = 200
        # now create the canvas
        self.canvas = tk.Canvas(self, width=CVS_W, height=CVS_H, bg="gray45")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # draw the graph
        self.draw_graph(pos)

        # update the graph every 1 sec
        self.update_graph()
        
    def update_graph(self):
        self.canvas.delete("all")
        pos, CVS_W, CVS_H = self.get_pos_w_h()
        if pos is not None:
            # resize the canvas
            #print("Updating graph every 1 sec")
            self.canvas.config(width=CVS_W, height=CVS_H)
            self.draw_graph(pos)
        else:
            self.canvas.create_text(100, 100, text="No nodes yet, wait please ...")
        self.after(1000, self.update_graph)

    def draw_graph(self, pos):
        # draw nodes:
        # hint: pos is a dict: {nodeid: (x, y)}
        if pos is None:
            return
        for nodeid, (x, y) in pos.items():
            lbl = int(str(nodeid)[6:7]) * 256 + int(str(nodeid)[7:])
            node, text = self.draw_node(x, y, str(lbl))
        # draw edges:
        for e in self.gedges:
            x1, y1 = pos[e[0]]
            x2, y2 = pos[e[1]]
            line1, line2 = self.draw_line(x1, y1, x2, y2)

    def draw_line(self, x1, y1, x2, y2):
        line1 = self.canvas.create_line(x1, y1, x2, y2, arrow=None, fill="#222", width=2)
        line2 = self.canvas.create_line(x1, y1, x2, y2, arrow=None, fill="#222", width=1.5)
        self.canvas.tag_lower(line1)
        self.canvas.tag_lower(line2)
        return line1, line2
    
    def draw_node(self, x, y, name):
        tname = name
        ncolor = "grey10"
        tcolor = "white"
        if name == '0':
            tname = "BR"
            ncolor = "green"
            tcolor = "white"
        node = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=ncolor, outline="#222", width=2)
        text = self.canvas.create_text(x, y, text=tname, font=(False, 8), fill=tcolor)
        return node, text

    def update_frequency(self):
        # required to update canvas and attached toolbar!
        self.canvas.draw()

    def get_sim_topology(self):
        gnodes, gedges = get_sim_nodes()
        if not gnodes or not gedges:
            return
        bordernode = ""
        for p in gedges:
            if not p[1] in gnodes:
                bordernode = p[1]
        gnodes.append(bordernode)
        self.gedges = gedges
        self.gnodes = gnodes
        return MeshPlot(gedges, True)

    def get_pos_w_h(self):
        pos = self.get_sim_topology()
        # scale posses to fit in max size we can draw:
        max_hz = 1400 # define max W
        max_vt = 900 # define max H
        if pos == None:
            return None, None, None
        # check the max x and y in pos:
        max_pos_x = max(pos.values(), key=lambda x: x[0])[0]
        max_pos_y = max(pos.values(), key=lambda x: x[1])[1]
        scale_x = 1
        scale_y = 1
        if max_pos_x > max_hz or max_pos_y > max_vt:
            scale_x = (max_hz/max_pos_x)/1
            scale_y = (max_vt/max_pos_y)/1.5
        new_pos = {}
        for k in pos:
            new_pos[k] = (pos[k][0]*scale_x, pos[k][1]*scale_y)
        pos = new_pos
        # Determine W and H of canvas to be drawn:
        CVS_W = max(pos.values(), key=lambda x: x[0])[0] + 15 # 15 is margin right and bottom
        CVS_H = max(pos.values(), key=lambda x: x[1])[1] + 15
        # subtract CVS_H from y of poses to flip the graph:
        new_pos = {}
        for k in pos:
            new_pos[k] = (pos[k][0], CVS_H-pos[k][1])
        pos = new_pos
        return pos, CVS_W, CVS_H

    def on_closing(self):
        # destroy the window when the "WM_DELETE_WINDOW" event is triggered
        self.destroy()

############################################################
# Global variables
globalinfo = GlobalInfo()
plotd = None

############################################################
# Main
def main():

    _root = tk.Tk()
    _root.title("GMNsim") # Graph and Mesh Network Simulation Tool
    # '_root.geometry("800x500")
    _root.resizable(1,1)

    ttkstyle = ttk.Style()
    ttkstyle.theme_use('alt')
    ttkstyle.configure('blue.Horizontal.TProgressbar',
        troughcolor  = 'grey',
        troughrelief = 'flat',
        background   = '#0078d4')

    def retrive_sim_info():
    # Check the number of MAC/PHY processes as TOTAL_NODES:
        if is_sim_running():
            
            answer = tk.messagebox.askyesno("A simulation found running.","Do you want to retrieve its information?")
            if answer:
                filename = "/tmp/graph.txt"
                if os.path.exists(filename):
                    read_sim_dump(filename)
                else:
                    pids = subprocess.check_output(["pgrep", "wshwsim"])
                    pids = pids.decode('utf-8').split('\n')
                    globalinfo.set_total_nodes(len(pids) - 2)
            else:
                globalinfo.reset_total_nodes()

    def read_sim_dump(file):
        with open(file, 'r') as f:
            lines = f.readlines()
            edges = []
            nodes = int(lines[0])
            for _l in lines[1:]:
                _edge = _l.split(',')
                e1 = int(_edge[0])
                e2 = int(_edge[1])
                if [e2, e1] not in edges:
                    edges.append([e1, e2])
            builder.draw_graph_from_list(nodes, edges)
            

    def on_window_close():
        sim_settings = globalinfo.get_sim_settings()
        print(sim_settings)
        # Store the settings in the config dict to be written into file upon exit:
        serialized_sim_settings = {}
        serialized_sim_settings['varTundev'] = sim_settings['varTundev'].get()
        serialized_sim_settings['varNano'] = sim_settings['varNano'].get()
        serialized_sim_settings['varRadio'] = sim_settings['varRadio'].get()
        serialized_sim_settings['varLog'] = sim_settings['varLog']
        serialized_sim_settings['varCleartmp'] = sim_settings['varCleartmp'].get()
        serialized_sim_settings['varTunip'] = sim_settings['varTunip']
        serialized_sim_settings['sim_path'] = sim_settings['sim_path']
        with open("config.json", "w") as f:
            json.dump(serialized_sim_settings, f)
        _root.quit()
    _root.protocol("WM_DELETE_WINDOW", on_window_close)


    def open_config_dialog():
        sim_settings = globalinfo.get_sim_settings()
        print(sim_settings)
        simconf = ConfigDialog(_root, sim_settings['varTundev'], sim_settings['varNano'],
                                 sim_settings['varRadio'], sim_settings['varLog'],
                                 sim_settings['varCleartmp'], sim_settings['varTunip'])
        simconf.grab_set()  # disable interaction with other windows
        _root.wait_window(simconf)  # wait for the dialog to be closed

        if simconf.result is not None:
            print(f"Selected settings: {simconf.result}")
            globalinfo.set_sim_setting_element('varTunip', simconf.result[0])
            globalinfo.set_sim_setting_element('varLog', simconf.result[1])
        #print(sim_settings)

    def select_dir():
        dir = filedialog.askdirectory()
        if dir:
            sim_path.set(dir)
            globalinfo.set_sim_setting_element('sim_path', dir)

    def export_runscript(for_sim=False):
        print("Exporting configuration")
        sim_settings = globalinfo.get_sim_settings()
        if builder.node_list_index < 1:
            return
        edg = []
        for e in builder.edges:
            anedge =(e[0],e[1])
            edg.append(list(anedge))
        if edg[0][0] != 0:
            edg = [[x-1, y-1] for x, y in edg]
        # Gettings options
        tunip = sim_settings['varTunip']
        cleanup_tmp = sim_settings['varCleartmp'].get()
        add_tun = sim_settings['varTundev'].get()
        be_logged = sim_settings['varLog']
        if "e" in be_logged or be_logged == '':
            be_logged = []
        else:
            be_logged = be_logged.split(",")
        log_nano = sim_settings['varNano'].get()
        log_radio = sim_settings['varRadio'].get()

        print("Selected directory: ", sim_path.get())
        complete_conf = SimConfGen(builder.node_list_index, edg, sim_path.get(), cleanup_tmp, add_tun, tunip, log_nano, log_radio, be_logged, None)
        new_name = ''
        if for_sim:
            new_name = "run.sh"
            print("Running simulation")
        else:
            new_name = "run_" + str(time.strftime("%d_%H_%M_%S_n")) + str(builder.node_list_index) + ".sh"
        with open(new_name, "w") as f:
            f.write(complete_conf)
            f.close()

    def check_tun_interface(ipv6_addr):
        output = subprocess.check_output(['ip', '-6', 'addr'])
        lines = output.decode().split('\n')
        #print(lines)
        fnd1 = False
        fnd2 = False
        for line in lines:
            #print(line)
            if 'tun' in line:
                fnd1 = True
                break
        for line in lines:
            if ipv6_addr in line:
                fnd2 = True
                break
        return fnd1 and fnd2

    def start_sim():
        if builder.node_list_index < 1:
            return
        sim_settings = globalinfo.get_sim_settings()
        tunip = sim_settings['varTunip']
        if not (check_tun_interface(tunip)) and not sim_settings['varTundev'].get():
            print("Tunnel interface not found")
            tk.messagebox.showwarning(title="Tun not found", message="Tunnel interface not found with IP: " + tunip)
            return
        # check if there is already a simulation running:
        pid = is_sim_running()
        if pid:
            print("Simulation already running with PID: ", pid)
            tk.messagebox.showwarning(title="Simulation already running", message="Simulation already running with PID: " + pid)
            return
        if sim_path.get() == '$(pwd)':
            print("Please select a directory")
            tk.messagebox.showinfo(title="First Things First!", message="Please select simulation executables directory")
            return
        export_runscript(True)
        # Run "run.sh" script
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'bash run.sh; exec bash'])

    def stop_sim():
        process_name = 'wssimserver'
        try:
            pid = subprocess.check_output(['pgrep', process_name])
            pid = pid.decode().strip()
            # Killing wssimserver will kill all the nodes
            # wssimserver runs in userspace, no need to sudo here
            subprocess.run(['kill', '-9', str(pid)])
            # check if any instance of PlotDialog class is created:
            if plotd is not None:
                plotd.destroy()
            globalinfo.reset_connected_nodes()
            # If total nodes value retrived from the running sim and there is not
            # any nodes in canvas:
            if builder.node_list_index < 1:
                globalinfo.reset_total_nodes()
            update_status_progress_bar()
            globalinfo.del_all_timestamp()
        except subprocess.CalledProcessError:
            print("No simulation running")
            tk.messagebox.showwarning(title="No simulation running", message="No simulation running")

    def get_random_mesh_graph():
        Nnodes = int(nSimNodes.get())
        Mdegree = int(maxDegree.get())
        if Nnodes < 1:
            return
        if genmode.get() == "Semi-Managed":
            Alpha = alpha.get()
            Beta = beta.get()
            edges = RndMeshGen(Nnodes, Mdegree, float(Alpha), float(Beta))
        else: # Managed
            lys = int(nlyrnum.get())
            min_npl = int(nminnum.get())
            max_npl = int(nmaxnum.get())
            n_l1 = int(n1stnum.get())
            acc = int(accurate.get())
            if acc:
                if (lys * max_npl)/Nnodes < 1.15 or (Nnodes > 200 and (max_npl/min_npl) > 2):
                    yesno = tk.messagebox.askyesno(title="Warning", message="Finding a solution may be impossible. Continue?")
                    if not yesno:
                        return
            _ , edges = MngRndMeshGen(Nnodes, lys, min_npl, max_npl, n_l1, Mdegree, acc)
            if len(edges) == 0:
                tk.messagebox.showwarning(title="Warning", message="No solution found, adjust parameters and try again")
                return
        #RndMeshPlot(edges, None) # plot the by matplotlib
        builder.draw_graph_from_list(Nnodes, edges) # plot in canvas
        update_status_progress_bar()
        return edges

    def drae_connection_time():
        # !! Copy the dict becuase it is passed by reference, any modification will affect the original dict
        tss = globalinfo.get_all_timestamp().copy()
        if len(tss) != 0:
            #tss = {'ref': 1683561755.1005516, '32345603': 1683561824.0648172, '32345604': 1683561824.0648172, '32345601': 1683561825.2489476, '323456015': 1683561825.2489476, '32345602': 1683561826.385973, '32345606': 1683561884.6940851, '32345607': 1683561889.2430131, '32345605': 1683561891.500941, '32345609': 1683561892.6465416, '323456016': 1683561898.3393831, '323456018': 1683561899.5295408, '323456017': 1683561901.8306823, '32345608': 1683561904.0679207, '323456019': 1683561906.346794, '323456020': 1683561919.9453602, '323456010': 1683561949.4046113, '323456011': 1683561953.9771814, '323456014': 1683561956.2122586, '323456013': 1683561964.1541753, '323456012': 1683561966.4329965}
            ref = tss['ref']
            #print('tss: ', tss)
            tss.pop('ref')
            yy = list(tss.values())
            yy = [y - ref for y in yy]
            xx = list(tss.keys())
            xx = [int(str(x)[6:7]) * 256 + int(str(x)[7:]) for x in xx]
            #print('lbl: ', xx)
            fig, (ax, bx) = plt.subplots(1, 2, figsize=(15, 8))
            colours = plt.get_cmap('Blues')(np.linspace(0.2, 0.9, len(xx)))
            ax.bar(xx, yy, color=colours)
            ax.set_ylabel('Connection time (s)')
            ax.set_xlabel('Node index')
            ax.set_xticks(range(0, int(max(xx)), 3))
            ax.set_yticks(range(0, int(max(yy)), 20))
            ax.set_axisbelow(True)
            ax.yaxis.grid(True, color='#EEEEEE')
            ax.xaxis.grid(False)
            ax.set_title('Connection time for each node')
            
            ncls = builder.get_graph_diameter_from_edges()
            print(ncls)
            X = np.array(yy).reshape(-1, 1)
            # Cluster the data using the optimal number of clusters
            kmeans = KMeans(n_clusters=ncls, init='k-means++', random_state=42, n_init='auto')
            kmeans.fit_predict(X)
            labels = kmeans.predict(X)
            labels = [l+1 for l in labels]
            bx.scatter(labels, X, c=labels)
            bx.set_xticks(range(0, ncls))
            #bx.set_xticklabels([f"cat_{x}" for x in range(0,ncls)])
            bx.grid(True, color='#EEEEEE')
            bx.set_title('Groupe of nodes in each layer')
            bx.set_ylabel('Connection time (s)')
            bx.set_ylabel('Catagory')

            fig.tight_layout()
            plt.show()

    def draw_sim_topology():
        gnodes, gedges = get_sim_nodes()
        # plot the graph:
        if selected_plot_opt.get() == "Static plot":
            if gnodes is None or gedges is None:
                return
            MeshPlot(gedges, None)
        else:
            open_plot_dialog()
    
    def open_plot_dialog():
        global plotd
        if plotd is not None:
            plotd.destroy()
        plotd = PlotDialog(_root)
        #plotd.grab_set()
        #_root.wait_window(plotd)
    
    def update_status_progress_bar():
        all_nodes.config(text=str(globalinfo.get_connected_nodes())+"/"+str(globalinfo.get_total_nodes()))
        progress_bar.config(value=globalinfo.get_connected_nodes(), maximum=globalinfo.get_total_nodes())

    def start_progress_bar():
        if is_sim_running():
            try:
                # This is a hack to check if the plot dialog is exists
                # Since upon closing the plot dialog, plotd is not set to None
                if plotd.state() == "withdrawn":
                    pass
            except:
                get_sim_nodes()
            if globalinfo.get_total_nodes() > 0:
                update_status_progress_bar()
        _root.after(1000, start_progress_bar)

    def update_gen_mode():
        if genmode.get() == "Managed":
            alpha.config(state=tk.DISABLED)
            beta.config(state=tk.DISABLED)
            nlyrnum.config(state=tk.NORMAL)
            n1stnum.config(state=tk.NORMAL)
            nminnum.config(state=tk.NORMAL)
            nmaxnum.config(state=tk.NORMAL)
            accuratelbl.config(state=tk.NORMAL)
        elif genmode.get() == "Semi-Managed":
            alpha.config(state=tk.NORMAL)
            beta.config(state=tk.NORMAL)
            nlyrnum.config(state=tk.DISABLED)
            n1stnum.config(state=tk.DISABLED)
            nminnum.config(state=tk.DISABLED)
            nmaxnum.config(state=tk.DISABLED)
            accuratelbl.config(state=tk.DISABLED)
    
    def _import():
        builder.import_graph()
        update_status_progress_bar()

    def _clear():
        builder.clear()
        update_status_progress_bar()

    def _update():
        builder.reinddex_nodes_and_edges()
        update_status_progress_bar()

    _root.configure(background=_BG)

    # add status bar
    status_frame = tk.Frame(_root, bd=1, relief=tk.SUNKEN, bg=_BG)
    status_frame.pack(side=tk.BOTTOM, padx=5, pady=1, fill=tk.BOTH, expand=0)
    status = Lb(status_frame, text="Ready", anchor=tk.W)
    status.pack(padx=5, pady=0, side=tk.LEFT)
    # Version 0.MONTH+ABCDE...
    version = tk.Label(status_frame, text="v. " + _VERSION, anchor=tk.E, bg=_BG, fg="grey")
    version.pack(padx=5, pady=0, side=tk.RIGHT)
    # Progress bar
    progress_bar = ttk.Progressbar(status_frame, style='blue.Horizontal.TProgressbar',orient=tk.HORIZONTAL, length=120, mode='determinate')
    progress_bar.pack(padx=0, pady=0, side=tk.RIGHT)
    all_nodes = Lb(status_frame, text="?", anchor=tk.E)
    all_nodes.pack(padx=1, pady=0, side=tk.RIGHT)
    elapsed_time = Lb(status_frame, text="?", anchor=tk.E)
    elapsed_time.pack(padx=1, pady=0, side=tk.RIGHT)

    builder = GBuilder(_root,1500,700, _EBG, status)

    # Create the labelframe
    sim_frame = Lf(_root, text="Simulator")
    sim_frame.pack(side=tk.BOTTOM, padx=5, pady=1, fill=tk.BOTH, expand=0)
    simDirlbl = Lb(sim_frame, text="Simulator location:")
    simDirlbl.pack(padx=5, pady=10, side=tk.LEFT)
    select_dir_btn = Bt(sim_frame, command=select_dir, text="Select")
    select_dir_btn.pack(padx=5, pady=10, side=tk.LEFT)
    cfg_btn = Bt(sim_frame,command=open_config_dialog, text="Simulator config")
    cfg_btn.pack(padx=10, pady=10, side=tk.LEFT)
    export_grf_btn = Bt(sim_frame, command=export_runscript, text="Export runscript")
    export_grf_btn.pack(padx=10, pady=10, side=tk.LEFT)
    #varDocker = tk.IntVar()
    #Docker = tk.Checkbutton(sim_frame, text="Export for Docker", variable=varDocker, bg=_BG, fg=_FG)
    #Docker.pack(padx=1, pady=10, side=tk.LEFT)
    sim_path = tk.StringVar(value="$(pwd)")
    selection_frame=tk.Frame(sim_frame, bg=_BG)
    selection_frame.pack(padx=10, pady=0, side=tk.LEFT)
    selected_plot_opt = tk.StringVar(value="Dynamic plot")
    # create 2 radio buttons for RPL plot
    rb1 = Rb(selection_frame, text="Static plot (Matplotlib)", variable=selected_plot_opt, value="Static plot", width=18, anchor=tk.W)
    rb2 = Rb(selection_frame, text="Dynamic plot (Native)", variable=selected_plot_opt, value="Dynamic plot", width=18, anchor=tk.W)
    rb1.pack(pady=0)
    rb2.pack(pady=0)
    plt_rpl = Bt(sim_frame, command=draw_sim_topology, text="RPL plot")
    plt_rpl.pack(padx=10, pady=10, side=tk.LEFT)
    conn_time = Bt(sim_frame, command=drae_connection_time, text="Connection time")
    conn_time.pack(padx=10, pady=10, side=tk.LEFT)
    mk_report = Bt(sim_frame, command=None, text="Create report")
    mk_report.pack(padx=10, pady=10, side=tk.LEFT)
    start_sim_btn = Bt(sim_frame, color='green', command=start_sim, text="Start simulation")
    start_sim_btn.pack(padx=10, pady=10, side=tk.RIGHT)
    stop_sim_btn = Bt(sim_frame, color='red', command=stop_sim, text="Stop simulation")
    stop_sim_btn.pack(padx=10, pady=10, side=tk.RIGHT)


    rnd_gframe = Lf(_root, text="Random Mesh Graph", height=100)
    rnd_gframe.pack(side=tk.LEFT, padx=5, pady=1, fill=tk.BOTH, expand=1)
    generate_btn = Bt(rnd_gframe, command=get_random_mesh_graph, text="Generate")
    generate_btn.pack(padx=5, pady=10, side=tk.RIGHT)
    rnd_sub_frame0 = tk.Frame(rnd_gframe, bg=_BG)
    rnd_sub_frame0.pack(side=tk.LEFT, padx=0, pady=0, expand=0, anchor=tk.W)
    rnd_sub_frame1 = tk.Frame(rnd_gframe, bg=_BG)
    rnd_sub_frame1.pack(side=tk.TOP, padx=0, pady=0, expand=1, anchor=tk.W)
    rnd_sub_frame2 = tk.Frame(rnd_gframe, bg=_BG)
    rnd_sub_frame2.pack(side=tk.TOP, padx=0, pady=0, expand=1, anchor=tk.W)

    genmode = tk.StringVar(value="Managed")
    rbgemode1 = Rb(rnd_sub_frame0, text="Managed", variable=genmode, value="Managed", width=12, anchor=tk.W, command=update_gen_mode)
    rbgemode2 = Rb(rnd_sub_frame0, text="Semi-Managed", variable=genmode, value="Semi-Managed", width=12, anchor=tk.W, command=update_gen_mode)
    rbgemode1.pack(pady=4, side=tk.BOTTOM)
    rbgemode2.pack(pady=4, side=tk.BOTTOM)
    
    nSimNodeslbl = Lb(rnd_sub_frame1, text="Nodes:", width=7)
    nSimNodeslbl.pack(padx=5, pady=0, side=tk.LEFT)
    nSimNodes = En(rnd_sub_frame1, width=5)
    nSimNodes.insert(0, "50")
    nSimNodes.pack(padx=5, pady=0, side=tk.LEFT)
    maxDegreelbl = Lb(rnd_sub_frame1, text="Max(NBR):",  width=8)
    maxDegreelbl.pack(padx=5, pady=0, side=tk.LEFT)
    maxDegree = En(rnd_sub_frame1, width=5)
    maxDegree.insert(0, "5")
    maxDegree.pack(padx=5, pady=0, side=tk.LEFT)
    alphalbl = Lb(rnd_sub_frame1, text="Shape:",  width=8)
    alphalbl.pack(padx=5, pady=0, side=tk.LEFT)
    alpha = En(rnd_sub_frame1, width=5)
    alpha.insert(0, "1")
    alpha.pack(padx=5, pady=0, side=tk.LEFT)
    betalbl = Lb(rnd_sub_frame1, text="Regularity:",  width=8)
    betalbl.pack(padx=5, pady=0, side=tk.LEFT)
    beta = En(rnd_sub_frame1, width=5)
    beta.insert(0, "0.5")
    beta.pack(padx=5, pady=0, side=tk.LEFT)

    nlyrlbl = Lb(rnd_sub_frame2, text="Layers:",  width=7)
    nlyrlbl.pack(padx=5, pady=0, side=tk.LEFT)
    nlyrnum = En(rnd_sub_frame2, width=5)
    nlyrnum.insert(0, "6")
    nlyrnum.pack(padx=5, pady=0, side=tk.LEFT)
    n1stlbl = Lb(rnd_sub_frame2, text="N/L1:",  width=8)
    n1stlbl.pack(padx=5, pady=0, side=tk.LEFT)
    n1stnum = En(rnd_sub_frame2, width=5)
    n1stnum.insert(0, "4")
    n1stnum.pack(padx=5, pady=0, side=tk.LEFT)
    nmaxlbl = Lb(rnd_sub_frame2, text="Max(N/L):",  width=8)
    nmaxlbl.pack(padx=5, pady=0, side=tk.LEFT)
    nmaxnum = En(rnd_sub_frame2, width=5)
    nmaxnum.insert(0, "12")
    nmaxnum.pack(padx=5, pady=0, side=tk.LEFT)
    nminlbl = Lb(rnd_sub_frame2, text="Min(N/L):",  width=8)
    nminlbl.pack(padx=5, pady=0, side=tk.LEFT)
    nminnum = En(rnd_sub_frame2, width=5)
    nminnum.insert(0, "5")
    nminnum.pack(padx=5, pady=0, side=tk.LEFT)
    accurate = tk.IntVar(value=1)
    accuratelbl = Cb(rnd_sub_frame2, text="Accurate",  variable=accurate)
    accuratelbl.pack(padx=5, pady=0, side=tk.LEFT)


    ctl_gframe = Lf(_root, text="Control Graph", height=100)
    ctl_gframe.pack(side=tk.LEFT, padx=5, pady=1, fill=tk.BOTH, expand=1)
    # read image:
    img = tk.PhotoImage(data=GetWisunImg())
    help_btn = Bt(ctl_gframe, command=None, image=img)
    help_btn.pack(padx=10, pady=10, side=tk.RIGHT)
    import_btn = Bt(ctl_gframe, command=_import, text="Import")
    import_btn.pack(padx=10, pady=10, side=tk.LEFT)
    export_btn = Bt(ctl_gframe, command=builder.export, text="Export")
    export_btn.pack(padx=10, pady=10, side=tk.LEFT)
    clear_btn = Bt(ctl_gframe, command=_clear, text="Clear")
    clear_btn.pack(padx=10, pady=10, side=tk.LEFT)
    reindex_btn = Bt(ctl_gframe, command=_update, text="Update")
    reindex_btn.pack(padx=10, pady=10, side=tk.LEFT)
    change_lbl = Bt(ctl_gframe, command=builder.change_labels_to_hex, text="HEX/INT IDs")
    change_lbl.pack(padx=10, pady=10, side=tk.LEFT)

    root_width = max(builder.canvas.winfo_reqwidth(), sim_frame.winfo_reqwidth())
    root_height = builder.canvas.winfo_reqheight() + sim_frame.winfo_reqheight() + rnd_gframe.winfo_reqheight() + ctl_gframe.winfo_reqheight()
    _root.geometry(f"{root_width}x{root_height}")

    # load config file and initialize variables
    sw_config = {}
    globalinfo.init_sim_settings()
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            try:
                sw_config = json.load(f)
            except json.decoder.JSONDecodeError:
                print("Error: config.json is not a valid JSON file")
                os.remove("config.json")
            if sw_config != {}:  # if config file is not empty
                globalinfo.set_sim_settings(sw_config)
                if 'sim_path' in sw_config.keys():
                    if sw_config['sim_path'] != "":
                        sim_path.set(sw_config['sim_path'])

    # If user wants to retrieve the sim info
    retrive_sim_info()
    update_status_progress_bar()
    # Start progress bar
    start_progress_bar()

    update_gen_mode()

    _root.mainloop()

if __name__ == "__main__":
    main()