from pandas import DataFrame

import src.package.consts as c
import src.package.ml_helper as mlh


def impute_mean(df: DataFrame, field: str = "", other: str = "", clustered: bool = True, percentile: float = 0.5):
    """ fills missing values for specified field based on (clustered) mean values of other column """

    if field is "":
        field = c.FIELD_VOLUME_TOTAL_116
        other = c.FIELD_VOLUME_TOTAL_416

    if field is c.FIELD_VOLUME_TOTAL_416:
        other = c.FIELD_VOLUME_TOTAL_116

    # compute desired multiplication factors
    imps = __get_imputation_factors(df, field, other, clustered, percentile)
    mlh.serialize_object(imps, 'cluster_means')  # serialize to reuse in API

    # # if clustered, fill based on clustering
    # if clustered:
    #     df_cpy = df.groupby(c.FIELD_USAGE_CLUSTER).apply(
    #         lambda x: __apply_cluster_mean(x, x[c.FIELD_USAGE_CLUSTER].iloc[0], field, other, imps))
    #     return df_cpy
    #
    # # fill unclustered
    # return df.apply(
    #     lambda x: __apply_mean(x, field, other, imps))


def __get_imputation_factors(df, field, other, clustered, percentile):
    imp_df = df.copy()
    imp_df['filler_ratio'] = (imp_df[field] / imp_df[other])

    if clustered:
        imp_df = imp_df[[c.FIELD_USAGE_CLUSTER, 'filler_ratio']]
        imp_df = imp_df.groupby(c.FIELD_USAGE_CLUSTER).describe().reset_index()
        imp_df.columns = imp_df.columns.droplevel(0)
        imp_df = imp_df[["", "{:.0%}".format(percentile)]]
        return imp_df.set_index(imp_df[""]).to_dict()["{:.0%}".format(percentile)]

    imp_df = imp_df['filler_ratio'].describe()["{:.0%}".format(percentile)]
    imps = imp_df.set_index(imp_df[c.FIELD_USAGE_CLUSTER]).to_dict()['filler_ratio']

    return imps


# def __apply_cluster_mean(grp, grp_name, field, other, imps):
#     factor = imps[grp_name]
#     grp[field] = grp[field].fillna(grp[other] * float(factor))
#
#     return grp


# def __apply_mean(df, field, other, factor):
#     df[field] = df[field].fillna(df[other] * float(factor))
#
#     return df
