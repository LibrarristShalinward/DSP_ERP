from dsp import *
from ..components import *
from .base import AutoResizeWindow
from typing import Iterable



class SelectItemWindow(AutoResizeWindow): 
    COL = 20
    def __init__(self, 
                items: list[Item], 
            ) -> None:
        """选择物品窗口

        Args:
            items (list[Item]): 可选择的物品
        """
        self.items = items
        self.ROW = len(self.items) // self.COL + 1
        AutoResizeWindow.__init__(self, "选择物品", "select_item_window")
        self.dpg_item_buttons = {
            item: DPGItemButton(
                item, 
                (
                    (i % self.COL) + .5, 
                    (i // self.COL) + .5
                ), 
                .8, 
                visible = True, 
                parent = self.base_node
            )
            for i, item in enumerate(self.items)
        }
    
    @property
    def resize_standard_size(self) -> tuple[float, float]: 
        return self.COL, self.ROW
    
    @property
    def button_require_resize(self) -> Iterable[DPGItemButton]: 
        return self.dpg_item_buttons.values()
    
    def interaction(self): 
        pass