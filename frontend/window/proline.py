from ..components import *
from ..layout import *
from .base import AutoResizeWindow
from dsp import *
from pathlib import Path
from typing import Iterable, TypedDict
import dearpygui.dearpygui as dpg
import json

class ScaleCfg(TypedDict): 
    row: int
    col: int
    inner_vcon_cap: int
    inner_hcon_cap: int
    outer_lcon_cap: int
    outer_rcon_cap: int
    outer_tcon_cap: int

class SubWindowCfg(TypedDict): 
    tag: str
    node: list[int]
    recipe: list[int]

class WindowCfg(TypedDict): 
    scale: ScaleCfg
    nodes: list[tuple[int, tuple[int, int]]]
    recipes: list[tuple[int, list[tuple[list[float], list[float]]]]]
    recipe_colors: list[tuple[int, tuple[int, int, int]]]
    layers: list[SubWindowCfg]




class ProdectionLineWindow(AutoResizeWindow): 
    def __init__(self, 
                init_items: set[Item] = set(dsp_items.values()), 
                init_recipes: set[Recipe] = set(dsp_recipes.values())
            ) -> None: 
        with open(
                Path(__file__).parent / "ui.json", 
                "r", 
                encoding = "utf-8"
            ) as f: 
            self.cfg: WindowCfg = json.load(f)
        self.layout = ProLineLayout(
            self.cfg["scale"]["row"], 
            self.cfg["scale"]["col"], 
            (
                self.cfg["scale"]["inner_vcon_cap"], 
                self.cfg["scale"]["inner_hcon_cap"], 
            ), 
            (
                self.cfg["scale"]["outer_lcon_cap"], 
                self.cfg["scale"]["outer_rcon_cap"], 
                self.cfg["scale"]["outer_tcon_cap"]
            )
        )
        self.sub_tags = [
            cfg["tag"] for cfg in self.cfg["layers"]
        ]
        self.sub_include_items = [
            {dsp_items[iid] for iid in cfg["node"]} for cfg in self.cfg["layers"]
        ]
        self.sub_include_rcps = [
            {dsp_recipes[rid] for rid in cfg["recipe"]} for cfg in self.cfg["layers"]
        ]
        self.items = {
            dsp_items[iid]: rc for iid, rc in self.cfg["nodes"]
        }
        rcp_colors = {
            rid: rgb for rid, rgb in self.cfg["recipe_colors"]
        }
        AutoResizeWindow.__init__(self, "Prodection Line", "proline_window")
        with dpg.menu_bar(parent = self.window): 
            with dpg.menu(label = "产线"): 
                for i, tg in enumerate(self.sub_tags): 
                    dpg.add_menu_item(
                        label = tg, 
                        callback = self.show_subfig(i)
                    )
        with  dpg.draw_node(parent = self.base_node) as self.recipe_node: 
            self.dpg_recipes = {
                dsp_recipes[rid]: DPGRecipe(
                    xys, 3, 
                    visible = False, 
                    head_extend = self.layout.cfg.icon_size / 2, 
                    color = rcp_colors[rid]
                ) for rid, xys in self.cfg["recipes"]
            }
        with dpg.draw_node(parent = self.base_node) as self.item_node: 
            self.dpg_item_buttons = {
                item: DPGItemButton(
                    item, 
                    self.layout.icon_pos[r, c], 
                    self.layout.cfg.icon_size, 
                    visible = False
                )
                for item, (r, c) in self.items.items()
            }
        self.focus_items, self.focus_recipes = init_items, init_recipes
        self.show_subfig(0)()
        # 获取当前窗口可显示区域的大小和左上角坐标
    
    @property
    def resize_standard_size(self) -> tuple[float, float]: 
        return self.layout.fig_size
    
    @property
    def button_require_resize(self) -> Iterable[DPGItemButton]: 
        return self.dpg_item_buttons.values()
    
    def show_subfig(self, sub_idx: int): 
        def setter(*_, **__): 
            recipes = self.focus_recipes & self.sub_include_rcps[sub_idx]
            if recipes: 
                itms = self.focus_items & self.sub_include_items[sub_idx] & set.union(*[
                    set(rcp.items.keys()) | set(rcp.results.keys()) for rcp in recipes
                ])
            else: 
                itms = self.focus_items & set()
            for item, button in self.dpg_item_buttons.items(): 
                button.set_visible(item in itms)
            for recipe, cons in self.dpg_recipes.items(): 
                cons.set_visible(recipe in recipes)
        return setter