from enum import Enum
from operator import attrgetter
import random

class Role:
    class RoleType(Enum):
        CAPTAIN = 1
        MAYOR = 2
        TRADER = 3
        BUILDER = 4
        PROSPECTOR = 5
        CRAFTSMAN = 6
        SETTLER = 7
        
        INVALID = 0
        
        def __str__(self) -> str:
            return f"{self.name}"
        
    def __init__(self, type):
        self.type = type
        self.coins = 0
    
    def __str__(self) -> str:
        return f"{self.type} (coins: {self.coins})"
    
    def __repr__(self) -> str:
        return str(self)

class Building:
    class BuildingType(Enum):
        # max discount: 1
        SMALL_INDIGO_PLANT = 1
        SMALL_MARKET = 2
        HACIENDA = 3
        CONSTRUCTION_HUT = 4
        SMALL_SUGAR_MILL = 5
        SMALL_WAREHOUSE = 6
        # max discount: 2
        LARGE_INDIGO_PLANT = 7
        HOSPICE = 8
        OFFICE = 9
        LARGE_MARKET = 10
        LARGE_WAREHOUSE = 11
        LARGE_SUGAR_MILL = 12
        # max discount: 3
        TOBACCO_STORAGE = 13
        FACTORY = 14
        UNIVERSITY = 15
        HARBOR = 16
        COFFEE_ROASTER = 17
        WHARF = 18
        # max discount: 4
        GUILD_HALL = 19
        RESIDENCE = 20
        FORTRESS = 21
        CUSTOMS_HOUSE = 22
        CITY_HALL = 23
        
        INVALID = 0
        
        def __str__(self) -> str:
            return f"{self.name}"
    
    def __init__(self, type, cost, spaces_occupied, max_discount, max_workers, points):
        self.type = type
        self.cost = cost
        self.spaces_occupied = spaces_occupied
        self.max_discount = max_discount
        self.max_workers = max_workers
        self.points = points
        
    def __str__(self) -> str:
        return f"{self.type}(cost: {self.cost}, max_discount: {self.max_discount}, max_workers: {self.max_workers}, points: {self.points})"
    
    def __repr__(self) -> str:
       return str(self) 

class Crop:
    class CropType(Enum):
        CORN = 1
        INDIGO = 2
        SUGAR = 3
        TOBACCO = 4
        COFFEE = 5
        
        def __str__(self) -> str:
            return f"{self.name}"
    
    def __init__(self, type):
        self.type = type
        self.value = self.type.value - 1
        
    def __str__(self) -> str:
        return f"{self.type}(value: {self.value})"
        

class Plantation:
    #define constanst for planation types:
    class PlantationType(Enum):
        CORN = 1
        INDIGO = 2
        SUGAR = 3
        TOBACCO = 4
        COFFEE = 5
        QUARRY = 6
        
        def __str__(self) -> str:
            return f"{self.name}"
        def __repr__(self) -> str:
            return str(self)

    def __init__(self, type):
        self.type = type
        self.active = False
        
    def __str__(self) -> str:
        result = str(self.type)
        if self.active:
            result += " (active)"
        else:
            result += " (inactive)"
        return result
    
    def __repr__(self) -> str:
        return str(self)    

class Ship:
    def __init__(self, capacity):
        self.capacity = capacity
        self.crop_type = None
        self.amount = 0

    def __str__(self):
        return f"Capacity: {self.capacity}, Crop type: {self.crop_type}, Amount: {self.amount}"

    def __repr__(self):
        return str(self)
    
           
