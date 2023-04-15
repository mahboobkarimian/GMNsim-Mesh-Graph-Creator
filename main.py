import json
import os
import subprocess
import tkinter as tk
from tkinter import filedialog as filedialog
import time
import dbus

from confgen import configure as SimConfGen
from daggen import random_mesh_graph_gen as RndMeshGen
from daggen import plot_dag_as_tree as MeshPlot
from daggen import get_pos_dag as RndGetPos


def get_sim_nodes():
    bus = dbus.SessionBus()
    interface_name = 'com.silabs.Wisun.BorderRouter'
    object_path = '/com/silabs/Wisun/BorderRouter'
    property_name = 'Nodes'
    try:
        proxy_obj = bus.get_object(interface_name, object_path)
    except:
        print("Error: Could not connect to the border router")
        tk.messagebox.showerror(title="D-BUS error", message="Could not connect to the border router. Is simulation running?")
        return None, None
    interface = dbus.Interface(proxy_obj, dbus_interface='org.freedesktop.DBus.Properties')
    try:
        nodes = interface.Get(interface_name, property_name)
    except:
        print("Error: too soon to read nodes property")
        tk.messagebox.showerror(title="D-BUS error", message="too soon to read nodes property")
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
    return gnodes, gedges
############################################################
# Class: Theme
class Bt(tk.Button):
    def __init__ (self, *args, color=None, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self['bg'] = '#0078d4'
        self['fg'] = 'white'
        self['activebackground'] = '#1092cb'
        self['activeforeground'] = 'white'
        self['relief'] = tk.SOLID
        if color == 'green':
            self['bg'] = "#25a004"
            self['activebackground'] = '#3ca858'
        elif color == 'red':
            self['bg'] = "#A0042a"
            self['activebackground'] = '#c3042a'

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
        self.text = canvas_name.create_text(x, y, text=str(index-1), font=("Arial", 15), fill="white")

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

    def __init__(self, root, width, height, bgc):
        self.root = root
        self.canvas = tk.Canvas(root, height=height, widt=width, bg=bgc)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas_width = width
        self.canvas_height = height

        self.canvas.bind("<Button-1>", self.canvas_mouseClick)
        self.canvas.bind("<Button-3>", self.canvas_mouseRightClick)
        # bind double click event:
        self.canvas.bind("<Double-Button-1>", self.canvas_mouseDoubleClick)
        self.canvas.bind("<Control-Button-1>", self.canvas_ctrlMouseRightClick)
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.edges = []
        self.node_list_index = 0

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node

    def draw_line(self, x1, y1, x2, y2):
        line1 = self.canvas.create_line(x1, y1, x2, y2, arrow=None, fill="#222", width=2.5)
        line2 = self.canvas.create_line(x1, y1, x2, y2, arrow=None, fill="#222", width=2)
        self.canvas.tag_lower(line1)
        self.canvas.tag_lower(line2)
        return line1, line2

    def canvas_mouseClick(self, event):
        if self.connecting:
            return
        # 'Check for collision:
        for n in self.nodes:
            if n.is_collide(event.x, event.y):
                return
        # 'Add new node:
        self.node_list_index += 1
        new_node = Node(event.x, event.y, 20, self.node_list_index, self.canvas)
        print(event.x, event.y)
        self.nodes.append(new_node)

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
                print("Moving edges", self.edges)
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
                            n2.text = self.canvas.create_text(n2.x, n2.y, text=str(n2.index-1), font=("Arial", 15), fill="black")
                for e in self.edges:
                    if e[0] > idx:
                        e[0] -= 1
                    if e[1] > idx:
                        e[1] -= 1
                self.node_list_index -= 1
            else:
                tmp_nodes.append(n1)
        self.nodes = tmp_nodes

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
        if len(edges_copy[0]) > 2:
            edges = [[x, y] for x, y, m, l in edges_copy]
        else:
            edges = [[x+1, y+1] for x, y in edges_copy]

        nx_pos = RndGetPos(edges)
        pos = dict(sorted(nx_pos.items()))
        # calculate the scale factor by checking the nuumber of nodes
        # in the most crowded row and column:
        max_vrtcal_nodes = [i[0] for i in list(pos.values())]
        max_hrztal_nodes = [i[1] for i in list(pos.values())]
        mode_v = max(set(max_vrtcal_nodes), key=max_vrtcal_nodes.count)
        mode_h = max(set(max_hrztal_nodes), key=max_hrztal_nodes.count)
        max_v = max_vrtcal_nodes.count(mode_v)
        max_h = max_hrztal_nodes.count(mode_h)
        scale_factor_v = max(max_v/6,2.15)
        scale_factor_h = max(max_h/3,2.2)
        # check also for ratio of the canvas
        if (max_v/max_h) > 4:
            scale_factor_h = scale_factor_h/2
        #print(scale_factor_v, scale_factor_h, "max_v:", max_v, "max_h:", max_h, "mode_v:", mode_v, "mode_h:", mode_h)
        # move coordinates center to canvas top left corner
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        for n in pos:
            x = pos[n][0] * canvas_width/scale_factor_h + canvas_width/2
            y = pos[n][1] * canvas_height/scale_factor_v + canvas_height/2
            new_node = (Node(x, y, 20, n, self.canvas))
            self.nodes.append(new_node)
            self.node_list_index += 1

        for e in edges:
            line1, line2 = self.draw_line(self.nodes[e[0]].x, self.nodes[e[0]].y, self.nodes[e[1]].x, self.nodes[e[1]].y)
            edge = [e[0],e[1], line1, line2]
            self.edges.append(edge)

    def clear(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()

        # 'Reset nodes:
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.node_list_index = 0

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node

    def export(self):
        if self.node_list_index < 1:
            return
        name = "graph_" + str(time.strftime("%d_%H_%M_%S_n")) + str(self.node_list_index) + ".txt"
        f = open(name,"w")
        f.write(f"{self.node_list_index}\n")
        for e in self.edges:
            f.write(f"{e[0]},{e[1]}\n")
        f.write("---")
        f.close()

############################################################
# Class: Config Window
class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, VarTundev, VarNano, VarRadio, VarLog, VarCleartmp, VarTunip):
        super().__init__(parent)

        self.title("Simulation configuration")
        self.configure(bg="grey98")
        self.resizable(False, False)
        self.varTundev = VarTundev
        self.varNano = VarNano
        self.varRadio = VarRadio
        self.varLog = VarLog
        self.varCleartmp = VarCleartmp
        self.varTunip = VarTunip

        sim_frame = tk.Frame(self, bg = "grey98")
        sim_frame.pack(side=tk.TOP, padx=5, anchor=tk.NW)
        loglbl = tk.Label(sim_frame, text="Log:", bg="grey98", fg="#000")
        loglbl.pack(padx=5, pady=10, side=tk.LEFT)
        self.log = tk.Entry(sim_frame)
        self.log.insert(0, VarLog)
        self.log.pack(padx=5, pady=10, side=tk.LEFT)
        
        Nano = tk.Checkbutton(sim_frame, text="IP stack log", variable=self.varNano, bg="grey98", fg="#000")
        Nano.pack(padx=1, pady=10, side=tk.LEFT)
        
        Radio = tk.Checkbutton(sim_frame, text="MAC/RF log", variable=self.varRadio, bg="grey98", fg="#000")
        Radio.pack(padx=1, pady=10, side=tk.LEFT)
        
        Cleartmp = tk.Checkbutton(sim_frame, text="Clear /tmp logs", variable=self.varCleartmp, bg="grey98", fg="#000")
        Cleartmp.pack(padx=1, pady=10, side=tk.LEFT)

        sim_frame1 = tk.Frame(self, bg = "grey98")
        sim_frame1.pack(side=tk.TOP, padx=5, anchor=tk.NW)
        
        Tundev = tk.Checkbutton(sim_frame1, text="Create TUN interface", variable=self.varTundev, bg="grey98", fg="#000")
        Tundev.pack(padx=1, pady=10, side=tk.LEFT)
        Tuniplbl = tk.Label(sim_frame1, text="TUN IP:", bg="grey98", fg="#000")
        Tuniplbl.pack(padx=5, pady=10, side=tk.LEFT)
        self.Tunip = tk.Entry(sim_frame1)
        self.Tunip.insert(0, self.varTunip)
        self.Tunip.pack(padx=5, pady=10, side=tk.LEFT)

        sim_frame2 = tk.Frame(self, bg = "grey98")
        sim_frame2.pack(side=tk.TOP, padx=5, anchor=tk.NW)
        war_label = tk.Label(sim_frame2, text="Tip: Close this window to interact again with main window!", bg="grey98", fg="Red")
        war_label.pack(side=tk.LEFT)


        # create OK and Cancel buttons
        button_frame = tk.Frame(self, bg="grey98")
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

        self.title(" RPL Tree Plot")
        self.configure(bg="grey98")
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
        self.canvas = tk.Canvas(self, width=CVS_W, height=CVS_H, bg="grey98")
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
            self.canvas.create_text(100, 100, text="No nodes yet, wait ...")
        self.after(1000, self.update_graph)

    def draw_graph(self, pos):
        # draw nodes:
        # hint: pos is a dict: {nodeid: (x, y)}
        if pos is None:
            return
        for nodeid, (x, y) in pos.items():
            node, text = self.draw_node(x, y, nodeid[7:])
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
        ncolor = "#fff"
        tcolor = "#000"
        tname = name
        if name == '0':
            tname = "BR"
            ncolor = "green"
            tcolor = "white"
        node = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=ncolor, outline="#222", width=2)
        text = self.canvas.create_text(x, y, text=tname, font=("Arial", 8), fill=tcolor)
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
        max_hz = 1200 # define max W
        max_vt = 600 # define max H
        if pos == None:
            return None, None, None
        # check the max x and y in pos:
        max_pos_x = max(pos.values(), key=lambda x: x[0])[0]
        max_pos_y = max(pos.values(), key=lambda x: x[1])[1]
        scale_x = 1
        scale_y = 1
        if max_pos_x > max_hz or max_pos_y > max_vt:
            scale_x = (max_hz/max_pos_x)/2 # 2 is a margin by experiment
            scale_y = (max_vt/max_pos_y)/2
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
# Main
def main():

    _root = tk.Tk()
    _root.title("GMNsim") # Graph and Mesh Network Simulation Tool
    # '_root.geometry("800x500")
    _root.resizable(1,1)

    global sw_config
    global sim_settings

    def init_sim_settings():
        global sim_settings
        sim_settings = {'varTundev': tk.IntVar(value=1), 'varNano': tk.IntVar(value=1),
                'varRadio': tk.IntVar(value=1), 'varLog': "e.g: 1,5,6,50",
                'varCleartmp': tk.IntVar(value=1), 'varTunip': "fd12:3456::1/64"}

    def on_window_close():
        global sw_config
        with open("config.json", "w") as f:
            json.dump(sw_config, f)
        _root.quit()
    _root.protocol("WM_DELETE_WINDOW", on_window_close)


    def open_config_dialog():
        global sim_settings
        print(sim_settings)
        simconf = ConfigDialog(_root, sim_settings['varTundev'], sim_settings['varNano'],
                                 sim_settings['varRadio'], sim_settings['varLog'],
                                 sim_settings['varCleartmp'], sim_settings['varTunip'])
        simconf.grab_set()  # disable interaction with other windows
        _root.wait_window(simconf)  # wait for the dialog to be closed

        if simconf.result is not None:
            print(f"Selected settings: {simconf.result}")
            sim_settings['varTunip'] = simconf.result[0]
            sim_settings['varLog'] = simconf.result[1]
        # Store the settings in the config dict to be written into file upon exit:
        global sw_config
        serialized_sim_settings = {}
        serialized_sim_settings['varTundev'] = sim_settings['varTundev'].get()
        serialized_sim_settings['varNano'] = sim_settings['varNano'].get()
        serialized_sim_settings['varRadio'] = sim_settings['varRadio'].get()
        serialized_sim_settings['varLog'] = sim_settings['varLog']
        serialized_sim_settings['varCleartmp'] = sim_settings['varCleartmp'].get()
        serialized_sim_settings['varTunip'] = sim_settings['varTunip']
        sw_config['sim_settings'] = serialized_sim_settings
        #print(sim_settings)

    def select_dir():
        global sw_config
        dir = filedialog.askdirectory()
        if dir:
            sim_path.set(dir)
            sw_config['sim_path'] = dir

    def export_runscript(for_sim=False):
        print("Exporting configuration")
        global sim_settings
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

    def start_sim():
        # check if there is already a simulation running:
        process_name = 'wssimserver'
        try:
            pid = subprocess.check_output(['pgrep', process_name])
            pid = pid.decode().strip()
            print("Simulation already running with PID: ", pid)
            tk.messagebox.showwarning(title="Simulation already running", message="Simulation already running with PID: " + pid)
            return
        except subprocess.CalledProcessError:
            print("No simulation running")
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
        except subprocess.CalledProcessError:
            print("No simulation running")
            tk.messagebox.showwarning(title="No simulation running", message="No simulation running")

    def get_random_mesh_graph():
        Nnodes = int(nSimNodes.get())
        if Nnodes < 1:
            return
        Alpha = alpha.get()
        Beta = beta.get()
        Mdegree = maxDegree.get()
        edges = RndMeshGen(Nnodes, int(Mdegree), float(Alpha), float(Beta))
        #RndMeshPlot(edges, None) # plot the by matplotlib
        builder.draw_graph_from_list(Nnodes, edges) # plot in canvas
        return edges

    def draw_sim_topology():
        gnodes, gedges = get_sim_nodes()
        if gnodes is None or gedges is None:
            return
        # plot the graph:
        if selected_plot_opt.get() == "Static plot":
            MeshPlot(gedges, None)
        else:
            open_plot_dialog()
    
    def open_plot_dialog():
        plotd = PlotDialog(_root)
        #plotd.grab_set()
        #_root.wait_window(plotd)

    _root.configure(background="grey98")
    
    builder = GBuilder(_root,1500,700,"grey98")

    # add status bar
    status = tk.Label(_root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="grey98")
    status.pack(side=tk.BOTTOM, fill=tk.X)

    # Create the labelframe
    sim_frame = tk.LabelFrame(_root, text="Simulator", bg="grey98")
    sim_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.BOTH, expand=0)
    simDirlbl = tk.Label(sim_frame, text="Simulator location:", bg="grey98", fg="#000")
    simDirlbl.pack(padx=5, pady=10, side=tk.LEFT)
    select_dir_btn = Bt(sim_frame, command=select_dir, text="Select")
    select_dir_btn.pack(padx=5, pady=10, side=tk.LEFT)
    cfg_btn = Bt(sim_frame,command=open_config_dialog, text="Simulator config")
    cfg_btn.pack(padx=10, pady=10, side=tk.LEFT)
    export_grf_btn = Bt(sim_frame, command=export_runscript, text="Export runscript")
    export_grf_btn.pack(padx=10, pady=10, side=tk.LEFT)
    #varDocker = tk.IntVar()
    #Docker = tk.Checkbutton(sim_frame, text="Export for Docker", variable=varDocker, bg="grey98", fg="#000")
    #Docker.pack(padx=1, pady=10, side=tk.LEFT)
    sim_path = tk.StringVar(value="$(pwd)")
    selection_frame=tk.Frame(sim_frame, bg="grey98")
    selection_frame.pack(padx=10, pady=0, side=tk.LEFT)
    selected_plot_opt = tk.StringVar(value="Dynamic plot")
    # create 2 radio buttons for RPL plot
    rb1 = tk.Radiobutton(selection_frame, text="Static plot", variable=selected_plot_opt, value="Static plot", bg="grey98", width=12, anchor=tk.W)
    rb2 = tk.Radiobutton(selection_frame, text="Dynamic plot", variable=selected_plot_opt, value="Dynamic plot", bg="grey98", width=12, anchor=tk.W)
    rb1.pack(pady=0)
    rb2.pack(pady=0)
    plt_rpl = Bt(sim_frame, command=draw_sim_topology, text="RPL plot")
    plt_rpl.pack(padx=10, pady=10, side=tk.LEFT)
    conn_time = Bt(sim_frame, command=None, text="Connection time")
    conn_time.pack(padx=10, pady=10, side=tk.LEFT)
    mk_report = Bt(sim_frame, command=None, text="Create report")
    mk_report.pack(padx=10, pady=10, side=tk.LEFT)
    start_sim_btn = Bt(sim_frame, color='green', command=start_sim, text="Start simulation")
    start_sim_btn.pack(padx=10, pady=10, side=tk.RIGHT)
    stop_sim_btn = Bt(sim_frame, color='red', command=stop_sim, text="Stop simulation")
    stop_sim_btn.pack(padx=10, pady=10, side=tk.RIGHT)


    rnd_gframe = tk.LabelFrame(_root, text="Random Mesh Graph", bg="grey98", height=100)
    rnd_gframe.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=1)
    nSimNodeslbl = tk.Label(rnd_gframe, text="# Nodes:", bg="grey98", fg="#000")
    nSimNodeslbl.pack(padx=5, pady=10, side=tk.LEFT)
    nSimNodes = tk.Entry(rnd_gframe, width=5)
    nSimNodes.insert(0, "50")
    nSimNodes.pack(padx=5, pady=10, side=tk.LEFT)
    alphalbl = tk.Label(rnd_gframe, text="Shape (branching factor):", bg="grey98", fg="#000")
    alphalbl.pack(padx=5, pady=10, side=tk.LEFT)
    alpha = tk.Entry(rnd_gframe, width=5)
    alpha.insert(0, "1")
    alpha.pack(padx=5, pady=10, side=tk.LEFT)
    betalbl = tk.Label(rnd_gframe, text="Regularity:", bg="grey98", fg="#000")
    betalbl.pack(padx=5, pady=10, side=tk.LEFT)
    beta = tk.Entry(rnd_gframe, width=5)
    beta.insert(0, "0.5")
    beta.pack(padx=5, pady=10, side=tk.LEFT)
    maxDegreelbl = tk.Label(rnd_gframe, text="Max RF neighbors:", bg="grey98", fg="#000")
    maxDegreelbl.pack(padx=5, pady=10, side=tk.LEFT)
    maxDegree = tk.Entry(rnd_gframe, width=5)
    maxDegree.insert(0, "5")
    maxDegree.pack(padx=5, pady=10, side=tk.LEFT)
    generate_btn = Bt(rnd_gframe, command=get_random_mesh_graph, text="Random graph")
    generate_btn.pack(padx=5, pady=10, side=tk.LEFT)

    ctl_gframe = tk.LabelFrame(_root, text="Control Graph", bg="grey98", height=100)
    ctl_gframe.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=1)
    export_btn = Bt(ctl_gframe, command=builder.export, text="Export graph")
    export_btn.pack(padx=10, pady=10, side=tk.LEFT)
    clear_btn = Bt(ctl_gframe, command=builder.clear, text="Clear")
    clear_btn.pack(padx=10, pady=10, side=tk.LEFT)
    reindex_btn = Bt(ctl_gframe, command=builder.reinddex_nodes_and_edges, text="Update")
    reindex_btn.pack(padx=10, pady=10, side=tk.LEFT)
    help_btn = Bt(ctl_gframe, command=None, text="HELP (?)")
    help_btn.pack(padx=10, pady=10, side=tk.LEFT)

    root_width = max(builder.canvas.winfo_reqwidth(), sim_frame.winfo_reqwidth())
    root_height = builder.canvas.winfo_reqheight() + sim_frame.winfo_reqheight() + rnd_gframe.winfo_reqheight() + ctl_gframe.winfo_reqheight()
    _root.geometry(f"{root_width}x{root_height}")

    # load config file and initialize variables
    sw_config = {}
    init_sim_settings()
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            try:
                sw_config = json.load(f)
            except json.decoder.JSONDecodeError:
                print("Error: config.json is not a valid JSON file")
                os.remove("config.json")
            if 'sim_path' in sw_config:
                sim_path.set(sw_config['sim_path'])
            if 'sim_settings' in sw_config:
                sim_settings['varTundev'].set(sw_config['sim_settings']['varTundev'])
                sim_settings['varNano'].set(sw_config['sim_settings']['varNano'])
                sim_settings['varRadio'].set(sw_config['sim_settings']['varRadio'])
                sim_settings['varLog'] = sw_config['sim_settings']['varLog']
                sim_settings['varCleartmp'].set(sw_config['sim_settings']['varCleartmp'])
                sim_settings['varTunip'] = sw_config['sim_settings']['varTunip']
    #print(sw_config) # debug

    _root.mainloop()

if __name__ == "__main__":
    main()