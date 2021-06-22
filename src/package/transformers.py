from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder as Le

import src.package.consts as c
import pandas as pd
import src.package.shared as sh
import src.package.importer_usages as im_usages

usage_wohnen_mfh = ['WOHNBAUTEN__MFH_HIGH', 'WOHNBAUTEN__MFH_MEDIUM', 'WOHNBAUTEN__MFH_LOW']
usage_wohnen_efh = ['WOHNBAUTEN__EFH_REIHEN_LOW', 'WOHNBAUTEN__EFH_REIHEN_MEDIUM', 'WOHNBAUTEN__EFH_REIHEN_HIGH']
other_usages = ['ANDERES', 'OFFENE_BAUTEN', 'TECHNIK', 'IRRELEVANT', 'AUSSENANLAGEN']


def combine_usage(usage_main, usage_cluster):
    if usage_main in usage_wohnen_efh:
        return 'WOHNEN_EFH'
    elif usage_cluster in usage_wohnen_efh:
        return 'WOHNEN_MFH'
    elif usage_cluster in other_usages:
        # TODO: remove completely?
        return 'ANDERS'
    else:
        return usage_cluster


class CombineFeatures(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self  # nothing else to do

    def transform(self, X, y=None):
        # calculate HNF / GF ratio
        X[c.FIELD_HNF_GF_RATIO] = X.eval(f'{c.FIELD_AREA_MAIN_USAGE} / {c.FIELD_AREA_TOTAL_FLOOR_416}')

        # combine usage cluster with main usage
        X[c.FIELD_COMBINED_USAGE] = X.apply(
            lambda x: combine_usage(x[c.FIELD_NOM_USAGE_MAIN], x[c.FIELD_USAGE_CLUSTER]), axis=1
        )

        return X


class EncodeLabelsTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self  # nothing else to do

    def transform(self, X, y=None):
        # encode and serialize usage
        # usage_encoder = Le()
        if c.FIELD_USAGE_CLUSTER in X.columns:
            X[c.FIELD_USAGE_CLUSTER] = Le().fit_transform(X[c.FIELD_USAGE_CLUSTER])

        if c.FIELD_NOM_USAGE_MAIN in X.columns:
            X[c.FIELD_NOM_USAGE_MAIN] = Le().fit_transform(X[c.FIELD_NOM_USAGE_MAIN])

        if c.FIELD_COMBINED_USAGE in X.columns:
            X[c.FIELD_COMBINED_USAGE] = Le().fit_transform(X[c.FIELD_COMBINED_USAGE])
        # sh.serialize_object(usage_encoder, 'usage_encoder')  # serialize to reuse in API

        return X


class NumericalImputationTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, imputation_values):
        self.imputation_values = imputation_values

    def fit(self, X, y=None):
        return self  # nothing else to do

    def __apply_cluster_mean(self, grp, grp_name, field, other, imps):
        factor = imps[grp_name]
        grp[field] = grp[field].fillna(grp[other] * float(factor))

        return grp

    def __apply_mean(self, df, field, other, factor):
        df[field] = df[field].fillna(df[other] * float(factor))

    def transform(self, X, y=None):
        # impute volume values
        field = c.FIELD_VOLUME_TOTAL_416
        other = c.FIELD_VOLUME_TOTAL_116

        X = X.groupby(c.FIELD_USAGE_CLUSTER).apply(
            lambda x: self.__apply_cluster_mean(x, x[c.FIELD_USAGE_CLUSTER].iloc[0], field, other,
                                                self.imputation_values))

        return X


class OneHotEncodingTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self  # nothing else to do

    def transform(self, X, y=None):
        # transform clusters

        encoded_columns = pd.get_dummies(X[c.FIELD_USAGE_CLUSTER])
        X = X.join(encoded_columns).drop(c.FIELD_USAGE_CLUSTER, axis=1)

        return X