class City:
    def __init__(self, number_of_players):
        self.available_roles = self.__init_roles(number_of_players)
        self.ships = self.__init_ships(number_of_players)
        self.available_buildings = self.__init_buildings()
        self.remaining_quarries = 8
        self.plantations_storage = self.__init_plantations_storage()
        self.available_plantations = []
        self.rejected_plantations = []
        self.available_crops = self.__init_crops()
        self.market = []
        self.available_points = self.__init_total_points(number_of_players)
        self.total_workers = self.__init_total_workers(number_of_players)
        self.available_workers = number_of_players
    
    def __str__(self):
        result = ""
        
        result += "Ships:\n"
        for ship in self.ships:
            result += "\t" + str(ship) + "\n"

        result += "Buildings:\n"
        for building_type, available in self.available_buildings.items():
            result += "\t" + str(building_type) + ": " + str(available) + "\n"      

        result += "Plantations storage:\n"
        for plantation_type in set(self.plantations_storage):
            result += "\t" + str(plantation_type) + ": " + str(self.plantations_storage.count(plantation_type)) + "\n"
            
        result += "Available plantations:\n"
        for plantation_type in set(self.available_plantations):
            result += "\t" + str(plantation_type) + ": " + str(self.available_plantations.count(plantation_type)) + "\n"
            
        result += "Rejected plantations:\n"
        for plantation_type in set(self.rejected_plantations):
            result += "\t" + str(plantation_type) + ": " + str(self.rejected_plantations.count(plantation_type)) + "\n"
            
        result += "Crops:\n"
        for crop_type, available in self.available_crops.items():
            result += "\t" + str(crop_type) + ": " + str(available) + "\n"

        result += "Available roles:\n"
        for role in self.available_roles:
            result += "\t" + str(role) + "\n"

        result += "Market: "
        if len(self.market) == 0:
            result += "\tEmpty\n"
        else:
            for crop in self.market:
                result += "\t" + str(crop) + "\n"
        
        result += "Available points: " + str(self.available_points) + "\n"
        result += "Available workers: " + str(self.available_workers) + " + " + str(self.total_workers) + " to come"
        
        return result

    def __init_roles(self, number_of_players):
        roles = [
            Role(Role.RoleType.CAPTAIN), 
            Role(Role.RoleType.MAYOR), 
            Role(Role.RoleType.TRADER), 
            Role(Role.RoleType.BUILDER), 
            Role(Role.RoleType.CRAFTSMAN),
            Role(Role.RoleType.SETTLER),
        ]
        if number_of_players >= 4:
            roles.append(Role(Role.RoleType.PROSPECTOR))
        if number_of_players == 5:
            roles.append(Role(Role.RoleType.PROSPECTOR))
        return roles
    
    def __init_ships(self, number_of_players):
        if number_of_players == 3:
            return [Ship(4), Ship(5), Ship(6)]
        elif number_of_players == 4:
            return [Ship(5), Ship(6), Ship(7)]
        elif number_of_players == 5:
            return [Ship(6), Ship(7), Ship(8)]
        else:
            return []
    
    def __init_buildings(self):
        return {
            Building(Building.BuildingType.SMALL_INDIGO_PLANT, cost=1, spaces_occupied=1, max_discount=1, max_workers=1, points=1): 4,
            Building(Building.BuildingType.SMALL_MARKET, cost=1, spaces_occupied=1, max_discount=1, max_workers=1, points=1): 2,
            Building(Building.BuildingType.HACIENDA, cost=2, spaces_occupied=1, max_discount=1, max_workers=1, points=1): 2,
            Building(Building.BuildingType.CONSTRUCTION_HUT, cost=2, spaces_occupied=1, max_discount=1, max_workers=1, points=1): 2,
            Building(Building.BuildingType.SMALL_SUGAR_MILL, cost=2, spaces_occupied=1, max_discount=1, max_workers=1, points=1): 2,
            Building(Building.BuildingType.SMALL_WAREHOUSE, cost=3, spaces_occupied=1, max_discount=1, max_workers=1, points=1): 2,

            Building(Building.BuildingType.LARGE_INDIGO_PLANT, cost=3, spaces_occupied=1, max_discount=2, max_workers=3, points=2): 2,
            Building(Building.BuildingType.HOSPICE, cost=4, spaces_occupied=1, max_discount=2, max_workers=1, points=2): 2,
            Building(Building.BuildingType.OFFICE, cost=5, spaces_occupied=1, max_discount=2, max_workers=1, points=2): 2,
            Building(Building.BuildingType.LARGE_MARKET, cost=5, spaces_occupied=1, max_discount=2, max_workers=1, points=2): 2,
            Building(Building.BuildingType.LARGE_WAREHOUSE, cost=6, spaces_occupied=1, max_discount=2, max_workers=1, points=2): 2,
            Building(Building.BuildingType.LARGE_SUGAR_MILL, cost=4, spaces_occupied=1, max_discount=2, max_workers=3, points=2): 2,
            
            Building(Building.BuildingType.TOBACCO_STORAGE, cost=5, spaces_occupied=1, max_discount=3, max_workers=3, points=3): 3,
            Building(Building.BuildingType.FACTORY, cost=7, spaces_occupied=1, max_discount=3, max_workers=1, points=3): 2,
            Building(Building.BuildingType.UNIVERSITY, cost=8, spaces_occupied=1, max_discount=3, max_workers=1, points=3): 2,
            Building(Building.BuildingType.HARBOR, cost=8, spaces_occupied=1, max_discount=3, max_workers=1, points=3): 2,
            Building(Building.BuildingType.COFFEE_ROASTER, cost=6, spaces_occupied=1, max_discount=3, max_workers=2, points=3): 3,
            Building(Building.BuildingType.WHARF, cost=9, spaces_occupied=1, max_discount=3, max_workers=1, points=3): 2,
            
            Building(Building.BuildingType.GUILD_HALL, cost=10, spaces_occupied=2, max_discount=4, max_workers=1, points=4): 1,
            Building(Building.BuildingType.RESIDENCE, cost=10, spaces_occupied=2, max_discount=4, max_workers=1, points=4): 1,
            Building(Building.BuildingType.FORTRESS, cost=10, spaces_occupied=2, max_discount=4, max_workers=1, points=4): 1,
            Building(Building.BuildingType.CUSTOMS_HOUSE, cost=10, spaces_occupied=2, max_discount=4, max_workers=1, points=4): 1,
            Building(Building.BuildingType.CITY_HALL, cost=10, spaces_occupied=2, max_discount=4, max_workers=1, points=4): 1,
        }
        
    def __init_plantations_storage(self):
        corn_storage =   [Plantation.PlantationType.CORN for i in range(10)]
        indigo_storage = [Plantation.PlantationType.INDIGO for i in range(12)]
        sugar_storage =  [Plantation.PlantationType.SUGAR for i in range(11)]
        tobacco_storage =[Plantation.PlantationType.TOBACCO for i in range(9)]
        coffee_storage = [Plantation.PlantationType.COFFEE for i in range(8)]
        result = (corn_storage + indigo_storage + sugar_storage + tobacco_storage + coffee_storage)
        return result
        
    def __init_crops(self):
        return {
            Crop(Crop.CropType.CORN): 10,
            Crop(Crop.CropType.INDIGO): 12,
            Crop(Crop.CropType.SUGAR): 11,
            Crop(Crop.CropType.TOBACCO): 9,
            Crop(Crop.CropType.COFFEE): 8,
        }
        
    def __init_total_points(self, number_of_players):
        if number_of_players == 3:
            return 75
        elif number_of_players == 4:
            return 100
        elif number_of_players == 5:
            return 122
        else:
            return 0
        
    def __init_total_workers(self, number_of_players):
        if number_of_players == 3:
            return 55
        elif number_of_players == 4:
            return 75
        elif number_of_players == 5:
            return 95
        else:
            return 0
        
        
