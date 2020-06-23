import datetime, pygame, os, random, math, sys, ctypes
from noise import snoise4
from time import sleep
from worldMap import image_grayscale_to_dict
import time

TILE_SIZE = 16
NB_SNE = 4
NB_UMBRELLA = 1
NB_SEAT = 2
NB_NPC = 55
shiny_probability = 0.02
rain_probability = 10
raining = random.random() < rain_probability / 100
excludedSne = [1, 3, 4]

seed = random.randint(0, sys.maxsize)
zaad = seed
random.seed(zaad)


def get_int(lower_bound, upper_bound, message):
    integer = int(input(message + " (" + str(lower_bound) + "-" + str(upper_bound) + "): "))
    while integer < lower_bound or integer > upper_bound:
        integer = int(input(message + " (" + str(lower_bound) + "-" + str(upper_bound) + "): "))
    return integer


def fill_up_grass(layer, decoration_rate, offset_x, offset_y):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if not (x, y) in layer.keys():
                layer[(x, y)] = random_grass(decoration_rate, x, y, offset_x, offset_y)


def random_grass(decoration_rate, x, y, offset_x, offset_y):
    octaves = 1
    freq = 7
    sne_probability = snoise4((x + offset_x) / freq, (y + offset_y) / freq, octaves) + 0.5

    if sne_probability > (decoration_rate / 100):
        grass_type = random.randint(0, 3)
        return "g_" + str(grass_type)
    elif can_spawn_pokemon(0.001, "Diglet"):
        ground_Tiles["Diglet"] = True
        return "diglet_2" if random.random() < shiny_probability else "diglet_1"
    else:
        return choose_sne_type(excludedSne)


def can_spawn_pokemon(spawn_probability, pokemon):
    return random.random() < spawn_probability and not ground_Tiles[pokemon]


def choose_sne_type(excluded_sne):
    sne_type = random.randint(0, NB_SNE)
    while sne_type in excluded_sne:
        sne_type = random.randint(0, NB_SNE)

    # Turn 80 percent of the flowers into tall grass
    if sne_type == 2 and random.random() < 0.8: sne_type = 0
    # Turn 0.5 percent of the tall grass into tall grass with a hidden item
    if sne_type == 0 and random.random() < 0.005: sne_type = "0_p"

    return "sne_" + str(sne_type)


def generate_path(layer, path_type, path_width):
    for house in range(0, len(houses_Connecters) - 1):
        distance1 = int(houses_Connecters[house]["Left_Connect"][0] - houses_Connecters[house + 1]["Right_Connect"][0])
        distance2 = int(houses_Connecters[house]["Right_Connect"][0] - houses_Connecters[house + 1]["Left_Connect"][0])
        if distance1 <= -2 and distance2 <= -2:
            x_difference = max(distance1, distance2)
            y_difference = houses_Connecters[house]["Left_Connect"][1] - houses_Connecters[house + 1]["Left_Connect"][1]
            start_x_horizontal = int(houses_Connecters[house]["Right_Connect"][0])
            start_y_horizontal = int(houses_Connecters[house + 1]["Left_Connect"][1])
            start_x_vertical = int(houses_Connecters[house]["Right_Connect"][0])
            start_y_vertical = min(int(houses_Connecters[house]["Left_Connect"][1]), houses_Connecters[house + 1]["Left_Connect"][1])
        elif distance1 >= 2 and distance2 >= 2:
            x_difference = min(distance1, distance2)
            y_difference = houses_Connecters[house]["Left_Connect"][1] - houses_Connecters[house + 1]["Left_Connect"][1]
            start_x_horizontal = int(houses_Connecters[house + 1]["Right_Connect"][0])
            start_y_horizontal = int(houses_Connecters[house]["Left_Connect"][1])
            start_x_vertical = int(houses_Connecters[house + 1]["Right_Connect"][0])
            start_y_vertical = min(int(houses_Connecters[house]["Left_Connect"][1]), houses_Connecters[house + 1]["Left_Connect"][1])
        elif distance1 <= 2 and distance2 >= 0:
            x_difference = int(houses_Connecters[house]["Left_Connect"][0] - houses_Connecters[house + 1]["Left_Connect"][0])
            y_difference = houses_Connecters[house]["Left_Connect"][1] - houses_Connecters[house + 1]["Left_Connect"][1]
            start_x_horizontal = int(houses_Connecters[house + 1]["Left_Connect"][0])
            start_y_horizontal = int(houses_Connecters[house]["Left_Connect"][1])
            start_x_vertical = int(houses_Connecters[house + 1]["Left_Connect"][0])
            start_y_vertical = min(int(houses_Connecters[house]["Left_Connect"][1]), houses_Connecters[house + 1]["Left_Connect"][1])
        else:
            x_difference = int(houses_Connecters[house]["Right_Connect"][0] - houses_Connecters[house + 1]["Right_Connect"][0])
            y_difference = houses_Connecters[house]["Left_Connect"][1] - houses_Connecters[house + 1]["Left_Connect"][1]
            start_x_horizontal = int(houses_Connecters[house]["Right_Connect"][0])
            start_y_horizontal = int(houses_Connecters[house]["Left_Connect"][1])
            start_x_vertical = int(houses_Connecters[house + 1]["Right_Connect"][0])
            start_y_vertical = min(int(houses_Connecters[house]["Left_Connect"][1]), houses_Connecters[house + 1]["Left_Connect"][1])

        x_difference = abs(x_difference)
        y_difference = abs(y_difference)

        draw_vertical_path(layer, start_x_vertical, start_y_vertical, y_difference, path_type, path_width)
        draw_horizontal_path(layer, start_x_horizontal, start_y_horizontal, x_difference, path_type, path_width)

    fixit(layer)


def generate_dijkstra_path(layer, path_type):

    def initialize_dijkstra():
        for y in range(map_Size_Y):
            weight_array = []
            for x in range(map_Size_X):
                weight_array.append(determine_weight(x, y))
            current_weight.append(map_Size_X * [sys.maxsize])
            weight.append(weight_array)
            visited.append(map_Size_X * [False])
            previous_tile.append(map_Size_X * [(0, 0)])

    def determine_weight(x, y):
        PATH_WEIGHT = 1
        GRASS_WEIGHT = 3
        HILL_WEIGHT = 5
        WATER_WEIGHT = 10

        if "h_" in house_Tiles.get((x - 1, y), "") or "pm_" in house_Tiles.get((x - 1, y),  "") or "pc_" in house_Tiles.get((x - 1, y), ""): return 999999
        if "h_" in house_Tiles.get((x, y), "") and ("h_" in house_Tiles.get((x, y + 1), "") or "h_" in house_Tiles.get((x, y - 1), "")): return 999999
        if "pm_" in house_Tiles.get((x, y), "") and ("pm_" in house_Tiles.get((x, y + 1), "") or "pm_" in house_Tiles.get((x, y - 1), "")): return 999999
        if "pc_" in house_Tiles.get((x, y), "") and ("pc_" in house_Tiles.get((x, y + 1), "") or "pc_" in house_Tiles.get((x, y - 1), "")): return 999999
        if is_actual_path(ground_Tiles, x, y) or "b_" in ground_Tiles.get((x, y), "") or "mrk" in ground_Tiles.get((x, y), ""): return PATH_WEIGHT
        if ground_Tiles.get((x, y), "") == "" or "p_4" in ground_Tiles.get((x, y), ""): return GRASS_WEIGHT
        if "m_" in ground_Tiles.get((x, y), ""): return HILL_WEIGHT
        if "pd_" in ground_Tiles.get((x, y), "") or "pd_" in ground_Tiles.get((x - 1, y), ""): return WATER_WEIGHT
        return 999999

    def handle_current_tile():
        current_x = current_tile[0]
        current_y = current_tile[1]
        visited[current_y][current_x] = True
        for tile_around in range(4):
            around_x = current_x - 1 + ((2 * tile_around) + 1) % 3
            around_y = current_y - 1 + ((2 * tile_around) + 1) // 3
            if not out_of_bounds(around_x, around_y):
                new_weight = current_weight[current_y][current_x] + weight[around_y][around_x]
                if not visited[around_y][around_x] and current_weight[around_y][around_x] > new_weight:
                    current_weight[around_y][around_x] = new_weight
                    previous_tile[around_y][around_x] = current_tile
                    handle_tiles[(around_x, around_y)] = new_weight
        handle_tiles.pop(current_tile)

    def find_min_tile():
        min_weight = sys.maxsize
        for tile in handle_tiles:
            if handle_tiles[tile] < min_weight:
                min_weight = handle_tiles[tile]
                min_tile = tile
        return min_tile



    for front_door in range(len(houses_Front_Doors) - 1):
        current_tile = houses_Front_Doors[front_door]
        target_tile = houses_Front_Doors[front_door + 1]
        weight = []
        current_weight = []
        visited = []
        previous_tile = []
        handle_tiles = {}
        initialize_dijkstra()

        visited[current_tile[1]][current_tile[0]] = True
        current_weight[current_tile[1]][current_tile[0]] = 0
        previous_tile[current_tile[1]][current_tile[0]] = (0, 0)
        handle_tiles[(current_tile[0], current_tile[1])] = 0
        handle_current_tile()
        while not current_tile == target_tile:
            current_tile = find_min_tile()
            handle_current_tile()

        path = []
        while not previous_tile[current_tile[1]][current_tile[0]] == (0, 0):
            path.append(current_tile)
            if not is_actual_path(layer, current_tile[0], current_tile[1]): layer[current_tile] = house_path_type
            current_tile = previous_tile[current_tile[1]][current_tile[0]]

    fixit(ground_Tiles)


