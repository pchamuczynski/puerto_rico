import pygame
from board import *

PLAYER_BOARD_COLOR = (101, 173, 81)
CITY_BOARD_COLOR = (48, 0, 48)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

CORN = (255, 255, 0)
INDIGO = (10, 38, 219)
SUGAR = (255, 255, 255)
TOBACCO = (39, 130, 36)
COFFEE = (66, 66, 66)
QUARRY = (128, 128, 128)

WORKER = (155, 92, 9)

INDIGO_PLANT_COLOR = (109,124,219)
SUGAR_MILL_COLOR = (237, 237, 237)
TOBACCO_STORAGE_COLOR = (137, 193,135)
COFFEE_ROASTER_COLOR = (66, 66, 66)
CITY_BUILDING_COLOR = (221, 218, 197)

MARGIN = 10

PLANTATIONS = {
    Plantation.PlantationType.CORN: CORN,
    Plantation.PlantationType.INDIGO: INDIGO,
    Plantation.PlantationType.SUGAR: SUGAR,
    Plantation.PlantationType.TOBACCO: TOBACCO,
    Plantation.PlantationType.COFFEE: COFFEE,
    Plantation.PlantationType.QUARRY: QUARRY,
}

class PlayerBoard:
    pass

class CityBoard:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self, city_board):
        pygame.draw.rect(self.screen, CITY_BOARD_COLOR, (self.x, self.y, self.width, self.height))
        
