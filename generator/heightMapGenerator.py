import random
from math import floor
from noise import snoise2


# Creates a perlin noise field to be used as height map with ints as height ranging from 0 to pmap.max_hill_height
def create_hills(pmap, x_offset, y_offset):
    octaves = 1
    freq = 80
    off_x = x_offset
    off_y = y_offset

    for y in range(0, pmap.height):
        for x in range(0, pmap.width):
            pmap.tile_heights[(x, y)] = abs(floor((snoise2((x // 3 + off_x) / freq, (y // 3 + off_y) / freq, octaves)) * pmap.max_hill_height))


# Calculates where to draw edges of hills
def create_hill_edges(pmap, update=False):

    # Determines which sprite to use at (x, y)
    def define_hill_edge_texture(x, y):

        # Looks for the tile heights around (x, y) and adds their relative height to an array. 1 means the tile is
        # situated higher than the central tile, 0 means equal height, -1 means lower
        def get_hills_around_tile():
            current_tile_height = pmap.tile_heights[(x, y)]
            hills_around_tile = []
            for around in range(0, 9):
                tile_coordinate = (x + around % 3 - 1, y + around // 3 - 1)
                if pmap.tile_heights.get(tile_coordinate, current_tile_height) > current_tile_height: hills_around_tile.append(1)
                elif pmap.tile_heights.get(tile_coordinate, current_tile_height) < current_tile_height: hills_around_tile.append(-1)
                elif pmap.tile_heights.get(tile_coordinate, current_tile_height) == current_tile_height: hills_around_tile.append(0)
            return hills_around_tile

        # using the array of relative heights, this calculates the sprite for the hill texture
        hills_around = get_hills_around_tile()
        if pmap.tile_heights.get((x, y), 0) < 2: return -1
        if hills_around[3] == 0 and hills_around[6] == -1 and hills_around[7] == 0: return 9
        if hills_around[5] == 0 and hills_around[7] == 0 and hills_around[8] == -1: return 10
        if hills_around[0] == -1 and hills_around[1] == 0 and hills_around[3] == 0: return 4
        if hills_around[1] == 0 and hills_around[2] == -1 and hills_around[5] == 0: return 4
        if hills_around[1] == -1 and hills_around[3] == -1 and hills_around[5] == -1 and hills_around[7] == -1: return 15
        if hills_around[1] == -1 and hills_around[3] == 0 and hills_around[5] == -1 and hills_around[7] == -1: return 15
        if hills_around[1] == -1 and hills_around[3] == -1 and hills_around[5] == -1 and hills_around[7] == 0: return 15
        if hills_around[1] == -1 and hills_around[3] == -1 and hills_around[5] == 0 and hills_around[7] == -1: return 15
        if hills_around[1] == 0 and hills_around[3] == -1 and hills_around[5] == -1 and hills_around[7] == -1: return 15
        if hills_around[1] == 0 and hills_around[3] == 0 and hills_around[5] == 0 and hills_around[7] == 0: return -1
        if hills_around[1] == 0 and hills_around[3] == -1 and hills_around[7] == 0: return 1
        if hills_around[3] == 0 and hills_around[5] == 0 and hills_around[7] == -1: return 2
        if hills_around[1] == 0 and hills_around[5] == -1 and hills_around[7] == 0: return 3
        if hills_around[1] == -1 and hills_around[3] == 0 and hills_around[5] == 0: return 4
        if hills_around[1] == -1 and hills_around[3] == -1: return 5
        if hills_around[3] == -1 and hills_around[7] == -1: return 6
        if hills_around[5] == -1 and hills_around[7] == -1: return 7
        if hills_around[1] == -1 and hills_around[5] == -1: return 8
        return -1

    for y in range(0, pmap.height):
        for x in range(0, pmap.width):
            hill_edge_texture = str(define_hill_edge_texture(x, y))
            if hill_edge_texture == "4" and pmap.tile_heights.get((x, y), -1) == pmap.highest_path + 1:
                hill_edge_texture += "_sg"
            elif hill_edge_texture in ["1", "3", "4", "5", "6", "7", "8"] and pmap.tile_heights.get((x, y), -1) > pmap.highest_path + 1:
                hill_edge_texture += "_s"

            if not hill_edge_texture == "-1" and "sta_" not in pmap.ground_layer.get((x, y), ""):
                if update:
                    pmap.ground_layer[(x, y)] = "m_" + hill_edge_texture
                elif (x, y) not in pmap.ground_layer.keys():
                    pmap.ground_layer[(x, y)] = "m_" + hill_edge_texture
            elif hill_edge_texture == "-1" and "m_" in pmap.ground_layer.get((x, y), ""):
                pmap.ground_layer.pop((x, y))


# Creates a visual height map which can be rendered
# It's a feature for debugging (pls dont set max height over 15 when using this)
def generate_height_map(pmap):
    for y in range(0, pmap.height):
        for x in range(0, pmap.width):
            pmap.height_map[(x, y)] = "height_" + str(pmap.tile_heights[(x, y)])

# tile_Heights = [] image_grayscale_to_dict("world_height_map_downscaled2.jpg")
