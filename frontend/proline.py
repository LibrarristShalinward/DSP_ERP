from .components import *
from dsp import *
from pathlib import Path
from typing import TypedDict
import dearpygui.dearpygui as dpg
import json

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
    def __init__(self, 
                init_items: set[Item] = set(dsp_items.values()), 
                init_recipes: set[Recipe] = set(dsp_recipes.values())
            ) -> None: 
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
        self.fig_size = self.hg * self.col, self.vg * self.row
        with dpg.window(label = "Prodection Line", tag = self.tag): 
            with dpg.menu_bar(): 
                with dpg.menu(label = "产线"): 
                    for i, tg in enumerate(self.sub_tags): 
                        dpg.add_menu_item(
                            label = tg, 
                            callback = self.show_subfig(i)
                        )
            with dpg.draw_node() as self.base_node: 
                with dpg.draw_node() as self.item_node: 
                    self.dpg_item_buttons = {
                        item: DPGItemButton(
                            item, 
                            ((c + .5) * self.hg, (r + .5) * self.vg), 
                            30., 
                            visible = False
                        )
                        for item, (r, c) in self.item_pos.items()
                    }
        self.focus_items, self.focus_recipes = init_items, init_recipes
        self.show_subfig(0)()
        # 获取当前窗口可显示区域的大小和左上角坐标
    
    def update_fig_position(self, *_, **__): 
        actual_size = dpg.get_item_rect_size(self.tag)
        vgap, hgap = 10., 10.
        assert actual_size[0] > hgap * 2 and actual_size[1] > vgap * 2, "窗口太小"
        scale = min(
            (actual_size[0] - hgap * 2) / self.fig_size[0], 
            (actual_size[1] - vgap * 2) / self.fig_size[1]
        )
        dpg.apply_transform(
            self.base_node, 
            dpg.create_translation_matrix((
                (actual_size[0] - self.fig_size[0] * scale) / 2, 
                vgap
            )) * 
            dpg.create_scale_matrix((scale, scale))
        )
    
    def show_subfig(self, sub_idx: int): 
        def setter(*_, **__): 
            for item, button in self.dpg_item_buttons.items(): 
                button.set_visible(item in self.focus_items and item in self.sub_include_items[sub_idx])
        return setter