def fixit(layer):
    make_path_double(layer)
    remove_half_stairs(layer)
    move_faulty_stairs(layer)
    finish_stairs(layer)
    remove_half_stairs(layer)
    apply_platform_sprites(layer)
    apply_hill_sprites(layer)
    finishing_touches_bridges(layer)


def make_path_double(layer):
    path_extention = []
    for y in range(map_Size_Y):
        for x in range(map_Size_X):
            if house_path_type in layer.get((x, y), ""):
                path_extention.append((x, y - 1))
                if (x, y) not in house_Tiles.keys():
                    path_extention.append((x - 1, y))
                    path_extention.append((x - 1, y - 1))

    for path in path_extention:
        x = path[0]
        y = path[1]
        if tile_Heights.get((x, y), 0) < 1:
            layer[(x, y)] = "b_"
        elif not is_actual_path(layer, x, y): layer[(x, y)] = house_path_type


def draw_vertical_path(layer, start_x_vertical, start_y_vertical, y_difference, path_type, path_width):
    path_height = tile_Heights.get((start_x_vertical, start_y_vertical), 0)
    tile_Heights[(start_x_vertical, start_y_vertical)] = min(tile_Heights[(start_x_vertical, start_y_vertical)], tile_Heights[(start_x_vertical + 1, start_y_vertical)])
    tile_Heights[(start_x_vertical + 1, start_y_vertical)] = min(tile_Heights[(start_x_vertical, start_y_vertical)], tile_Heights[(start_x_vertical + 1, start_y_vertical)])

    for path in range(path_width * y_difference + 4):
        x = start_x_vertical + (path % path_width)
        y = start_y_vertical + math.floor(path / path_width)

        if path % 2 == 0 and path_height > 0:
            try_horizontal_stairs(x, y, path_height)
            try_backdoor(house_Tiles, x, y + 1)

        if "b_" not in layer.get((x, y), "") and (layer.get((x, y), "") == "pd_" or layer.get((x, y + 1), "") == "pd_"):
            layer[(x, y)] = "b_" + str((path % 2) + 3)
        elif not (x, y) in layer.keys():
            ground_Tiles[(x, y)] = "p_" + str(path_type)

        if path % 2 == 0 and path_height > 0:
            if tile_Heights.get((x - 1, y), path_height) < path_height and not is_actual_path(layer, x - 1, y) and "sta_" not in layer.get((x - 1, y), ""): tile_Heights[(x - 1, y)] = path_height
            if tile_Heights.get((x + 2, y), path_height) < path_height and not is_actual_path(layer, x + 2, y) and "sta_" not in layer.get((x + 2, y), ""): tile_Heights[(x + 2, y)] = path_height

        path_height = tile_Heights.get((x, y + 1), path_height)

    finish_bridges(layer)


