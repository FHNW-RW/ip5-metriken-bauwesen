from typing import Final, Union

import numpy as np
import pandas as pd
from pandas import DataFrame, Series

import src.package.consts as c
import json

# JSON CODES
USAGE_TYPE: Final = "type"
USAGE_PERCENTAGE: Final = "percentage"


def __decode_usages(raw_json: str):
    """ Decode usage types and percentages """

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


def __extract_usages(df: DataFrame):
    """ Extract usages as columns """

    extracted_usages = pd.DataFrame()
    usage_types = []

    # extract usages for each row
    for index, row in df.iterrows():
        usages_json = row[c.FIELD_USAGES]
        decoded_usages = __decode_usages(usages_json)

        # assign percentages for each usage type for current row
        for inner_index, inner_row in decoded_usages.iterrows():
            name = inner_row['usage']
            percentage = inner_row['percentage']

            # add column if type not present in source df
            if name not in extracted_usages:
                extracted_usages[name] = 0.0
                usage_types.append(name)

            extracted_usages.at[index, name] = percentage

        extracted_usages.fillna(inplace=True, value=0.0)

    return extracted_usages, usage_types


def __reduce_to_highest(df: DataFrame, usage_types: list, max_fields: int = 4, percentages_only: bool = False):
    """ Reduce usages to highest values (primary, secondary, tertiary and quaternary) """

    # copy usages only
    usages = df[usage_types]

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
    for object_index, object_row in usages.iterrows():
        decoded_usages = []
        decoded_percentages = []

        for usage_name, usage_percentage in object_row.iteritems():
            decoded_usages.append(usage_name)
            decoded_percentages.append(usage_percentage)

        object_usages = pd.DataFrame(list(zip(decoded_usages, decoded_percentages)), columns=['usage', 'percentage'])

        # sort usages ascending and select highest values
        decoded_usages = object_usages.sort_values(by='percentage', ascending=False)

        if len(decoded_usages) >= 1:
            primary_usages.append(decoded_usages.iloc[0]['usage'])
            primary_percentage.append(decoded_usages.iloc[0]['percentage'])
        else:
            primary_usages.append(None)
            primary_percentage.append(float(100.0))

        if len(decoded_usages) >= 2:
            secondary_usages.append(decoded_usages.iloc[1]['usage'])
            secondary_percentage.append(decoded_usages.iloc[1]['percentage'])
        else:
            secondary_usages.append(None)
            secondary_percentage.append(float(0.0))

        if len(decoded_usages) >= 3:
            tertiary_usages.append(decoded_usages.iloc[2]['usage'])
            tertiary_percentage.append(decoded_usages.iloc[2]['percentage'])
        else:
            tertiary_usages.append(None)
            tertiary_percentage.append(float(0.0))

        if len(decoded_usages) >= 4:
            quaternary_usages.append(decoded_usages.iloc[3]['usage'])
            quaternary_percentage.append(decoded_usages.iloc[3]['percentage'])
        else:
            quaternary_usages.append(None)
            quaternary_percentage.append(float(0.0))

    # prepare data to be inserted to df
    primary = np.column_stack((primary_usages, primary_percentage))
    if max_fields > 1: secondary = np.column_stack((secondary_usages, secondary_percentage))
    if max_fields > 2: tertiary = np.column_stack((tertiary_usages, tertiary_percentage))
    if max_fields > 3: quaternary = np.column_stack((quaternary_usages, quaternary_percentage))

    # replace usages in df with primary, secondary, tertiary and quaternary usages and percentages
    df[c.NOM_PRIMARY_USAGE] = primary[:, 0]
    if max_fields > 1: df[c.NOM_SECONDARY_USAGE] = secondary[:, 0]
    if max_fields > 2: df[c.NOM_TERTIARY_USAGE] = tertiary[:, 0]
    if max_fields > 3: df[c.NOM_QUATERNARY_USAGE] = quaternary[:, 0]

    df[c.PRIMARY_USAGE_PERCENTAGE] = primary[:, 1]
    if max_fields > 1: df[c.SECONDARY_USAGE_PERCENTAGE] = secondary[:, 1]
    if max_fields > 2: df[c.TERTIARY_USAGE_PERCENTAGE] = tertiary[:, 1]
    if max_fields > 3: df[c.QUATERNARY_USAGE_PERCENTAGE] = quaternary[:, 1]

    # set dtype to numeric
    df[c.PRIMARY_USAGE_PERCENTAGE] = pd.to_numeric(df[c.PRIMARY_USAGE_PERCENTAGE], errors='coerce')
    if max_fields > 1: df[c.SECONDARY_USAGE_PERCENTAGE] = pd.to_numeric(df[c.SECONDARY_USAGE_PERCENTAGE],
                                                                        errors='coerce')
    if max_fields > 2: df[c.TERTIARY_USAGE_PERCENTAGE] = pd.to_numeric(df[c.TERTIARY_USAGE_PERCENTAGE], errors='coerce')
    if max_fields > 3: df[c.QUATERNARY_USAGE_PERCENTAGE] = pd.to_numeric(df[c.QUATERNARY_USAGE_PERCENTAGE],
                                                                         errors='coerce')

    # remove usage features except garages
    if c.FIELD_GARAGE_TYPE_UG in usage_types:
        usage_types.remove(c.FIELD_GARAGE_TYPE_UG)
    if c.FIELD_GARAGE_TYPE_OG in usage_types:
        usage_types.remove(c.FIELD_GARAGE_TYPE_OG)
    df.drop(inplace=True, columns=usage_types)

    # names of new fields
    new_fields = [c.NOM_PRIMARY_USAGE,
                  c.PRIMARY_USAGE_PERCENTAGE,
                  c.FIELD_GARAGE_TYPE_UG,
                  c.FIELD_GARAGE_TYPE_OG
                  ]

    if max_fields > 1: new_fields.extend([c.NOM_SECONDARY_USAGE, c.SECONDARY_USAGE_PERCENTAGE])
    if max_fields > 2: new_fields.extend([c.NOM_TERTIARY_USAGE, c.TERTIARY_USAGE_PERCENTAGE])
    if max_fields > 3: new_fields.extend([c.NOM_QUATERNARY_USAGE, c.QUATERNARY_USAGE_PERCENTAGE])

    # remove percentage fields
    if percentages_only:
        nom_fields = [c.NOM_PRIMARY_USAGE,
                      c.NOM_SECONDARY_USAGE,
                      c.NOM_TERTIARY_USAGE,
                      c.NOM_QUATERNARY_USAGE]
        for nom_field in nom_fields:
            if nom_field in new_fields: new_fields.remove(nom_field)

    return df, new_fields


