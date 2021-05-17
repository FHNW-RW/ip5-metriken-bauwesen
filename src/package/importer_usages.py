from pandas import DataFrame

import src.package.importer as im
import json

# decode usage types and percentages
def __decode_json(raw_json: str):
    decoded_usages = []
    decoded_percentages = []
    usages_dict_raw = json.loads(raw_json)

    for usage in usages_dict_raw:
        decoded_usages.append(usage['type'])
        decoded_percentages.append(usage['percentage'])

    return decoded_usages, decoded_percentages


# assign decoded usages to dataframe
def __extract_usages(df):
    # prepare lists
    primary_usages = []
    secondary_usages = []
    tertiary_usages = []

    for index, row in df.iterrows():
        usages_json = row[im.FIELD_USAGES]
        usages_list, percentages_list = __decode_json(usages_json)

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


# describe usages
def __describe_usages(df):
    return df[['nom_primary_usage', 'nom_secondary_usage', 'nom_tertiary_usage']]


# extract usages and add features to df
def extract_usage_details(df: DataFrame, describe: bool):
    data = df.copy()
    primary, secondary, tertiary = __extract_usages(data)

    # print(type(primary))
    # print(len(primary))

    # se = DataFrame.Series(primary)
    # df['new_col'] = se.values

    data['nom_primary_usage'] = primary
    data['nom_secondary_usage'] = secondary
    data['nom_tertiary_usage'] = tertiary

    if describe:
        short = __describe_usages(data)
        return data, short

    return data
