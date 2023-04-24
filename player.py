from board import Role, Building, Plantation
import random

class AbstractPlayer:        
    def __init__(self):
        self.board = None
    
    def take_turn(self, role, board, bonus):
        if role.type == Role.RoleType.CAPTAIN:
            self.play_captain(board, bonus)
            
    def board(self, board):
        self.board = board
        
class RandomPlayer(AbstractPlayer):
    def __init__(self):
        pass
        
    def select_role(self, roles):
        selected = roles[random.randint(0, len(roles) - 1)]
        print("AI selected " + str(selected) + ".")
        return selected
    
    def play_captain(self, board, bonus):
        print("AI playing captain")
        pass
    
    def select_building(self, buildings):
        if len(buildings) == 0:
            return None
        selected = random.choice(list(buildings.keys()))
        print("\tAI builds " + str(selected.type) + ".")
        return selected
    
    def select_plantation(self, plantations):
        if len(plantations) == 0:
            return None
        selected = random.choice(plantations)
        print("\tAI plants " + str(selected) + ".")
        return selected
    
    def get_additional_plantation(self):
        choice = random.choice([True, False])
        print("\tAI takes additional plantation: " + str(choice))
        return choice
    
    def activate_plantation(self, plantation):
        choice = random.choice([True, False])
        print("\tAI activates " + str(plantation) + ": " + str(choice))
        return choice
    
    def assign_workers(self, plantations, buildings, workers):
        for plantation in plantations:
            plantation.active = False
        for building in buildings:
            buildings[building] = 0

        empty_plantation_spaces = len(plantations)
        empty_building_spaces = sum(building.max_workers - buildings[building] for building in buildings)
        workers_to_assign = min(workers, empty_plantation_spaces + empty_building_spaces)

        #indexes of plantatiosn/building spaces to activate
        activated = random.sample(range(empty_plantation_spaces + empty_building_spaces), workers_to_assign)
        
        serialized_buildings = []
        for building in buildings:
            for i in range(building.max_workers):
                serialized_buildings.append(building)
        
        
        for index in activated:
            if index < empty_plantation_spaces:
                plantations[index].active = True
            else:
                buildings[serialized_buildings[index - empty_plantation_spaces]] += 1
        
        return (plantations, buildings)
        
    def select_bonus_crop(self, bonus):
        choice = random.choice(bonus)
        print("\tAI selects " + str(choice) + " as bonus crop.")
        return choice
    
    def select_crop_to_sale(self, crop_prices):
        #select most expensive crop to sell
        if len(crop_prices) == 0:
            return None
        choice = max(crop_prices, key=lambda crop: crop_prices[crop])
        print(f"\tAI sells {choice} for {crop_prices[choice]} doublons.")
        return choice
        
    def select_shipment(self, crops):
        if len(crops) == 0:
            return None
        choice = random.choice(crops)
        print(f"\tAI sends {choice[0]} to Europe on the ship {choice[1]}.")
        return choice
    
    def select_crop_to_keep_in_warehouse(self, crops):
        if len(crops) == 0:
            return None
        print(f"\tAI selects from {crops} to keep in the warehouse.")
        choice = random.choice(list(crops))
        print(f"\tAI keeps {choice} in the warehouse.")
        return choice

    def select_crop_to_keep_on_the_beach(self, crops):
        if len(crops) == 0:
            return None
        print(f"\tAI selects from {crops} to keep on the beach.")
        choice = random.choice(list(crops))
        print(f"\tAI keeps {choice} on the beach.")
        return choice

  
