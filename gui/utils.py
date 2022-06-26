"""
File with useful functions.
"""

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


def save_data_to_excel(file_name: str, xs: List[float], ys: List[float]):
    """
    Function saves data to excel file.
    :param file_name: name of file to save data;
    :param xs:
    :param ys:
    """

    data = pd.DataFrame({"x": xs, "y": ys})
    data.to_excel(file_name, engine="xlsxwriter")


def save_data_to_txt(file_name: str, xs: List[float], ys: List[float]):
    """
    Function saves data to txt file.
    :param file_name: name of file to save data;
    :param xs:
    :param ys:
    """

    with open(file_name, "w", encoding="utf-8") as file:
        for index in range(len(xs)):
            file.write(f"{xs[index]:.5f}  {ys[index]:.5f}\n")
