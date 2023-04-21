from board import GameState, Role, Building, Plantation, Crop
from player import RandomPlayer, HumanPlayer
import random
from copy import copy

class Game:
    def __init__(self, players):
        self.players = players
        self.board = GameState(list(players.keys()))
        self.turn_order = list(players.keys())
        self.rounds_played = 0
        self.removed_roles = []
        self.__refresh_plantations()
        
    def play(self):
        self.game_over = False
        [player.board(self.board.players[player_name]) for player_name, player in self.players.items()]

        while self.rounds_played < 10:
        # while not self.game_over:
            print(f"++++++++++++++++++++++++ Round {self.rounds_played + 1} +++++++++++++++++++++")
            print(f"Turn order: {self.turn_order}")
            print("City board")
            print(self.board.city)
            for player_name in self.turn_order:
                # print(f"{player_name} board")
                # print(self.board.players[player_name])
                self.__play_turn(player_name)
            self.rounds_played += 1
            self.turn_order.append(self.turn_order.pop(0))
            for role in self.board.city.available_roles:
                role.coins += 1
                
            self.board.city.available_roles.extend(self.removed_roles)
            self.removed_roles = []
           
    def __refresh_plantations(self):
        required_plantations = len(self.board.players) + 1
        self.board.city.rejected_plantations.extend(self.board.city.available_plantations)
        if len(self.board.city.plantations_storage) >= required_plantations:
            self.board.city.available_plantations = self.board.city.plantations_storage[:required_plantations]
            self.board.city.plantations_storage = self.board.city.plantations_storage[required_plantations:]
        else:
            self.board.city.available_plantations = self.board.city.plantations_storage
            self.board.city.plantations_storage = self.board.city.rejected_plantations
            random.shuffle(self.board.city.plantations_storage)
            missing_plantations = required_plantations - len(self.board.city.available_plantations)
            self.board.city.available_plantations.extend(self.board.city.plantations_storage[:missing_plantations])
            self.board.city.plantations_storage = self.board.city.plantations_storage[missing_plantations:]

    def __play_turn(self, player_name):       
        available_roles = self.board.city.available_roles
        player = self.players[player_name]
        role = player.select_role(available_roles)
        self.board.players[player_name].money += role.coins
        role.coins = 0
        available_roles.remove(role)
        self.removed_roles.append(role)
        turn_order = self.turn_order[self.turn_order.index(player_name):] + self.turn_order[:self.turn_order.index(player_name)]
        
        if role.type == Role.RoleType.CAPTAIN:
            self.__play_captain(turn_order)
        elif role.type == Role.RoleType.MAYOR:
            self.__play_mayor(turn_order)
        elif role.type == Role.RoleType.TRADER:
            self.__play_trader(turn_order)
        elif role.type == Role.RoleType.BUILDER:
            self.__play_builder(turn_order)
        elif role.type == Role.RoleType.PROSPECTOR:
            self.__play_prospector(turn_order)
        elif role.type == Role.RoleType.SETTLER:
            self.__play_settler(turn_order)
        elif role.type == Role.RoleType.CRAFTSMAN:
            self.__play_craftsman(turn_order)
            
    def __play_captain(self, turn_order):
        pass
    
    def __play_mayor(self, turn_order):
        print(f"{self.board.city.available_workers} workers to distribute among {len(turn_order)} players")
        for index, player_name in enumerate(turn_order):
            player_board = self.board.players[player_name]
            available_workers = int(self.board.city.available_workers / len(turn_order))
            if self.board.city.available_workers % len(turn_order) > index :
                available_workers += 1 
            if index == 0:
                available_workers += 1
                self.board.city.total_workers -= 1
            player_board.workers += available_workers
            (plantations, buildings) = self.players[player_name].assign_workers(copy(player_board.plantations), copy(player_board.buildings), player_board.workers)
            player_board.plantations = plantations
            player_board.buildings = buildings
                    
        empty_buildings = sum(board.empty_building_worker_spaces() for board in self.board.players.values())
        new_workers = max(len(turn_order), empty_buildings)
        if self.board.city.total_workers < new_workers:
            self.game_over = True
        else:
            self.board.city.available_workers = new_workers
            self.board.city.total_workers -= new_workers
        
    
    def __play_trader(self, turn_order): 
        market = self.board.city.market
        for index, player_name in enumerate(turn_order):
            if len(market) == 4:
                break
            player_board = self.board.players[player_name]
            crops_to_sell = [crop_type for crop_type, count in player_board.crops.items() if count > 0]
            if not player_board.active(Building.BuildingType.OFFICE):
                crops_to_sell = [crop_type for crop_type in crops_to_sell if crop_type not in self.board.city.market]
            bonus = 0
            if index == 0:
                bonus = 1
            if player_board.active(Building.BuildingType.SMALL_MARKET):
                bonus += 1
            if player_board.active(Building.BuildingType.LARGE_MARKET):
                bonus += 2
            
            crops = {Crop(crop_type).type : Crop(crop_type).price + bonus for crop_type in crops_to_sell}
            if len(crops) != 0:
                selected_crop = self.players[player_name].select_crop_to_sale(crops)
                if selected_crop != None:
                    player_board.crops[selected_crop] -= 1
                    market.append(selected_crop)
                    player_board.money += Crop(selected_crop).price
        if len(market) == 4:
            for crop_type in market:
                self.board.city.available_crops[crop_type] +=1
            market = []
            
        
    
    def __play_builder(self, turn_order):
        for index, player_name in enumerate(turn_order):
            player_board = self.board.players[player_name]
            
            discount = 0
            if index == 0:
                discount = 1
                
            price_function = lambda building, discount, querries: building.cost - min(querries, building.max_discount) - discount
            active_quarries = player_board.active_quarries()

            temp_buildings = [building for building, count in self.board.city.available_buildings.items() if count > 0]                
            temp_buildings = [building for building in temp_buildings if building.spaces_occupied <= player_board.free_building_spaces()]
            temp_buildings = [building for building in temp_buildings if building not in player_board.buildings]
            temp_buildings = [building for building in temp_buildings if price_function(building, discount, active_quarries) <= player_board.money]
            
            available_buildings = {building : price_function(building, discount, active_quarries) for building in temp_buildings}
            selected_building = self.players[player_name].select_building(available_buildings)
            if selected_building != None:
                self.board.city.available_buildings[selected_building] -= 1
                self.board.players[player_name].money -= available_buildings[selected_building]
                self.board.players[player_name].buildings[selected_building] = 0
                if player_board.active(Building.BuildingType.UNIVERSITY):
                    self.board.players[player_name].buildings[selected_building] = 1
                    self.board.city.total_workers -= 1
                if player_board.free_building_spaces == 0:
                    self.game_over = True
                
            
    def __play_prospector(self, turn_order):
        player_name = turn_order[0]
        self.board.players[player_name].money += 1
    
    def __play_settler(self, turn_order):
        for index, player_name in enumerate(turn_order):
            player_board = self.board.players[player_name]
            player = self.players[player_name]
            if player_board.occupied_plantation_spaces == 12:
                continue
            plantations_to_choose = copy(self.board.city.available_plantations)
            if (index == 0 or player_board.active(Building.BuildingType.CONSTRUCTION_HUT)) and self.board.city.remaining_quarries > 0:
                print("Addding quarry")
                plantations_to_choose.append(Plantation.PlantationType.QUARRY)
            
            if player_board.active(Building.BuildingType.HACIENDA): 
                if player.get_additional_plantation() and len(self.board.city.plantations_storage) > 0:
                    additional_plantation = self.board.city.plantations_storage[0]
                    print(f"Adding additional plantation {additional_plantation}")
                    self.board.city.plantations_storage = self.board.city.plantations_storage[1:]
                    self.board.players[player_name].plantations.append(Plantation(additional_plantation))                
                
            selected_plantation = self.players[player_name].select_plantation(plantations_to_choose)
            if selected_plantation != Plantation.PlantationType.QUARRY:                
                self.board.city.available_plantations.remove(selected_plantation)
            else:
                self.board.city.remaining_quarries -= 1
            plantation = Plantation(selected_plantation)
            if player_board.active(Building.BuildingType.HOSPICE):
                if player.activate_plantation(selected_plantation):
                    plantation.active = True
                    self.board.city.total_workers += 1        
            self.board.players[player_name].plantations.append(plantation)
        self.__refresh_plantations()

    def __play_craftsman(self, turn_order):
        for index, player_name in enumerate(turn_order):
            player_board = self.board.players[player_name]
            player = self.players[player_name]
            produced_crops = []
            for crop_type, volume in player_board.production_potential().items():
                crop_production = min(volume, self.board.city.available_crops[crop_type])
                if crop_type not in player_board.crops:
                    player_board.crops[crop_type] = 0
                if crop_production > 0:
                    print(f"{player_name} produced {crop_production} of {crop_type}")
                    player_board.crops[crop_type] += crop_production
                    self.board.city.available_crops[crop_type] -= crop_production
                    produced_crops.append(crop_type)
            if index == 0:
                print(f"Selecting bonus from produced crops {produced_crops}")
                bonus_selection = [crop for crop in produced_crops if self.board.city.available_crops[crop] > 0]
                print(f"Bonus selection {bonus_selection}")
                if len(bonus_selection) > 0:
                    bonus_crop = player.select_bonus_crop(bonus_selection)
                    print(f"{player_name} selected {bonus_crop} as his bonus crop")
                    if bonus_crop != None:
                        player_board.crops[bonus_crop] += 1
            if player_board.active(Building.BuildingType.FACTORY):
                extra_money = 0
                if len(produced_crops) == 2:
                    extra_money = 1
                if len(produced_crops) == 3:
                    extra_money = 2
                if len(produced_crops) == 4:
                    extra_money = 3
                if len(produced_crops) == 5:
                    extra_money = 5
                player_board.money += extra_money
                

players = {
    "Player1": RandomPlayer(),
    "Player2": RandomPlayer(),
    "Player3": RandomPlayer(),
    "Player4": RandomPlayer(),
    "Patryk": HumanPlayer("Patryk")
    
}

game = Game(players)
game.play()