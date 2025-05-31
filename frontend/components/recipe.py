import dearpygui.dearpygui as dpg



class DPGConnection: 
    def __init__(self, 
            xys: tuple[list[float], list[float]], 
            width: int, 
            parent: int | str = 0, 
        ) -> None:
        xs, ys = xys
        self.xys: list[tuple[float, float]] = list(sum(
            zip(
                zip(xs, ys[:-1]), 
                zip(xs, ys[1:]), 
            ), 
            tuple()
        ))
        self.tag = dpg.draw_polyline(
            [list(i) for i in self.xys], 
            thickness = width, 
            color = (0, 0, 0), 
            parent = parent
        )

class DPGRecipe: 
    def __init__(self, 
            xys: list[tuple[list[float], list[float]]], 
            width: int, 
            parent: int | str = 0, 
        ) -> None: 
        with dpg.draw_node(parent = parent) as self.tag: 
            self.connections = [
                DPGConnection(xy, width, self.tag)
                for xy in xys
            ]