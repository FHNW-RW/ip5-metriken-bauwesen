from typing import Final
from pandas import DataFrame

import src.package.consts as c
import json

# JSON CODES
USAGE_TYPE: Final = "type"
USAGE_PERCENTAGE: Final = "percentage"

# new features
GARAGE_INDOOR: Final = "garage_indoor"
GARAGE_OUTDOOR: Final = "garage_outdoor"

NOM_PRIMARY_USAGE: Final = "nom_primary_usage"
NOM_SECONDARY_USAGE: Final = "nom_secondary_usage"
NOM_TERTIARY_USAGE: Final = "nom_tertiary_usage"


# decode usage types and percentages
def __decode_usages(raw_json: str):
    decoded_usages = []
    decoded_percentages = []

    usages_dict_raw = json.loads(raw_json)

    for usage in usages_dict_raw:
        decoded_usages.append(usage[USAGE_TYPE])
        decoded_percentages.append(usage[USAGE_PERCENTAGE])

    return decoded_usages, decoded_percentages


# decode garages
def __decode_garages(raw_json: str):
    parking_garage = False
    outdoor_garage = False

    usages_dict_raw = json.loads(raw_json)

    for usage in usages_dict_raw:
        usage_type = usage[USAGE_TYPE]
        found_indoor = usage_type.upper().count(c.GARAGE_TYPE_INDOOR)
        found_outdoor = usage_type.upper().count(c.GARAGE_TYPE_OUTDOOR)

        if found_indoor > 0:
            parking_garage = True
        if found_outdoor > 0:
            outdoor_garage = True

    return parking_garage, outdoor_garage


# extract usages
def __extract_usages(df):
    # prepare lists
    primary_usages = []
    secondary_usages = []
    tertiary_usages = []

    for index, row in df.iterrows():
        usages_json = row[c.FIELD_USAGES]
        usages_list, percentages_list = __decode_usages(usages_json)

        if len(usages_list) >= 1:
            primary_usages.append(usages_list[0])
        else:
            primary_usages.append(None)

        if len(usages_list) >= 2:
            secondary_usages.append(usages_list[1])
        else:
            secondary_usages.append(None)

        if len(usages_list) >= 3:
            tertiary_usages.append(usages_list[2])
        else:
            tertiary_usages.append(None)

    return primary_usages, secondary_usages, tertiary_usages


#  extract garages
def __extract_garages(data):
    # prepare lists
    indoor = []
    outdoor = []

    # check all entries for garages
    for index, row in data.iterrows():
        usages_json = row[c.FIELD_USAGES]
        parking_garage_found, outdoor_garage_found = __decode_garages(usages_json)

        indoor.append(parking_garage_found)
        outdoor.append(outdoor_garage_found)

    return indoor, outdoor


# prepare df to describe usages
def __describe_usages(df):
    return df[[NOM_PRIMARY_USAGE, NOM_SECONDARY_USAGE, NOM_TERTIARY_USAGE]]


# prepare df to describe garages
def __describe_garages(df):
    return df[[GARAGE_INDOOR, GARAGE_OUTDOOR]]


# extract usages and add features to df
def extract_usage_details(df: DataFrame, shortened_df: bool):
    data = df.copy()
    primary, secondary, tertiary = __extract_usages(data)

    data[NOM_PRIMARY_USAGE] = primary
    data[NOM_SECONDARY_USAGE] = secondary
    data[NOM_TERTIARY_USAGE] = tertiary

    if shortened_df:
        short = __describe_usages(data)
        return data, short

    return data


# extract garages and add features to df
def extract_garage_details(df: DataFrame, shortened_df: bool):
    data = df.copy()
    indoor, outdoor = __extract_garages(data)

    data[GARAGE_INDOOR] = indoor
    data[GARAGE_OUTDOOR] = outdoor

    if shortened_df:
        short = __describe_garages(data)
        return data, short

    return data
