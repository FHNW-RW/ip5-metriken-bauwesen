import json

import pandas as pd
import numpy as np
from pandas import DataFrame

import src.package.consts as c


def _get_from_json(jsonstr, attribute):
    loaded_json = json.loads(jsonstr)
    if attribute in loaded_json:
        return loaded_json[attribute]


def _get_total_expenses(jsonstr: str):
    """ Return total expenses from BKP_08 or EBKP_12 if present """
    loaded_json = json.loads(jsonstr)

    if c.JSON_FIELD_TOTAL_EXPENSES_BKP in loaded_json:
        return _get_from_json(jsonstr, c.JSON_FIELD_TOTAL_EXPENSES_BKP)

    elif c.JSON_FIELD_TOTAL_EXPENSES_EBKP in loaded_json:
        return _get_from_json(jsonstr, c.JSON_FIELD_TOTAL_EXPENSES_EBKP)


def _fillna_cluster_median(df, field):
    df[field] = df[field].fillna(df.groupby(c.FIELD_USAGE_CLUSTER)[field].transform('mean'))


def get_dataset(csv_path, raw=False, verification_status=None) -> DataFrame:
    df = pd.read_csv(csv_path, sep=';')

    if not raw:
        # only use neubau data from switzerland
        df = df[df[c.FIELD_NOM_COUNTRY] == c.COUNTRY_CH]
        df = df[df[c.FIELD_NEUBAU_UMBAU] == c.CONSTRUCTION_TYPE_NEUBAU]

        # use verified or partially verified if not set
        if verification_status is None:
            verification_status = [c.STATUS_VERIFIED, c.STATUS_PARTIALLY_VERIFIED]
        df = df[df[c.FIELD_VERIFICATION_STATUS].isin(verification_status)]

        # remove small or irrelevant usage types
        df = df[~df[c.FIELD_USAGE_CLUSTER].isin(['AUSSENANLAGEN', 'IRRELEVANT'])]

    return df


def get_extended_dataset(csv_path, remove_na=False, fill_cluster_median=False, verification_status=None,
                         cluster_threshold: int = 0, hnf_gf_ratio: bool = True) -> DataFrame:
    df = get_dataset(csv_path=csv_path, verification_status=verification_status, )

    # extract cost and expenses from json
    df[c.FIELD_TOTAL_EXPENSES] = df[c.FIELD_DYN_EXPENSES_JSON].apply(
        lambda jsonstr: _get_total_expenses(jsonstr))

    df = __import_cost_ref_fields(df)

    # remove missing data
    if remove_na:
        df.dropna(how="any")
    elif fill_cluster_median:
        # fill GF and HNF with median
        _fillna_cluster_median(df, c.FIELD_AREA_MAIN_USAGE)
        _fillna_cluster_median(df, c.FIELD_AREA_TOTAL_FLOOR_416)

    df = calculate_gf_ratio(df,
                            other_field=c.FIELD_AREA_MAIN_USAGE,
                            ratio_field=c.FIELD_HNF_GF_RATIO,
                            cut_lower=0.0,
                            cut_upper=1.0)

    # remove rows with too less cluster entries
    for cluster in df[c.FIELD_USAGE_CLUSTER].unique().copy():
        rows_of_cluster = df[df[c.FIELD_USAGE_CLUSTER] == cluster]
        if len(rows_of_cluster.index) < cluster_threshold:
            df.drop(rows_of_cluster.index, inplace=True)

    return df


def cap_upper_gf_field(df: DataFrame, upper_percentile='75%', field: str = None) -> DataFrame:
    percentile_decimal = float(upper_percentile.strip('%')) / 100.0
    gf_upper = df[c.FIELD_AREA_TOTAL_FLOOR_416].describe(percentiles=[percentile_decimal])[upper_percentile]
    if field is None:
        field_upper = df[c.FIELD_AREA_MAIN_USAGE].describe(percentiles=[percentile_decimal])[upper_percentile]
    else:
        field_upper = df[field].describe(percentiles=[percentile_decimal])[upper_percentile]

    if field is None:
        capped_df = df[df[c.FIELD_AREA_MAIN_USAGE] <= field_upper]
    else:
        capped_df = df[df[field] <= field_upper]

    capped_df = capped_df[df[c.FIELD_AREA_TOTAL_FLOOR_416] <= gf_upper]
    return capped_df


def select_relevant_features(df: DataFrame, additional_features=None) -> DataFrame:
    features = [
        c.FIELD_NOM_USAGE_MAIN,
        c.FIELD_USAGE_CLUSTER,
        c.FIELD_NOM_FACADE,
        c.FIELD_AREA_TOTAL_FLOOR_416,
        c.FIELD_AREA_NET_FLOOR_416,
        c.FIELD_AREA_MAIN_USAGE,
        c.FIELD_VOLUME_TOTAL_416,
        c.FIELD_VOLUME_TOTAL_116,
        c.FIELD_NUM_BUILDINGS,
        c.FIELD_NUM_FLOORS_OVERGROUND,
        c.FIELD_NUM_FLOORS_UNDERGROUND,
        c.FIELD_TOTAL_EXPENSES,
        # c.FIELD_COST_REF_GF, # same as area_total_floor_416
        c.FIELD_COST_REF_GSF,
        c.FIELD_HNF_GF_RATIO
    ]

    if additional_features is not None:
        features.extend(additional_features)

    return df.copy().loc[:, features]


def calculate_gf_ratio(df: DataFrame, other_field: str, ratio_field: str, cut_upper=None, cut_lower=None):
    df[ratio_field] = df.eval(f'{other_field} / {c.FIELD_AREA_TOTAL_FLOOR_416}')
    if cut_lower is not None:
        df.drop(df.loc[df[ratio_field] < cut_lower].index, inplace=True)  # ratio can not be lower than x
    if cut_upper is not None:
        df.drop(df.loc[df[ratio_field] > cut_upper].index, inplace=True)  # ratio can not be higher than x
    return df


def __import_cost_ref_fields(df):
    areas = ['GF', 'GSF', 'FAW', 'FB', 'BUF', 'VAU']

    for area in areas:
        df[eval(f'c.FIELD_COST_REF_{area}')] = df[c.FIELD_DYN_COST_REF].apply(
            lambda jsonstr: _get_from_json(jsonstr, eval(f'c.JSON_FIELD_{area}')))

    return df
