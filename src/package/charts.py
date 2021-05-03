from typing import Final

import seaborn as sns
from pandas import DataFrame
from seaborn import FacetGrid

import src.package.importer as im

LABEL_GF: Final = "Geschossfläche GF"
LABEL_HNF: Final = "Hauptnutzfläche HNF"

CHART_HEIGHT: Final = 10
CHART_WIDTH: Final = 8


def set_plot_size(seaborn, rc=(CHART_HEIGHT, CHART_WIDTH)):
    """ set size of seaborn plots """
    seaborn.set(rc={'figure.figsize': rc})


def lmplot_gf_hnf(df: DataFrame, hue=None) -> FacetGrid:
    gf = sns.lmplot(
        data=df,
        x=im.FIELD_AREA_TOTAL_FLOOR_416, y=im.FIELD_AREA_MAIN_USAGE,
        scatter_kws={'alpha': 0.5},
        hue=hue,
        height=CHART_HEIGHT, aspect=CHART_HEIGHT/CHART_WIDTH
    )

    gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)

    return gf


def regplot_gf_hnf(df: DataFrame, logscale=False) -> FacetGrid:
    gf = sns.regplot(
        data=df,
        x=im.FIELD_AREA_TOTAL_FLOOR_416, y=im.FIELD_AREA_MAIN_USAGE,
        scatter_kws={'alpha': 0.5},
    )

    gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)
    gf.figure.set_size_inches(CHART_HEIGHT, CHART_WIDTH)

    if logscale:
        gf.set_xscale('log')
        gf.set_yscale('log')

    return gf

