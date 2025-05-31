import os

import json
dsp_folder = os.path.dirname(__file__)
with open(
        os.path.join(
            dsp_folder, 
            r"resources/FractionateEverything.json"
        ), 
        "r", 
        encoding = "utf-8"
    ) as f: 
    factory = json.load(f)

from .items import Item, ItemType, dsp_items
from .recipe import Recipe, RecipeType, dsp_recipes, dsp_recipes_basic