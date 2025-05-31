from .policy.recipe import RecipePolicy
from .policy.petro import PetroPolicy, Policy16
from dsp import *
from functools import cached_property



# region 配置项
class ScalePlanConfig: 
    def __init__(self, 
                recipe_policy: RecipePolicy = RecipePolicy(), 
                petro_policy: PetroPolicy = PetroPolicy(Policy16, Policy16), 
            ) -> None: 
        self.pp = petro_policy
        self.rp = recipe_policy
# endregion


class ScalePlan: 
    """由生产需求计算各产线及中间产物规模"""
    # region 功能函数
    @staticmethod
    def get_pre_product(rcp: Recipe) -> set[Item]: 
        """获取产量与某一产物产量有关的产物

        Args:
            rcp (Recipe): 目标产物

        Returns:
            set[Item]: 相关产物
        """
        return set(rcp.items.keys()) | set(rcp.results.keys())
    
    @staticmethod
    def _item_scale_reliance(
                graph: dict[Item, Recipe], 
                raw: set[Item] = {
                    dsp_items["氢"], 
                    dsp_items["高能石墨"], 
                    dsp_items["精炼油"], 
                }, 
            ) -> dict[Item, set[Item]]: 
        """对于产线graph，获取计算每个产物产量时所需已知产量的产物

        Args:
            graph (dict[Item, Recipe]): 产线图
            raw (set[Item], optional): 视为原料的产物. 默认为{氢, 高能石墨, 精炼油}.

        Returns:
            dict[Item, set[Item]]: {目标产物: {*相关产物, ...}}
        """
        raw_ = raw | {
            item for item, rcp in graph.items() if not rcp.items
        }
        basic_dict = {
            item: {
                it_
                for it_, rcp in graph.items()
                if it_ not in raw_ and 
                item in rcp.items.keys() 
            }
            for item in graph.keys()
        }
        return {
            it: its for it, its in basic_dict.items()
            if its
        }

    # region 中间函数
    def get_all_recipes(self, 
                items: set[Item], 
            ) -> dict[Item, Recipe]: 
        if not items: return dict[Item, Recipe]()
        basic = {
            item: self.rp[item]
            for item in items
        }
        return basic | self.get_all_recipes(
            set.union(*[
                self.get_pre_product(rcp) 
                for rcp in basic.values()
            ]) - items
        )
    # endregion

    # region 中间属性
    @cached_property
    def rcp_graph(self) -> dict[Item, Recipe]: 
        """获取所有涉及的配方"""
        return self.get_all_recipes(set(self.tar.keys()))
    
    @cached_property
    def reliances(self) -> dict[Item, set[Item]]:
        """获取计算各产物的规模时所需已知规模的产物"""
        return self._item_scale_reliance(self.rcp_graph)
    # endregion

    # region 主函数
    def __init__(self, 
                targets: dict[Item, float], 
                config: ScalePlanConfig = ScalePlanConfig(), 
            ) -> None:
        self.rp, self.pp = config.rp, config.pp
        self.tar = targets
    
    @cached_property
    def scales(self): 
        """{产物: 产量(单位/min), ...}, {配方: 生产力(单位为一台基础设施的生产力), ...}"""
        item_scale = self.tar.copy()
        rcp_scale = {
            self.rcp_graph[item]: self.rcp_graph[item].result2prod(item, s)
            for item, s in item_scale.items()
        }
        
        def _get_rcp_scale_from_item(item: Item): 
            if not item in item_scale.keys(): 
                _update_rcp_scale_from_item(item)
            return rcp_scale[self.rcp_graph[item]]

        def _update_rcp_scale_from_item(item: Item): 
            ps: float = sum([
                self.rcp_graph[it].prod2require(
                    item, 
                    _get_rcp_scale_from_item(it)
                ) for it in self.reliances[item]
            ])
            item_scale[item] = ps
            rcp_scale[self.rcp_graph[item]] = self.rcp_graph[item].result2prod(item, ps)
        
        for it in self.reliances.keys():
            _get_rcp_scale_from_item(it)
        pis, prs = self.pp(item_scale)
        
        return item_scale | pis, rcp_scale | prs
    # endregion