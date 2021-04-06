import pandas as pd
from typing import Final

# check data/README.me for more info about dataset

# relevant features
ID: Final = "id"
SOURCE: Final = "source"
VERIFICATION_STATUS: Final = "verification_status"
TITLE: Final = "title"
NEUBAU_UMBAU: Final = "neubau_umbau"
NOM_USAGE_MAIN: Final = "nom_usage_main"
USAGES: Final = "usages"
NOM_FACADE: Final = "nom_facade"
AREA_TOTAL_FLOOR_416: Final = "area_total_floor_416"
AREA_NET_FLOOR_416: Final = "area_net_floor_416"
AREA_MAIN_USAGE: Final = "area_main_usage"
VOLUME_TOTAL_416: Final = "volume_total_416"
VOLUME_TOTAL_116: Final = "volume_total_116"
NUM_BUILDINGS: Final = "num_buildings"
NUM_FLOORS_OVERGROUND: Final = "num_floors_overground"
NUM_FLOORS_UNDERGROUND: Final = "num_floors_underground"
DYN_EXPENSES_JSON: Final = "dyn_expenses_json"
DYN_COST_REF: Final = "dyn_cost_ref"

# TODO: analyse jsons and get relevant features out of it

# relevant features of "dyn_expenses_json"

# relevant features of "dyn_cost_ref"

dataset = pd.read_csv('dataset.csv', sep='delimiter')
print(dataset.head(5))


# remove missing data https://pandas.pydata.org/docs/user_guide/10min.html

