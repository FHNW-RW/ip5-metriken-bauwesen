from pandas import DataFrame

import src.package.importer_usages as im_usages


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
