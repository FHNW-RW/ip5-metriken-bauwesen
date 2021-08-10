from pandas import DataFrame

import src.package.consts as c
import src.package.shared as sh


def impute_mean(df: DataFrame, field: str = "", other: str = "", clustered=True, percentile: float = 0.5,
                serialize=False):
    """ fills missing values for specified field based on (clustered) mean values of other column """

    if field is "":
        field = c.FIELD_VOLUME_TOTAL_416
        other = c.FIELD_VOLUME_TOTAL_116

    # compute desired multiplication factors
    imps = __get_imputation_factors(df, field, other, clustered, percentile)

    # serialize to reuse in api
    if serialize:
        sh.serialize_object(imps, 'cluster_means')

    return imps


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
