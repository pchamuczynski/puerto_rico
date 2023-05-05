#!/usr/bin/python3
from display import *
from board import *
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
        self.game_over_condition = "Unknown"
        self.display = GameScreen(players.keys())
        
    def play(self):
        self.game_over = False
        [player.board(self.board.players[player_name]) for player_name, player in self.players.items()]

        while not self.game_over:
            print(f"++++++++++++++++++++++++ Round {self.rounds_played + 1} +++++++++++++++++++++")
            print(f"Turn order: {self.turn_order}")
            print("City board")
            print(self.board.city)
            for player in self.board.players.values():
                player.selected_role = None
                
            for player_name in self.turn_order:
                # print(f"{player_name} board")
                # print(self.board.players[player_name])
                self.display.draw(self.board)
                self.__play_turn(player_name)
            self.rounds_played += 1
            self.turn_order.append(self.turn_order.pop(0))
            for role in self.board.city.available_roles:
                role.coins += 1
                
            self.board.city.available_roles.extend(self.removed_roles)
            self.removed_roles = []
                    
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f"City: {self.board.city}")
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        
        for player_name in self.players:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(f"{player_name} board")
            print(self.board.players[player_name])
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        scores = {player_name : self.board.players[player_name].score() for player_name in self.players}        
        print(f"Game over after {self.rounds_played} rounds by {self.game_over_condition}")
        print(f"Scores: {scores}")
        input("Press Enter to continue...")
        return (self.rounds_played, scores)
           
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
        self.board.players[player_name].selected_role = role
        self.display.draw(self.board)
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
        skipped = 0
        print(f"Ships:")
        [print(f"{ship.type} ({ship.amount}/{ship.capacity})") for ship in self.board.city.ships]
        while skipped < len(turn_order):
            skipped = 0
            wharf_used = {player_name : False for player_name in turn_order}
            captain_bonus = 1
            for index, player_name in enumerate(turn_order):
                print(f"Shipment for player {player_name}")
                player_board = self.board.players[player_name]
                loaded = []
                available_ships = [ship for ship in self.board.city.ships if ship.amount < ship.capacity]
                print(f"Available ships: {available_ships}")

                for ship in self.board.city.ships:
                    if ship.crop_type != None and ship.amount != ship.capacity:
                        loaded.append(ship.crop_type)
                shipments = []
                
                for crop_type in player_board.crops:
                    if player_board.crops[crop_type] == 0:
                        continue
                    for ship in available_ships:
                        if ship.crop_type == crop_type:
                            shipment = (crop_type, ship.type)
                            print(f"appending shipment: {shipment} ({ship.crop_type} ({ship.amount}/{ship.capacity})) for player {player_name}")
                            shipments.append(shipment)
                        elif ship.crop_type == None and crop_type not in loaded:
                            shipment = (crop_type, ship.type)
                            print(f"appending shipment: {shipment} ({ship.crop_type} ({ship.amount}/{ship.capacity})) for player {player_name}")
                            shipments.append(shipment)
                        elif player_board.active(Building.BuildingType.WHARF) and not wharf_used[player_name]:
                            shipment = (crop_type, Ship.ShipType.WHARF)
                            print(f"appending shipment: {shipment} for player {player_name}")
                            shipments.append(shipment)
                            
                if len(shipments) == 0:
                    print(f"Player {player_name} has no shipments to send")
                    skipped += 1
                    continue
                
                print(f"{player_name} crops to send:")
                [print(f"{crop_type} ({amount})") for crop_type, amount in player_board.crops.items()]
                
                (crop_type, ship_type) = self.players[player_name].select_shipment(shipments)
                print(f"{player_name} selected {crop_type} on Ship {ship_type}")
                amount_to_load = 0
                if ship_type == Ship.ShipType.WHARF:
                    wharf_used[player_name] = True
                    amount_to_load = player_board.crops[crop_type]
                else:
                    ship = [ship for ship in self.board.city.ships if ship.type == ship_type][0]
                    amount_to_load = min(player_board.crops[crop_type], ship.capacity - ship.amount)
                    ship.amount += amount_to_load
                    ship.crop_type = crop_type
                player_board.crops[crop_type] -= amount_to_load
                points = amount_to_load
                if index == 0:
                    points += captain_bonus
                    captain_bonus = 0
                if player_board.active(Building.BuildingType.HARBOR):
                    points += 1
                player_board.export_points += points
                self.board.city.available_points -= points
                print(f"{player_name} sent {amount_to_load} {crop_type} to {ship_type} and got {points} points")
                if self.board.city.available_points <= 0:
                    self.game_over = True
                    self.game_over_condition = "end of export points"
            
        for ship in self.board.city.ships:
            if ship.amount == ship.capacity:
                self.board.city.available_crops[ship.crop_type] += ship.amount
                ship.crop_type = None
                ship.amount = 0
                
        for player_name in turn_order:
            if sum(amount for amount in self.board.players[player_name].crops.values()) != 0:
                crops_to_keep = {crop_type : amount for crop_type, amount in self.board.players[player_name].crops.items() if amount > 0}
                player_board = self.board.players[player_name]
                warehouse_spaces = 0
                if player_board.active(Building.BuildingType.LARGE_WAREHOUSE):
                    warehouse_spaces += 2
                if player_board.active(Building.BuildingType.SMALL_WAREHOUSE):
                    warehouse_spaces += 1
                if len(crops_to_keep) <= warehouse_spaces:
                    continue
                
                crops_in_warehouse = []
                while warehouse_spaces > 0:
                    crop_type = self.players[player_name].select_crop_to_keep_in_warehouse(crops_to_keep)
                    crops_to_keep.pop(crop_type)
                    warehouse_spaces -= 1
                    crops_in_warehouse.append(crop_type)

                crop_on_the_beach = None
                if len(crops_to_keep) == 1:
                    crop_on_the_beach = list(crops_to_keep.keys())[0]
                    
                elif len(crops_to_keep) > 1:
                    crop_on_the_beach = self.players[player_name].select_crop_to_keep_on_the_beach(crops_to_keep)
                if crop_on_the_beach != None:
                    print(f"{player_name} keeps 1 piece of {crop_on_the_beach} on the beach")
                    
                for crop_type, amount in player_board.crops.items():
                    if amount == 0:
                        continue
                    if crop_type == crop_on_the_beach:
                        self.board.city.available_crops[crop_type] += amount - 1
                        player_board.crops[crop_type] = 1
                    elif crop_type not in crops_in_warehouse:
                        self.board.city.available_crops[crop_type] += amount
                        player_board.crops[crop_type] = 0
                        
    def __play_mayor(self, turn_order):
        print(f"{self.board.city.available_workers} workers to distribute among {len(turn_order)} players")
        for index, player_name in enumerate(turn_order):
            player_board = self.board.players[player_name]
            new_workers = int(self.board.city.available_workers / len(turn_order))
            if self.board.city.available_workers % len(turn_order) > index :
                new_workers += 1 
            if index == 0:
                new_workers += 1
                self.board.city.total_workers -= 1
            player_board.workers += new_workers
            print(f"{player_name} gets {new_workers} workers")
            (plantations, buildings) = self.players[player_name].assign_workers(copy(player_board.plantations), copy(player_board.buildings), player_board.workers)
            player_board.plantations = plantations
            player_board.buildings = buildings
                    
        empty_buildings = sum(board.empty_building_worker_spaces() for board in self.board.players.values())
        new_workers = max(len(turn_order), empty_buildings)
        if self.board.city.total_workers < new_workers:
            self.game_over = True
            self.game_over_condition = "end of workers"
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
                crops_to_sell = [crop_type for crop_type in crops_to_sell if crop_type not in market]
                
            bonus = 0
            if index == 0:
                bonus = 1
            if player_board.active(Building.BuildingType.SMALL_MARKET):
                bonus += 1
            if player_board.active(Building.BuildingType.LARGE_MARKET):
                bonus += 2
            
            crops = {crop_type : Crop(crop_type).price + bonus for crop_type in crops_to_sell}
            if len(crops) != 0:
                selected_crop = self.players[player_name].select_crop_to_sale(crops)
                if selected_crop != None:
                    player_board.crops[selected_crop] -= 1
                    market.append(selected_crop)
                    player_board.money += crops[selected_crop]
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
                    self.game_over_condition = "end of building spaces"
                
            
    def __play_prospector(self, turn_order):
        player_name = turn_order[0]
        self.board.players[player_name].money += 1
    
    def __play_settler(self, turn_order):
        for index, player_name in enumerate(turn_order):
            player_board = self.board.players[player_name]
            player = self.players[player_name]
            if player_board.occupied_plantation_spaces() >= 12:
                continue
            plantations_to_choose = copy(self.board.city.available_plantations)
            if (index == 0 or player_board.active(Building.BuildingType.CONSTRUCTION_HUT)) and self.board.city.remaining_quarries > 0:
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
                bonus_selection = [crop for crop in produced_crops if self.board.city.available_crops[crop] > 0]
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

player_names = [
    "Player1",
    "Player2",
    "Player3",
    "Player4",
    "Player5",
    # "Patryk"
]


total_rounds = 0
total_scores = {player_name :0 for player_name in player_names}

def player_gen(player_name):
    if player_name == "Patryk":
        return HumanPlayer(player_name)
    return RandomPlayer()

games_to_play = 1
for i in range(games_to_play):
    players = { player_name : player_gen(player_name) for player_name in player_names}
    (rounds, scores) = Game(players).play()
    total_rounds += rounds
    for player, score in scores.items():
        total_scores[player] += score
    
print(f"Average rounds: {total_rounds / games_to_play}")

[print(f"Average score: {total_scores[player_name] / games_to_play}") for player_name in players.keys()]
