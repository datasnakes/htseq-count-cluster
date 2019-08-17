# -*- coding: utf-8 -*-
import pandas as pd


def csvtolist(csvfile, column=0):
    """Convert a column of a csv file to a list.

    :param csvfile: A comma delimited file.
    :type csvfile: str
    :param column: The number of the column to convert.
    :type column: int
    :return: A list
    :rtype: list
    """
    df = pd.read_csv(csvfile, header=None)
    output_list = sorted(list(df[column]))

    return output_list
