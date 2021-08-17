import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

import src.package.consts as c
import src.package.shared as sh
import src.package.importer as im
import src.package.numeric_imputations as nimp
from src.package.transformers import VolumeImputer, OneHotEncodingTransformer, LabelEncoderTransformer

from joblib import load

pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)

df = im.get_extended_dataset('datasets/previous_versions/train_set.csv')

df = df.copy().loc[:, [c.FIELD_AREA_TOTAL_FLOOR_416,
                       c.FIELD_USAGE_CLUSTER,
                       c.FIELD_TOTAL_EXPENSES,
                       c.FIELD_VOLUME_TOTAL_416,
                       c.FIELD_VOLUME_TOTAL_116]]

usage_cluster_index = df.columns.tolist().index(c.FIELD_USAGE_CLUSTER)
column_transformers = ColumnTransformer([
    # ('cat', LabelEncoder(), [usage_cluster_index])
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse=False), [usage_cluster_index])
])
print(df)

transform_pipeline = Pipeline([
    ('volume_imputer', VolumeImputer(nimp.impute_mean(df))),
    # ('usage_encoder', OneHotEncoder(categories=[1]))
    ('usage_encoder', OneHotEncodingTransformer(c.FIELD_USAGE_CLUSTER)),
    # ('usage_encoder', LabelEncoderTransformer(c.FIELD_USAGE_CLUSTER)),
    # ('usage_encoder', column_transformers)
])

# full_pipeline = ColumnTransformer([
#     ("num", transform_pipeline, [
#                        c.FIELD_USAGE_CLUSTER,
#                        c.FIELD_VOLUME_TOTAL_416,
#                        c.FIELD_VOLUME_TOTAL_116]),
#     #("cat", OneHotEncoder(), [c.FIELD_USAGE_CLUSTER]),
# ])


df = transform_pipeline.fit_transform(df)

sh.serialize_object(transform_pipeline, 'transform_pipeline')

print(df)

test_set = im.get_extended_dataset('datasets/previous_versions/test_set.csv')

test_set = test_set.copy().loc[:, [c.FIELD_AREA_TOTAL_FLOOR_416,
                                   c.FIELD_USAGE_CLUSTER,
                                   c.FIELD_TOTAL_EXPENSES,
                                   c.FIELD_VOLUME_TOTAL_416,
                                   c.FIELD_VOLUME_TOTAL_116]]

export_directory = sh.export_directory_path(f'transform_pipeline.joblib')
print(f'Location: {export_directory}')

pipeline = load(export_directory)
test_set = pipeline.transform(test_set)

# test_set = transform_pipeline.transform(test_set)

print(test_set)
