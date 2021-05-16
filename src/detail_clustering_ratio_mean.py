import numpy as np

import package.importer as im
import package.manipulations as mani

# birch clustering
from numpy import unique
from numpy import where
from sklearn.datasets import make_classification
from sklearn.cluster import Birch
from matplotlib import pyplot
from sklearn import preprocessing

le = preprocessing.LabelEncoder()

# load dataset
df = im.get_dataset('package/dataset.csv')
relevant_features = df.copy().loc[:, [im.FIELD_HNF_GF_RATIO, im.FIELD_NOM_USAGE_MAIN]]

# prepare new dataframe
uniqueRows = relevant_features.groupby(im.FIELD_NOM_USAGE_MAIN).first().reset_index()

# get different main usages
usages = df[im.FIELD_NOM_USAGE_MAIN].unique()

# calculate mean of different main usages
uniqueRows['usage_mean'] = 2
for usage in usages:
    # get data for current usage
    current_data = df[df[im.FIELD_NOM_USAGE_MAIN] == usage]
    current_mean = current_data[im.FIELD_HNF_GF_RATIO].mean()

    # assign calculated mean to usage
    uniqueRows.loc[uniqueRows[im.FIELD_NOM_USAGE_MAIN] == usage, 'usage_mean'] = current_mean

print(uniqueRows.head())

