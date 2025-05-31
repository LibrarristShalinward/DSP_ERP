from dsp import *
import dearpygui.dearpygui as dpg
from .icon import dsp_icons


class DPGItemButton: 
    def __init__(self, 
                item: Item, 
                pos: tuple[float, float], 
                size: float, 
                rounding: float = .1, 
                parent: int | str = 0, 
                visible: bool = True, 
            ) -> None:
        self.icon = dsp_icons[item]
        dp = .5 - rounding
        with dpg.draw_node(label = "icon_node", parent = parent, show = visible) as self.tag: 
            self.button = dpg.draw_rectangle(
                (-.5, -.5), (.5, .5), 
                color = self.icon.color, fill = self.icon.color, 
                thickness = 0, rounding = rounding * size
            )
            self.texture = dpg.draw_image(self.icon.tag,  (-dp, -dp), (dp, dp))
        dpg.apply_transform(
            self.tag, 
            dpg.create_translation_matrix(pos) * dpg.create_scale_matrix((size, size))
        )
    
    def set_visible(self, visible: bool): 
        dpg.configure_item(self.tag, show = visible)