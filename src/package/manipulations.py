from pandas import DataFrame

import src.package.importer as im


def compute_ratio_hnf_gf(df: DataFrame) -> DataFrame:
    # TODO: Uses SIA 416 only
    df['ratio_hnf_gf'] = df.eval(f'{im.FIELD_AREA_MAIN_USAGE} / {im.FIELD_AREA_TOTAL_FLOOR_416}')

    return df
