import tkinter as tk
from tkinter import filedialog as filedialog
import time

from confgen import configure as SimConfGen
from daggen import random_mesh_graph_gen as RndMeshGen
from daggen import plot_dag as RndMeshPlot
from daggen import get_pos_dag as RndGetPos

############################################################
# Class: Theme
class Bt(tk.Button):
    def __init__ (self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self['bg'] = '#0078d4'
        self['fg'] = 'white'
        self['activebackground'] = '#1092cb'
        self['activeforeground'] = 'white'
        self['relief'] = tk.SOLID

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
        f = open("model.txt","w+")
        f.write("#{0}\n".format(self.node_list_index))
        for e in self.edges:
            f.write("{0}\n".format(e))
        f.write("---")
        f.close()

############################################################
# Main
def main():

    sim_dir = "$(pwd)"
    def select_dir():
        dir = filedialog.askdirectory()
        global sim_dir
        if dir:
            sim_dir = dir
        
    
    def export_config():
        print("Exporting configuration")
        if builder.node_list_index < 1:
            return
        edg = []
        for e in builder.edges:
            anedge =(e[0],e[1])
            edg.append(list(anedge))

        if edg[0][0] != 0:
            edg = [[x-1, y-1] for x, y in edg]

        # get l2 value from sim_frame
        tunip = Tunip.get()
        #print("IP:", tunip)
        cleanup_tmp = varCleartmp.get()
        add_tun = varTundev.get()
        complete_conf = SimConfGen(builder.node_list_index, edg, sim_dir, cleanup_tmp, add_tun, tunip, None)
        # check if file exists
        new_name = "run_" + str(time.strftime("%d_%H_%M_%S_n")) + str(builder.node_list_index) + ".sh"
        with open(new_name, "w") as f:
            f.write(complete_conf)
            f.close()


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

    _root = tk.Tk()
    _root.title("Mesh Graph Builder")
    # '_root.geometry("800x500")
    _root.resizable(1,1)

    _root.configure(background="grey98")
    
    builder = GBuilder(_root,1500,700,"grey98")

    # Create the labelframe
    sim_frame = tk.LabelFrame(_root, text="Simulator", bg="grey98")
    sim_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.BOTH, expand=0)
    loglbl = tk.Label(sim_frame, text="Log:", bg="grey98", fg="#000")
    loglbl.pack(padx=5, pady=10, side=tk.LEFT)
    log = tk.Entry(sim_frame)
    log.insert(0, "e.g: 1,5,6,50")
    log.pack(padx=5, pady=10, side=tk.LEFT)
    varNano = tk.IntVar(value=1)
    Nano = tk.Checkbutton(sim_frame, text="IP stack log", variable=varNano, bg="grey98", fg="#000")
    Nano.pack(padx=1, pady=10, side=tk.LEFT)
    varRadio = tk.IntVar(value=1)
    Radio = tk.Checkbutton(sim_frame, text="MAC/RF log", variable=varRadio, bg="grey98", fg="#000")
    Radio.pack(padx=1, pady=10, side=tk.LEFT)
    varCleartmp = tk.IntVar(value=1)
    Cleartmp = tk.Checkbutton(sim_frame, text="Clear /tmp logs", variable=varCleartmp, bg="grey98", fg="#000")
    Cleartmp.pack(padx=1, pady=10, side=tk.LEFT)
    varTundev = tk.IntVar(value=1)
    Tundev = tk.Checkbutton(sim_frame, text="Create TUN interface", variable=varTundev, bg="grey98", fg="#000")
    Tundev.pack(padx=1, pady=10, side=tk.LEFT)
    Tuniplbl = tk.Label(sim_frame, text="TUN IP:", bg="grey98", fg="#000")
    Tuniplbl.pack(padx=5, pady=10, side=tk.LEFT)
    Tunip = tk.Entry(sim_frame)
    Tunip.insert(0, "fd12:3456::1/64")
    Tunip.pack(padx=5, pady=10, side=tk.LEFT)
    simDirlbl = tk.Label(sim_frame, text="Simulator location:", bg="grey98", fg="#000")
    simDirlbl.pack(padx=5, pady=10, side=tk.LEFT)
    select_dir_btn = Bt(sim_frame, command=select_dir, text="Select")
    select_dir_btn.pack(padx=5, pady=10, side=tk.LEFT)
    export_grf_btn = Bt(sim_frame, command=export_config, text="Export Config")
    export_grf_btn.pack(padx=10, pady=10, side=tk.LEFT)
    varDocker = tk.IntVar()
    Docker = tk.Checkbutton(sim_frame, text="Export for Docker", variable=varDocker, bg="grey98", fg="#000")
    Docker.pack(padx=1, pady=10, side=tk.LEFT)

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
    generate_btn = Bt(rnd_gframe, command=get_random_mesh_graph, text="Random Graph")
    generate_btn.pack(padx=5, pady=10, side=tk.LEFT)

    ctl_gframe = tk.LabelFrame(_root, text="Control Graph", bg="grey98", height=100)
    ctl_gframe.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=1)
    export_btn = Bt(ctl_gframe, command=builder.export, text="Export Graph")
    export_btn.pack(padx=10, pady=10, side=tk.LEFT)
    clear_btn = Bt(ctl_gframe, command=builder.clear, text="Clear")
    clear_btn.pack(padx=10, pady=10, side=tk.LEFT)
    reindex_btn = Bt(ctl_gframe, command=builder.reinddex_nodes_and_edges, text="Update")
    reindex_btn.pack(padx=10, pady=10, side=tk.LEFT)

    root_width = max(builder.canvas.winfo_reqwidth(), sim_frame.winfo_reqwidth())
    root_height = builder.canvas.winfo_reqheight() + sim_frame.winfo_reqheight() + rnd_gframe.winfo_reqheight() + ctl_gframe.winfo_reqheight()
    _root.geometry(f"{root_width}x{root_height}")

    _root.mainloop()

if __name__ == "__main__":
    main()