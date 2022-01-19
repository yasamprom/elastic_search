from .CodeData import Utils
from .LanguagesAndReadme import GetLanguagesAndReadme
from .CodeData import GetImports
from .CodeData import GetNames
from .CodeData import GetDocstrings
from threading import Thread
import json
import os
import subprocess


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        if self._return is None:
            raise Exception("This function hasn't return value")
        return self._return


def get_json(path: str, as_url: bool = False):
    """
    :param path: 1) path to file ( ~ doesn't work with os ) or 2) url to github repository
    :param as_url: False (default) - path is treated as 1), True - path is treated as 2)
    :return: json dump
    """

    repo_name = ""
    if as_url:
        if not os.path.exists('repos'):
            os.mkdir('repos')
        cmd = "(cd repos && git clone " + path + ")"
        p = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        if path.endswith(".git"):
            path = path[:-4]
        repo_name = path
        path = path.split("/")[-1]
        path = os.path.abspath(os.getcwd()) + "/repos/" + path

    if not os.path.exists(path):
        raise FileNotFoundError(path, "is incorrect path")

    if not as_url:
        repo_name = path.split("/")[-1]

    lang_and_readme_thread = ThreadWithReturnValue(
        target=GetLanguagesAndReadme.get_languages_and_readme, args=(path, 20,))
    import_thread = ThreadWithReturnValue(
        target=GetImports.get_imports, args=(path,))
    name_thread = ThreadWithReturnValue(
        target=GetNames.get_names, args=(path,))
    docstring_thread = ThreadWithReturnValue(
        target=GetDocstrings.get_docstrings, args=(path,))

    lang_and_readme_thread.start()
    import_thread.start()
    name_thread.start()
    docstring_thread.start()

    [stats, readme] = lang_and_readme_thread.join()
    imports = import_thread.join()
    names = name_thread.join()
    docstrings = docstring_thread.join()

    readme_content = []

    for filename in readme:
        with open(path + "/" + filename, 'r') as file:
            readme_content.append(file.read())

    print(readme)

    languages = []
    percentages = []
    for percentage, language in stats:
        percentages.append(percentage.strip("%"))
        languages.append(language)

    if as_url:
        Utils.remove_dir(path)

    return json.dumps(
        {"repo_name": repo_name, "readme": readme_content, "languages": languages,
         "percentages": percentages, "imports": list(imports),
         "names": list(names), "docstrings": list(docstrings)})
