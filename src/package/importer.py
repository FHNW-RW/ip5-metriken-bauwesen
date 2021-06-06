import json

import pandas as pd
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


def get_dataset(csv_path, remove_na=False, fill_cluster_median=False, verification_status=None) -> DataFrame:
    df = pd.read_csv(csv_path, sep=';')

    # only use neubau data from switzerland
    df = df[df[c.FIELD_NOM_COUNTRY] == c.COUNTRY_CH]
    df = df[df[c.FIELD_NEUBAU_UMBAU] == c.CONSTRUCTION_TYPE_NEUBAU]

    # use verified or partially verified if not set
    if verification_status is None:
        verification_status = [c.STATUS_VERIFIED, c.STATUS_PARTIALLY_VERIFIED]
    df = df[df[c.FIELD_VERIFICATION_STATUS].isin(verification_status)]

    # extract cost and expenses from json
    df[c.FIELD_TOTAL_EXPENSES] = df[c.FIELD_DYN_EXPENSES_JSON].apply(
        lambda jsonstr: _get_total_expenses(jsonstr))

    df[c.FIELD_COST_REF_GF] = df[c.FIELD_DYN_COST_REF].apply(
        lambda jsonstr: _get_from_json(jsonstr, c.JSON_FIELD_GF))

    df[c.FIELD_COST_REF_GSF] = df[c.FIELD_DYN_COST_REF].apply(
        lambda jsonstr: _get_from_json(jsonstr, c.JSON_FIELD_GSF))

    # remove missing data
    if remove_na:
        df.dropna(how="any")
    elif fill_cluster_median:
        # fill GF and HNF with median
        _fillna_cluster_median(df, c.FIELD_AREA_MAIN_USAGE)
        _fillna_cluster_median(df, c.FIELD_AREA_TOTAL_FLOOR_416)

    # calculate HNF / GF ratio
    df[c.FIELD_HNF_GF_RATIO] = df.eval(f'{c.FIELD_AREA_MAIN_USAGE} / {c.FIELD_AREA_TOTAL_FLOOR_416}')

    return df


def cap_upper_gf_hnf(df: DataFrame, upper_percentile='75%') -> DataFrame:
    gf_upper = df[c.FIELD_AREA_TOTAL_FLOOR_416].describe()[upper_percentile]
    hnf_upper = df[c.FIELD_AREA_MAIN_USAGE].describe()[upper_percentile]

    capped_df = df[df[c.FIELD_AREA_MAIN_USAGE] <= hnf_upper]
    capped_df = capped_df[df[c.FIELD_AREA_TOTAL_FLOOR_416] <= gf_upper]
    return capped_df


def select_relevant_features(df: DataFrame) -> DataFrame:
    return df.copy().loc[:, [
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
                                c.FIELD_COST_REF_GF,
                                c.FIELD_COST_REF_GSF,
                                c.FIELD_HNF_GF_RATIO
                            ]]
