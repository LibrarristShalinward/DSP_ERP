from . import factory
from enum import Enum
from .items import Item, dsp_items
from typing import Callable



class RecipeType(Enum): 
    SMT = 1
    CHM = 2
    RFN = 3
    MNF = 4
    PTC = 5
    FRC = 8
    RSC = 15
    EXP = -1
    def __str__(self):
        return {
            RecipeType.SMT: "冶炼", 
            RecipeType.CHM: "化工", 
            RecipeType.RFN: "精炼", 
            RecipeType.MNF: "制造", 
            RecipeType.PTC: "粒子对撞", 
            RecipeType.FRC: "分馏", 
            RecipeType.RSC: "研究", 
            RecipeType.EXP: "开采", 
        }[self]
    def __repr__(self):
        return str(self)
    @property
    def facilities(self): 
        return set(
            dsp_items[iid] for iid in {
                RecipeType.SMT: [2302, 2315, 2319], 
                RecipeType.CHM: [2309, 2317], 
                RecipeType.RFN: [2308], 
                RecipeType.MNF: [2303, 2304, 2305, 2318], 
                RecipeType.PTC: [2310], 
                RecipeType.FRC: [2314], 
                RecipeType.RSC: [2901, 2902], 
                RecipeType.EXP: [2301, 2316], 
            }[self]
        )



class Recipe: 
    def __init__(self, 
                id: int, 
                rtype: RecipeType, 
                name: str, 
                items: dict[Item, int], 
                results: dict[Item, int], 
                time: float, 
                icon: str
            ):
        self.id = id
        self.rtype = rtype
        self.name = name
        self.items = items
        self.results = results
        self.time = time
        self.icon = icon
    
    @classmethod
    def from_dict(self, dt: dict[str, str]): 
        return Recipe(
            int(dt["ID"]), 
            RecipeType(int(dt["Type"])), 
            dt["Name"], 
            dict(
                zip(
                    [dsp_items[iid] for iid in dt["Items"]], 
                    dt["ItemCounts"]
                )
            ), 
            dict(
                zip(
                    [dsp_items[iid] for iid in dt["Results"]], 
                    dt["ResultCounts"]
                )
            ), 
            dt["TimeSpend"], 
            dt["IconName"]
        )
    
    @staticmethod
    def amount2str(amt: dict[Item, int]): 
        return " + ".join(
            f"{k.name}x{v}" for k, v in amt.items()
        )
    
    @property
    def edges(self): 
        return set(
            (it, re) for it in self.items.keys() for re in self.results.keys()
        )
    
    def __repr__(self):
        return f"{self.name}(#{self.id})【{self.amount2str(self.items)} -{self.rtype}x{self.time / 60.}s-> {self.amount2str(self.results)}】"
    
    def __hash__(self):
        return self.id
    
    def all_objs_satisfies(self, cri: Callable[[Item], bool]) -> bool: 
        for i in self.items.keys(): 
            if not cri(i): return False
        for i in self.results.keys(): 
            if not cri(i): return False
        return True
    
    def any_objs_satisfies(self, cri: Callable[[Item], bool]) -> bool: 
        return not self.all_objs_satisfies(
            lambda i: not cri(i)
        )
    
    # region 计算函数
    def result2prod(self, 
                result: Item, scale: float
            ) -> float: 
        """根据产物产量计算配方所需生产力

        Args:
            result (Item): 目标产物
            scale (float): 目标产量(单位/min)

        Returns:
            float: 生产力(单位为一台基础设施的生产力)
        """
        if result in self.results.keys(): 
            rs = self.results[result]
            if result in self.items.keys(): 
                rs -= self.items[result]
        else: 
            assert False, f"【{result}】不是合成路线的产物"
        return scale * self.time / rs / 3600.
    
    def prod2require(self, 
                raw: Item, scale: float
            ) -> float: 
        """根据生产力计算配方中原料的需求产量

        Args:
            raw (Item): 目标原料
            scale (float): 生产力(单位为一台基础设施的生产力)

        Returns:
            float: 原料需求产量(单位/min)
        """
        return scale * 3600. * self.items[raw] / self.time
    
    # endregion

dsp_recipes = {
    rc.id: rc for rc in sorted(
        [
            Recipe.from_dict(i) for i in factory["recipes"]
        ], 
        key = lambda it: it.id
    )
}

dsp_recipes_basic = {
    rid: rcp
    for rid, rcp in dsp_recipes.items()
    if
        set(rcp.items.keys()) != set(rcp.results.keys()) and
        (
            rid <= 160 or
            (
                rid >= 11000 and
                rid <= 11031
            )
        )
}