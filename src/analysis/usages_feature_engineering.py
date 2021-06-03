from typing import Final

import pandas as pd
import numpy as np
from pandas import DataFrame

import src.package.consts as c
import src.package.importer_usages as im_usages
import json


def garage_count(df):
    grp_df = df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(add_total_garage_count)
    grp_df = grp_df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(add_total_indoor_garage_count)

    return grp_df


def add_total_garage_count(grp):
    garages_present = grp[
        (grp[im_usages.GARAGE_INDOOR_PRESENT] == True) | (grp[im_usages.GARAGE_OUTDOOR_PRESENT] == True)]
    grp['garages_total'] = (len(garages_present.index) / len(grp))

    return grp


def add_total_indoor_garage_count(grp):
    garages_present = grp[(grp[im_usages.GARAGE_INDOOR_PRESENT] == True)]
    grp['indoor_garages_total'] = (len(garages_present.index) / len(grp))

    return grp
