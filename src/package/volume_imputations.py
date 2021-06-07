from pandas import DataFrame

import src.package.consts as c
import src.package.importer_usages as im_usages


def impute_mean(df: DataFrame, clustered: bool = True, percentile: float = 0.5):
    """ replaces missing values of volume_total_416 with mean of respecting volume_total_116 if present """
    df = df[[c.FIELD_USAGE_CLUSTER, c.FIELD_VOLUME_TOTAL_416, c.FIELD_VOLUME_TOTAL_116]]

    # calc imputation ratios
    imp_df = df.copy()
    imp_df['volume_total_116_416_ratio'] = (imp_df[c.FIELD_VOLUME_TOTAL_116] - imp_df[c.FIELD_VOLUME_TOTAL_416]) / imp_df[
        c.FIELD_VOLUME_TOTAL_116]
    imp_df = imp_df[[c.FIELD_USAGE_CLUSTER, c.FIELD_VOLUME_TOTAL_116]]
    imp_df = imp_df.groupby(c.FIELD_USAGE_CLUSTER).describe()
    imp_df = imp_df[c.FIELD_VOLUME_TOTAL_116+"/"+"{:.0%}".format(percentile)]

    if clustered:
        df = df.groupby(c.FIELD_USAGE_CLUSTER).apply(lambda x: __apply_cluster_mean(x, x[c.FIELD_USAGE_CLUSTER].iloc[0], imp_df, percentile))

    # TODO else

    return df


def __apply_cluster_mean(grp, grp_name, imps):
    multi = imps.loc[(imps.index == grp_name)]
    grp[c.FIELD_VOLUME_TOTAL_416].fillna(grp[c.FIELD_VOLUME_TOTAL_116] * multi)

    return grp
