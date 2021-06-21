from numpy import mean, std
from pandas import DataFrame
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error, mean_absolute_percentage_error
from sklearn.model_selection import cross_validate, RepeatedKFold
from sklearn.pipeline import Pipeline

import src.package.consts as c
import src.package.importer as im
from src.package.transformers import CombineFeatures, EncodeLabelsTransformer


def hnf_dataset(df: DataFrame, upper_percentile=None):
    """ Returns dataset to estimate HNF based on GF and usage cluster """
    dataset = df.copy().loc[:, [c.FIELD_AREA_TOTAL_FLOOR_416,
                                c.FIELD_AREA_MAIN_USAGE,
                                c.FIELD_USAGE_CLUSTER,
                                c.FIELD_NOM_USAGE_MAIN]]

    # preprocess dataset
    dataset = dataset.dropna(how="any")

    transform_pipeline = Pipeline([
        ('combine_features', CombineFeatures()),
        ('encode_labels', EncodeLabelsTransformer()),
    ])
    dataset = transform_pipeline.fit_transform(dataset)

    if upper_percentile is not None:
        dataset = im.cap_upper_gf_hnf(dataset, upper_percentile=upper_percentile)

    # features / labels
    X = dataset[[c.FIELD_AREA_TOTAL_FLOOR_416, c.FIELD_COMBINED_USAGE]]
    y = dataset[c.FIELD_AREA_MAIN_USAGE]

    return X, y


def hnf_dataset_full(df: DataFrame):
    # TODO: Dataset with as many features as possible that could be useful
    # num_floors_overground
    # num_floors_underground
    # area_net_floor_416
    # num_buildings
    # garage_indoor
    # garage_outdoor
    # Maybe others?

    return None


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


def get_outliers(df, feature, factor=3):
    upper_lim = df[feature].mean() + df[feature].std() * factor
    lower_lim = df[feature].mean() - df[feature].std() * factor
    return df[(df[feature] > upper_lim) | (df[feature] < lower_lim)]
