from typing import Final

import numpy as np
import pandas as pd
from pandas import DataFrame

import src.package.consts as c
import json

# JSON CODES
USAGE_TYPE: Final = "type"
USAGE_PERCENTAGE: Final = "percentage"

# new features
GARAGE_INDOOR_PRESENT: Final = "garage_indoor"
GARAGE_OUTDOOR_PRESENT: Final = "garage_outdoor"

GARAGE_INDOOR_PERCENTAGE: Final = "garage_indoor_percentage"
GARAGE_OUTDOOR_PERCENTAGE: Final = "garage_outdoor_percentage"

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

    parking_garage_percentage = 0.0
    outdoor_garage_percentage = 0.0

    usages = __decode_usages(raw_json)

    for usage in usages:
        if c.GARAGE_TYPE_INDOOR in usage[0]:
            parking_garage = True
            parking_garage_percentage = float(usage[1])

        if c.GARAGE_TYPE_OUTDOOR in usage[0]:
            outdoor_garage = True
            outdoor_garage_percentage = float(usage[1])

    return parking_garage, outdoor_garage, parking_garage_percentage, outdoor_garage_percentage


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
            primary_percentage.append(float(usages[0, 1]))
        else:
            primary_usages.append(None)
            primary_percentage.append(None)

        if len(usages) >= 2:
            secondary_usages.append(usages[1, 0])
            secondary_percentage.append(float(usages[1, 1]))
        else:
            secondary_usages.append(None)
            secondary_percentage.append(None)

        if len(usages) >= 3:
            tertiary_usages.append(usages[2, 0])
            tertiary_percentage.append(float(usages[2, 1]))
        else:
            tertiary_usages.append(None)
            tertiary_percentage.append(None)

        if len(usages) >= 4:
            quaternary_usages.append(usages[3, 0])
            quaternary_percentage.append(float(usages[3, 1]))
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
    indoor_present = []
    outdoor_present = []

    indoor_percentages = []
    outdoor_percentages = []

    # check all entries for garages
    for index, row in data.iterrows():
        usages_json = row[c.FIELD_USAGES]
        parking_garage_found, outdoor_garage_found, indoor_percentage, outdoor_percentage = __decode_garages(
            usages_json)

        indoor_present.append(parking_garage_found)
        indoor_percentages.append(indoor_percentage)

        outdoor_present.append(outdoor_garage_found)
        outdoor_percentages.append(outdoor_percentage)

    return np.column_stack((indoor_present, indoor_percentages, outdoor_present, outdoor_percentages))


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
    return df[[GARAGE_INDOOR_PRESENT, GARAGE_INDOOR_PERCENTAGE,
               GARAGE_OUTDOOR_PRESENT, GARAGE_OUTDOOR_PERCENTAGE
               ]]


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

    # set dtype to numeric
    data[PRIMARY_USAGE_PERCENTAGE] = pd.to_numeric(data[PRIMARY_USAGE_PERCENTAGE], errors='coerce')
    data[SECONDARY_USAGE_PERCENTAGE] = pd.to_numeric(data[SECONDARY_USAGE_PERCENTAGE], errors='coerce')
    data[TERTIARY_USAGE_PERCENTAGE] = pd.to_numeric(data[TERTIARY_USAGE_PERCENTAGE], errors='coerce')
    data[QUATERNARY_USAGE_PERCENTAGE] = pd.to_numeric(data[QUATERNARY_USAGE_PERCENTAGE], errors='coerce')

    if shortened_df:
        short = __describe_usages(data)
        return data, short

    return data


# extract garages and add features to df
def extract_garage_details(df: DataFrame, shortened_df: bool):
    data = df.copy()
    garages_info = __extract_garages(data)

    data[GARAGE_INDOOR_PRESENT] = garages_info[:, 0]
    data[GARAGE_INDOOR_PERCENTAGE] = garages_info[:, 1]

    data[GARAGE_OUTDOOR_PRESENT] = garages_info[:, 2]
    data[GARAGE_OUTDOOR_PERCENTAGE] = garages_info[:, 3]

    # set dtype to numeric
    data[GARAGE_INDOOR_PERCENTAGE] = pd.to_numeric(data[GARAGE_INDOOR_PERCENTAGE], errors='coerce')
    data[GARAGE_OUTDOOR_PERCENTAGE] = pd.to_numeric(data[GARAGE_OUTDOOR_PERCENTAGE], errors='coerce')

    if shortened_df:
        short = __describe_garages(data)
        return data, short

    return data
