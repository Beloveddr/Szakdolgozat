import json
from csv import reader
from os import walk

import pygame.image


def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map


def import_folder(path):
    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list


def import_one_line(path):
    with open(path, 'r') as f:
        content = f.read()
    f.close()
    return content


def change_one_line(path, data):
    with open(path, 'w') as f:
        f.write(str(data))
    f.close()


def import_ini_file(path, index):
    with open(path, 'r') as f:
        contents = f.readlines()
        dictionary = contents[index]
        parsed_contents = json.loads(dictionary)
    f.close()
    return parsed_contents


def modify_ini_file(path, index, value):
    with open(path, 'r') as f:
        content = f.read()
        converted = json.loads(content)
        converted[index] = value
    f.close()

    with open(path, 'w') as f:
        converted_again = str(converted).replace("'", '"')
        f.write(converted_again)
    f.close()


def import_last_position_file(path):
    with open(path, 'r') as f:
        content = f.read()
        file_list = content.split('\n')
    f.close()
    return file_list


def modify_stats_file(path, dict):
    f = open(path, "w")
    f.write(dict)
    f.close()
