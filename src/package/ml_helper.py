from numpy import mean, std
from pandas import DataFrame
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error, mean_absolute_percentage_error
from sklearn.model_selection import cross_validate, RepeatedKFold
from sklearn.pipeline import Pipeline

import src.package.consts as c
import src.package.importer as im
import src.package.numeric_imputations as nimp
from src.package.transformers import CombineFeatures, EncodeLabelsTransformer, NumericalImputationTransformer, \
    OneHotEncodingTransformer


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
        ('one_hot_encoder', OneHotEncodingTransformer()),
        # ('encode_labels', EncodeLabelsTransformer()),
    ])
    dataset = transform_pipeline.fit_transform(dataset)

    if upper_percentile is not None:
        dataset = im.cap_upper_gf_hnf(dataset, upper_percentile=upper_percentile)

    # features / labels
    X = dataset[[c.FIELD_AREA_TOTAL_FLOOR_416, c.FIELD_USAGE_CLUSTER]]
    y = dataset[c.FIELD_AREA_MAIN_USAGE]

    return X, y


def hnf_dataset_full(df: DataFrame, features=None, remove_features=None):
    # TODO: nom_facade & nom_usage_main encode?

    # add default features
    if features is None:
        features = [
            c.FIELD_AREA_TOTAL_FLOOR_416,
            c.FIELD_USAGE_CLUSTER,
            # c.FIELD_NOM_USAGE_MAIN,
            # c.FIELD_NUM_FLOORS_UNDERGROUND,
            # c.FIELD_NUM_FLOORS_OVERGROUND,
            # c.GARAGE_INDOOR_PRESENT,
            # c.GARAGE_INDOOR_PERCENTAGE,
            c.FIELD_TOTAL_EXPENSES,
            # c.PRIMARY_USAGE_PERCENTAGE,
            # c.SECONDARY_USAGE_PERCENTAGE,
            # c.TERTIARY_USAGE_PERCENTAGE,
            # c.QUATERNARY_USAGE_PERCENTAGE,
            c.FIELD_VOLUME_TOTAL_416,
            c.FIELD_VOLUME_TOTAL_116
        ]

    # remove certain features
    if remove_features is not None:
        for to_remove in remove_features:
            while to_remove in features: features.remove(to_remove)

    features.append(c.FIELD_AREA_MAIN_USAGE)
    dataset = df.copy().loc[:, features]

    # add features for one hot encoding
    features.extend(df[c.FIELD_USAGE_CLUSTER].unique())

    # preprocess dataset
    transform_pipeline = Pipeline([
        # ('combine_features', CombineFeatures()),
        ('volume_imputation', NumericalImputationTransformer(nimp.impute_mean(dataset))),
        # ('encode_labels', EncodeLabelsTransformer()),
        ('one_hot_encoding', OneHotEncodingTransformer())
    ])
    dataset = transform_pipeline.fit_transform(dataset)

    # TODO: use median for some of the fields?
    dataset = dataset.drop(columns=[c.FIELD_VOLUME_TOTAL_116])
    dataset = dataset.dropna(how="any")

    # features / labels
    features.remove(c.FIELD_VOLUME_TOTAL_116)
    features.remove(c.FIELD_AREA_MAIN_USAGE)
    features.remove(c.FIELD_USAGE_CLUSTER)

    X = dataset[features]
    y = dataset[c.FIELD_AREA_MAIN_USAGE]

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


def get_outliers(df, feature, factor=3.0):
    upper_lim = df[feature].mean() + df[feature].std() * factor
    lower_lim = df[feature].mean() - df[feature].std() * factor
    return df[(df[feature] > upper_lim) | (df[feature] < lower_lim)]


def remove_outliers(df, factor=3.0):
    ratio_outliers = get_outliers(df, c.FIELD_HNF_GF_RATIO, factor)
    removal_list = ratio_outliers[c.FIELD_ID].values
    return df[~df[c.FIELD_ID].isin(removal_list.tolist())]
