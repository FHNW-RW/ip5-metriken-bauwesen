from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder as Le

import src.package.consts as c
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
        usage_encoder = Le()
        X[c.FIELD_COMBINED_USAGE] = usage_encoder.fit_transform(X[c.FIELD_COMBINED_USAGE])
        # mlh.serialize_object(usage_encoder, 'usage_encoder')  # serialize to reuse in API

        return X
