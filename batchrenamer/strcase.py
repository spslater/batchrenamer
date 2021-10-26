"""Methods to change the case of strings"""
import re
from random import random


def default(string):
    """no change"""
    return string


def upper(string):
    """UPPER CASE"""
    return string.upper()


def lower(string):
    """lower case"""
    return string.lower()


def title(string):
    """Title Case"""
    return string.title()


def kebab(string):
    """kebab-case"""
    return "-".join(string.split())


def dekebab(string):
    """kebab-case -> kebab case"""
    return " ".join(string.split("-"))


def snake(string):
    """snake_case"""
    return "_".join(string.split())


def desnake(string):
    """snake_case -> snake case"""
    return " ".join(string.split("_"))


def squash(string):
    """File  name -> filename"""
    return re.sub(r"\s+", "", string).strip()


def trim(string):
    """Long  File   Name -> Long File Name"""
    return re.sub(r"\s+", " ", string).strip()


def camel(string):
    """camelCase"""
    split = string.split()
    split[0] = split[0].lower()
    if len(split) > 1:
        split[1:] = [s.title() for s in split[1:]]
    return "".join(split)

def pascal(string):
    """PascalCase"""
    return "".join([s.title() for s in string.split()])


def unsquash(string):
    """camelCase / PascalCase -> camel Case / Pascal Case"""
    new = ""
    for char in string:
        new += f" {char}" if char.isupper() else char
    return new.strip()


def sponge(string):
    """sPonGeBOb CasE"""
    new = ""
    for char in string:
        if char.isalpha():
            new += char.upper() if random() > 0.5 else char.lower()
        else:
            new += char
    return new

CASE = {
    "upper": upper, "u": upper,
    "lower": lower, "l": lower,
    "title": title, "t": title,

    "kebab": kebab, "k": kebab,
    "snake": snake, "s": snake,
    "dekebab": dekebab, "dk": dekebab,
    "desnake": desnake, "ds": desnake,

    "squash": squash, "sq": squash,
    "trim": trim, "tr": trim,
    "camel": camel, "c": camel,
    "pascal": pascal, "p": pascal,
    "unsquash": unsquash, "us": unsquash,

    "sponge": sponge, "b": sponge,

    "default": default,
}
