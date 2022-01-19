from . import Utils
import os


def get_docstrings(path: str):
    """
    :param path: the path of the project to get all imports in all programs
    :return: set of imports in project
    """
    cur_path = os.path.abspath(os.getcwd()) + "/pfsp/CodeData"
    cmd = "echo " + path + " > " + cur_path + "/path.txt"
    os.system(cmd)
    cmd = "cd " + cur_path + "/buckwheat && python3 -m buckwheat.run --local -i ../path.txt -o ../ -g docstrings"
    os.system(cmd)
    docstrings = set()
    Utils.remove_file(cur_path + "/path.txt")
    with open(cur_path + "/wabbit_sequences_docstrings_0.txt", 'r', encoding='utf-8') as r:
        is_new_el = False
        new_el = ""
        for line in r:
            if line.strip() == '"""':
                if is_new_el:
                    docstrings.add(new_el)
                is_new_el = not is_new_el
                new_el = ""
                continue
            if is_new_el:
                new_el += line
    #Utils.remove_file(cur_path + "/wabbit_sequences_docstrings_0.txt")
    return docstrings
