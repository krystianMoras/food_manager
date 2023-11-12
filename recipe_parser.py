from pathlib import Path
import json

class RecipeParser:

    def __init__(self, recipe_directory:str):
        self.recipe_directory = Path(recipe_directory)

    def parse_directory(self):
        recipes = []
        for recipe_file in self.recipe_directory.iterdir():
            recipes.append(self.parse_recipe(recipe_file))

        # write into json
        with open('recipes.json', 'w') as f:
            json.dump(recipes, f, indent=4)

    
    def parse_recipe(self, recipe_file:Path):
        
        recipe = {}

        # title is recipe_file.name without the extension
        recipe['title'] = recipe_file.stem

        # file is markdown
        # there are 3 headers: ingredients, directions, notes
        # ingredients and directions are lists
        # notes is a string

        with open(recipe_file, 'r') as f:
            lines = f.readlines()
            # find the ingredients header
            ingredients_header_index = None
            directions_header_index = None
            notes_header_index = None
            for i, line in enumerate(lines):
                if line.startswith('# Ingredients'):
                    ingredients_header_index = i
                if line.startswith('# Directions'):
                    directions_header_index = i

                if line.startswith('# Notes'):
                    notes_header_index = i

            # ingredients
            ingredients = []

            for line in lines[ingredients_header_index+1:directions_header_index]:
                if line.startswith('- '):
                    ingredients.append(line[2:].strip())

            recipe['ingredients'] = ingredients

            # directions

            directions = []

            for line in lines[directions_header_index+1:notes_header_index]:
                # if line starts with 1. or 2. or 3. etc
                if line[0].isdigit() and line[1] == '.':
                    directions.append(line[2:].strip())

            recipe['directions'] = directions

            # notes is the rest of the file
            recipe['notes'] = ''.join(lines[notes_header_index+1:])

        return recipe


if __name__ == '__main__':
    import yaml

    with open('planner.yaml', 'r') as f:
        # read yaml with polish characters
        config = yaml.safe_load(f)
    print(config)

    recipe_parser = RecipeParser(config['recipe_directory'])
    recipe_parser.parse_directory()