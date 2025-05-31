import dearpygui.dearpygui as dpg



class DPGConnection: 
    def __init__(self, 
            xys: tuple[list[float], list[float]], 
            width: int, 
            color: tuple[int, int, int], 
            parent: int | str = 0, 
            head_extend: float = 0., 
        ) -> None:
        xs, ys = xys
        ys[0] -= head_extend
        ys[-1] += head_extend
        self.xys: list[tuple[float, float]] = list(sum(
            zip(
                zip(xs, ys[:-1]), 
                zip(xs, ys[1:]), 
            ), 
            tuple()
        ))
        self.tags = [
            dpg.draw_line(
                p1, p2, 
                thickness = width, 
                color = color, 
                parent = parent
            ) for p1, p2 in zip(self.xys[:-1], self.xys[1:])
        ]

class DPGRecipe: 
    def __init__(self, 
            xys: list[tuple[list[float], list[float]]], 
            width: int, 
            color: tuple[int, int, int], 
            parent: int | str = 0, 
            visible: bool = True, 
            head_extend: float = 0., 
        ) -> None: 
        with dpg.draw_node(parent = parent, show = visible) as self.tag: 
            self.connections = [
                DPGConnection(xy, width, color, head_extend = head_extend)
                for xy in xys
            ]
    
    def set_visible(self, visible: bool): 
        dpg.configure_item(self.tag, show = visible)