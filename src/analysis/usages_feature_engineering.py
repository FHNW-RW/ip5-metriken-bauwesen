import src.package.importer_usages as im_usages


def garage_count(df):
    """ adds fields with percentage of objects with garage per object primary usage type  """
    grp_df = df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(add_total_garage_count)
    grp_df = grp_df.groupby(im_usages.NOM_PRIMARY_USAGE).apply(add_total_indoor_garage_count)

    return grp_df


def add_total_garage_count(grp):
    """ calculates percentage of objects with garage (either indoor or outdoor) for the respecting group  """
    garages_present = grp[
        (grp[im_usages.GARAGE_INDOOR_PRESENT] == True) | (grp[im_usages.GARAGE_OUTDOOR_PRESENT] == True)]
    grp['garages_total'] = (len(garages_present.index) / len(grp))

    return grp


def add_total_indoor_garage_count(grp):
    """ calculates percentage of objects with garage (indoor) for the respecting group  """
    garages_present = grp[(grp[im_usages.GARAGE_INDOOR_PRESENT] == True)]
    grp['indoor_garages_total'] = (len(garages_present.index) / len(grp))

    return grp