class PlayerBoard:
    def __init__(self, screen, name, x, y, width, height):
        self.screen = screen
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.name_font_size = min(20, self.height // 10)
        self.plantations_width = self.width // 4
        self.buildings_width = self.width // 2
        self.resources_width = self.width // 4
        
    def draw(self, player_board):
        pygame.draw.rect(self.screen, PLAYER_BOARD_COLOR, self.rect)
        pygame.draw.rect(self.screen, BLACK, self.rect, 1)
        font = pygame.font.SysFont('Arial', self.name_font_size)
        if player_board.selected_role != None:
            text = font.render(f"{self.name} : {player_board.selected_role.type}", True, WHITE)
        else:
            text = font.render(f"{self.name}", True, WHITE)
        self.screen.blit(text, (self.x + MARGIN, self.y + MARGIN))
        self.__draw_plantations(player_board.plantations)
        self.__draw_buildings(player_board.buildings)

    def __draw_plantations(self, plantations):
        plantations_height = self.height - MARGIN - self.name_font_size - MARGIN
        plantations_y = self.y + MARGIN + self.name_font_size + MARGIN
        self.plantation_size = (plantations_height - (3 * MARGIN)) // 3
        self.plantation_size = min(self.plantation_size, (self.plantations_width - 5 * MARGIN) // 4)
        self.worker_radius = self.plantation_size // 5
        plantations_offset = (self.plantations_width - 4 * self.plantation_size - 2 * MARGIN) // 3
        for i in range(4):
            x = self.x + MARGIN + i * (self.plantation_size + MARGIN)
            for j in range(3):
                y = plantations_y + j * (self.plantation_size + plantations_offset)
                surf = pygame.Surface((self.plantation_size, self.plantation_size))
                if 4 * j + i < len(plantations):
                    plantation  = plantations[4 * j + i]
                    color = PLANTATIONS[plantation.type]
                    surf.fill(color)
                    if plantation.active:
                        print(f"plantation: {plantation} of player {self.name} is active")
                        worker_center = (3 * (self.plantation_size // 4), 3 * (self.plantation_size // 4))
                        print(f"worker_center: {worker_center}")
                        print(f"worker_radius: {self.worker_radius}")
                        pygame.draw.circle(surf, WORKER, worker_center, self.worker_radius)
                else:
                    surf.fill(WHITE)
                    surf.set_alpha(128)
                    
                self.screen.blit(surf, (x, y))
    
    def __draw_buildings(self, buildings):
        building_height = (self.height - 4 * MARGIN) // 3
        building_width = (self.buildings_width - (5 * MARGIN)) // 4
        building_height = min(building_height, building_width // 2)
        building_width = min(2 * building_height, building_width)
        self.building_size = (building_width, building_height)
        building_offset_x = (self.buildings_width - (4 * building_width) - (2 * MARGIN)) // 3
        building_offset_y = (self.height - 3 * building_height - 2 * MARGIN) // 2
        building_offset_y = min(building_offset_y, 3 * MARGIN)
        text_margin_width = int(building_width * 0.03)
        text_margin_height = int(building_height * 0.03)
        building_name_font_size = building_height//4
        building_name_font = pygame.font.SysFont('Arial', building_name_font_size)
        building_value_font_size = building_height//3
        building_value_font = pygame.font.SysFont('Arial', building_value_font_size, bold=True)
        
        for i in range(4):
            x = self.plantations_width + MARGIN + i * (building_width + building_offset_x)
            for j in range(3):
                y = self.y + MARGIN + j * (building_height + building_offset_y)
                surf = pygame.Surface(self.building_size)
                color = WHITE
                if j * 4 + i < len(buildings):
                    building, workers = list(buildings.items())[j * 4 + i]
                    if workers > 0:
                        print(f"building: {building.type} of player {self.name} has {workers} workers")
                    if building.type == Building.BuildingType.SMALL_INDIGO_PLANT or building.type == Building.BuildingType.LARGE_INDIGO_PLANT:
                        color = INDIGO_PLANT_COLOR
                    elif building.type == Building.BuildingType.SMALL_SUGAR_MILL or building.type == Building.BuildingType.LARGE_SUGAR_MILL:
                        color = SUGAR_MILL_COLOR
                    elif building.type == Building.BuildingType.TOBACCO_STORAGE:
                        color = TOBACCO_STORAGE_COLOR
                    elif building.type == Building.BuildingType.COFFEE_ROASTER:
                        color = COFFEE_ROASTER_COLOR
                    else:
                        color = CITY_BUILDING_COLOR
                        
                    surf.fill(color)
                    for worker in range(workers):
                        worker_center_x = MARGIN + (building_width // 4) * (worker)
                        worker_center_y = 3 * (building_height // 4)
                        print(f"worker_center: {worker_center_x}, {worker_center_y}")
                        pygame.draw.circle(surf, WORKER, (worker_center_x, worker_center_y), self.worker_radius)
                    
                    text_to_write = str(building.type).replace('_', ' ')
                    #print all words but the last in line 1                
                    line_1_text = text_to_write.split(' ')[:-1]
                    line_2_text = text_to_write.split(' ')[-1:]
                    line_1 = building_name_font.render(' '.join(line_1_text), True, BLACK)
                    if line_1.get_width() > building_width - 2 * text_margin_width:
                        #scale down the line
                        line_1 = pygame.transform.scale(line_1, (building_width - 2 * text_margin_width, line_1.get_height()))                        
                    surf.blit(line_1, (text_margin_width, text_margin_height))
                    if len(line_2_text) > 0:
                        line_2 = building_name_font.render(line_2_text[0], True, BLACK)
                        surf.blit(line_2, (text_margin_width, 2 * text_margin_height + building_name_font_size))                                       

                    points_text = building_value_font.render(str(building.points), True, BLACK)
                    surf.blit(points_text, (building_width - points_text.get_width() - text_margin_width, building_height - points_text.get_height() - text_margin_height))
                    
                else:
                    surf.fill(WHITE)
                    surf.set_alpha(128)

                    
                self.screen.blit(surf, (x, y))
        
    
class GameScreen:
    def __init__(self, player_names):
        pygame.init()
        # self.screen = pygame.display.set_mode([0, 0], flags=pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode([1280, 720], flags=pygame.RESIZABLE)
        
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        self.city = CityBoard(self.screen, self.width // 2, 0, self.width // 2, self.height)
        self.player_boards = {}
        for i, name in enumerate(player_names):
            height = self.height // len(player_names)
            y = height * i
            self.player_boards[name] = PlayerBoard(self.screen, name, 0, y, self.width // 2, height)

    def __del__(self):
        pygame.quit()
        
    def draw(self, board):
        self.screen.fill(BLACK)
        self.city.draw(board.city)
        for name, player_board in board.players.items():
            self.player_boards[name].draw(player_board)
        pygame.display.flip()