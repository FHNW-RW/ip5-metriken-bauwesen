from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from seaborn import FacetGrid

import src.package.consts as c

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
        x=c.FIELD_AREA_TOTAL_FLOOR_416, y=c.FIELD_AREA_MAIN_USAGE,
        scatter_kws={'alpha': 0.5},
        hue=hue,
        height=CHART_HEIGHT, aspect=CHART_HEIGHT / CHART_WIDTH,
        truncate=True
    )

    gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)

    return gf


def regplot_gf_hnf(df: DataFrame, logscale=False) -> FacetGrid:
    gf = sns.regplot(
        data=df,
        x=c.FIELD_AREA_TOTAL_FLOOR_416, y=c.FIELD_AREA_MAIN_USAGE,
        scatter_kws={'alpha': 0.5},
    )

    gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)
    gf.figure.set_size_inches(CHART_HEIGHT, CHART_WIDTH)

    if logscale:
        gf.set_xscale('log')
        gf.set_yscale('log')

    return gf


def plot_feature_importance(importance, names, model_type):
    # Create arrays from feature importance and feature names
    feature_importance = np.array(importance)
    feature_names = np.array(names)

    # Create a DataFrame using a Dictionary
    data = {'feature_names': feature_names, 'feature_importance': feature_importance}
    fi_df = pd.DataFrame(data)

    # Sort the DataFrame in order decreasing feature importance
    fi_df.sort_values(by=['feature_importance'], ascending=False, inplace=True)

    # Define size of bar plot
    plt.figure(figsize=(10, 8))
    # Plot Searborn bar chart
    sns.barplot(x=fi_df['feature_importance'], y=fi_df['feature_names'])
    # Add chart labels
    plt.title(model_type + 'FEATURE IMPORTANCE')
    plt.xlabel('FEATURE IMPORTANCE')
    plt.ylabel('FEATURE NAMES')
