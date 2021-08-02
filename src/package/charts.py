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


def set_preferences(seaborn, rc=(CHART_HEIGHT, CHART_WIDTH), font_scale: int = 1):
    """ set size of seaborn plots """
    seaborn.set(rc={'figure.figsize': rc})
    sns.set(font_scale=font_scale)


def lmplot_gf_hnf(df: DataFrame, hue=None) -> FacetGrid:
    gf = sns.lmplot(
        data=df,
        x=c.FIELD_AREA_TOTAL_FLOOR_416, y=c.FIELD_AREA_MAIN_USAGE,
        scatter_kws={'alpha': 0.5},
        hue=hue,
        height=CHART_HEIGHT,
        aspect=CHART_HEIGHT / CHART_WIDTH,
        truncate=False,
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


def scatter_highlight(df, df_highlight, x, y, show_id=True):
    fig, ax = plt.subplots()

    ax.scatter(x=df[x], y=df[y])
    ax.scatter(x=df_highlight[x], y=df_highlight[y], c='red')

    # show id on highlighted data points
    if show_id:
        for i, row in df_highlight.iterrows():
            ax.annotate(row[c.FIELD_ID], (row[x], row[y]))

    plt.gcf()
    plt.plot()


def barplot_reversed_percentiles(data: DataFrame, df_full: DataFrame, label: str, percentile: int):

    # preprocess data
    percentiles = data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[(percentile)/100])
    percentiles = percentiles[[f'{percentile}%']]
    percentiles.columns = [f'{100-percentile}%']  # reversed percentiles

    # reshape and sort data
    percentiles = percentiles.stack()
    percentiles = percentiles.reset_index(level=[0, 1])
    percentiles.columns = [c.FIELD_USAGE_CLUSTER, 'percentile', 'ratio']

    # setp preferences
    set_preferences(sns, rc=[15, 8], font_scale=2)

    # Plot data
    sns.set_style("whitegrid")
    plt.xlim(0, 1)
    ax = sns.barplot(y=c.FIELD_USAGE_CLUSTER, x='ratio', data=percentiles,
                     order=percentiles.sort_values('ratio')[c.FIELD_USAGE_CLUSTER],
                     palette=sns.color_palette("Set2"))
    for p in ax.patches:
        width = p.get_width()  # get bar length
        ax.text(width + 0.01,  # set the text at 1 unit right of the bar
                p.get_y() + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                '{:1.2f}'.format(width),  # set variable to display, 2 decimals
                ha='left',  # horizontal alignment
                va='center')  # vertical alignment
    ax.set(xlabel=f'{100-percentile}% mit Ratio grösser als', ylabel='Nutzungstyp')

    # Save figure
    plt.savefig(f'exports/barplot_{label}_{percentile}percentile_reversed.png', bbox_inches="tight", dpi=200)

