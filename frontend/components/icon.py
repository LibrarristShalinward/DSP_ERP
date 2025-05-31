from PIL import Image
from dsp.items import _all_items
from functools import cached_property
import dearpygui.dearpygui as dpg
import numpy as np



class DPGIcon: 
    def __init__(self, icon_path: str) -> None: 
        self.icon_path = icon_path
    
    @cached_property
    def image(self): 
        return np.array(Image.open(self.icon_path))
    
    @cached_property
    def tag(self): 
        self.H, self.W, *_ = self.image.shape
        with dpg.texture_registry(): 
            return dpg.add_static_texture(
                self.W, self.H, 
                (self.image / 255).reshape(-1).tolist(), 
            )
    
    @cached_property
    def color(self) -> tuple[int, int, int]: 
        image_ = self.image.astype(np.float32)
        average = (image_[..., :3] *  image_[..., 3:]).sum((0, 1)) / image_[..., 3].sum()
        return tuple(average.astype(np.uint8).tolist())

dsp_icons = {item: DPGIcon(item.icon) for item in _all_items}