from dsp import *



def get_basic_recipe(
            item: Item
        ): 
    for _, rcp in sorted(dsp_recipes_basic.items(), reverse = True): 
        if set(rcp.results.keys()) == {item}: 
            return rcp
    assert False, f"无法确定【{item}】的合成路线"

class RecipePolicy: 
    """（除氢、精炼油和高能石墨外）各产物选择配方的策略"""
    DEFAULT = {
        dsp_items["氢"]: dsp_recipes[11120], 
        dsp_items["精炼油"]: dsp_recipes[16], 
        dsp_items["反物质"]: dsp_recipes[74], 
        dsp_items["临界光子"]: dsp_recipes[11208], 
        dsp_items["蓄电器（满）"]: dsp_recipes[12208], 
    }
    def __init__(self, specify: dict[Item, Recipe] = {}) -> None:
        self.special = RecipePolicy.DEFAULT | specify
    
    def __getitem__(self, item: Item): 
        if item in self.special.keys(): 
            return self.special[item]
        else: 
            return get_basic_recipe(item)