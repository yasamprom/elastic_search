import os
import subprocess


def get_languages_and_readme(path, k=1):
    """
    :param path: the path of the project to define the main language for
    :param k: desired amount of most popular languages
    :return: list of two elements, first is list of pairs [rate, language] of no more than k most popular languages;
    second is list of readmes content
    """
    cur_path = os.path.abspath(os.getcwd()) + "/LanguagesAndReadme"
    cmd = cur_path + "/enry -all -doc -breakdown " + path
    p = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stats = []
    i = 0
    lines = p.stdout.readlines()
    for line in lines:
        if i >= k or line == "\n":
            break
        stats.append(line.strip().split('\t'))
        i += 1
    readme = []
    if 'Documentation\n' in lines:
        for i in range(lines.index('Documentation\n') + 1, len(lines)):
            if lines[i] == "\n":
                break
            readme.append(lines[i].strip("\n"))
    return [stats, readme]
