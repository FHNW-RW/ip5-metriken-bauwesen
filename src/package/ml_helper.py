from numpy import mean
from numpy import std
from pandas import DataFrame
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error, mean_absolute_percentage_error
from sklearn.model_selection import cross_validate, RepeatedKFold
from sklearn.preprocessing import LabelEncoder as Le

import src.package.importer as im


def hnf_dataset(df: DataFrame, upper_percentile=None):
    """ Returns dataset to estimate HNF based on GF and usage cluster """
    relevant_features = df.copy().loc[:,
                        [im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_AREA_MAIN_USAGE, im.FIELD_USAGE_CLUSTER]]

    # preprocess dataset
    relevant_features = relevant_features.dropna(how="any")
    relevant_features[im.FIELD_USAGE_CLUSTER] = Le().fit_transform(relevant_features[im.FIELD_USAGE_CLUSTER])

    if upper_percentile is not None:
        relevant_features = im.cap_upper_gf_hnf(relevant_features, upper_percentile=upper_percentile)

    # features / labels
    X = relevant_features[[im.FIELD_AREA_TOTAL_FLOOR_416, im.FIELD_USAGE_CLUSTER]]
    y = relevant_features[im.FIELD_AREA_MAIN_USAGE]

    return X, y


def cross_validation(model, X, y, cv=RepeatedKFold(n_splits=5, n_repeats=3, random_state=0)):
    """ Use repeated cross validation to evaluate model """

    scoring = [
        'r2',
        'neg_mean_absolute_percentage_error',
        'neg_root_mean_squared_error',
        'neg_mean_absolute_error',
        'max_error'
    ]

    return cross_validate(model, X, y, cv=cv, scoring=scoring)


def evaluate_cv_scores(scores_map):
    """ Evaluates the scores of the cross validation """

    print("Evaluation")
    print("-------------------------")
    print("Fit time: %f" % mean(scores_map["fit_time"]))
    print("Score time: %f" % mean(scores_map["score_time"]))
    print()

    for key in scores_map.keys():
        if key in {'fit_time', 'score_time'}:
            continue

        scores = scores_map[key]
        print(f'[{key}]')
        print('mean=%f std=%f' % (mean(scores), std(scores)))
        print()
    print()


def evaluate_model(predictions, actual, r2_value):
    """ Evaluates and prints model results """

    print("Evaluation")
    print("-------------------------")
    print("R^2 value: ", r2_value)
    print("Mean Absolute Error (MAE): ", mean_absolute_error(actual, predictions))
    print("Mean Absolute Percentage Error (MAPE): ", mean_absolute_percentage_error(actual, predictions))
    print("Root Mean Squared Error (RMSE): ", mean_squared_error(actual, predictions))
    print("Max error: ", max_error(actual, predictions))
    print()


def print_predictions(predictions, actual, preview_count=10):
    """ Prints actual vs. predicted values of model """

    print(f"First {preview_count} result of prediction")
    print("-------------------------")
    print("Prediction: ", predictions[:preview_count])
    print("Actual: ", actual[:preview_count])
    print()