class PlayerBoard:
    
    def __init__(self, money, plantation):
        self.money = money
        self.plantations = [plantation]
        self.buildings = {}
        self.workers = 0
        self.crops = {
            Plantation.PlantationType.CORN: 0, 
            Plantation.PlantationType.INDIGO: 0, 
            Plantation.PlantationType.SUGAR: 0, 
            Plantation.PlantationType.TOBACCO: 0, 
            Plantation.PlantationType.COFFEE: 0
        }
        self.export_points = 0
        
    def __str__(self) -> str:
        result = ""
        result += f"Money: {self.money}\n"
        result += "Plantations: \n"
        for plantation in sorted(self.plantations, key=attrgetter('active')):
            result += f"\t{plantation}\n"
        result += "Buildings: \n"
        for building, workers in self.buildings.items():
            result += f"\t{building.type} ({workers}/{building.max_workers})\n"
        result += f"Unemployed workers: {self.unemployed_workers()}\n"
        result += f"Export points: {self.export_points}\n"
        result += "Crops:\n"
        for crop, amount in self.crops.items():
            result += f"\t{crop}: {amount}\n"
        return result
        
    def inactive_plantations(self):
        return sum(1 for plantation in self.plantations if plantation.active == False)
    
    def unemployed_workers(self):
        return self.workers - sum(self.buildings.values()) - sum(1 for plantation in self.plantations if plantation.active)
    
    def occupied_building_spaces(self):
        return sum(building.spaces_occupied for building in self.buildings.keys())
    
    def free_building_spaces(self):
        return 12 - self.occupied_building_spaces()
    
    def occupied_plantation_spaces(self):
        return len(self.plantations)
    
    def empty_building_worker_spaces(self):
        return sum(building.max_workers for building in self.buildings) - sum(self.buildings.values())
    
    def active_quarries(self):
        return sum(1 for plantation in self.plantations if plantation.type == Plantation.PlantationType.QUARRY and plantation.active)
    
    def active(self, building_type):
        for building in self.buildings.keys():
            if building.type == building_type and self.buildings[building] > 0:
                return True
        return False
    
    def clear(self):
        for plantation in self.plantations:
            plantation.active = False 
        for building in self.buildings:
            self.buildings[building] = 0
        

