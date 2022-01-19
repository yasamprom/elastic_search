import os
from shutil import rmtree


def remove_file(path: str):
    """
    must be used for removing path.txt and wabbit_sequences_names_0.txt
    :param path: path of file which should be removed
    """
    if os.path.exists(path):
        os.remove(path)


def remove_dir(path: str):
    """
    must be used for removing downloaded repository
    :param path: path of directory which should be removed
    """
    if os.path.exists(path):
        rmtree(path)

