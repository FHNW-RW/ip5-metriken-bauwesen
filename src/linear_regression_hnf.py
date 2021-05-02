from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder as Le

import package.importer as im
import package.ml_helper as ml_helper

# load dataset
df = im.get_dataset('package/dataset.csv')
relevant_features = df.copy().loc[:, [im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_AREA_MAIN_USAGE, im.FIELD_USAGE_CLUSTER]]

# preprocess dataset
relevant_features = relevant_features.dropna(how="any")
relevant_features[im.FIELD_USAGE_CLUSTER] = Le().fit_transform(relevant_features[im.FIELD_USAGE_CLUSTER])

# features / labels
X = relevant_features[[im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_USAGE_CLUSTER]]
y = relevant_features[im.FIELD_AREA_MAIN_USAGE]

# algorithm
l_reg = linear_model.LinearRegression()

# Use 20% of package for testing the model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# train
model = l_reg.fit(X_train, y_train)

# evaluate
predictions = model.predict(X_test).astype(int)
actual = y_test.to_numpy().astype(int)
r_score = l_reg.score(X, y)
ml_helper.l_reg_evaluation(predictions, actual, r_score)
