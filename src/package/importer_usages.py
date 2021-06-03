from typing import Final

import numpy as np
from pandas import DataFrame

import src.package.consts as c
import json

# JSON CODES
USAGE_TYPE: Final = "type"
USAGE_PERCENTAGE: Final = "percentage"

# new features
GARAGE_INDOOR_PRESENT: Final = "garage_indoor"
GARAGE_OUTDOOR_PRESENT: Final = "garage_outdoor"

GARAGE_INDOOR_PERCENTAGE: Final = "garage_indoor"
GARAGE_OUTDOOR_PERCENTAGE: Final = "garage_outdoor"

NOM_PRIMARY_USAGE: Final = "nom_primary_usage"
NOM_SECONDARY_USAGE: Final = "nom_secondary_usage"
NOM_TERTIARY_USAGE: Final = "nom_tertiary_usage"
NOM_QUATERNARY_USAGE: Final = "nom_quaternary_usage"

PRIMARY_USAGE_PERCENTAGE: Final = "primary_percentage"
SECONDARY_USAGE_PERCENTAGE: Final = "secondary_percentage"
TERTIARY_USAGE_PERCENTAGE: Final = "tertiary_percentage"
QUATERNARY_USAGE_PERCENTAGE: Final = "quaternary_percentage"


# decode usage types and percentages
def __decode_usages(raw_json: str):
    decoded_usages = []
    decoded_percentages = []

    usages_dicts_raw = json.loads(raw_json)

    # remove None values
    for usage in usages_dicts_raw:
        if usage[USAGE_PERCENTAGE] is None:
            usage[USAGE_PERCENTAGE] = 0.0

    for usage in usages_dicts_raw:
        decoded_usages.append(usage[USAGE_TYPE])
        decoded_percentages.append(usage[USAGE_PERCENTAGE])

    return np.column_stack((decoded_usages, decoded_percentages))


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
    quaternary_usages = []

    primary_percentage = []
    secondary_percentage = []
    tertiary_percentage = []
    quaternary_percentage = []

    # extract values
    for index, row in df.iterrows():
        usages_json = row[c.FIELD_USAGES]
        usages = __decode_usages(usages_json)

        # sort ascending percentages
        usages = usages[usages[:, 1].argsort()[::-1]]

        if len(usages) >= 1:
            primary_usages.append(usages[0, 0])
            primary_percentage.append(usages[0, 1])
        else:
            primary_usages.append(None)
            primary_percentage.append(None)

        if len(usages) >= 2:
            secondary_usages.append(usages[1, 0])
            secondary_percentage.append(usages[1, 1])
        else:
            secondary_usages.append(None)
            secondary_percentage.append(None)

        if len(usages) >= 3:
            tertiary_usages.append(usages[2, 0])
            tertiary_percentage.append(usages[2, 1])
        else:
            tertiary_usages.append(None)
            tertiary_percentage.append(None)

        if len(usages) >= 4:
            quaternary_usages.append(usages[3, 0])
            quaternary_percentage.append(usages[3, 1])
        else:
            quaternary_usages.append(None)
            quaternary_percentage.append(None)

    primary = np.column_stack((primary_usages, primary_percentage))
    secondary = np.column_stack((secondary_usages, secondary_percentage))
    tertiary = np.column_stack((tertiary_usages, tertiary_percentage))
    quaternary = np.column_stack((quaternary_usages, quaternary_percentage))

    return primary, secondary, tertiary, quaternary


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
    return df[[c.FIELD_ID,
               NOM_PRIMARY_USAGE, PRIMARY_USAGE_PERCENTAGE,
               NOM_SECONDARY_USAGE, SECONDARY_USAGE_PERCENTAGE,
               NOM_TERTIARY_USAGE, TERTIARY_USAGE_PERCENTAGE,
               NOM_QUATERNARY_USAGE, QUATERNARY_USAGE_PERCENTAGE
               ]]


# prepare df to describe garages
def __describe_garages(df):
    return df[[GARAGE_INDOOR_PRESENT, GARAGE_OUTDOOR_PRESENT]]


# extract usages and add features to df
def extract_usage_details(df: DataFrame, shortened_df: bool):
    data = df.copy()
    primary, secondary, tertiary, quaternary = __extract_usages(data)

    data[NOM_PRIMARY_USAGE] = primary[:, 0]
    data[NOM_SECONDARY_USAGE] = secondary[:, 0]
    data[NOM_TERTIARY_USAGE] = tertiary[:, 0]
    data[NOM_QUATERNARY_USAGE] = quaternary[:, 0]

    data[PRIMARY_USAGE_PERCENTAGE] = primary[:, 1]
    data[SECONDARY_USAGE_PERCENTAGE] = secondary[:, 1]
    data[TERTIARY_USAGE_PERCENTAGE] = tertiary[:, 1]
    data[QUATERNARY_USAGE_PERCENTAGE] = quaternary[:, 1]

    if shortened_df:
        short = __describe_usages(data)
        return data, short

    return data


# extract garages and add features to df
def extract_garage_details(df: DataFrame, shortened_df: bool):
    data = df.copy()
    indoor, outdoor = __extract_garages(data)

    data[GARAGE_INDOOR_PRESENT] = indoor
    data[GARAGE_OUTDOOR_PRESENT] = outdoor

    if shortened_df:
        short = __describe_garages(data)
        return data, short

    return data
