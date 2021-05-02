from typing import Final

import seaborn as sns
from pandas import DataFrame
from seaborn import FacetGrid

import src.package.importer as im

LABEL_GF: Final = "Geschossfläche GF"
LABEL_HNF: Final = "Hauptnutzfläche HNF"


def lmplot_gf_hnf(df: DataFrame, hue=None) -> FacetGrid:
    gf = sns.lmplot(
        data=df,
        x=im.FIELD_AREA_TOTAL_FLOOR_416, y=im.FIELD_AREA_MAIN_USAGE,
        hue=hue
    )

    gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)

    return gf


def regplot_gf_hnf(df: DataFrame, logscale=False) -> FacetGrid:
    gf = sns.regplot(
        data=df,
        x=im.FIELD_AREA_TOTAL_FLOOR_416, y=im.FIELD_AREA_MAIN_USAGE
    )

    gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)

    if logscale:
        gf.set_xscale('log')
        gf.set_yscale('log')

    return gf
