import tkinter as tk


class Node:
    def __init__(self, x, y, r, index):
        self.x = x
        self.y = y
        self.r = r
        self.index = index

    def draw(self,canvas_name,color="blue"):  # center coordinates, radius
        x0 = self.x - self.r
        y0 = self.y - self.r
        x1 = self.x + self.r
        y1 = self.y + self.r
        return canvas_name.create_oval(x0, y0, x1, y1,fill=color)

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
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<Button-3>", self.mouse_right_click)
        dummy_node = Node(0, 0, 0, 0)
        self.nodes = [dummy_node]
        self.num_of_nodes = 0

    def mouse_click(self, event):
        for n in self.nodes:
            if n.is_collide(event.x, event.y):
                return
        self.num_of_nodes += 1
        new_node = Node(event.x, event.y, 20, self.num_of_nodes)
        new_node.draw(self.canvas)
        self.nodes.append(new_node)

    def mouse_right_click(self, event):
        for n in self.nodes:
            if n.is_clicked(event.x, event.y):
                n.print_node()


def main():
    _root = tk.Tk()

    builder = GBuilder(_root,700,500)

    btn = tk.Button(_root,text="Export Graph")
    btn.pack()
    _root.mainloop()


if __name__ == "__main__":
    main()