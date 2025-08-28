from ..components import *
from abc import ABC, abstractmethod
from typing import Iterable
import dearpygui.dearpygui as dpg



class AutoResizeWindow(ABC): 
    """可根据窗口自动缩放的内窗口类"""
    def __init__(self, 
                label: str, 
                tag: str, 
            ) -> None:
        self.tag = tag
        with dpg.window(label = label, tag = self.tag) as self.window: 
            self.base_node = dpg.add_draw_node()
    
    @property
    @abstractmethod
    def resize_standard_size(self) -> tuple[float, float]: 
        """获取窗口缩放标准尺寸"""
        pass

    @property
    @abstractmethod
    def button_require_resize(self) -> Iterable[DPGItemButton]: 
        """需要缩放的按钮"""
        pass

    def update_fig_position(self, *_, **__): 
        """更新窗口内容位置"""
        actual_size = dpg.get_item_rect_size(self.tag)
        vgap, hgap = 10., 10.
        assert actual_size[0] > hgap * 2 and actual_size[1] > vgap * 2, "窗口太小"
        standard_size = self.resize_standard_size
        scale = min(
            (actual_size[0] - hgap * 2) / standard_size[0], 
            (actual_size[1] - vgap * 2) / standard_size[1]
        )
        dpg.apply_transform(
            self.base_node, 
            dpg.create_translation_matrix((
                (actual_size[0] - standard_size[0] * scale) / 2, 
                vgap
            )) * 
            dpg.create_scale_matrix((scale, scale))
        )
        for button in self.button_require_resize: 
            button.set_scale(scale)