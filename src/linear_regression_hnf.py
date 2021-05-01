from sklearn import linear_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder as Le

import dataset.importer as im

df = im.get_dataset('dataset/dataset.csv')
relevant_features = df.copy().loc[:, [im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_AREA_MAIN_USAGE, im.FIELD_USAGE_CLUSTER]]
print(relevant_features.head())

# preprocessing dataset
relevant_features = relevant_features.dropna(how="any")
relevant_features[im.FIELD_USAGE_CLUSTER] = Le().fit_transform(relevant_features[im.FIELD_USAGE_CLUSTER])
print(relevant_features.head())

# features / labels
X = relevant_features[[im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_USAGE_CLUSTER]]
y = relevant_features[im.FIELD_AREA_MAIN_USAGE]

# algorithm
l_reg = linear_model.LinearRegression()

# Use 20% of dataset for testing the model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# train
model = l_reg.fit(X_train, y_train)
predictions = model.predict(X_test)
actual = y_test.to_numpy()

# evaluate
print("Prediction: ", predictions[:10].astype(int))
print("Actual: ", actual[:10])

print("R^2 value: ", l_reg.score(X, y))
print("Mean Absolute Error (MAE): ", mean_absolute_error(actual, predictions))
print("Root Mean Squared Error (RMSE): ", mean_squared_error(actual, predictions))
print("Max error: ", max_error(actual, predictions))
