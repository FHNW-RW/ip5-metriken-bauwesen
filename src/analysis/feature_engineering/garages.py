import pandas as pd

import src.package.consts as c


def garage_count_per_usage(df, ug_garages_separately: bool = False):
    """ adds fields with percentage of objects with garage per object primary usage type  """

    grp_df = df.groupby(c.NOM_PRIMARY_USAGE).apply(__add_total_garage_count)

    if ug_garages_separately:
        grp_df = grp_df.groupby(c.NOM_PRIMARY_USAGE).apply(__add_total_underground_garage_count)

    return grp_df


def add_garage_present(df, ug_garages_separately: bool = False):
    if ug_garages_separately:
        df[c.FIELD_FIELD_GARAGE_COMBINED_PRESENT] = df[
            (df[c.FIELD_GARAGE_TYPE_UG] > 0.0) | (df[c.FIELD_GARAGE_TYPE_OG] > 0.0)]

    else:
        df[c.FIELD_FIELD_GARAGE_COMBINED_PRESENT] = df[c.FIELD_GARAGE_COMBINED] > 0.0

    return df


def garage_avg_per_usage(df):
    """ adds field with average percentage of garage per main usage cluster """
    grp_df = df.groupby(c.NOM_PRIMARY_USAGE).apply(__add_avg_garage_percentage)

    return grp_df


def __add_total_garage_count(grp):
    """ calculates percentage of objects with garage (either indoor or outdoor) for the respecting group  """
    if c.FIELD_GARAGE_COMBINED in grp:
        garages_present = grp[(grp[c.FIELD_GARAGE_COMBINED] > 0.0)]

    else:
        garages_present = grp[
            (grp[c.FIELD_GARAGE_TYPE_UG] > 0.0) | (grp[c.FIELD_GARAGE_TYPE_OG] > 0.0)]

    grp[c.OBJECTS_WITH_GARAGES_PER_MAIN_USAGE] = (len(garages_present.index) / len(grp))

    return grp


def __add_total_underground_garage_count(grp):
    """ calculates share of objects with garage, grouped by main usage of objects  """
    garages_present = grp[(grp[c.FIELD_GARAGE_TYPE_UG] > 1.0)]
    grp[c.OBJECTS_WITH_GARAGES_UG_PER_MAIN_USAGE] = (len(garages_present.index) / len(grp))

    return grp


def __add_avg_garage_percentage(grp):
    """ calculates the average percentages of garagen area per main usage cluster  """

    if c.FIELD_GARAGE_COMBINED in grp:
        grp[c.FIELD_GARAGE_COMBINED_AVG_PERCENTAGE_PER_MAIN_USAGE] = grp[c.FIELD_GARAGE_COMBINED].mean()

    else:
        grp[c.FIELD_GARAGE_COMBINED_AVG_PERCENTAGE_PER_MAIN_USAGE] = (grp[c.FIELD_GARAGE_TYPE_UG].sum() + grp[
            c.FIELD_GARAGE_TYPE_OG].sum()) / len(grp.index)

    return grp
