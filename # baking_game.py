# Import necessary modules (assuming there are organization-specific modules to be imported)
# from org_specific_module import specific_function

class BakingGame:
    def __init__(self):
        self.ingredients = ["flour", "sugar", "butter", "eggs", "milk", "chocolate", "vanilla"]
        self.recipes = {
            ("flour", "sugar", "butter"): "cake",
            ("flour", "sugar", "eggs"): "cookies",
            ("chocolate", "milk"): "hot chocolate",
            ("flour", "milk", "eggs"): "pancakes",
            ("flour", "eggs", "butter"): "bread"
        }
        self.inventory = {item: 0 for item in self.ingredients}
        self.inventory.update({recipe: 0 for recipe in self.recipes.values()})
        self.running = True

    def display_inventory(self):
        print("\nCurrent Inventory:")
        for item, count in self.inventory.items():
            if count > 0:
                print(f"{item}: {count}")

    def display_ingredients(self):
        print("\nAvailable Ingredients:")
        for ingredient in self.ingredients:
            print(ingredient)

    def combine_ingredients(self, selected_ingredients):
        selected_ingredients = tuple(sorted(selected_ingredients, key=str.lower))
        result = self.recipes.get(selected_ingredients)
        if result:
            print(f"Success! You made {result}.")
            for ingredient in selected_ingredients:
                self.inventory[ingredient] -= 1
            self.inventory[result] += 1
        else:
            print("That combination didn't work. Try again.")

    def update_inventory(self):
        for ingredient in self.ingredients:
            self.inventory[ingredient] += 1

    def play(self):
        print("Welcome to the Baking Game!")
        self.update_inventory()  # Update inventory with 1 of each ingredient
        while self.running:
            self.display_inventory()
            self.display_ingredients()
            print("\nEnter the ingredients you want to combine (comma-separated), or 'exit' to quit:")
            user_input = input().strip()
            if user_input.lower() == "exit":
                self.running = False
                print("Thank you for playing!")
            else:
                selected_ingredients = [item.strip() for item in user_input.split(",")]
                if all(item in self.inventory and self.inventory[item] > 0 for item in selected_ingredients):
                    self.combine_ingredients(selected_ingredients)
                else:
                    print("Invalid ingredients or insufficient quantity. Please try again.")

# Example usage:
# game = BakingGame()
# game.play()