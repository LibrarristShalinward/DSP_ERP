from pathlib import Path
import json
HOME = Path(__file__).parent.parent

with open(
        str(HOME / r"resources/FractionateEverything.json"), 
        "r", 
        encoding = "utf-8"
    ) as f: 
    factory = json.load(f)

from .items import Item, ItemType, dsp_items
from .recipe import Recipe, RecipeType, dsp_recipes, dsp_recipes_basic