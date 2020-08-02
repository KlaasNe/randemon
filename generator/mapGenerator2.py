import ctypes
import datetime
import os
import random
import sys
import time
from threading import Thread

from PIL import Image
import utilities.inputs as inputs
import utilities.spriteSheetManager as ssm
# from worldMap import image_grayscale_to_dict
from generators.buildingGenerator import spawn_house, add_random_ends
from generators.decorationGenerator import spawn_truck, spawn_rocks, spawn_balloon
# from worldMap import image_grayscale_to_dict
from generators.heightMapGenerator import create_hills, create_hill_edges
from generators.npcGenerator import spawn_npc
from generators.pathGenerator import apply_path_sprites, generate_dijkstra_path, create_lanterns
from generators.plantGenerator import create_trees, grow_grass, create_rain
from generators.pokemonGenerator import spawn_pokemons
from generators.waterGenerator import create_rivers, create_beach


def render2(pmap, layer, draw_sheet):
    def try_get_tile(curr_tile):
        try:
            img = sheet_writer.get_tile(curr_tile[1], curr_tile[2], curr_tile[3])
        except IndexError:
            img = sheet_writer.get_tile(curr_tile[1], curr_tile[2])
        return img

    previous_tile, previous_img = None, None
    for sw_name in sheet_writers.keys():
        sheet_writer = sheet_writers[sw_name]
        for tile_x, tile_y in getattr(pmap, layer).keys():
            current_tile = pmap.get_tile(layer, tile_x, tile_y)
            if sw_name == current_tile[0]:
                if current_tile != previous_tile:
                    try:
                        tile_img = try_get_tile(current_tile)
                        sheet_writer.draw_tile(tile_img, draw_sheet, tile_x * 16, tile_y * 16)
                        previous_tile, previous_img = pmap.get_tile(layer, tile_x, tile_y), tile_img
                    except KeyError:
                        pass
                else:
                    sheet_writer.draw_tile(previous_img, draw_sheet, tile_x * 16, tile_y * 16)


def render_npc(pmap, layer, draw_sheet):
    def try_get_tile(curr_tile):
        try:
            img = sheet_writer.get_tile(curr_tile[1], curr_tile[2], curr_tile[3])
        except IndexError:
            img = sheet_writer.get_tile(curr_tile[1], curr_tile[2])
        return img

    previous_tile, previous_img = None, None
    sheet_writer = ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "npc.png")), 20, 23)
    for tile_x, tile_y in getattr(pmap, layer).keys():
        current_tile = pmap.get_tile(layer, tile_x, tile_y)
        if current_tile != previous_tile:
            try:
                tile_img = try_get_tile(current_tile)
                sheet_writer.draw_tile(tile_img, draw_sheet, tile_x * 16, tile_y * 16 - 7)
                previous_tile, previous_img = pmap.get_tile(layer, tile_x, tile_y), tile_img
            except KeyError:
                pass
        else:
            sheet_writer.draw_tile(previous_img, draw_sheet, tile_x * 16, tile_y * 16 - 7)


class Map:

    TILE_SIZE = 16  # Side of a tile in pixels

    def __init__(self, width, height, max_hill_height, tall_grass_coverage, tree_coverage, rain_rate,
                 seed=random.randint(0, sys.maxsize)):
        self.seed = seed
        self.width = width
        self.height = height
        self.max_hill_height = max_hill_height
        self.tall_grass_coverage = tall_grass_coverage
        self.tree_coverage = tree_coverage
        self.rain_rate = rain_rate

        self.raining = False
        self.front_doors = []
        self.end_points = []
        self.tile_heights = dict()
        self.ground_layer = dict()
        self.secondary_ground = dict()
        self.buildings = dict()
        self.rain = dict()
        self.decoration_layer = dict()
        self.npc_layer = dict()
        self.height_map = dict()
        self.grass_layer = dict()

        self.highest_path = 0

        random.seed(seed)

    def out_of_bounds(self, x, y):
        return x < 0 or y < 0 or x >= self.width or y >= self.height

    def get_tile(self, layer, x, y, default=""):
        try:
            return getattr(self, layer)[(x, y)]
        except KeyError:
            return default
        except AttributeError as a:
            print(a)

    def get_tile_type(self, layer, x, y, default=""):
        try:
            return self.get_tile(layer, x, y, default)[0]
        except IndexError:
            return default


# Here starts the main program

# get command line options
parser = inputs.make_parser()
args = parser.parse_args()

