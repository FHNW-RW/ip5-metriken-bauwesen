from numpy import mean, std
from pandas import DataFrame
from sklearn.metrics import mean_absolute_error, mean_squared_error, max_error, mean_absolute_percentage_error
from sklearn.model_selection import cross_validate, RepeatedKFold
from sklearn.pipeline import Pipeline

import src.package.consts as c
import src.package.importer as im
import src.package.numeric_imputations as nimp
import src.package.shared as sh
from src.package.transformers import CombineFeatures, VolumeImputer, OneHotEncodingTransformer


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
        dataset = im.cap_upper_gf_field(dataset, upper_percentile=upper_percentile)

    # features / labels
    X = dataset[[c.FIELD_AREA_TOTAL_FLOOR_416, c.FIELD_USAGE_CLUSTER]]
    y = dataset[c.FIELD_AREA_MAIN_USAGE]

    return X, y


def ml_dataset_full(df: DataFrame, field_to_predict=c.FIELD_AREA_MAIN_USAGE, features=None, remove_features=None,
                    additional_features=None, fitted_pipeline=None):

    # add default features
    if features is None:
        features = [
            c.FIELD_USAGE_CLUSTER,
            c.FIELD_NUM_FLOORS_UNDERGROUND,
            c.FIELD_NUM_FLOORS_OVERGROUND,
            c.GARAGE_COMBINED,
            c.FIELD_TOTAL_EXPENSES,
            c.PRIMARY_USAGE_PERCENTAGE,
            c.FIELD_VOLUME_TOTAL_416,
            c.FIELD_VOLUME_TOTAL_116,
        ]

    # add additional fields
    if additional_features is not None:
        features.extend(additional_features)

    # remove certain features
    if remove_features is not None:
        for to_remove in remove_features:
            while to_remove in features: features.remove(to_remove)

    features.append(field_to_predict)
    dataset = df.copy().reindex(columns=features)

    # preprocess dataset
    if fitted_pipeline is None:
        cluster_mean_values = nimp.impute_mean(df, serialize=True)

        transform_pipeline = Pipeline([
            ('volume_imputer', VolumeImputer(cluster_mean_values)),
            ('usage_encoder', OneHotEncodingTransformer(c.FIELD_USAGE_CLUSTER)),
            # ('label_encoder1', LabelEncoderTransformer(c.NOM_PRIMARY_USAGE)), # activate if HIGHEST_ONLY with usage name
            # ('label_encoder2', LabelEncoderTransformer(c.NOM_SECONDARY_USAGE)), # activate if HIGHEST_ONLY with usage name
            # ('label_encoder3', LabelEncoderTransformer(c.NOM_TERTIARY_USAGE)), # activate if HIGHEST_ONLY with usage name
            # ('label_encoder4', LabelEncoderTransformer(c.NOM_QUATERNARY_USAGE)), # activate if HIGHEST_ONLY with usage name
        ])

        # fit/transform & serialize pipeline
        dataset = transform_pipeline.fit_transform(dataset)
        sh.serialize_object(transform_pipeline, 'fitted_pipeline')
    else:
        dataset = fitted_pipeline.transform(dataset)

    # TODO: use median for some of the fields?
    dataset = dataset.dropna(how="any")

    X = dataset.drop(field_to_predict, axis=1)
    y = dataset[field_to_predict].copy()

    return X, y


def cross_validation(model, X, y, cv=RepeatedKFold(n_splits=5, n_repeats=10, random_state=0)):
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
