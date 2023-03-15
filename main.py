import tkinter as tk
from tkinter import ttk

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
        self.text = canvas_name.create_text(x, y, text=str(index), font=("Arial", 15), fill="white")

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

class GBuilder:
    # TODO: Add DoubleClick event so the nodes can be moved
    # TODO: Add option the remove edge

    def __init__(self, root, width, height, bgc):
        self.root = root
        self.canvas = tk.Canvas(root, height=height, widt=width, bg=bgc)
        #self.canvas.place(relx = 0.1, rely = 0.1, relheight = 0.8, relwidth = 0.8)
        #self.canvas.pack()
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.bind("<Button-1>", self.canvas_mouseClick)
        self.canvas.bind("<Button-3>", self.canvas_mouseRightClick)
        # bind double click event:
        self.canvas.bind("<Double-Button-1>", self.canvas_mouseDoubleClick)
        self.canvas.bind("<Control-Button-1>", self.canvas_ctrlMouseRightClick)
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.edges = []
        self.node_list_index = 0

        self.btn_frame = tk.Canvas(root, bg="#000")
        self.btn_frame.pack()
        self.rrr = tk.Frame(self.btn_frame)
        self.rrr.pack()

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node

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
        self.nodes.append(new_node)

    def canvas_mouseRightClick(self, event):
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                if self.connecting:
                    self.selectedNode.clicked_up()
                    if n is not self.selectedNode:
                        # 'Connecting two nodes:
                        line1 = self.canvas.create_line(self.selectedNode.x, self.selectedNode.y, n.x, n.y, arrow=tk.LAST, fill="#AAA", width=2.5)
                        line2 = self.canvas.create_line(self.selectedNode.x, self.selectedNode.y, n.x, n.y, arrow=tk.LAST, fill="#000", width=2)
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
                        line1 = self.canvas.create_line(self.nodes[e[0]].x, self.nodes[e[0]].y, self.nodes[e[1]].x, self.nodes[e[1]].y, arrow=tk.LAST, fill="#AAA", width=2.5)
                        line2 = self.canvas.create_line(self.nodes[e[0]].x, self.nodes[e[0]].y, self.nodes[e[1]].x, self.nodes[e[1]].y, arrow=tk.LAST, fill="#000", width=2)
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
                print(tmp_edges, "||||", self.edges)
                self.edges = tmp_edges
                break

    def reinddex_nodes_and_edges(self):
        # 'Reindex nodes:
        tmp_nodes = []
        for n1 in self.nodes:
            if n1.hidden:
                idx = n1.index
                for n2 in self.nodes:
                    if n2.index > idx:
                        n2.index -= 1
                        self.canvas.delete(n2.text)
                        n2.text = self.canvas.create_text(n2.x, n2.y, text=str(n2.index), font=("Arial", 15), fill="black")
                for e in self.edges:
                    if e[0] > idx:
                        e[0] -= 1
                    if e[1] > idx:
                        e[1] -= 1
                self.node_list_index -= 1
            else:
                tmp_nodes.append(n1)
        self.nodes = tmp_nodes

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


def main():
    _root = tk.Tk()
    _root.title("Mesh Graph Builder")
    # '_root.geometry("800x500")
    _root.resizable(1,1)

    _root.configure(background="grey98")
    
    builder = GBuilder(_root,1200,700,"grey98")

    # Create the labelframe
    btn_frame = tk.LabelFrame(_root, text="Export Configuration", bg="grey98", height=100, width=100)
    btn_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=1)

    lt = tk.Label(btn_frame, text="Log output:", bg="grey98", fg="#000")
    lt.pack(padx=5, pady=10, side=tk.LEFT)
    et = tk.Entry(btn_frame)
    et.pack(padx=5, pady=10, side=tk.LEFT)


    varNano = tk.IntVar()
    c = tk.Checkbutton(btn_frame, text="Nanostack", variable=varNano, bg="grey98", fg="#000")
    c.pack(padx=1, pady=10, side=tk.LEFT)

    varRadio = tk.IntVar()
    c = tk.Checkbutton(btn_frame, text="MAC/RF", variable=varRadio, bg="grey98", fg="#000")
    c.pack(padx=1, pady=10, side=tk.LEFT)

    export_btn = tk.Button(btn_frame, command=builder.export, text="Export", bg="#BCCEF8", fg="#000")
    export_btn.pack(padx=10, pady=10, side=tk.LEFT)
    clear_btn = tk.Button(btn_frame, command=builder.clear, text="Clear", bg="#BCCEF8", fg="#000")
    clear_btn.pack(padx=10, pady=10, side=tk.LEFT)
    reindex_btn = tk.Button(btn_frame, command=builder.reinddex_nodes_and_edges, text="Reorder", bg="#BCCEF8", fg="#000")
    reindex_btn.pack(padx=10, pady=10, side=tk.LEFT)


    sim_frame = tk.LabelFrame(_root, text="Random Mesh Generator", bg="grey98", height=100)
    sim_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.BOTH, expand=1)
    l1 = tk.Label(sim_frame, text="# Nodes:", bg="grey98", fg="#000")
    l1.pack(padx=5, pady=10, side=tk.LEFT)
    e1 = tk.Entry(sim_frame)
    e1.pack(padx=5, pady=10, side=tk.LEFT)

    l2 = tk.Label(sim_frame, text="Alpha:", bg="grey98", fg="#000")
    l2.pack(padx=5, pady=10, side=tk.LEFT)
    e2 = tk.Entry(sim_frame)
    e2.pack(padx=5, pady=10, side=tk.LEFT)

    l3 = tk.Label(sim_frame, text="Beta:", bg="grey98", fg="#000")
    l3.pack(padx=5, pady=10, side=tk.LEFT)
    e3 = tk.Entry(sim_frame)
    e3.pack(padx=5, pady=10, side=tk.LEFT)

    l4 = tk.Label(sim_frame, text="Degree:", bg="grey98", fg="#000")
    l4.pack(padx=5, pady=10, side=tk.LEFT)
    e4 = tk.Entry(sim_frame)
    e4.pack(padx=5, pady=10, side=tk.LEFT)

    generate_btn = tk.Button(sim_frame, command=builder.export, text="Generate", bg="#BCCEF8", fg="#000")
    generate_btn.pack(padx=5, pady=10, side=tk.LEFT)

    root_width = max(builder.canvas.winfo_reqwidth(), btn_frame.winfo_reqwidth())
    root_height = builder.canvas.winfo_reqheight() + btn_frame.winfo_reqheight() + sim_frame.winfo_reqheight()
    _root.geometry(f"{root_width}x{root_height}")
    _root.mainloop()


if __name__ == "__main__":
    main()