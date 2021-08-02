import codecs
import json

with open("data/ingredients.json") as initial_file:
    raw_ingredients = json.load(initial_file)

dimensions_dict = dict()
ingredients_dict = dict()

for row in raw_ingredients:
    dimension_name = row["dimension"].lower()
    ingredient_name = row["title"].lower()
    if ingredient_name != "" and dimension_name != "":
        if dimension_name not in dimensions_dict:
            dimensions_dict[dimension_name] = {
                "model": "recipes.measurementunit",
                "pk": len(dimensions_dict) + 1,
                "fields": {
                    "name": dimension_name,
                },
            }
        if ingredient_name not in ingredients_dict:
            ingredients_dict[ingredient_name] = {
                "model": "recipes.ingredient",
                "pk": len(ingredients_dict) + 1,
                "fields": {
                    "name": ingredient_name,
                    "measurement_unit": dimensions_dict[dimension_name]["pk"],
                },
            }

dump_list = list(dimensions_dict.values()) + list(ingredients_dict.values())

with codecs.open(
    "data/ingredients_updated.json", "w", encoding="utf-8"
) as dest:
    json.dump(dump_list, dest, ensure_ascii=False)