if not args.credits_opt:
    sheet_writers = {
        "pa": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "path.png"))),
        "wa": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "water.png"))),
        "na": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "nature.png"))),
        "hi": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "hills.png"))),
        "ro": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "road.png"))),
        "ho": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "houses.png"))),
        "fe": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "fences.png"))),
        "po": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "pokemon.png"))),
        "de": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "decoration.png"))),
        "ra": ssm.SpriteSheetWriter(Image.open(os.path.join("resources", "rain.png")))
    }

    # full hd -> 120,68; my phone -> 68,147
    x_maps = args.x_split
    y_maps = args.y_split
    map_size_x = args.map_size_x * x_maps  # The horizontal amount of tiles the map consists of
    map_size_y = args.map_size_y * y_maps  # The vertical amount of tiles the map consists of
    all_pokemon = False
    screen_Size_X = Map.TILE_SIZE * map_size_x
    screen_Size_Y = Map.TILE_SIZE * map_size_y
    x_offset = random.randint(0, 1000000)
    y_offset = random.randint(0, 1000000)

    random_map = Map(map_size_x, map_size_y, 5, 30, 10, 0.2, args.seed_opt)

    if args.headless_opt: os.environ["SDL_VIDEODRIVER"] = "dummy"

    visual = ssm.DrawSheet(screen_Size_X, screen_Size_Y)

    to_time = time.time()
    print("*creating landscape*")
    create_hills(random_map, x_offset, y_offset)
    create_rivers(random_map)
    create_beach(random_map, x_offset, y_offset)
    add_random_ends(random_map, ("pa", 0, 0))
    create_hill_edges(random_map)
    house = time.time()
    spawn_house(random_map, "pokecenter", ("pa", 0, 0))
    spawn_house(random_map, "pokemart", ("pa", 0, 0))
    spawn_house(random_map, "gym", ("pa", 0, 0))
    spawn_house(random_map, "powerplant", ("pa", 0, 0))
    for house_type in range(22):
        for x in range(1):
            spawn_house(random_map, house_type, ("pa", 0, 0))
    random.shuffle(random_map.front_doors)
    random_map.front_doors += random_map.end_points
    generate_dijkstra_path(random_map, ("pa", 0, 0))
    apply_path_sprites(random_map)

    create_hill_edges(random_map, update=True)
    create_trees(random_map, 30, x_offset, y_offset)
    all_pokemon = spawn_pokemons(random_map)
    spawn_npc(random_map, 1)
    create_lanterns(random_map)
    spawn_truck(random_map, 0.05)
    spawn_rocks(random_map, 0.01)
    spawn_balloon(random_map)
    grow_grass(random_map, random_map.tall_grass_coverage, x_offset, y_offset)
    create_rain(random_map, 0.1, random_map.rain_rate)

    print("*rendering*")
    render2(random_map, "grass_layer", visual.drawable())
    render2(random_map, "ground_layer", visual.drawable())
    render2(random_map, "secondary_ground", visual.drawable())
    render2(random_map, "buildings", visual.drawable())
    render_npc(random_map, "npc_layer", visual.drawable())
    render2(random_map, "decoration_layer", visual.drawable())
    render2(random_map, "rain", visual.drawable())

    # generate_height_map(random_map)
    # random_map.render(random_map.height_map)
    print("time = " + str(time.time() - to_time) + " seconds")
    print("Seed: " + str(random_map.seed))

    def prompt():
        if args.save_opt:
            save = "y"
        else:
            save = input("Save this image? (y/n/w): ")
        file_name = datetime.datetime.now().strftime("%G-%m-%d %H-%M-%S")
        if save == "y" or save == "w":
            if not os.path.isdir("saved images"):
                os.mkdir("saved images")
            if x_maps * y_maps == 1:
                visual.save(file_name)
            else:
                visual.save_split(file_name, x_maps, y_maps)
            if save == "w":
                cwd = os.getcwd()
                ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.join(cwd, "saved images", file_name + ".png"), 0)

        visual.close()
        quit()

    def image_thread():
        if not args.headless_opt:
            visual.show()

    t = Thread(target=prompt)
    t.daemon = True
    img_t = Thread(target=image_thread)
    img_t.daemon = True
    t.start()
    img_t.start()
    t.join()
    img_t.join()

else:
    print(
        "\n"
        "C R E D I T S" + "\n\n"
        "* Map generator by Klaas" + "\n"
        "* Javascript stuff and various assistance by Dirk" + "\n"
        "* inputs argparser by Bethune Bryant" + "\n"
        "* Rocket balloon by Akhera" + "\n"
        "* Npc sprites ripped by Silentninja" + "\n\n"
        "(Cool ideas and some inspiration from nice redditors on r/pokemon)")
