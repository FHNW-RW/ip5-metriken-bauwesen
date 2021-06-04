import pandas as pd
from pandas import DataFrame

import src.package.importer_usages as im_usages


def garage_count_per_usage(df):
    """ adds fields with percentage of objects with garage per object primary usage type  """
    grp_df = df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(__add_total_garage_count)
    grp_df = grp_df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(__add_total_indoor_garage_count)

    return grp_df


def garage_avg_per_usage(df):
    """ adds field with average percentage of garage per main usage cluster """
    garages = garage_total_percentage(df)
    grp_df = garages.groupby(im_usages.NOM_PRIMARY_USAGE).apply(__add_avg_garage_percentage)

    return grp_df


def garage_total_percentage(df):
    """ adds field with total percentage of garage for each object """

    df['garage_total_percentage'] = df[im_usages.GARAGE_INDOOR_PERCENTAGE] + df[im_usages.GARAGE_OUTDOOR_PERCENTAGE]

    return df


def __add_total_garage_count(grp):
    """ calculates percentage of objects with garage (either indoor or outdoor) for the respecting group  """
    garages_present = grp[
        (grp[im_usages.GARAGE_INDOOR_PRESENT] == True) | (grp[im_usages.GARAGE_OUTDOOR_PRESENT] == True)]
    grp['garages_total'] = (len(garages_present.index) / len(grp))

    return grp


def __add_total_indoor_garage_count(grp):
    """ calculates percentage of objects with garage (indoor) for the respecting group  """
    garages_present = grp[(grp[im_usages.GARAGE_INDOOR_PRESENT] == True)]
    grp['indoor_garages_total'] = (len(garages_present.index) / len(grp))

    return grp


def __add_avg_garage_percentage(grp):
    """ calculates percentage of objects with garage (indoor) for the respecting group  """
    grp_sum = grp['garage_total_percentage'].sum()

    grp['garages_avg'] = (grp_sum / len(grp))

    return grp


def drop_lessthan(df: DataFrame, min: int):
    """ drops usage types with less than specified elements """
    df = df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(__add_usage_count)
    df.drop(df[df['object_per_usagetype'] < min].index, inplace=True)

    return df

def __add_usage_count(grp):
    """ calculates number of objects of the respecting group  """
    grp_count = len(grp)
    grp['object_per_usagetype'] = grp_count

    return grp


# TODO: Same for secondary?
# TODO: Same for tertiary?
