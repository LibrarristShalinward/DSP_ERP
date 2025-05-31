"""
对于配方：
- 等离子精炼(#16)【原油x2 -精炼x4.0s-> 氢x1 + 精炼油x2】
解决氢(Hydro-)或精炼油(Refined-)需求不满足上述产物比例的问题: 提供利用以下配方或组合将多余产物转化为需求产物的方案：
- X射线裂解(#58)【精炼油x1 + 氢x2 -精炼x4.0s-> 氢x3 + 高能石墨x1】
- 重整精炼(#121)【精炼油x2 + 氢x1 + 煤矿x1 -精炼x4.0s-> 精炼油x3】
- 氢(#11120)【 -开采x1.0s-> 氢x1】
"""
from abc import ABC, abstractmethod
from dsp import *
from typing import Callable
C = dsp_items["高能石墨"]
CH = dsp_items["精炼油"]
CM = dsp_items["煤矿"]
H = dsp_items["氢"]
PT = dsp_items["原油"]
_16 = dsp_recipes[16]
"""等离子精炼(#16)【原油x2 -精炼x4.0s-> 氢x1 + 精炼油x2】"""
_17 = dsp_recipes[17]
"""高能石墨(#17)【煤矿x2 -冶炼x2.0s-> 高能石墨x1】"""
_58 = dsp_recipes[58]
"""X射线裂解(#58)【精炼油x1 + 氢x2 -精炼x4.0s-> 氢x3 + 高能石墨x1】"""
_121 = dsp_recipes[121]
"""重整精炼(#121)【精炼油x2 + 氢x1 + 煤矿x1 -精炼x4.0s-> 精炼油x3】"""
_11006 = dsp_recipes[11006]
"""煤矿(#11006)【 -开采x1.0s-> 煤矿x1】"""
_11007 = dsp_recipes[11007]
"""原油(#11007)【 -开采x1.0s-> 原油x1】"""



class OverPolicy(ABC): 
    """某种需求过多时的平衡方案"""
    @staticmethod
    def safe_requirement_getter(
                item_scale: dict[Item, float], 
            ) -> Callable[[Item], float]: 
        """ 生成一个安全的需求量获取接口

        Args:
            item_scale (dict[Item, float]): 需求量列表

        Returns:
            Callable[[Item], float]: 需求量获取接口
        """
        def getter(item: Item): 
            """获取特定物品的需求量。若无需求则返回0。

            Args:
                item (Item): 目标物品

            Returns:
                float: 需求量
            """
            if item in item_scale.keys(): 
                return item_scale[item]
            else: 
                return 0.
        return getter
    @staticmethod
    def get_ch_requirements(item_scale: dict[Item, float]) -> tuple[float, float, float, Callable[[Item], float]]: 
        """获取高能石墨/精炼油/氢的合成需求量

        Args:
            item_scale (dict[Item, float]): 物品合成量

        Returns:
            tuple[float, float, float, Callable[[Item], float]]: 高能石墨/精炼油/氢的需求量, 需求量获取器
        """
        sgetter = OverPolicy.safe_requirement_getter(item_scale)
        return (
            sgetter(C), 
            sgetter(CH), 
            sgetter(H), 
            sgetter
        )
    @staticmethod
    @abstractmethod
    def scales(
        item_scale: dict[Item, float], 
    ) -> tuple[dict[Item, float], dict[Recipe, float]]: 
        """平衡后的配方配比

        Args:
            item_scale (dict[Item, float]): 物品需求量

        Returns:
            tuple[dict[Item, float], dict[Recipe, float]]: {产物: 产量(单位/min), ...}, {配方: 生产力(单位为一台基础设施的生产力), ...}
        """

# region 氢需求平衡
class OverHydroPolicy(OverPolicy): 
    """氢需求过多时的平衡方案"""
class Policy58(OverHydroPolicy): 
    """利用X射线裂解将多余精炼油转化为氢"""
    @staticmethod
    def scales(
        item_scale: dict[Item, float], 
    ) -> tuple[dict[Item, float], dict[Recipe, float]]: 
        cS, chS, hS, sgetter = Policy58.get_ch_requirements(item_scale)
        # 等离子精炼(#16) chS16 == 2 * hS16
        # X射线裂解(#58) chS58 = - hS58
        # chS = chS16 + chS58
        # hS = hS16 + hS58
        hS58 = (2. * hS - chS) / 3.

        p58 = _58.result2prod(H, hS58)
        chS16 = chS + _58.prod2require(CH, p58)
        cS17 = cS - hS58
        p16 = _16.result2prod(CH, chS16)
        p17 = _17.result2prod(C, cS17)
        cmS = sgetter(CM) + _17.prod2require(CM, p17)
        ptS = sgetter(PT) + _16.prod2require(PT, p16)
        return {
            CH: chS16, 
            PT: ptS, 
            **({
                C: cS17, 
                CM: cmS, 
            } if cS17 > 0. else {})
        }, {
            _16: p16, 
            _58: p58, 
            _11007: _11007.result2prod(PT, ptS), 
            **({
                _17: p17, 
                _11006: _11006.result2prod(CM, cmS), 
            } if p17 > 0. else {})
        }
# endregion

# region 精炼油需求平衡
class OverRefinedPolicy(OverPolicy): 
    """精炼油需求过多时的平衡方案"""
class Policy16(OverHydroPolicy, OverRefinedPolicy): 
    """将多余精炼油或氢作为废料"""
    @staticmethod
    def scales(
        item_scale: dict[Item, float], 
    ): 
        cS, chS, hS, sgetter = Policy16.get_ch_requirements(item_scale)
        p16 = max(
            _16.result2prod(H, hS), 
            _16.result2prod(CH, chS)
        )
        p17 = _17.result2prod(C, cS)
        cmS = sgetter(CM) + _17.prod2require(CM, p17)
        ptS = sgetter(PT) + _16.prod2require(PT, p16)
        return {
            CM: cmS,
            PT: ptS, 
        }, {
            _16: p16, 
            _17: p17,
            _11006: _11006.result2prod(CM, cmS), 
            _11007: _11007.result2prod(PT, ptS), 
        }
# endregion

# region 总平衡
class PetroPolicy: 
    def __init__(self, 
                hydro_policy: type[OverHydroPolicy], 
                refined_policy: type[OverRefinedPolicy], 
            ) -> None:
        self.hp, self.rp = hydro_policy, refined_policy
    
    def __call__(self, 
        item_scale: dict[Item, float], 
    ) -> tuple[dict[Item, float], dict[Recipe, float]]: 
        _, chS, hS, _ = OverPolicy.get_ch_requirements(item_scale)
        if chS < hS * 2.: 
            return self.hp.scales(item_scale)
        else: 
            return self.rp.scales(item_scale)
# endregion