from pandas import DataFrame
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error
from sklearn.preprocessing import LabelEncoder as Le

import src.package.importer as im


def hnf_dataset(df: DataFrame):
    """ Returns dataset to estimate HNF based on GF and usage cluster """
    relevant_features = df.copy().loc[:, [im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_AREA_MAIN_USAGE, im.FIELD_USAGE_CLUSTER]]

    # preprocess dataset
    relevant_features = relevant_features.dropna(how="any")
    relevant_features[im.FIELD_USAGE_CLUSTER] = Le().fit_transform(relevant_features[im.FIELD_USAGE_CLUSTER])

    # features / labels
    X = relevant_features[[im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_USAGE_CLUSTER]]
    y = relevant_features[im.FIELD_AREA_MAIN_USAGE]

    return X, y


def l_reg_evaluation(predictions, actual, r2_value, preview_count=10):
    """ Evaluates and prints linear regression model results """

    print(f"First {preview_count} result of prediction")
    print("-------------------------")
    print("Prediction: ", predictions[:preview_count])
    print("Actual: ", actual[:preview_count])
    print()

    print("Evaluation")
    print("-------------------------")
    print("R^2 value: ", r2_value)
    print("Mean Absolute Error (MAE): ", mean_absolute_error(actual, predictions))
    print("Root Mean Squared Error (RMSE): ", mean_squared_error(actual, predictions))
    print("Max error: ", max_error(actual, predictions))
