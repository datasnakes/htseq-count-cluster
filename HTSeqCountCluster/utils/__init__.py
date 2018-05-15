# -*- coding: utf-8 -*-
import pandas as pd


def csvtolist(csvfile):
    df = pd.read_csv(csvfile, header=None)
    output_list = sorted(list(df[0]))

    return output_list
