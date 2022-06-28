"""
File with useful functions.
"""

import os
import sys
from datetime import datetime
from typing import List
import pandas as pd


def create_file_name(extension: str):
    """
    Function creates name of file.
    :param extension: extension of file.
    :return: name of file.
    """

    return datetime.now().strftime("%Y-%m-%d %H-%M-%S") + extension


def get_dir_name() -> str:
    """
    Function returns path to directory with executable file or code files.
    :return: path to directory.
    """

    if getattr(sys, "frozen", False):
        path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def save_data_to_excel(file_name: str, xs: List[float], ys: List[List[float]]):
    """
    Function saves data to excel file.
    :param file_name: name of file to save data;
    :param xs:
    :param ys:
    """

    y_data = {f"y{index}": [y[index] for y in ys] for index in range(len(ys[0]))}
    data = pd.DataFrame({"x": xs, **y_data})
    data.to_excel(file_name, engine="xlsxwriter")


def save_data_to_txt(file_name: str, xs: List[float], ys: List[List[float]]):
    """
    Function saves data to txt file.
    :param file_name: name of file to save data;
    :param xs:
    :param ys:
    """

    with open(file_name, "w", encoding="utf-8") as file:
        for index in range(len(xs)):
            file.write(f"{xs[index]:.5f}{'  '.join(map(str, ys[index]))}\n")