class GameState:
    def __init__(self, player_names):
        self.city = City(len(player_names))
        self.players = self.__init_players(player_names)
        
    def __str__(self) -> str:
        result = f"City:\n{self.city}\n\n"
        result += "Players:\n"
        
        for player_name in self.players.keys():
            result += f"{player_name}:\n{self.players[player_name]}\n"

        return result        
        
    def __init_players(self, player_names):
        if(len(player_names) == 3):
            players = {
                player_names[0]: PlayerBoard(2, Plantation(Plantation.PlantationType.INDIGO)),
                player_names[1]: PlayerBoard(2, Plantation(Plantation.PlantationType.INDIGO)),
                player_names[2]: PlayerBoard(2, Plantation(Plantation.PlantationType.CORN)),
                }
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.CORN)
        elif(len(player_names) == 4):
            players = {
                player_names[0]: PlayerBoard(3, Plantation.PlantationType.INDIGO),
                player_names[1]: PlayerBoard(3, Plantation.PlantationType.INDIGO),
                player_names[2]: PlayerBoard(3, Plantation.PlantationType.CORN),
                player_names[3]: PlayerBoard(3, Plantation.PlantationType.CORN),
            }
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.CORN)
            self.city.plantations_storage.remove(Plantation.PlantationType.CORN)
        elif(len(player_names) == 5):
            players = {
                player_names[0]: PlayerBoard(4, Plantation(Plantation.PlantationType.INDIGO)),
                player_names[1]: PlayerBoard(4, Plantation(Plantation.PlantationType.INDIGO)),
                player_names[2]: PlayerBoard(4, Plantation(Plantation.PlantationType.INDIGO)),
                player_names[3]: PlayerBoard(4, Plantation(Plantation.PlantationType.CORN)),
                player_names[4]: PlayerBoard(4, Plantation(Plantation.PlantationType.CORN)),
            }   
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.INDIGO)
            self.city.plantations_storage.remove(Plantation.PlantationType.CORN)
            self.city.plantations_storage.remove(Plantation.PlantationType.CORN)
        else:
            print("Invalid number of players")
            
        random.shuffle(self.city.plantations_storage)
        return players
                    


