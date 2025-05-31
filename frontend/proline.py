from .components import *
from .layout import *
from dsp import *
from pathlib import Path
from typing import TypedDict
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
        with dpg.window(label = "Prodection Line", tag = self.tag): 
            with dpg.menu_bar(): 
                with dpg.menu(label = "产线"): 
                    for i, tg in enumerate(self.sub_tags): 
                        dpg.add_menu_item(
                            label = tg, 
                            callback = self.show_subfig(i)
                        )
            with dpg.draw_node() as self.base_node: 
                with  dpg.draw_node() as self.recipe_node: 
                    self.dpg_recipes = {
                        dsp_recipes[rid]: DPGRecipe(
                            xys, 3, 
                            visible = False, 
                            head_extend = self.layout.cfg.icon_size / 2, 
                            color = rcp_colors[rid]
                        ) for rid, xys in self.cfg["recipes"]
                    }
                with dpg.draw_node() as self.item_node: 
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
    
    def update_fig_position(self, *_, **__): 
        actual_size = dpg.get_item_rect_size(self.tag)
        vgap, hgap = 10., 10.
        assert actual_size[0] > hgap * 2 and actual_size[1] > vgap * 2, "窗口太小"
        scale = min(
            (actual_size[0] - hgap * 2) / self.layout.fig_size[0], 
            (actual_size[1] - vgap * 2) / self.layout.fig_size[1]
        )
        dpg.apply_transform(
            self.base_node, 
            dpg.create_translation_matrix((
                (actual_size[0] - self.layout.fig_size[0] * scale) / 2, 
                vgap
            )) * 
            dpg.create_scale_matrix((scale, scale))
        )
        for button in self.dpg_item_buttons.values(): 
            button.set_scale(scale)
    
    def show_subfig(self, sub_idx: int): 
        def setter(*_, **__): 
            recipes = self.focus_recipes & self.sub_include_rcps[sub_idx]
            itms = self.focus_items & self.sub_include_items[sub_idx] & set.union(*[
                set(rcp.items.keys()) | set(rcp.results.keys()) for rcp in recipes
            ])
            for item, button in self.dpg_item_buttons.items(): 
                button.set_visible(item in itms)
            for recipe, cons in self.dpg_recipes.items(): 
                cons.set_visible(recipe in recipes)
        return setter