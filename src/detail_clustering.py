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
df = mani.compute_ratio_hnf_gf(df)
relevant_features = df.copy().loc[:, ['ratio_hnf_gf', im.FIELD_NOM_USAGE_MAIN]]
# relevant_features = df.copy().loc[:, ['ratio_hnf_gf']]
# relevant_features, _ = make_classification(n_samples=1000, n_features=2, n_informative=2, n_redundant=0, n_clusters_per_class=1, random_state=4)
# define the model

# define the model
model = Birch(threshold=0.01, n_clusters=10)

# fit the model
relevant_features = relevant_features.dropna(how="any")
relevant_features[im.FIELD_NOM_USAGE_MAIN] = le.fit_transform(relevant_features[im.FIELD_NOM_USAGE_MAIN])
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
    pyplot.scatter(relevant_features[row_ix, 0], relevant_features[row_ix, 1])
# show the plot
pyplot.show()
print(list(le.inverse_transform([40, 20, 10])))

# Create List of key value pairs for identified clusters
# labels = relevant_features.copy
# labels[im.FIELD_NOM_USAGE_MAIN] = le.inverse_transform(labels[im.FIELD_NOM_USAGE_MAIN])
# labels.head()


# TODO Pro Cluster wie viele von welcher Main Usage
