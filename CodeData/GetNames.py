from . import Utils
import os


def get_names(path: str):
    """
    :param path: the path of the project to get all names in all programs
    :return: set of names in project
    """
    cur_path = os.path.abspath(os.getcwd()) + "/pfsp/CodeData"
    cmd = "echo " + path + " > " + cur_path + "/path.txt"
    os.system(cmd)
    cmd = "cd " + cur_path + "/buckwheat && python3 -m buckwheat.run --local -i ../path.txt -o ../ -g names"
    os.system(cmd)
    names = set()
    Utils.remove_file(cur_path + "/path.txt")
    with open(cur_path + "/wabbit_sequences_names_0.txt", 'r', encoding='utf-8') as r:
        for line in r:
            for i in line.strip().split():
                names.add(i)
    #Utils.remove_file(cur_path + "/wabbit_sequences_names_0.txt")
    return names
