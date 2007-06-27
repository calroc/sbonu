#!/usr/bin/env python
from Tkinter import *
import bonus
import math


_R = list(range(bonus.DIMENSION))
SCALE = 10
DIM = bonus.DIMENSION * SCALE


class TkBonus:

    def __init__(self, canvas, space):
        self.canvas = canvas
        self.space = space
        self.items = {}

        self.update()

    def update(self):
        for x in _R:
            for y in _R:
                self._updateXY(x, y)

    def _updateXY(self, x, y):
        coords = x, y

        gui = self.items.get(coords)
        things = self.space.get(x, y)

        if gui and not things:
            self._clear(gui, coords)

        elif things and not gui:
            self._render(coords, things)

    def _clear(self, gui_canvas_item, coords):
        self.canvas.delete(gui_canvas_item)
        del self.items[coords]

    def _render(self, coords, location):

        fud = location.food
        if not fud:
            return

        radius = int(round(math.log(fud.amount, 2))) + 1

        x, y = (n * SCALE + SCALE / 2 for n in coords)
        x0 = x - radius
        y0 = y - radius
        x1 = x + radius
        y1 = y + radius

        self.items[coords] = self.canvas.create_oval(
            x0, y0, x1, y1,
            fill="green",
            outline="white",
            )




root = Tk()
root.title('Tk-bonus')
canvas = Canvas(
    root,
    height=DIM,
    width=DIM,
    background='brown',
    )
canvas.pack(expand=True, fill=BOTH)

space = bonus.Space()
space.generate()
space.generate()
space.generate()
print space

tkb = TkBonus(canvas, space)
root.mainloop()
