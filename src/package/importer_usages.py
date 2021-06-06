from typing import Final

import numpy as np
import pandas as pd
from pandas import DataFrame

import src.package.consts as c
import src.package.importer as imp
import json


# TODO combine garage and usages in one function
# decode usage types and percentages
def __decode_usages(raw_json: str):
    decoded_usages = []
    decoded_percentages = []

    usages_dicts_raw = json.loads(raw_json)

    # remove None values
    for usage in usages_dicts_raw:
        if usage[c.USAGE_PERCENTAGE] is None:
            usage[c.USAGE_PERCENTAGE] = float(0.0)

    for usage in usages_dicts_raw:
        decoded_usages.append(usage[c.USAGE_TYPE])
        decoded_percentages.append(float(usage[c.USAGE_PERCENTAGE]))

    return pd.DataFrame(list(zip(decoded_usages, decoded_percentages)), columns=['usage', 'percentage'])


# decode garages
def __decode_garages(raw_json: str):
    parking_garage = False
    outdoor_garage = False

    parking_garage_percentage = 0.0
    outdoor_garage_percentage = 0.0

    usages = __decode_usages(raw_json)

    # check for garages
    if len(usages[usages['usage'].str.contains(c.GARAGE_TYPE_INDOOR)]) > 0:
        parking_garage = True
        parking_garage_percentage = usages[usages['usage'].str.contains(c.GARAGE_TYPE_INDOOR)]['percentage'].sum()

    if len(usages[usages['usage'].str.contains(c.GARAGE_TYPE_OUTDOOR)]) > 0:
        outdoor_garage = True
        outdoor_garage_percentage = usages[usages['usage'].str.contains(c.GARAGE_TYPE_OUTDOOR)]['percentage'].sum()

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

        # TODO
        if row[c.FIELD_ID] == 353.0:
            print(row)

        usages = __decode_usages(usages_json)

        # sort ascending percentages
        usages = usages.sort_values(by='percentage', ascending=False)

        if len(usages) >= 1:
            primary_usages.append(usages.iloc[0]['usage'])
            primary_percentage.append(usages.iloc[0]['percentage'])
        else:
            primary_usages.append(None)
            primary_percentage.append(None)

        if len(usages) >= 2:
            secondary_usages.append(usages.iloc[1]['usage'])
            secondary_percentage.append(usages.iloc[1]['percentage'])
        else:
            secondary_usages.append(None)
            secondary_percentage.append(None)

        if len(usages) >= 3:
            tertiary_usages.append(usages.iloc[2]['usage'])
            tertiary_percentage.append(usages.iloc[2]['percentage'])
        else:
            tertiary_usages.append(None)
            tertiary_percentage.append(None)

        if len(usages) >= 4:
            quaternary_usages.append(usages.iloc[3]['usage'])
            quaternary_percentage.append(usages.iloc[3]['percentage'])
        else:
            quaternary_usages.append(None)
            quaternary_percentage.append(None)

    primary = np.column_stack((primary_usages, primary_percentage))
    secondary = np.column_stack((secondary_usages, secondary_percentage))
    tertiary = np.column_stack((tertiary_usages, tertiary_percentage))
    quaternary = np.column_stack((quaternary_usages, quaternary_percentage))

    return primary, secondary, tertiary, quaternary


#  extract garages
def __extract_garages(df):
    # prepare lists
    indoor_present = []
    outdoor_present = []

    indoor_percentages = []
    outdoor_percentages = []

    # check for garages
    for index, row in df.iterrows():
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
               c.NOM_PRIMARY_USAGE, c.PRIMARY_USAGE_PERCENTAGE,
               c.NOM_SECONDARY_USAGE, c.SECONDARY_USAGE_PERCENTAGE,
               c.NOM_TERTIARY_USAGE, c.TERTIARY_USAGE_PERCENTAGE,
               c.NOM_QUATERNARY_USAGE, c.QUATERNARY_USAGE_PERCENTAGE
               ]]


