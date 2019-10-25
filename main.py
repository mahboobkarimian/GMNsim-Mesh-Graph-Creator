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

    def __init__(self, root, width, height):
        self.root = root
        self.canvas = tk.Canvas(root, height=height, widt=width, bg="red")
        #self.canvas.place(relx = 0.1, rely = 0.1, relheight = 0.8, relwidth = 0.8)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.canvas_mouseClick)
        self.canvas.bind("<Button-3>", self.canvas_mouseRightClick)
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes = [dummy_node]
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
                        self.canvas.create_line(self.selectedNode.x, self.selectedNode.y, n.x, n.y)
                    self.connecting = False
                else:
                    n.clicked_down()
                    self.selectedNode = n
                    self.connecting = True

    def clear(self):
        self.canvas.delete("all")
        # 'Re-setting nodes:
        dummy_node = Node(0, 0, 0, 0, canvas_name=self.canvas)
        self.nodes.clear()
        self.nodes = [dummy_node]
        self.num_of_nodes = 0

        # 'Connecting Nodes Variables:
        self.connecting = False
        self.selectedNode = dummy_node

    # TODO: Add DoubleClick event so the nodes can be moved

def main():
    _root = tk.Tk()

    builder = GBuilder(_root,700,500)

    export_btn = tk.Button(_root,text="Export Graph")
    export_btn.pack()

    clear_btn = tk.Button(_root, text="Clear", command=builder.clear())
    clear_btn.pack()

    _root.mainloop()


if __name__ == "__main__":
    main()