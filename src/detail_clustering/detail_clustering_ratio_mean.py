# birch clustering
import matplotlib.pyplot as plt
from sklearn import preprocessing

import package.importer as im

le = preprocessing.LabelEncoder()

# IMPORTANT NOTE: This visualisation alone is not very valuable.
# It builds the basis for future investigations
# During the process we agreed on reprioritizing this matter

# load dataset
df = im.get_dataset('package/dataset.csv')
relevant_features = df.copy().loc[:, [im.FIELD_HNF_GF_RATIO, im.FIELD_NOM_USAGE_MAIN]]

# prepare new dataframe
mean_per_usage = relevant_features.groupby(im.FIELD_NOM_USAGE_MAIN).first().reset_index()

# get different main usages
usages = df[im.FIELD_NOM_USAGE_MAIN].unique()

# calculate mean of different main usages
mean_per_usage['usage_mean'] = 2
for usage in usages:
    # get data for current usage
    current_data = df[df[im.FIELD_NOM_USAGE_MAIN] == usage]
    current_mean = current_data[im.FIELD_HNF_GF_RATIO].mean()

    # assign calculated mean to usage
    mean_per_usage.loc[mean_per_usage[im.FIELD_NOM_USAGE_MAIN] == usage, 'usage_mean'] = current_mean

# assign numerical values to main usages
mean_per_usage[im.FIELD_NOM_USAGE_MAIN] = le.fit_transform(mean_per_usage[im.FIELD_NOM_USAGE_MAIN])

# plot mean for each main usage
print(mean_per_usage.head())
mean_per_usage = mean_per_usage[[im.FIELD_NOM_USAGE_MAIN, 'usage_mean']]
cols = list(mean_per_usage.columns.values)
mean_per_usage = mean_per_usage.to_numpy()

plt.scatter(mean_per_usage[:, 0], mean_per_usage[:, 1])
plt.show()

# Create List of key value pairs for identified clusters
params = le.classes_
ind = 0
for value in params:
    print(ind, '->', value)
    ind += 1
