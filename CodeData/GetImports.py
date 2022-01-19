from . import Utils
import os


def get_imports(path: str):
    """
    :param path: the path of the project to get all imports in all programs
    :return: set of imports in project
    """
    cur_path = os.path.abspath(os.getcwd()) + "/pfsp/CodeData"
    cmd = "echo " + path + " > " + cur_path + "/path.txt"
    os.system(cmd)
    cmd = "cd " + cur_path + "/buckwheat && python3 -m buckwheat.run --local -i ../path.txt -o ../ -g imports"
    os.system(cmd)
    imports = set()
    Utils.remove_file(cur_path + "/path.txt")
    with open(cur_path + "/wabbit_sequences_imports_0.txt", 'r', encoding='utf-8') as r:
        for line in r:
            imports.add(line.strip())
    #Utils.remove_file(cur_path + "/wabbit_sequences_imports_0.txt")
    return imports
