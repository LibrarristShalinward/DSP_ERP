from . import dsp_folder, factory
from enum import Enum
import os

icon_folder = os.path.join(dsp_folder, r"resources/icon")
assert os.path.exists(icon_folder)



class ItemType(Enum): 
    ORI = 1
    SUB = 2
    PRO = 3
    AMM = 4
    TRS = 5
    FAC = 6
    UTI = 10
    ATT = 8
    FUN = 9
    MAT = 11
    ELS = -1
    def __str__(self):
        return {
            ItemType.ORI: "物品-原料", 
            ItemType.SUB: "物品-单质", 
            ItemType.PRO: "物品-产品", 
            ItemType.AMM: "物品-弹药", 
            ItemType.TRS: "建筑-运输", 
            ItemType.FAC: "建筑-生产", 
            ItemType.UTI: "物品-特殊", 
            ItemType.ATT: "建筑-攻击", 
            ItemType.FUN: "建筑-辅助", 
            ItemType.MAT: "物品-矩阵", 
            ItemType.ELS: "其他", 
        }[self]
    def __repr__(self):
        return str(self)



class Item: 
    def __init__(self, id: int, itype: ItemType, name: str, idx: tuple[int, int], icon: str):
        self.id = id
        self.itype = itype
        self.name = name
        self.idx = idx
        self.icon = icon

    @classmethod
    def from_dict(self, dt: dict[str, str]): 
        gidxn = int(dt["GridIndex"])
        return Item(
            int(dt["ID"]), 
            ItemType(int(dt["Type"])), 
            dt["Name"], 
            (gidxn // 100, gidxn % 100), 
            os.path.join(
                icon_folder, 
                dt["IconName"] + r".png"
            )
        )
    
    def __repr__(self):
        return f"{self.name}(#{self.id}, {self.itype})"
    
    def __hash__(self):
        return self.id

__all_items = sorted(
    [
        Item.from_dict(i) for i in factory["items"]
    ], 
    key = lambda it: it.id
)
dsp_items = {it.id: it for it in __all_items} | {it.name: it for it in __all_items}