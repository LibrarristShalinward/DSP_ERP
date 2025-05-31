from pathlib import Path
from typing import TypedDict
import dearpygui.dearpygui as dpg
import json
from .components import *
from dsp import *

class ScaleCfg(TypedDict): 
    row: int
    col: int
    col_idx_start: int

class AllocCfg(TypedDict): 
    node: list[tuple[int, tuple[int, int]]]

class SubWindowCfg(TypedDict): 
    tag: str
    scale: ScaleCfg
    alloc: AllocCfg




class ProdectionLineWindow: 
    tag: str = "proline_window"
    def __init__(self, ) -> None: 
        with open(
                Path(__file__).parent / "ui.json", 
                "r", 
                encoding = "utf-8"
            ) as f: 
            self.cfg: list[SubWindowCfg] = json.load(f)
        self.row = max(
            cfg["scale"]["row"] for cfg in self.cfg
        )
        self.col = max(
            cfg["scale"]["col"] for cfg in self.cfg
        )
        self.sub_tags = [
            cfg["tag"] for cfg in self.cfg
        ]
        self.sub_include_items = [
            {dsp_items[iid] for iid, _ in cfg["alloc"]["node"]} for cfg in self.cfg
        ]
        self.items = [
            {
                iid: (r, c + cfg["scale"]["col_idx_start"] + 2) for iid, (r, c) in cfg["alloc"]["node"]
            } for cfg in self.cfg
        ]
        self.item_pos: dict[Item, tuple[int, int]] = {
            dsp_items[iid]: rc for iid, rc in
            set.union(*[
                set(i.items()) for i in self.items
            ])
        }
        self.hg, self.vg = 50., 50.

        with dpg.window(label = "Prodection Line", tag = self.tag): 
            with dpg.menu_bar(): 
                with dpg.menu(label = "产线"): 
                    for i, tg in enumerate(self.sub_tags): 
                        dpg.add_menu_item(
                            label = tg, 
                            callback = self.show_subfig(i)
                        )
            with dpg.draw_node() as self.item_node: 
                self.dpg_item_buttons = {
                    item: DPGItemButton(
                        item, 
                        (c * self.hg, r * self.vg), 
                        30., 
                        visible = False
                    )
                    for item, (r, c) in self.item_pos.items()
                }
        self.show_subfig(0)()
    
    def show_subfig(self, sub_idx: int): 
        def setter(*_, **__): 
            for item, button in self.dpg_item_buttons.items(): 
                button.set_visible(item in self.sub_include_items[sub_idx])
        return setter