class HumanPlayer(AbstractPlayer):
    def __init__(self, name):
        self.name = name
        
    def select_role(self, available_roles):
        print(f"Your board: \n{self.board}")
        
        print("Available roles: ")
        [print(str(i) + ": " + str(role)) for i, role in enumerate(available_roles)]
        role = int(input("Select a role: "))
        selected = available_roles[role]
        print("You selected " + str(selected) + ".")
        return selected

    def play_captain(self, board, bonus):
        print("You are playing captain")
        pass
    
    def select_building(self, buildings):
        print("Available buildings: ")
        [print(str(i) + ": " + str(building.type) + " for " + str(price)) for i, (building, price) in enumerate(buildings.items())]
        building = input("Select a building (Enter for None): ")
        if building == '':
            return None
        selected = list(buildings.keys())[int(building)]
        print("You selected " + str(selected.type) + ".")
        return selected
    
    def select_plantation(self, plantations):
        print("Available plantations: ")
        [print(str(i) + ": " + str(plantation)) for i, plantation in enumerate(plantations)]
        plantation = input("Select a plantation (Enter for None): ")
        if plantation == '':
            return None
        selected = plantations[int(plantation)]
        print("You selected " + str(selected) + ".")
        return selected
    
    def get_additional_plantation(self):
        choice = input("Do you want to take an additional plantation? (Y/N): ").capitalize()
        while choice != 'Y' and choice != 'N':
            choice = input("Do you want to take an additional plantation? (Y/N): ")
        return choice == 'Y'
            
    def activate_plantation(self, plantation):
        choice = input("Do you want to activate " + str(plantation) + "? (Y/N): ").capitalize()
        while choice != 'Y' and choice != 'N':
            choice = input("Do you want to activate " + str(plantation) + "? (Y/N): ").capitalize()
        return choice.capitalize() == 'Y'
    
    def assign_workers(self, plantations, buildings, workers):
        print(f"Plantations assignments:")
        [print(f"{plantation}: {plantation.active}") for plantation in plantations]
        print(f"Building assignments:")
        [print(f"{building.type}: {buildings[building]}") for building in buildings]
        
        while True:
            plantations_with_workers = [plantation for plantation in plantations if plantation.active]
            buildings_with_workers = [building for building in buildings if buildings[building] > 0]
            
            populated_tokens = plantations_with_workers + buildings_with_workers
            if len(populated_tokens) == 0:
                break
            
            print(f"Populated tokens:\n")
            for index, token in enumerate(populated_tokens):
                print(f"{index}: {token.type}")
            
            index = input("Select a token to remove a worker from (Enter for None): ")
            if index == "":
                break
            
            if int(index) <= len(plantations_with_workers):
                populated_tokens[int(index)].active = False
            else:
                buildings[populated_tokens[index]] -= 1

        workers_to_distribute = workers - sum(plantation.active for plantation in plantations) - sum(buildings[building] for building in buildings)
        print(f"{workers_to_distribute} workers to distribute")
        
        empty_plantations = [plantation for plantation in plantations if not plantation.active]
        empty_buildings = [building for building in buildings if buildings[building] < building.max_workers]
        while (len(empty_plantations) > 0 or len(empty_buildings) > 0) and workers_to_distribute > 0:
            for index, token in enumerate(empty_plantations + empty_buildings):
                print(f"{index}: {token.type}")
            
            index = input("Select a token to add a worker to: ")
            
            if int(index) < len(empty_plantations):
                empty_plantations[int(index)].active = True
                workers_to_distribute -= 1
            else:
                buildings[empty_buildings[int(index) - len(empty_plantations)]] += 1
                workers_to_distribute -= 1
            empty_plantations = [plantation for plantation in plantations if not plantation.active]
            empty_buildings = [building for building in buildings if buildings[building] < building.max_workers]
        
        
        return (plantations, buildings)
    
    def select_bonus_crop(self, bonus_crops):
        print("Available bonus crops: ")
        [print(str(i) + ": " + str(bonus_crop)) for i, bonus_crop in enumerate(bonus_crops)]
        bonus_crop = input("Select a bonus crop: ")
        if bonus_crop == "":
            return None
        selected = bonus_crops[int(bonus_crop)]
        print("You selected " + str(selected) + ".")
        return selected
    
    def select_crop_to_sale(self, crop_prices):
        print("Available crops to sale: ")
        [print(f"{i}: {crop} for {crop_prices[crop]} doublons") for i, crop in enumerate(crop_prices)]
        crop = input("Select a crop to sale: (press Enter for None)")
        if crop == "":
            return None
        selected = list(crop_prices.keys())[int(crop)]
        print(f"You selected {selected}.")
        return selected
    
    def select_shipment(self, crops):
        print("Available crops to send: ")
        [print(f"{i}: {crop[0]} on the ship {crop[1]}") for i, crop in enumerate(crops)]
        crop = input("Select a crop to send: ")
        selected = crops[int(crop)]
        print(f"You selected {selected[0]} on the ship {selected[1]}.")
        return selected    

    def select_crop_to_keep_in_warehouse(self, crops):
        print("Available crops to keep in warehouse: ")
        [print(f"{i}: {crop_type} ({crop_count})") for i, (crop_type, crop_count) in enumerate(crops.items())] 
        choice = input("Select a crop to keep in warehouse: ")
        selected = list(crops.keys())[int(choice)]
        print(f"You selected {selected}.")
        return selected                

    def select_crop_to_keep_on_the_beach(self, crops):
        if len(crops) == 0:
            return None
        [print(f"{i}: {crop_type} ({crop_count - 1})") for i, (crop_type, crop_count) in enumerate(crops.items())]
        choice = input("Select a crop to keep on the beach: ")
        selected = list(crops.keys())[int(choice)]
        print(f"You selected {selected}.")
        return selected
        