# prepare df to describe garages
def __describe_garages(df):
    return df[[c.GARAGE_INDOOR_PRESENT, c.GARAGE_INDOOR_PERCENTAGE,
               c.GARAGE_OUTDOOR_PRESENT, c.GARAGE_OUTDOOR_PERCENTAGE
               ]]


#  TODO import from basic importer automatically
# extract usages and add features to df
def extract_usage_details(df: DataFrame, shortened_df: bool = False):
    data = df.copy()
    primary, secondary, tertiary, quaternary = __extract_usages(data)

    data[c.NOM_PRIMARY_USAGE] = primary[:, 0]
    data[c.NOM_SECONDARY_USAGE] = secondary[:, 0]
    data[c.NOM_TERTIARY_USAGE] = tertiary[:, 0]
    data[c.NOM_QUATERNARY_USAGE] = quaternary[:, 0]

    data[c.PRIMARY_USAGE_PERCENTAGE] = primary[:, 1]
    data[c.SECONDARY_USAGE_PERCENTAGE] = secondary[:, 1]
    data[c.TERTIARY_USAGE_PERCENTAGE] = tertiary[:, 1]
    data[c.QUATERNARY_USAGE_PERCENTAGE] = quaternary[:, 1]

    # set dtype to numeric
    data[c.PRIMARY_USAGE_PERCENTAGE] = pd.to_numeric(data[c.PRIMARY_USAGE_PERCENTAGE], errors='coerce')
    data[c.SECONDARY_USAGE_PERCENTAGE] = pd.to_numeric(data[c.SECONDARY_USAGE_PERCENTAGE], errors='coerce')
    data[c.TERTIARY_USAGE_PERCENTAGE] = pd.to_numeric(data[c.TERTIARY_USAGE_PERCENTAGE], errors='coerce')
    data[c.QUATERNARY_USAGE_PERCENTAGE] = pd.to_numeric(data[c.QUATERNARY_USAGE_PERCENTAGE], errors='coerce')

    if shortened_df:
        short = __describe_usages(data)
        return data, short

    return data


#  TODO import from basic importer automatically
# extract garages and add features to df
def extract_garage_details(df: DataFrame, shortened_df: bool = False):
    data = df.copy()
    garages_info = __extract_garages(data)

    data[c.GARAGE_INDOOR_PRESENT] = garages_info[:, 0]
    data[c.GARAGE_INDOOR_PERCENTAGE] = garages_info[:, 1]

    data[c.GARAGE_OUTDOOR_PRESENT] = garages_info[:, 2]
    data[c.GARAGE_OUTDOOR_PERCENTAGE] = garages_info[:, 3]

    # set dtype to numeric
    data[c.GARAGE_INDOOR_PERCENTAGE] = pd.to_numeric(data[c.GARAGE_INDOOR_PERCENTAGE], errors='coerce')
    data[c.GARAGE_OUTDOOR_PERCENTAGE] = pd.to_numeric(data[c.GARAGE_OUTDOOR_PERCENTAGE], errors='coerce')

    if shortened_df:
        short = __describe_garages(data)
        return data, short

    return data


# select relevant features including garage and multiple usage features
def select_relevant_features(df: DataFrame) -> DataFrame:
    df_rel = imp.select_relevant_features(df)
    df_rel_usg = df.copy().loc[:, [
                                      c.NOM_PRIMARY_USAGE,
                                      c.PRIMARY_USAGE_PERCENTAGE,
                                      c.NOM_SECONDARY_USAGE,
                                      c.SECONDARY_USAGE_PERCENTAGE,
                                      c.NOM_TERTIARY_USAGE,
                                      c.TERTIARY_USAGE_PERCENTAGE,
                                      c.NOM_QUATERNARY_USAGE,
                                      c.QUATERNARY_USAGE_PERCENTAGE,
                                      c.GARAGE_INDOOR_PRESENT,
                                      c.GARAGE_INDOOR_PERCENTAGE,
                                      c.GARAGE_OUTDOOR_PRESENT,
                                      c.GARAGE_OUTDOOR_PERCENTAGE
                                  ]]
    return pd.concat([df_rel_usg, df_rel], axis=1)
