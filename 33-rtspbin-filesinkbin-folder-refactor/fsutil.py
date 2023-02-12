import os
import time


def init():
    return True


def get_path():
    now = time.localtime()

    str_path = "./data/%04d%02d%02d_%02d%02d" % (
        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)

    is_exist = os.path.exists(str_path)
    if not is_exist:
        os.makedirs(str_path)

    return str_path


def print_statistics():
    num_of_dirs, num_of_files = get_files_all("./data")
    print("total : %d directories and %d files" % (num_of_dirs, num_of_files))


def get_files_all(dir_path):
    dir_cnt = 0
    file_cnt = 0

    for (root, dirs, files) in os.walk(dir_path):
        if len(dirs) > 0:
            dir_cnt = dir_cnt + len(dirs)
        if len(files) > 0:
            file_cnt = file_cnt + len(files)
    return dir_cnt, file_cnt