def extract_usage_details(df: DataFrame,
                          highest_only: bool = False,
                          include_garages: bool = True,
                          combine_garages: bool = True,
                          max_fields: int = 4,
                          percentages_only: bool = False) -> tuple[Union[DataFrame, Series], list]:
    """ Extract usages and add features to source df """

    data = df.copy()

    # extract usages
    usages, usage_types = __extract_usages(data)
    data = pd.concat([data, usages], axis=1)

    # replace usages by primary - quaternary
    if highest_only:
        data, new_fields = __reduce_to_highest(data,
                                               usage_types,
                                               max_fields=max_fields,
                                               percentages_only=percentages_only)
        usage_types = new_fields

    # combine garages
    if combine_garages:
        data[c.FIELD_GARAGE_COMBINED] = data[c.FIELD_GARAGE_TYPE_UG] + data[c.FIELD_GARAGE_TYPE_OG]
        data.drop(columns=[c.FIELD_GARAGE_TYPE_UG, c.FIELD_GARAGE_TYPE_OG], errors='ignore')

        usage_types.remove(c.FIELD_GARAGE_TYPE_UG)
        usage_types.remove(c.FIELD_GARAGE_TYPE_OG)
        usage_types.append(c.FIELD_GARAGE_COMBINED)

    # remove garages
    if not include_garages:
        df.drop(columns=[c.FIELD_GARAGE_TYPE_UG, c.FIELD_GARAGE_TYPE_OG, c.FIELD_GARAGE_COMBINED], errors='ignore')

        if combine_garages:
            usage_types.remove(c.FIELD_GARAGE_COMBINED)
        else:
            usage_types.remove(c.FIELD_GARAGE_TYPE_UG)
            usage_types.remove(c.FIELD_GARAGE_TYPE_OG)

    return data, usage_types