def draw_horizontal_path(layer, start_x_horizontal, start_y_horizontal, x_difference, path_type, path_width):
    path_height = tile_Heights.get((start_x_horizontal, start_y_horizontal), 0)
    tile_Heights[(start_x_horizontal, start_y_horizontal)] = min(tile_Heights[(start_x_horizontal, start_y_horizontal)], tile_Heights[(start_x_horizontal, start_y_horizontal + 1)])
    tile_Heights[(start_x_horizontal, start_y_horizontal + 1)] = min(tile_Heights[(start_x_horizontal, start_y_horizontal)], tile_Heights[(start_x_horizontal, start_y_horizontal + 1)])

    for path in range(path_width * (x_difference + 2)):
        x = start_x_horizontal + (path % (x_difference + 2))
        y = start_y_horizontal + path // (x_difference + 2)

        if path // (x_difference + 2) == 0 and path_height > 0:
            try_vertical_stairs(x, y, path_height)

        if "b_" not in layer.get((x, y), "") and (layer.get((x, y), "") == "pd_" or layer.get((x + 1, y), "") == "pd_" or tile_Heights.get((x - 1, y), path_height) < 1):
            layer[(x, y)] = "b_" + str(path // (x_difference + 2) + 1)
        elif not (x, y) in layer.keys():
            ground_Tiles[(x, y)] = "p_" + str(path_type)

        if path // (x_difference + 2) == 0 and path_height > 0:
            if tile_Heights.get((x, y - 1), path_height) < path_height and not is_actual_path(layer, x, y - 1) and "sta_" not in layer.get((x, y - 1), ""): tile_Heights[(x, y - 1)] = path_height
            if tile_Heights.get((x, y + 2), path_height) < path_height and not is_actual_path(layer, x, y + 2) and "sta_" not in layer.get((x, y + 2), ""): tile_Heights[(x, y + 2)] = path_height

        path_height = tile_Heights.get((x + 1, y), path_height)

    finish_bridges(layer)


def is_actual_path(layer, x, y):
    try:
        return "p_" in layer.get((x, y), "") and "p_4" not in layer.get((x, y), "")
    except Exception as e:
        print(e)
        print(layer.get((x, y), ""))


def try_horizontal_stairs(x, y, path_height):
    if not out_of_bounds(x + 1, y + 1) and not out_of_bounds(x, y) and min(tile_Heights[(x, y + 1)], tile_Heights[(x + 1, y + 1)]) > 0:
        tile_Heights[(x, y + 1)] = min(tile_Heights[(x, y + 1)], tile_Heights[(x + 1, y + 1)])
        tile_Heights[(x + 1, y + 1)] = min(tile_Heights[(x, y + 1)], tile_Heights[(x + 1, y + 1)])
        if path_height > 0:
            if tile_Heights[(x, y + 1)] < path_height > 0:
                ground_Tiles[(x, y)] = "sta_1_0"
                ground_Tiles[(x + 1, y)] = "sta_1_1"
            elif tile_Heights[(x, y + 1)] > path_height and tile_Heights[(x, y + 1)] > 0:
                ground_Tiles[(x, y + 1)] = "sta_8_0"
                ground_Tiles[(x + 1, y + 1)] = "sta_8_1"


def try_vertical_stairs(x, y, path_height):
    if not out_of_bounds(x + 1, y + 1) and not out_of_bounds(x, y) and min(tile_Heights[(x + 1, y)], tile_Heights[(x + 1, y + 1)]) > 0:
        tile_Heights[(x + 1, y)] = min(tile_Heights[(x + 1, y)], tile_Heights[(x + 1, y + 1)])
        tile_Heights[(x + 1, y + 1)] = min(tile_Heights[(x + 1, y)], tile_Heights[(x + 1, y + 1)])
        if path_height > 0:
            if tile_Heights[(x + 1, y)] < path_height > 0:
                ground_Tiles[(x, y)] = "sta_6_1"
                ground_Tiles[(x, y + 1)] = "sta_6_0"
            elif tile_Heights[(x + 1, y)] > path_height and tile_Heights[(x + 1, y)] > 0:
                ground_Tiles[(x + 1, y)] = "sta_3_1"
                ground_Tiles[(x + 1, y + 1)] = "sta_3_0"


def try_backdoor(layer, x, y):
    if "h_" in layer.get((x, y), "") and "h_" in layer.get((x + 1, y), "") and not "h_" in layer.get((x, y - 1), ""):
        if "bd_" in decoration_Tiles.get((x - 1, y), ""):
            decoration_Tiles[(x, y)] = "bd_1"
            if decoration_Tiles.get((x - 1, y), "") == "bd_2": decoration_Tiles[(x - 1, y)] = "bd_1"
        else:
            decoration_Tiles[(x, y)] = "bd_0"
        if "bd_" in decoration_Tiles.get((x + 2, y), ""):
            decoration_Tiles[(x + 1, y)] = "bd_1"
            if decoration_Tiles.get((x + 1, y), "") == "bd_0": decoration_Tiles[(x + 1, y)] = "bd_1"
        else:
            decoration_Tiles[(x + 1, y)] = "bd_2"


def finish_stairs(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if "sta_" in layer.get((x, y),""):
                if layer.get((x, y), "") == "sta_1_0" and "sta_" in layer.get((x - 1, y), ""):
                    layer[(x, y)] = "sta_1_1"
                if layer.get((x, y), "") == "sta_3_0" and "sta_" in layer.get((x, y + 1), ""):
                    layer[(x, y)] = "sta_3_1"
                if layer.get((x, y), "") == "sta_6_0" and "sta_" in layer.get((x, y + 1), ""):
                    layer[(x, y)] = "sta_6_1"

                if "sta_3" in layer.get((x, y - 1), "") and "sta_" in layer.get((x, y + 1), ""):
                    layer[(x, y)] = "sta_3"
                if "sta_6" in layer.get((x, y - 1), "") and "sta_" in layer.get((x, y + 1), ""):
                    layer[(x, y)] = "sta_6"
                if "sta_8" in layer.get((x - 1, y), "") and "sta_" in layer.get((x + 1, y), ""):
                    layer[(x, y)] = "sta_8"
                if "sta_1" in layer.get((x - 1, y), "") and "sta_" in layer.get((x + 1, y), ""):
                    layer[(x, y)] = "sta_1_1"


def remove_half_stairs(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if "sta_" in layer.get((x, y), ""):
                stair_type = layer[(x, y)][4]
                if not check_stairs_around(layer, x, y, stair_type):
                    layer[(x, y)] = "p_1"
                    if check_similar_height_around(x, y):
                        tile_Heights[(x, y)] = tile_Heights[(x, y)] - 1


def check_stairs_around(layer, x, y, stair_type):
    for tile in range(4):
        if "sta_" + stair_type in layer.get((x - 1 + ((2 * tile) + 1) % 3, y - 1 + ((2 * tile) + 1) // 3), ""):
            return True
    return False


def check_any_stairs_around(layer, x, y):
    for tile in range(4):
        if "sta_" in layer.get((x - 1 + ((2 * tile) + 1) % 3, y - 1 + ((2 * tile) + 1) // 3), ""):
            return True
    return False


def check_similar_height_around(x, y):
    for tile in range(4):
        if tile_Heights.get((x, y), 0) > tile_Heights.get((x - 1 + ((2 * tile) + 1) % 3, y - 1 + ((2 * tile) + 1) // 3), 0):
            return True
    return False


def move_faulty_stairs(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if "sta_" in layer.get((x, y), ""):
                move_stair(layer, x, y)


def move_stair(layer, x, y):
    if "sta_" in layer.get((x, y), ""):
        stair = layer.get((x, y), "")
        stair_type = int(stair[4])
        try:
            stair_subtype = int(stair[6])
        except Exception as e:
            stair_subtype = -1
        move_stair_tile(layer, x, y, stair, stair_type, stair_subtype)


def move_stair_tile(layer, x, y, stair, stair_type, stair_subtype):
    if stair_type == 1:
        if tile_Heights.get((x, y), 0) < tile_Heights.get((x, y - 1), 0):
            move_stair_tile_to(layer, x, y, x, y - 1, "p_1", stair)
            fix_adjacent_hill(x, y - 1, stair_type, stair_subtype)
        elif tile_Heights.get((x, y), 0) == tile_Heights.get((x, y + 1), 0):
            layer[(x, y)] = "p_1"
    elif stair_type == 3:
        if tile_Heights.get((x, y), 0) < tile_Heights.get((x + 1, y), 0):
            move_stair_tile_to(layer, x, y, x + 1, y, "p_1", stair)
            fix_adjacent_hill(x + 1, y, stair_type, stair_subtype)
        elif tile_Heights.get((x, y), 0) == tile_Heights.get((x - 1, y), 0):
            layer[(x, y)] = "p_1"
    elif stair_type == 6:
        if tile_Heights.get((x, y), 0) < tile_Heights.get((x - 1, y), 0):
            move_stair_tile_to(layer, x, y, x - 1, y, "p_1", stair)
            fix_adjacent_hill(x - 1, y, stair_type, stair_subtype)
        elif tile_Heights.get((x, y), 0) == tile_Heights.get((x + 1, y), 0):
            layer[(x, y)] = "p_1"
    elif stair_type == 8:
        if tile_Heights.get((x, y), 0) < tile_Heights.get((x, y + 1), 0):
            move_stair_tile_to(layer, x, y, x, y + 1, "p_1", stair)
            fix_adjacent_hill(x, y + 1, stair_type, stair_subtype)
        elif tile_Heights.get((x, y), 0) == tile_Heights.get((x, y - 1), 0):
            layer[(x, y)] = "p_1"


def move_stair_tile_to(layer, x, y, new_x, new_y, replace_tile, stair):
    if "sta_" in layer.get((x, y), ""):
        layer[(new_x, new_y)] = stair
        layer[(x, y)] = replace_tile


def fix_adjacent_hill(x, y, stair_type, stair_subtype):
    if stair_type == 1 or stair_type == 8:
        if stair_subtype == 0 and "p_" not in ground_Tiles.get((x - 1, y), ""):
            tile_Heights[(x - 1, y)] = tile_Heights[(x, y)]
        elif stair_subtype == 1 and "p_" not in ground_Tiles.get((x + 1, y), ""):
            tile_Heights[(x + 1, y)] = tile_Heights[(x, y)]
    elif stair_type == 3 or stair_type == 6:
        if stair_subtype == 1 and "p_" not in ground_Tiles.get((x, y - 1), ""):
            tile_Heights[(x, y - 1)] = tile_Heights[(x, y)]
        elif stair_subtype == 0 and "p_" not in ground_Tiles.get((x, y + 1), ""):
            tile_Heights[(x, y + 1)] = tile_Heights[(x, y)]


def out_of_bounds(x, y):
    return x < 0 or y < 0 or x >= map_Size_X or y >= map_Size_Y


def taken(layer, x, y):
    return (x, y) in layer.keys()


def apply_path_sprites(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if (x, y) in layer and "p_" in layer[(x, y)]:
                path = calculate_path_sprite(layer, x, y)
                if not path == "_er":
                    layer[(x, y)] = str(layer[(x, y)]) + str(path)
                else:
                    layer[(x, y)] = "g_0"

    finish_path_edges(decoration_Tiles)


def finish_bridges(layer):
    for y in range(0, map_Size_Y):
        for x in range(0, map_Size_X):
            if (is_actual_path(layer, x - 1, y) or "b_1" in layer.get((x - 1, y), "")) and "pd_" in layer.get((x, y - 1), "") and layer.get((x, y), "") == "b_":
                layer[(x, y)] = "b_2"
                layer[(x, y + 1)] = "b_1"
            if (is_actual_path(layer, x, y + 1) or "b_3" in layer.get((x, y - 1), "")) and "pd_" in layer.get((x - 1, y), "") and layer.get((x, y), "") == "b_":
                layer[(x, y)] = "b_3"
                layer[(x + 1, y)] = "b_4"
            # if layer.get((x, y), "") == "b_1" and "p_" in layer.get((x, y + 1), ""): layer[(x, y + 1)] = "b_2"
            # if layer.get((x, y), "") == "b_2" and "p_" in layer.get((x, y - 1), ""): layer[(x, y - 1)] = "b_1"
            # if layer.get((x, y), "") == "b_3" and "p_" in layer.get((x + 1, y), ""): layer[(x + 1, y)] = "b_4"
            # if layer.get((x, y), "") == "b_4" and "p_" in layer.get((x - 1, y), ""): layer[(x - 1, y)] = "b_3"

    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if "b_" in layer.get((x, y), ""):
                if (layer.get((x - 1, y), "") == "b_3" or layer.get((x - 1, y), "") == "b_6") and (layer.get((x + 1, y), "") == "b_3" or layer.get((x + 1, y), "") == "b_4" or layer.get((x + 1, y), "") == "b_6"):
                    layer[(x, y)] = "b_6"
                if (layer.get((x, y - 1), "") == "b_1" or layer.get((x, y - 1), "") == "b_5") and (layer.get((x, y + 1), "") == "b_1" or layer.get((x, y + 1), "") == "b_2" or layer.get((x, y + 1), "") == "b_5"):
                    layer[(x, y)] = "b_5"


def finishing_touches_bridges(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if "b_" in layer.get((x, y - 1), "") and "pd_" in layer.get((x, y), ""):
                decoration_Tiles[(x, y)] = "bu_0"


def apply_platform_sprites(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if layer.get((x, y), "") == "pl_":
                layer[(x, y)] = "pl_1"
                layer[(x + 1, y)] = "pl_2"
                layer[(x, y + 1)] = "pl_3"
                layer[(x + 1, y + 1)] = "pl_4"


def calculate_path_sprite(layer, x, y):
    tiles_around = []
    for around in range(0, 9):
        path_around = layer.get((x + (around % 3) - 1, y + math.floor(around / 3) - 1), 0)
        if path_around == 0: path_around = house_Tiles.get((x + (around % 3) - 1, y + math.floor(around / 3) - 1), 0)
        if "p_" in str(path_around) or "b_" in str(path_around) or "pl_" in str(path_around) or "sta_" in str(path_around) or "m_4_p" in str(path_around) or "pd_" in str(path_around) or out_of_bounds(x + (around % 3) - 1, y + math.floor(around / 3) - 1) or "mrk" in str(path_around):
            tiles_around.append(1)
        else:
            tiles_around.append(0)
    if tiles_around == [1, 1, 1, 1, 1, 1, 0, 1, 1]: return "_9"
    elif tiles_around == [1, 1, 1, 1, 1, 1, 1, 1, 0]: return "_10"
    elif tiles_around == [1, 1, 0, 1, 1, 1, 1, 1, 1]: return "_11"
    elif tiles_around == [0, 1, 1, 1, 1, 1, 1, 1, 1]: return "_12"
    elif tiles_around == [1, 1, 1, 1, 1, 1, 1, 1, 1] or (tiles_around[1] == 1 and tiles_around[3] == 1 and tiles_around[5] == 1 and tiles_around[7] == 1): return "_0"
    elif tiles_around == [0, 1, 1, 0, 1, 1, 0, 1, 1] or tiles_around == [1, 1, 1, 0, 1, 1, 0, 1, 1] or tiles_around == [0, 1, 1, 0, 1, 1, 1, 1, 1] or tiles_around == [1, 1, 1, 0, 1, 1, 1, 1, 1]: return "_1"
    elif tiles_around == [1, 1, 1, 1, 1, 1, 0, 0, 0] or tiles_around == [1, 1, 1, 1, 1, 1, 1, 0, 0] or tiles_around == [1, 1, 1, 1, 1, 1, 0, 0, 1] or tiles_around == [1, 1, 1, 1, 1, 1, 1, 0, 1]: return "_2"
    elif tiles_around == [1, 1, 0, 1, 1, 0, 1, 1, 0] or tiles_around == [1, 1, 1, 1, 1, 0, 1, 1, 0] or tiles_around == [1, 1, 0, 1, 1, 0, 1, 1, 1] or tiles_around == [1, 1, 1, 1, 1, 0, 1, 1, 1]: return "_3"
    elif tiles_around == [0, 0, 0, 1, 1, 1, 1, 1, 1] or tiles_around == [1, 0, 0, 1, 1, 1, 1, 1, 1] or tiles_around == [0, 0, 1, 1, 1, 1, 1, 1, 1] or tiles_around == [1, 0, 1, 1, 1, 1, 1, 1, 1]: return "_4"
    elif tiles_around[5] == 1 and tiles_around[7] == 1 and tiles_around[8] == 1: return "_5"
    elif tiles_around[1] == 1 and tiles_around[2] == 1 and tiles_around[5] == 1: return "_6"
    elif tiles_around[0] == 1 and tiles_around[1] == 1 and tiles_around[3] == 1: return "_7"
    elif tiles_around[3] == 1 and tiles_around[6] == 1 and tiles_around[7] == 1: return "_8"
    return "_er"


def finish_path_edges(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if is_actual_path(ground_Tiles, x, y):
                apply_path_edge(layer, x, y)
            elif "sta_" in ground_Tiles.get((x, y), ""):
                apply_stair_edge(layer, x, y)


def apply_path_edge(layer, x, y):
    if tile_Heights.get((x, y), 0) > tile_Heights.get((x, y + 1), 0) and ("p_" in ground_Tiles.get((x, y + 1), "") or "sta_3" in ground_Tiles.get((x, y + 1), "") or "sta_6" in ground_Tiles.get((x, y + 1), "")):
        layer[(x, y)] = "p_2_m"
    elif tile_Heights.get((x, y), 0) > tile_Heights.get((x, y - 1), 0) and ("p_" in ground_Tiles.get((x, y - 1), "") or "sta_3" in ground_Tiles.get((x, y - 1), "") or "sta_6" in ground_Tiles.get((x, y - 1), "")):
        layer[(x, y)] = "p_4_m"
    elif tile_Heights.get((x, y), 0) > tile_Heights.get((x + 1, y), 0) and ("p_" in ground_Tiles.get((x + 1, y), "") or "sta_1" in ground_Tiles.get((x + 1, y), "") or "sta_8" in ground_Tiles.get((x + 1, y), "")):
        layer[(x, y)] = "p_3_m"
    elif tile_Heights.get((x, y), 0) > tile_Heights.get((x - 1, y), 0) and ("p_" in ground_Tiles.get((x - 1, y), "") or "sta_1" in ground_Tiles.get((x - 1, y), "") or "sta_8" in ground_Tiles.get((x - 1, y), "")):
        layer[(x, y)] = "p_1_m"


def apply_stair_edge(layer, x, y):
    stair_type = int(ground_Tiles[(x, y)][4])
    if stair_type == 1 or stair_type == 8:
        if is_actual_path(ground_Tiles, x - 1, y):
            if tile_Heights.get((x, y), 0) > tile_Heights.get((x - 1, y), 0):
                layer[(x, y)] = "p_1_m"
            else:
                layer[(x - 1, y)] = "p_3_m"
        elif is_actual_path(ground_Tiles, x + 1, y):
            if tile_Heights.get((x, y), 0) > tile_Heights.get((x + 1, y), 0):
                layer[(x, y)] = "p_3_m"
            else:
                layer[(x + 1, y)] = "p_1_m"
    elif stair_type == 3 or stair_type == 6:
        if is_actual_path(ground_Tiles, x, y - 1):
            if tile_Heights.get((x, y), 0) > tile_Heights.get((x, y - 1), 0):
                layer[(x, y)] = "p_4_m"
            else:
                layer[(x, y - 1)] = "p_2_m"
        elif is_actual_path(ground_Tiles, x, y + 1):
            if tile_Heights.get((x, y), 0) > tile_Heights.get((x, y + 1), 0):
                layer[(x, y)] = "p_2_m"
            else:
                layer[(x, y + 1)] = "p_4_m"


def generate_beach(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if check_for_water_around(layer, x, y, 4) and (x, y) not in layer.keys() and tile_Heights.get((x, y), 0) == 1: layer[(x, y)] = "p_4"


def decorate_beach(layer, decoration_rate):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if not find_decoration_around(layer, x, y - 2, 2, 3) and "p_4" in ground_Tiles.get((x, y - 2), "") and flat_surface(x, y - 2, 2, 3) and check_availability_zone(house_Tiles, x, y - 2, 2, 3) and random.random() < decoration_rate / 300:
                umbrella_type = str(random.randint(1, NB_UMBRELLA))
                for tile in range(6):
                    layer[(x + tile % 2, y + tile // 2 - 2)] = "umb_" + umbrella_type + "_" + str(tile)
            if not find_decoration_around(layer, x, y - 1, 1, 2) and (x, y) not in layer.keys() and random.random() < decoration_rate / 300:
                if "p_4" in ground_Tiles.get((x, y), "") and "p_4" in ground_Tiles.get((x, y - 1), ""):
                    if random.randint(0, 1) == 0 and not raining: npc_Layer[(x, y - 1)] = "npc_" + str(shore_Npc[random.randint(1, len(shore_Npc) - 1)]) + "_1"
                    layer[(x, y - 1)] = "sts_2_0"
                    layer[(x, y)] = "sts_2_1"
                elif "pd_" in ground_Tiles.get((x, y - 1), "") and "pd_" in ground_Tiles.get((x, y), "") and not raining:
                    npc_Layer[(x, y - 1)] = "npc_" + str(shore_Npc[random.randint(1, len(shore_Npc) - 1)]) + "_1"
                    layer[(x, y - 1)] = "sts_1_0"
                    layer[(x, y)] = "sts_1_1"


def find_decoration_around(layer, x, y, x_size, y_size):
    for x_check in range(x_size):
        for y_check in range(y_size):
            if (x + x_check, y + y_check) in layer.keys():
                return True
    return False


def check_for_water_around(layer, x, y, beach_width):
    for around in range(0, (beach_width + 2) ** 2):
        check_x = x + around % (beach_width + 2) - beach_width + 1
        check_y = y + around // (beach_width + 2) - beach_width + 1
        water_around = layer.get((check_x, check_y), "")
        if "pd_" in str(water_around): #or "p_4" in str(water_around):
            return True
    return False


def apply_water_sprites(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if (x, y) in layer and (layer[(x, y)] == "pd_" or layer[(x, y)] == "b_"):
                water_sprite = calculate_water_sprite(layer, x, y)
                layer[(x, y)] = str(layer[(x, y)]) + str(water_sprite)


def create_rivers(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            tile_height = tile_Heights[(x, y)]
            if tile_height == 0:
                layer[(x, y)] = "pd_"


def calculate_water_sprite(layer, x, y):
    tiles_around = []
    for around in range(0, 9):
        path_around = (layer.get((x + (around % 3) - 1, y + math.floor(around / 3) - 1), "0"))
        if "p_" not in str(path_around) and ("pd_" in str(path_around) or "b_" in str(path_around) or "pl_" in str(path_around) or out_of_bounds(x + (around % 3) - 1, y + math.floor(around / 3) - 1)):
            tiles_around.append(1)
        else:
            tiles_around.append(0)
    if tiles_around[1] == 1 and tiles_around[3] == 1 and tiles_around[5] == 1 and tiles_around[7] == 1:
        return 0
    elif tiles_around[1] == 1 and tiles_around[5] == 1 and tiles_around[7] == 1: return "1"
    elif tiles_around[1] == 1 and tiles_around[3] == 1 and tiles_around[5] == 1: return "2"
    elif tiles_around[1] == 1 and tiles_around[3] == 1 and tiles_around[7] == 1: return "3"
    elif tiles_around[3] == 1 and tiles_around[5] == 1 and tiles_around[7] == 1: return "4"
    elif tiles_around[5] == 1 and tiles_around[7] == 1: return "5"
    elif tiles_around[1] == 1 and tiles_around[5] == 1: return "6"
    elif tiles_around[1] == 1 and tiles_around[3] == 1: return "7"
    elif tiles_around[3] == 1 and tiles_around[7] == 1: return "8"
    elif tiles_around[3] == 1 and tiles_around[5] == 1: return "13"
    elif tiles_around[1] == 1 and tiles_around[7] == 1: return "14"
    elif tiles_around[1] == 1: return "9"
    elif tiles_around[3] == 1: return "10"
    elif tiles_around[5] == 1: return "12"
    elif tiles_around[7] == 1: return "11"
    return "15"


def spawn_lapras(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if can_spawn_pokemon(0.001, "Lapras") and check_availability_water(layer, x - 1, y - 1, 3, 4):
                layer["Lapras"] = True
                if random.random() < shiny_probability:
                    # direction should be either 5 or 7
                    direction = 5 + 2 * random.randint(0, 1)
                else:
                    # direction should be either 1 or 3
                    direction = 1 + 2 * random.randint(0, 1)
                layer[(x, y + 1)] = "pd_l_" + str(direction + 1)
                layer[(x, y)] = "pd_l_" + str(direction)


def spawn_gyarados(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            shiny = 0
            if can_spawn_pokemon(0.001, "Gyarados") and check_availability_water(layer, x - 1, y - 1, 4, 4):
                if random.random() < shiny_probability: shiny = 4
                layer["Gyarados"] = True
                layer[(x + 1, y)] = "pd_g_" + str(2 + shiny)
                layer[(x, y + 1)] = "pd_g_" + str(3 + shiny)
                layer[(x + 1, y + 1)] = "pd_g_" + str(4 + shiny)
                layer[(x, y)] = "pd_g_" + str(1 + shiny)


def spawn_mne(layer, spawn_rate, offset_x, offset_y):
    octaves = 3
    freq = 40
    off_x = offset_x
    off_y = offset_y
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if not (x, y) in layer.keys() and not (x, y - 1) in layer.keys() and not (x, y - 2) in layer.keys() and not (x, y) in house_Tiles.keys() and not (x, y - 1) in house_Tiles.keys() and not (x, y - 2) in house_Tiles.keys() and (x, y - 1) not in npc_Layer.keys() and (x, y - 2) not in npc_Layer.keys():
                if snoise4((x + off_x) / freq, (y + off_y) / freq, octaves) * 2 > 0 and random.random() < spawn_rate / 100:
                    layer[(x, y)] = "st_0"
                    layer[(x, y - 1)] = "st_1"
                    layer[(x, y - 2)] = "st_2"


def spawn_house(layer, house_type, house_size_x, house_size_y, amount):
    for houses in range(0, amount):
        house_x = random.randint(1, map_Size_X - house_size_y)
        house_y = random.randint(1, map_Size_Y - house_size_x)
        attempt = 0
        while not check_availability_zone(ground_Tiles, house_x, house_y, house_size_x + 1, house_size_y + 2) or not check_availability_zone(house_Tiles, house_x, house_y, house_size_x, house_size_y + 2) or not flat_surface(house_x - 3, house_y + 2, house_size_x + 6, house_size_y + 1):
            attempt += 1
            if attempt > 99: return
            house_x = random.randint(1, map_Size_X - house_size_x)
            house_y = random.randint(1, map_Size_Y - house_size_y)
            if "h_" in layer.get((house_x, house_y), ""):
                house_x = find_lower_right_of_house(layer, house_x, house_y, house_size_y)[0]
                house_y = find_lower_right_of_house(layer, house_x, house_y, house_size_y)[1]
        for house_tile in range(1, house_size_x * house_size_y + 1):
            layer[(house_x + (house_tile - 1) % house_size_x, house_y  + math.floor((house_tile - 1) / house_size_x))] = "h_" + str(house_type) + "_" + str(house_tile)
        for front in range(4 * house_size_x):
            ground_Tiles[(house_x + front % house_size_x, house_y + math.floor(front / house_size_x) + house_size_y - 2)] = "p_3"
        houses_Connecters[len(houses_Connecters)] = {"Left_Connect": (house_x - 2, house_y + house_size_y), "Right_Connect": (house_x + house_size_x, house_y + house_size_y)}
        houses_Front_Doors.append((int(house_x + house_size_x / 2), int(house_y + house_size_y)))
        if random.randint(0, 1) == 1 and not taken(layer, house_x - 1, house_y + house_size_y - 2):
            layer[(house_x - 1, house_y + house_size_y - 1)] = "mbx_0"
            layer[(house_x - 1, house_y + house_size_y - 2)] = "mbx_1"


def flat_surface(x, y, x_size, y_size):
    reference_height = tile_Heights.get((x, y), -1)
    for tile in range(1, x_size * y_size + 1):
        if tile_Heights.get((x + (tile % x_size), y + (tile // x_size)), -2) != reference_height:
            return False
    return True


def find_lower_right_of_house(layer, x, y, size_y):
    while "h_" in layer.get((x - 1, y), "") or "h_" in layer.get((x, y - 1), ""):
        if "h_" in layer.get((x - 1, y), ""): y += 1
        if "h_" in layer.get((x, y - 1), ""): x += 1
    return (x, y - size_y)


def spawn_pokecenter(layer):
    pokecenter_size_x = 5
    pokecenter_size_y = 5
    house_x = random.randint(1, map_Size_X - pokecenter_size_x)
    house_y = random.randint(1, map_Size_Y - pokecenter_size_y)
    while not check_availability_zone(ground_Tiles, house_x - 1, house_y - 1, pokecenter_size_x + 1, pokecenter_size_y + 4) or not check_availability_zone(house_Tiles, house_x - 1, house_y - 1, pokecenter_size_x + 1, pokecenter_size_y + 4) or not flat_surface(house_x - 1, house_y + 1, pokecenter_size_x + 2, pokecenter_size_y + 2):
        house_x = random.randint(1, map_Size_X - pokecenter_size_x)
        house_y = random.randint(1, map_Size_Y - pokecenter_size_y)
    for house_tile in range(1, pokecenter_size_x * pokecenter_size_y + 1):
        layer[(house_x + (house_tile - 1) % pokecenter_size_x, house_y + math.floor((house_tile - 1) / pokecenter_size_x))] = "pc_" + str(house_tile)
    for front in range(4 * pokecenter_size_x):
        ground_Tiles[(house_x + front % 5, house_y + math.floor(front / 5) + 5 - 2)] = "p_2"
    houses_Connecters[len(houses_Connecters)] = {"Left_Connect": (house_x - 2, house_y + pokecenter_size_y), "Right_Connect": (house_x + pokecenter_size_x, house_y + pokecenter_size_y)}
    houses_Front_Doors.append((int(house_x + pokecenter_size_x / 2), int(house_y + pokecenter_size_y)))


def spawn_pokemarket(layer):
    pokemarket_size_x = 4
    pokemarket_size_y = 4
    house_x = random.randint(1, map_Size_X - pokemarket_size_x)
    house_y = random.randint(1, map_Size_Y - pokemarket_size_y)
    while not check_availability_zone(ground_Tiles, house_x - 1, house_y - 1, pokemarket_size_x + 1, pokemarket_size_y + 4) or not check_availability_zone(house_Tiles, house_x - 1, house_y - 1, pokemarket_size_x + 1, pokemarket_size_y + 4) or not flat_surface(house_x - 1, house_y + 1, pokemarket_size_x + 2, pokemarket_size_y + 2):
        house_x = random.randint(1, map_Size_X - pokemarket_size_x)
        house_y = random.randint(1, map_Size_Y - pokemarket_size_y)
    for house_tile in range(1, pokemarket_size_x * pokemarket_size_y + 1):
        layer[(house_x + (house_tile - 1) % pokemarket_size_x, house_y + math.floor((house_tile - 1) / pokemarket_size_x))] = "pm_" + str(house_tile)
    for front in range(pokemarket_size_x * pokemarket_size_y):
        ground_Tiles[(house_x + front % pokemarket_size_x, house_y + math.floor(front / pokemarket_size_x) + pokemarket_size_x - 2)] = "p_2"
    houses_Connecters[len(houses_Connecters)] = {"Left_Connect": (house_x - 2, house_y + pokemarket_size_y), "Right_Connect": (house_x + pokemarket_size_x, house_y + pokemarket_size_y)}
    houses_Front_Doors.append((int(house_x + pokemarket_size_x / 2), int(house_y + pokemarket_size_y)))


def spawn_truck(layer):
    import math, random
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if random.random() < 0.05 and "p_" in ground_Tiles.get((x, y + 3), "") and "p_" in ground_Tiles.get((x + 2, y + 3), "") and "p_4" not in ground_Tiles.get((x, y + 3), "") and "p_4" not in ground_Tiles.get((x + 2, y + 3), ""):
                if check_availability_zone(house_Tiles, x, y, 3, 3) and check_availability_zone(ground_Tiles, x, y, 3, 1) and flat_surface(x, y + 1, 3, 2) and not ground_Tiles["Truck"]:
                    for truck_tile in range(9):
                        layer[(x + truck_tile % 3, y + math.floor(truck_tile / 3))] = "t_" + str(truck_tile + 1)
                    ground_Tiles["Truck"] = True


def spawn_snorlax(layer):
    shiny = 0
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if can_spawn_pokemon(0.015, "Snorlax") and (("b_" in ground_Tiles.get((x, y), "") or "pl_" in ground_Tiles.get((x, y), "")) and check_bridge_space(ground_Tiles, x, y, 2, 2)):
                ground_Tiles["Snorlax"] = True
                if random.random() < shiny_probability: shiny = 4
                for snorlax_tile in range(4):
                    layer[(x + snorlax_tile % 2, y + math.floor(snorlax_tile / 2))] = "sn_" + str(snorlax_tile + 1 + shiny)


def spawn_pikachu(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if can_spawn_pokemon(0.001, "Pikachu") and layer.get((x, y), "") == "" and "pd_" not in ground_Tiles.get((x, y), "") and "m_" not in ground_Tiles.get((x, y), ""):
                ground_Tiles["Pikachu"] = True
                layer[(x, y)] = "pikachu_" + str(random.randint(1, 4)) # TODO: shiny pikachu


def spawn_exceguttor(layer):
    shiny = 0
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if can_spawn_pokemon(0.001, "Exceguttor") and "p_4" in ground_Tiles.get((x, y), ""):
                if random.random() < 0.02: shiny = 2
                layer[(x, y)] = "exc_" + str(1 + shiny)
                layer[(x, y - 1)] = "exc_" + str(2 + shiny)
                ground_Tiles["Exceguttor"] = True


def spawn_lanterns(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if layer.get((x - 1, y), "") == "p_1_3" and random.random() < 0.05 and check_availability_zone(layer, x, y - 2, 2, 3):
                layer[(x, y)] = "l_1"
                layer[(x, y - 1)] = "l_2"
                layer[(x, y - 2)] = "l_3"
                layer[(x + 1, y)] = "l_4"
            if layer.get((x + 1, y), "") == "p_1_1" and random.random() < 0.05 and check_availability_zone(layer, x, y - 2, 1, 3):
                layer[(x, y)] = "l_5"
                layer[(x, y - 1)] = "l_6"
                layer[(x, y - 2)] = "l_7"


def spawn_fountain(layer):
    house_x = random.randint(1, map_Size_X - 5)
    house_y = random.randint(1, map_Size_Y - 5)
    while not check_availability_zone(ground_Tiles, house_x - 1, house_y - 1, 7, 7) or not check_availability_zone(house_Tiles, house_x - 1, house_y - 1, 7, 7) or not flat_surface(house_x - 2, house_y - 2, 5 + 4, 5 + 4):
        house_x = random.randint(1, map_Size_X - 5)
        house_y = random.randint(1, map_Size_Y - 5)

    for house_tile in range(1, 10):
        layer[(house_x + (house_tile - 1) % 3, house_y + math.floor((house_tile - 1) / 3) + 3)] = "f_" + str(house_tile)
    for front in range(25):
        ground_Tiles[(house_x - 1 + front % 5, (house_y - 1 + front // 5) + 5 - 2)] = "p_2"
    houses_Connecters[len(houses_Connecters)] = {"Left_Connect": (house_x - 2, house_y + 4), "Right_Connect": (house_x + 4, house_y + 4)}


def spawn_mini_boats(layer):
    boat_size_x = 6
    boat_size_y = 3
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if check_availability_water(ground_Tiles, x - 1, y - 1, boat_size_x + 2, boat_size_y + 2) and check_availability_zone(decoration_Tiles, x - 2, y - 2, boat_size_x + 4, boat_size_y + 4) and random.random() < 0.005:
                if random.randint(0, 1) == 1: direction = 1
                else: direction = 19
                for boat_y in range(boat_size_y):
                    for boat_x in range(boat_size_x):
                        layer[(x + boat_x, y + boat_y)] = "mb_" + str(boat_x + 6 * boat_y + direction)


def spawn_npc(layer, population, path_only):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            direction = random.randint(1, 4)
            if (x, y) not in house_Tiles.keys() and "m_" not in ground_Tiles.get((x, y), "") and random.random() < 0.001 * population:
                npc_number = random.randint(1, NB_NPC)
                if path_only:
                    if "p_" in ground_Tiles.get((x, y), "") and "p_4_" not in ground_Tiles.get((x, y), "") or "b_" in ground_Tiles.get((x, y), ""):
                        if npc_number not in off_Path_Npc: layer[(x, y)] = "npc_" + str(npc_number) + "_" + str(direction)
                        if random.random() < 0.5 and direction == 2:
                            if (x + 1, y) not in layer.keys() and (x + 1, y) not in house_Tiles.keys() and ("p_" in ground_Tiles.get((x + 1, y), "") or "b_" in ground_Tiles.get((x, y), "")):
                                layer[(x + 1, y)] = "npc_" + str(random.randint(1, NB_NPC)) + "_4"
                elif random.randint(0, 4) == 0:
                    if not raining:
                        if "pd_" in ground_Tiles.get((x, y), ""):
                            npc_number = water_Npc[random.randint(1, len(water_Npc) - 1)]
                        elif "b_" in ground_Tiles.get((x, y), ""):
                            npc_number = bridge_Npc[random.randint(1, len(bridge_Npc) - 1)]
                        elif "p_4" in ground_Tiles.get((x, y), ""):
                            npc_number = shore_Npc[random.randint(1, len(shore_Npc) - 1)]
                    if (x, y) not in ground_Tiles.keys():
                        npc_number = outside_Npc[random.randint(1, len(outside_Npc) - 1)]
                    elif is_actual_path(ground_Tiles, x, y):
                        while npc_number in off_Path_Npc:
                            npc_number = random.randint(1, NB_NPC)
                    else:
                        break
                    if npc_number == 50: direction = 1
                    layer[(x, y)] = "npc_" + str(npc_number) + "_" + str(direction)
                    if random.random() < 0.5 and direction == 2:
                        if (x + 1, y) not in layer.keys() and (x + 1, y) not in house_Tiles.keys():
                            layer[(x + 1, y)] = "npc_" + str(random.randint(1, NB_NPC)) + "_4"


def check_bridge_space(layer, x, y, x_size, y_size):
    for bridge_tile in range(x_size * y_size):
        if "b_" not in layer.get((x + bridge_tile % x_size, y + math.floor(bridge_tile / x_size)), "") and "pl_" not in layer.get((x + bridge_tile % x_size, y + math.floor(bridge_tile / x_size)), ""):
            return False
    return True


def check_availability_zone(layer, start_x, start_y, x_size, y_size):
    for tile in range(x_size * y_size + 1):
        if (start_x + tile % x_size, start_y + (tile - 1) // x_size) in layer.keys() or out_of_bounds(start_x + tile % x_size, start_y + (tile - 1) // x_size):
            return False
    return True


def check_availability_water(layer, start_x, start_y, x_size, y_size):
    for tile in range(x_size * y_size + 1):
        if "pd_" not in layer.get((start_x + tile % x_size, start_y + math.floor((tile - 1) / x_size)), ""):
            return False
    return True


def mountainize(layer, max_height, offset_x, offset_y):
    from math import floor
    octaves = 1
    freq = 100
    off_x = offset_x
    off_y = offset_y
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            tile_height = abs(floor((snoise4(round((x + off_x) / freq, 2), round((y + off_y) / freq, 2), octaves)) * max_height))
            layer[(x, y)] = tile_height


def generate_height_map(layer, height_list):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            layer[(x, y)] = "height_" + str(height_list[(x, y)])


def calculate_hill_texture(height_list, x, y):
    hills_around = test_hills_around(height_list, x, y)

    if height_list.get((x, y), 0) < 2: return -1

    elif hills_around[3] == 0 and hills_around[6] == -1 and hills_around[7] == 0: return 9
    elif hills_around[5] == 0 and hills_around[7] == 0 and hills_around[8] == -1: return 10
    elif hills_around[0] == -1 and hills_around[1] == 0 and hills_around[3] == 0 and hills_around[7] == 0: return 4
    elif hills_around[1] == 0 and hills_around[2] == -1 and hills_around[5] == 0 and hills_around[7] == 0: return 4

    elif hills_around[1] == -1 and hills_around[3] == -1 and hills_around[5] == -1 and hills_around[7] == -1: return 15
    elif hills_around[1] == -1 and hills_around[3] == 0 and hills_around[5] == -1 and hills_around[7] == -1: return 15
    elif hills_around[1] == -1 and hills_around[3] == -1 and hills_around[5] == -1 and hills_around[7] == 0: return 15
    elif hills_around[1] == -1 and hills_around[3] == -1 and hills_around[5] == 0 and hills_around[7] == -1: return 15
    elif hills_around[1] == 0 and hills_around[3] == -1 and hills_around[5] == -1 and hills_around[7] == -1: return 15

    elif hills_around[1] == 0 and hills_around[3] == -1 and hills_around[7] == 0: return 1
    elif hills_around[3] == 0 and hills_around[5] == 0 and hills_around[7] == -1: return 2
    elif hills_around[1] == 0 and hills_around[5] == -1 and hills_around[7] == 0: return 3
    elif hills_around[1] == -1 and hills_around[3] == 0 and hills_around[5] == 0: return 4
    elif hills_around[1] == -1 and hills_around[3] == -1: return 5
    elif hills_around[3] == -1 and hills_around[7] == -1: return 6
    elif hills_around[5] == -1 and hills_around[7] == -1: return 7
    elif hills_around[1] == -1 and hills_around[5] == -1: return 8
    return -1


def test_hills_around(height_list, x, y):
    current_tile_height = height_list[(x, y)]
    hills_around = []
    for around in range(0, 9):
        tile_coo = (x + around % 3 - 1, y + around // 3 - 1)
        if height_list.get(tile_coo, current_tile_height) == current_tile_height: hills_around.append(0)
        if height_list.get(tile_coo, current_tile_height) < current_tile_height: hills_around.append(-1)
        if height_list.get(tile_coo, current_tile_height) > current_tile_height: hills_around.append(1)
    return hills_around


def apply_hill_sprites(layer):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            hill_texture = str(calculate_hill_texture(tile_Heights, x, y))
            if not hill_texture == "-1" and ((x, y) not in layer.keys() or "p_4" in layer.get((x, y), "")):
                layer[(x, y)] = "m_" + hill_texture


def generate_rain(layer, rain_rate):
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if random.randint(0, 100) < rain_rate:
                layer[(x, y)] = "r_" + str(random.randint(1, 2))
            elif (x, y) not in layer.keys():
                layer[(x, y)] = "r_0"
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if random.randint(0, 100) < rain_rate:
                if not taken(house_Tiles, x, y) and not taken(decoration_Tiles, x, y) and not taken(npc_Layer, x, y) and "m_" not in ground_Tiles.get((x, y), "") and "pd_" not in ground_Tiles.get((x, y), "") and "l_" not in ground_Tiles.get((x, y), "") and "st" not in ground_Tiles.get((x, y), "") and "sne_" not in ground_Tiles.get((x, y), ""):
                    layer[(x, y)] = "r_" + str(random.randint(3, 5))


def render(layer):
    correction = 0
    for x in range(0, map_Size_X):
        for y in range(0, map_Size_Y):
            if (x, y) in layer.keys():
                tile = str(layer[(x, y)])
                if "npc_" in layer[(x, y)]: correction = 3
                try:
                    screen.blit(pygame.image.load(os.path.join("resources", tile + ".png")), (x * TILE_SIZE, y * TILE_SIZE - correction))
                except Exception as e:
                    screen.blit(pygame.image.load(os.path.join("resources", "missing.png")), (x * TILE_SIZE, y * TILE_SIZE - correction))
                    print(e)

    pygame.display.update()


def add_watermark():
    for amount in range(0, math.ceil(screen_Size_X / 48)):
        screen.blit(pygame.image.load(os.path.join("resources", "randemon watermark" + ".png")), (amount * 48, screen_Size_Y - 16))


preset = input("preset: ")
if preset == "":
    map_Size_X = get_int(1, 500, "Amount of tiles on the map horizontally")
    map_Size_Y = get_int(1, 500, "Amount of tiles on the map vertically")
    sne_rate = get_int(0, 100, "Land coverage of tall grass")
    mne_rate = get_int(0, 100, "Land coverage of trees")

    x_Wallpapers = get_int(1, 100, "Amount of horizontally fitting seperate images to be generated")
    y_Wallpapers = get_int(1, 100, "Amount of vertically fitting seperate images to be generated")

    max_mountain_height = get_int(0, 100, "Maximal height of a mountain top")

    path_only_npc = input("Should npcs spawn on paths only? (y/n) ") == "y"
    npc_population = get_int(0, 100, "Population")
    house_path_type = "p_" + str(get_int(1, 3, "What type of path should be drawn between houses"))
elif preset == "default":
    map_Size_X = 80
    map_Size_Y = 50
    sne_rate = 50
    mne_rate = 30
    x_Wallpapers = 1
    y_Wallpapers = 1
    max_mountain_height = 4
    path_only_npc = False
    npc_population = 30
    house_path_type = "p_1"
elif preset == "paper":
    map_Size_X = 120
    map_Size_Y = 68
    sne_rate = 50
    mne_rate = 40
    x_Wallpapers = 1
    y_Wallpapers = 1
    max_mountain_height = 4
    path_only_npc = False
    npc_population = 30
    house_path_type = "p_1"

screen_Size_X = TILE_SIZE * map_Size_X
screen_Size_Y = TILE_SIZE * map_Size_Y
x_offset = random.randint(0, 1000000)
y_offset = random.randint(0, 1000000)
friendshipgoals = x_Wallpapers * y_Wallpapers

for background in range(friendshipgoals):
    x_offset_friendship = x_offset + map_Size_X * (background % x_Wallpapers)
    y_offset_friendship = y_offset + map_Size_Y * (background // x_Wallpapers)
    ground_Tiles = {"Lapras": False, "Diglet": False, "Gyarados": False, "Truck": False, "Snorlax": False, "Pikachu": False, "Exceguttor": False}
    npc_Layer = {}
    tile_Heights = {} #image_grayscale_to_dict("world_height_map_downscaled3.jpg")
    mne_biomes = {}
    house_Tiles = {}
    houses_Connecters = {}
    houses_Front_Doors = []
    decoration_Tiles = {}
    rain = {}
    off_Path_Npc = [14, 15, 26, 27, 28, 29, 30, 31, 32, 36, 37, 38, 39, 49]
    water_Npc = [28, 29, 30]
    shore_Npc = [31, 32, 37, 38]
    bridge_Npc = [31, 32, 36, 37, 38]
    outside_Npc = [14, 15, 26, 27, 39, 49]
    height_Tiles = {}
    print("*Creating hills*")
    mountainize(tile_Heights, max_mountain_height, x_offset_friendship, y_offset_friendship)
    print("*Filling rivers*")
    create_rivers(ground_Tiles)
    print("*building a village*")
    spawn_house(house_Tiles, 1, 4, 4, 1)

    spawn_fountain(house_Tiles)

    spawn_pokecenter(house_Tiles)
    spawn_pokemarket(house_Tiles)
    spawn_house(house_Tiles, 2, 5, 3, 1)
    spawn_house(house_Tiles, 3, 5, 4, 1)
    spawn_house(house_Tiles, 4, 4, 5, 1)
    spawn_house(house_Tiles, 5, 4, 7, 1)
    spawn_house(house_Tiles, 6, 5, 4, 1)
    spawn_house(house_Tiles, 7, 5, 4, 1)
    spawn_house(house_Tiles, 8, 4, 5, 1)
    spawn_house(house_Tiles, 9, 6, 4, 1)

    print("*Creating shores*")
    generate_beach(ground_Tiles)
    print("*Dijkstra*")
    #generate_path(ground_Tiles, house_path_type, 2)
    generate_dijkstra_path(ground_Tiles, house_path_type)
    print("*Adding some details*")
    apply_path_sprites(ground_Tiles)
    spawn_truck(house_Tiles)
    apply_hill_sprites(ground_Tiles)
    apply_water_sprites(ground_Tiles)
    print("*Spawning pokémon*")
    spawn_lapras(ground_Tiles)
    spawn_gyarados(ground_Tiles)
    spawn_snorlax(house_Tiles)
    spawn_pikachu(house_Tiles)
    spawn_exceguttor(house_Tiles)
    print("*Decorating*")
    spawn_lanterns(ground_Tiles)
    spawn_mne(ground_Tiles, mne_rate, x_offset_friendship, y_offset_friendship)
    print("*Adding humans*")
    spawn_npc(npc_Layer, npc_population, path_only_npc)
    print("*Filling empty spaces")
    fill_up_grass(ground_Tiles, sne_rate, x_offset_friendship, y_offset_friendship)
    print("*Decorating*")
    apply_hill_sprites(ground_Tiles)
    spawn_mini_boats(decoration_Tiles)
    decorate_beach(decoration_Tiles, 2.3)
    if raining:
        print("*Pouring rain*")
        generate_rain(rain, 20)

    screen = pygame.display.set_mode((screen_Size_X, screen_Size_Y))

    # generate_height_map(height_Tiles, tile_Heights)
    # render(height_Tiles)
    # time.sleep(1)

    print("*Rendering*")
    render(ground_Tiles)
    render(decoration_Tiles)
    render(house_Tiles)
    render(npc_Layer)
    render(rain)

    #add_watermark()

    cwd = os.getcwd()
    if friendshipgoals > 1:
        if background < 10:
            background_Number = "0" + str(background)
        else:
            background_Number = background
        pygame.image.save(screen, os.path.join(cwd, "saved images", str(background_Number) + ".png"))
        print("saved")

if friendshipgoals == 1:
    save = input("Save this image? (y/n/w/seed): ")
    while save == "seed" or save == "zaad":
        print(seed)
        save = input("Save this image? (y/n/seed): ")

    t = datetime.datetime.now().strftime("%G-%m-%d %H-%M-%S")
    if save == "y" or save == "w":
        pygame.image.save(screen, os.path.join("saved images", t + ".png"))
        if save == "w": ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(cwd, "saved images", t+".png"), 0)
        print("HOERA")

#sideways diagonal stairs (in src folder) are from pokemon gaia version (sta_2, sta_4, sta_5, sta_7)
