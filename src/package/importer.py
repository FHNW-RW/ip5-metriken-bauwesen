import json
from typing import Final

import pandas as pd
from pandas import DataFrame

# check data/README.me for more info about package

# general data info
FIELD_ID: Final = "id"
FIELD_SOURCE: Final = "source"
FIELD_TITLE: Final = "title"

# country
FIELD_NOM_COUNTRY: Final = "nom_country"
COUNTRY_CH: Final = "SWITZERLAND"
COUNTRY_DE: Final = "GERMANY"

# verification status
FIELD_VERIFICATION_STATUS: Final = "verification_status"
STATUS_VERIFIED: Final = "VERIFIED_OK"
STATUS_NOT_VERIFIED: Final = "NOT_VERIFIED"
STATUS_PARTIALLY_VERIFIED: Final = "PARTIALLY_VERIFIED"
STATUS_VERIFIED_OK_BUT_UNSUITABLE: Final = "VERIFIED_OK_BUT_UNSUITABLE"

# construction type
FIELD_NEUBAU_UMBAU: Final = "neubau_umbau"
CONSTRUCTION_TYPE_NEUBAU: Final = "NEUBAU"
CONSTRUCTION_TYPE_UMBAU: Final = "UMBAU"
CONSTRUCTION_TYPE_NEU_UND_UMBAU: Final = "NEU_UND_UMBAU"

# elevators
FIELD_ELEVATOR_PRESENT: Final = "bool_elevators"
FIELD_NUM_ELEVATOR: Final = "num_elevators"
FIELD_ELEVATOR_INCLINED_PRESENT: Final = "bool_elevators_inclined"
FIELD_NUM_ELEVATOR_INCLINED: Final = "num_elevators_inclined"

# usages
FIELD_USAGES: Final = "usages"
FIELD_USAGE_CLUSTER: Final = "usage_cluster"
FIELD_NOM_USAGE_MAIN: Final = "nom_usage_main"

# relevant features
FIELD_NOM_FACADE: Final = "nom_facade"
FIELD_AREA_TOTAL_FLOOR_416: Final = "area_total_floor_416"
FIELD_AREA_NET_FLOOR_416: Final = "area_net_floor_416"
FIELD_AREA_MAIN_USAGE: Final = "area_main_usage"
FIELD_VOLUME_TOTAL_416: Final = "volume_total_416"
FIELD_VOLUME_TOTAL_116: Final = "volume_total_116"
FIELD_NUM_BUILDINGS: Final = "num_buildings"
FIELD_NUM_FLOORS_OVERGROUND: Final = "num_floors_overground"
FIELD_NUM_FLOORS_UNDERGROUND: Final = "num_floors_underground"
FIELD_HNF_GF_RATIO: Final = "ratio_hnf_gf"

FIELD_DYN_EXPENSES_JSON: Final = "dyn_expenses_json"
FIELD_TOTAL_EXPENSES: Final = "total_expenses"
JSON_FIELD_TOTAL_EXPENSES_BKP: Final = "BKP_08"
JSON_FIELD_TOTAL_EXPENSES_EBKP: Final = "EBKP_12"

FIELD_DYN_COST_REF: Final = "dyn_cost_ref"
FIELD_COST_REF_GF: Final = "cost_ref_gf"
FIELD_COST_REF_GSF: Final = "cost_ref_gfs"
JSON_FIELD_GF: Final = "GF"
JSON_FIELD_GSF: Final = "GSF"


def _get_from_json(jsonstr, attribute):
    loaded_json = json.loads(jsonstr)
    if attribute in loaded_json:
        return loaded_json[attribute]


def _get_total_expenses(jsonstr: str):
    """ Return total expenses from BKP_08 or EBKP_12 if present """
    loaded_json = json.loads(jsonstr)

    if JSON_FIELD_TOTAL_EXPENSES_BKP in loaded_json:
        return _get_from_json(jsonstr, JSON_FIELD_TOTAL_EXPENSES_BKP)

    elif JSON_FIELD_TOTAL_EXPENSES_EBKP in loaded_json:
        return _get_from_json(jsonstr, JSON_FIELD_TOTAL_EXPENSES_EBKP)


def _fillna_cluster_median(df, field):
    df[field] = df[field].fillna(df.groupby(FIELD_USAGE_CLUSTER)[field].transform('mean'))


def get_dataset(csv_path, remove_na=False, fill_cluster_median=False) -> DataFrame:
    df = pd.read_csv(csv_path, sep=';')

    # only use neubau data from switzerland that is verified
    df = df[df[FIELD_NOM_COUNTRY] == COUNTRY_CH]
    df = df[df[FIELD_NEUBAU_UMBAU] == CONSTRUCTION_TYPE_NEUBAU]
    df = df[df[FIELD_VERIFICATION_STATUS] == STATUS_VERIFIED]

    # extract cost and expenses from json
    df[FIELD_TOTAL_EXPENSES] = df[FIELD_DYN_EXPENSES_JSON].apply(
        lambda jsonstr: _get_total_expenses(jsonstr))

    df[FIELD_COST_REF_GF] = df[FIELD_DYN_COST_REF].apply(
        lambda jsonstr: _get_from_json(jsonstr, JSON_FIELD_GF))

    df[FIELD_COST_REF_GSF] = df[FIELD_DYN_COST_REF].apply(
        lambda jsonstr: _get_from_json(jsonstr, JSON_FIELD_GSF))

    # remove missing data
    if remove_na:
        df.dropna(how="any")
    elif fill_cluster_median:
        # fill GF and HNF with median
        _fillna_cluster_median(df, FIELD_AREA_MAIN_USAGE)
        _fillna_cluster_median(df, FIELD_AREA_TOTAL_FLOOR_416)

    # calculate HNF / GF ratio
    df[FIELD_HNF_GF_RATIO] = df.eval(f'{FIELD_AREA_MAIN_USAGE} / {FIELD_AREA_TOTAL_FLOOR_416}')

    return df


def cap_upper_gf_hnf(df: DataFrame, gf_upper_percentile='75%', hnf_upper_percentile='75%') -> DataFrame:
    gf_upper = df[FIELD_AREA_TOTAL_FLOOR_416].describe()[gf_upper_percentile]
    hnf_upper = df[FIELD_AREA_MAIN_USAGE].describe()[hnf_upper_percentile]

    capped_df = df[df[FIELD_AREA_MAIN_USAGE] <= hnf_upper]
    capped_df = capped_df[df[FIELD_AREA_TOTAL_FLOOR_416] <= gf_upper]
    return capped_df


def select_relevant_features(df: DataFrame) -> DataFrame:
    return df.copy().loc[:, [
                                FIELD_NOM_USAGE_MAIN,
                                FIELD_USAGE_CLUSTER,
                                FIELD_NOM_FACADE,
                                FIELD_AREA_TOTAL_FLOOR_416,
                                FIELD_AREA_NET_FLOOR_416,
                                FIELD_AREA_MAIN_USAGE,
                                FIELD_VOLUME_TOTAL_416,
                                FIELD_VOLUME_TOTAL_116,
                                FIELD_NUM_BUILDINGS,
                                FIELD_NUM_FLOORS_OVERGROUND,
                                FIELD_NUM_FLOORS_UNDERGROUND,
                                FIELD_TOTAL_EXPENSES,
                                FIELD_COST_REF_GF,
                                FIELD_COST_REF_GSF,
                            ]]
