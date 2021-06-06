import pandas as pd

import src.package.consts
import src.package.importer_usages as im_usages


def garage_count_per_usage(df):
    """ adds fields with percentage of objects with garage per object primary usage type  """
    grp_df = df.groupby(src.package.consts.NOM_PRIMARY_USAGE).apply(__add_total_garage_count)
    grp_df = grp_df.groupby(src.package.consts.NOM_PRIMARY_USAGE).apply(__add_total_indoor_garage_count)

    return grp_df


def garage_avg_per_usage(df):
    """ adds field with average percentage of garage per main usage cluster """
    garages = garage_total_percentage(df)
    grp_df = garages.groupby(src.package.consts.NOM_PRIMARY_USAGE).apply(__add_avg_garage_percentage)

    return grp_df


def garage_total_percentage(df):
    """ adds field with total percentage of garage for each object """

    df['garage_total_percentage'] = df[src.package.consts.GARAGE_INDOOR_PERCENTAGE] + df[
        src.package.consts.GARAGE_OUTDOOR_PERCENTAGE]
    df['garage_total_percentage'] = pd.to_numeric(df['garage_total_percentage']) # change dtype to float

    return df


def __add_total_garage_count(grp):
    """ calculates percentage of objects with garage (either indoor or outdoor) for the respecting group  """
    garages_present = grp[
        (grp[src.package.consts.GARAGE_INDOOR_PRESENT] == 1.0) | (grp[
                                                                      src.package.consts.GARAGE_OUTDOOR_PRESENT] == 1.0)]
    grp['garages_total'] = (len(garages_present.index) / len(grp))

    return grp


def __add_total_indoor_garage_count(grp):
    """ calculates percentage of objects with garage (indoor) for the respecting group  """
    garages_present = grp[(grp[src.package.consts.GARAGE_INDOOR_PRESENT] == 1.0)]
    grp['indoor_garages_total'] = (len(garages_present.index) / len(grp))

    return grp


def __add_avg_garage_percentage(grp):
    """ calculates percentage of objects with garage (indoor) for the respecting group  """
    grp['garages_avg'] = grp['garage_total_percentage'].mean()

    return grp
