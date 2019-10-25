import tkinter as tk


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
        self.canvas_name = canvas_name
        self.oval = canvas_name.create_oval(x0, y0, x1, y1,fill="blue")

    def clicked_down(self):
        self.canvas_name.itemconfig(self.oval, fill="green")

    def clicked_up(self):
        self.canvas_name.itemconfig(self.oval, fill="blue")

    def is_collide(self,x,y):
        # print("({0} - {2})^2 + ({1} - {3})^2) < {4}^2".format(x,y,self.x,self.y,self.r))
        return ((x - self.x)**2 + (y - self.y)**2) < (self.r*2)**2

    def is_clicked(self,x,y):
        return ((x - self.x)**2 + (y - self.y)**2) < self.r**2

    def print_node(self):
        print("X: {0} Y: {1} R: {2} Index:{3}".format(self.x, self.y, self.r,self.index))

    def get_index(self): return self.index


class GBuilder:
    # TODO: Add DoubleClick event so the nodes can be moved
    # TODO: Add option the remove edge

    def __init__(self, root, width, height):
        self.root = root
        self.canvas = tk.Canvas(root, height=height, widt=width, bg="#ebe783")
        #self.canvas.place(relx = 0.1, rely = 0.1, relheight = 0.8, relwidth = 0.8)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.canvas_mouseClick)
        self.canvas.bind("<Button-3>", self.canvas_mouseRightClick)
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.edges = []
        self.num_of_nodes = 0

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
        self.num_of_nodes += 1
        new_node = Node(event.x, event.y, 20, self.num_of_nodes, self.canvas)
        self.nodes.append(new_node)

    def canvas_mouseRightClick(self, event):
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                if self.connecting:
                    self.selectedNode.clicked_up()
                    if n is not self.selectedNode:
                        # 'Connecting two nodes:
                        self.canvas.create_line(self.selectedNode.x, self.selectedNode.y, n.x, n.y, arrow=tk.LAST, width=2)
                        edge = (self.selectedNode.index,n.index)
                        self.edges.append(edge)
                    self.connecting = False
                else:
                    n.clicked_down()
                    self.selectedNode = n
                    self.connecting = True

    def clear(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()

        # 'Reset nodes:
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
        self.num_of_nodes = 0

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node

    def export(self):
        if self.num_of_nodes < 1:
            return
        f = open("model.txt","w+")
        f.write("#{0}\n".format(self.num_of_nodes))
        for e in self.edges:
            f.write("{0}\n".format(e))
        f.write("---")
        f.close()


def main():
    _root = tk.Tk()
    _root.title("Graph Builder")
    # '_root.geometry("800x500")
    _root.resizable(0,0)
    _root.configure(background="#f2eb22")
    builder = GBuilder(_root,800,500)

    btn_frame = tk.Frame(_root, bg="#f2eb22")
    btn_frame.pack()

    p1 = tk.PhotoImage(file = "res/button_export.png")
    export_btn = tk.Button(btn_frame, image = p1,command=builder.export)
    export_btn.pack(padx=5, pady=10, side=tk.LEFT)

    p2 = tk.PhotoImage(file="res/button_clear.png")
    clear_btn = tk.Button(btn_frame, image = p2, command=builder.clear)
    clear_btn.pack(padx=5, pady=10, side=tk.LEFT)

    _root.mainloop()


if __name__ == "__main__":
    main()