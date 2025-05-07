import os

BASE_DIR = os.getcwd()
MEDIA_DIR = "static/media"

SAVE_DIR = os.path.join(BASE_DIR, MEDIA_DIR)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def join_path(directory, filename):
    filepath = os.path.join(directory, filename)
    return filepath
