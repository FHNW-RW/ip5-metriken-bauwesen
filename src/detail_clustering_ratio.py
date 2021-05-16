from matplotlib import pyplot
# birch clustering
from numpy import unique
from numpy import where
from sklearn import preprocessing
from sklearn.cluster import Birch

import package.importer as im
import package.manipulations as mani

le = preprocessing.LabelEncoder()

# IMPORTANT NOTE: This visualisation alone is not very valuable.
# It builds the basis for future investigations
# During the process we agreed on reprioritizing

# load dataset
df = im.get_dataset('package/dataset.csv')
df = mani.compute_ratio_hnf_gf(df)
relevant_features = df.copy().loc[:, ['ratio_hnf_gf', im.FIELD_NOM_USAGE_MAIN]]

# define the model
model = Birch(threshold=0.5, n_clusters=10)

# fit the model
relevant_features = relevant_features.dropna(how="any")
relevant_features[im.FIELD_NOM_USAGE_MAIN] = le.fit_transform(relevant_features[im.FIELD_NOM_USAGE_MAIN])

# print(relevant_features.head())
relevant_features = relevant_features.to_numpy()
model.fit(relevant_features)

# assign a cluster to each example
yhat = model.predict(relevant_features)

# retrieve unique clusters
clusters = unique(yhat)

# create scatter plot for samples from each cluster
for cluster in clusters:
    # get row indexes for samples with this cluster
    row_ix = where(yhat == cluster)
    # create scatter of these samples
    pyplot.scatter(relevant_features[row_ix, 0], relevant_features[row_ix, 1], alpha=0.5)
# show the plot
pyplot.show()

# Create List of key value pairs for identified clusters
params = le.classes_
ind = 0
for value in params:
    print(ind, '->', value)
    ind += 1
