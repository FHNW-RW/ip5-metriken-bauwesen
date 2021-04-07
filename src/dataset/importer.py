import json
from typing import Final

import pandas as pd

# check data/README.me for more info about dataset

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

# relevant features
FIELD_NOM_USAGE_MAIN: Final = "nom_usage_main"
FIELD_USAGES: Final = "usages"
FIELD_NOM_FACADE: Final = "nom_facade"
FIELD_AREA_TOTAL_FLOOR_416: Final = "area_total_floor_416"
FIELD_AREA_NET_FLOOR_416: Final = "area_net_floor_416"
FIELD_AREA_MAIN_USAGE: Final = "area_main_usage"
FIELD_VOLUME_TOTAL_416: Final = "volume_total_416"
FIELD_VOLUME_TOTAL_116: Final = "volume_total_116"
FIELD_NUM_BUILDINGS: Final = "num_buildings"
FIELD_NUM_FLOORS_OVERGROUND: Final = "num_floors_overground"
FIELD_NUM_FLOORS_UNDERGROUND: Final = "num_floors_underground"

FIELD_DYN_EXPENSES_JSON: Final = "dyn_expenses_json"
FIELD_TOTAL_EXPENSES: Final = "total_expenses"
JSON_FIELD_TOTAL_EXPENSES: Final = "BKP_08"

FIELD_DYN_COST_REF: Final = "dyn_cost_ref"
FIELD_COST_REF_GF: Final = "cost_ref_gf"
FIELD_COST_REF_GSF: Final = "cost_ref_gfs"
JSON_FIELD_GF: Final = "GF"
JSON_FIELD_GSF: Final = "GSF"

df = pd.read_csv('dataset.csv', sep=';')

# only use neubau data from switzerland that is verified
df = df[df[FIELD_NOM_COUNTRY] == COUNTRY_CH]
df = df[df[FIELD_NEUBAU_UMBAU] == CONSTRUCTION_TYPE_NEUBAU]
df = df[df[FIELD_VERIFICATION_STATUS] == STATUS_VERIFIED]


# extract json

def extract_from_json(jsonstr, attribute):
    loaded_json = json.loads(jsonstr)
    if attribute in loaded_json:
        return loaded_json[attribute]


df[FIELD_TOTAL_EXPENSES] = df[FIELD_DYN_EXPENSES_JSON].apply(
    lambda jsonstr: extract_from_json(jsonstr, JSON_FIELD_TOTAL_EXPENSES))

df[FIELD_COST_REF_GF] = df[FIELD_DYN_COST_REF].apply(
    lambda jsonstr: extract_from_json(jsonstr, JSON_FIELD_GF))

df[FIELD_COST_REF_GSF] = df[FIELD_DYN_COST_REF].apply(
    lambda jsonstr: extract_from_json(jsonstr, JSON_FIELD_GSF))

print(df[FIELD_TOTAL_EXPENSES][5])
print(df[FIELD_COST_REF_GF][11])
print(df[FIELD_COST_REF_GSF][12])

# remove missing data https://pandas.pydata.org/docs/user_guide/10min.html
