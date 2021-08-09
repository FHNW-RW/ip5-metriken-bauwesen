from typing import Final

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pandas import DataFrame
from seaborn import FacetGrid

import src.package.consts as c
import src.analysis.feature_engineering.garages as grg

LABEL_GF: Final = "Geschossfläche GF"
LABEL_HNF: Final = "Hauptnutzfläche HNF"
LABEL_GV: Final = "Geschossvolumen GV"
LABEL_GSF: Final = "Grundstückfläche GSF"
LABEL_FAW: Final = "Äussere Wandbekleidung FAW"
LABEL_FB: Final = "Bedachung FB"
LABEL_BUF: Final = "Bearbeitete Umgebungsfläche BUF"
LABEL_VAU: Final = "Volumenaushub VAU"

LABEL_RATIO_HNF_GF: Final = "Verhältnis HNF – GF"
LABEL_RATIO_GV_GF: Final = "Verhältnis GV – GF"
LABEL_RATIO_GSF_GF: Final = "Verhältnis GSF – GF"
LABEL_RATIO_FAW_GF: Final = "Verhältnis FAW – GF"
LABEL_RATIO_FB_GF: Final = "Verhältnis FB – GF"
LABEL_RATIO_BUF_GF: Final = "Verhältnis BUF – GF"
LABEL_RATIO_VAU_GF: Final = "Verhältnis VAU – GF"

CHART_HEIGHT: Final = 10
CHART_WIDTH: Final = 8


def set_preferences(seaborn, rc=(CHART_HEIGHT, CHART_WIDTH), font_scale: float = 1.0):
    """ set size of seaborn plots """
    seaborn.set(rc={'figure.figsize': rc})
    sns.set(font_scale=font_scale)


def lmplot_gf_field(df: DataFrame, field: str = None, field_label: str = None, ratio_label: str = None,
                    percentile: str = None,
                    hue=None) -> FacetGrid:
    if field is None:
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

    else:
        gf = sns.lmplot(
            data=df,
            x=c.FIELD_AREA_TOTAL_FLOOR_416, y=field,
            scatter_kws={'alpha': 0.5},
            hue=hue,
            height=CHART_HEIGHT,
            aspect=CHART_HEIGHT / CHART_WIDTH,
            truncate=False,
        )

        gf.set(xlabel=LABEL_GF, ylabel=field_label)

    # Save figure
    if percentile is not None:
        gf.savefig(f'../exports/{ratio_label}/lmplot_{ratio_label}_{percentile}.png', bbox_inches="tight", dpi=200)

    return gf


def lmplot_clustered(df: DataFrame, y: str = None, y_label: str = None, ratio_label: str = None,
                     save_label: str = None):
    df = df.copy()
    df = df.rename(columns={c.FIELD_USAGE_CLUSTER: "Typ"})

    if y is None:
        gf = sns.lmplot(
            data=df,
            x=c.FIELD_AREA_TOTAL_FLOOR_416, y=c.FIELD_AREA_MAIN_USAGE,
            col="Typ",
            hue="Typ",
            scatter_kws={'alpha': 0.5},
            ci=None, col_wrap=4,
        )
    else:
        gf = sns.lmplot(
            data=df,
            x=c.FIELD_AREA_TOTAL_FLOOR_416, y=y,
            col="Typ",
            hue="Typ",
            scatter_kws={'alpha': 0.5},
            ci=None, col_wrap=4,
        )

    if y is None:
        gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)
        plt.subplots_adjust(hspace=0.5, wspace=0.5)
    else:
        gf.set(xlabel=LABEL_GF, ylabel=y_label)
        plt.subplots_adjust(hspace=0.5, wspace=0.5)

    # Save figure
    if save_label is not None:
        gf.savefig(f'../exports/{ratio_label}/lmplot_{save_label}_clustered.png', bbox_inches="tight", dpi=200)


def regplot_gf_field(df: DataFrame, field: str = None, field_label: str = None, logscale=False) -> FacetGrid:
    if field is None:
        gf = sns.regplot(
            data=df,
            x=c.FIELD_AREA_TOTAL_FLOOR_416, y=c.FIELD_AREA_MAIN_USAGE,
            scatter_kws={'alpha': 0.5},
        )

        gf.set(xlabel=LABEL_GF, ylabel=LABEL_HNF)
        gf.figure.set_size_inches(CHART_HEIGHT, CHART_WIDTH)
    else:
        gf = sns.regplot(
            data=df,
            x=c.FIELD_AREA_TOTAL_FLOOR_416, y=field,
            scatter_kws={'alpha': 0.5},
        )

        gf.set(xlabel=LABEL_GF, ylabel=field_label)
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


def barplot_reversed_percentiles(ratio_data: DataFrame, df_full: DataFrame, percentile: int, ratio_label: str,
                                 ratio_field: str = None,
                                 upper_limit=None, lower_limit=None):
    # preprocess data
    percentiles = ratio_data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[(percentile) / 100])
    percentiles = percentiles[[f'{percentile}%']]
    percentiles.columns = [f'{100 - percentile}%']  # reversed percentiles

    # reshape and sort data
    percentiles = percentiles.stack()
    percentiles = percentiles.reset_index(level=[0, 1])
    percentiles.columns = [c.FIELD_USAGE_CLUSTER, 'percentile', 'ratio']

    # setup preferences
    set_preferences(sns, rc=[15, 8], font_scale=2)
    sns.set_style("whitegrid")

    if upper_limit is not None and lower_limit is not None:
        plt.xlim(lower_limit, upper_limit)

    # Plot data
    ax = sns.barplot(y=c.FIELD_USAGE_CLUSTER, x='ratio', data=percentiles,
                     order=percentiles.sort_values('ratio')[c.FIELD_USAGE_CLUSTER],
                     palette=sns.color_palette("Set2"))
    for p in ax.patches:
        width = p.get_width()
        width = width + 0.05  # get bar length
        ax.text(width,  # set the text at 1 unit right of the bar
                p.get_y() + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                '{:1.2f}'.format(width),  # set variable to display, 2 decimals
                ha='left',  # horizontal alignment
                va='center')  # vertical alignment
    ax.set(xlabel=f'{100 - percentile}% mit {ratio_label} grösser als', ylabel='Nutzungstyp')

    if ratio_field is not None:
        # Save figure
        plt.savefig(f'../exports/{ratio_field}/barplot_{ratio_field}_{percentile}percentile_reversed.png',
                    bbox_inches="tight",
                    dpi=200)


def violinplot_ratios(data: DataFrame, ratio_field: str, ratio_label: str,
                      cut: float = 2, bw='scott', garage_hue: bool = True):
    # Add Garage Present Field
    plot_data = grg.add_garage_present(data)

    if ratio_field is None:
        if garage_hue:
            ax = sns.violinplot(x=c.FIELD_USAGE_CLUSTER, y=c.FIELD_HNF_GF_RATIO, hue=c.FIELD_GARAGE_COMBINED_PRESENT,
                                split=True,
                                data=plot_data,
                                cut=cut,
                                bw=bw)
            ax.legend(title='Garage vorhanden', handles=ax.legend_.legendHandles, labels=['Nein', 'Ja'])
        else:
            ax = sns.violinplot(x=c.FIELD_USAGE_CLUSTER, y=c.FIELD_HNF_GF_RATIO,
                                data=plot_data,
                                cut=cut,
                                bw=bw)

        ax.set(xlabel='Nutzungstyp (Cluster)', ylabel='Ratio HNF - GF')

    else:
        if garage_hue:
            ax = sns.violinplot(x=c.FIELD_USAGE_CLUSTER, y=ratio_field, hue=c.FIELD_GARAGE_COMBINED_PRESENT,
                                split=True,
                                data=plot_data,
                                cut=cut,
                                bw=bw)
            ax.legend(title='Garage vorhanden', handles=ax.legend_.legendHandles, labels=['Nein', 'Ja'])
        else:
            ax = sns.violinplot(x=c.FIELD_USAGE_CLUSTER, y=ratio_field,
                                data=plot_data,
                                cut=cut,
                                bw=bw)

        ax.set(xlabel='Nutzungstyp (Cluster)', ylabel=ratio_label)

    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='normal',
        fontsize='medium'
    )

    # Save figure
    additional_label = '_garages' if garage_hue else ''
    plt.savefig(f'../exports/{ratio_field}/violin_{ratio_field}{additional_label}_clustered.png', bbox_inches="tight",
                dpi=200)


def catplot_field(data: DataFrame, ratio_field: str = None, ratio_label: str = None):
    if ratio_field is None:
        gf = sns.catplot(x=c.FIELD_USAGE_CLUSTER, y=c.FIELD_HNF_GF_RATIO, kind="box", data=data)

        gf.set(xlabel='Nutzungstyp (Cluster))', ylabel='Ratio HNF - GF')
        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontweight='normal',
            fontsize='medium'
        )
    else:
        gf = sns.catplot(x=c.FIELD_USAGE_CLUSTER, y=ratio_field, kind="box", data=data)

        gf.set(xlabel='Nutzungstyp (Cluster))', ylabel=ratio_label)
        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontweight='normal',
            fontsize='medium'
        )


def describe_ratios(df_full: DataFrame, ratio_field: str = None):
    pd.options.mode.chained_assignment = None
    if ratio_field is None:
        # Check different cluster sizes
        df_full[c.FIELD_USAGE_CLUSTER] = df_full[c.FIELD_USAGE_CLUSTER].astype('category')
        pd.options.mode.chained_assignment = 'warn'
        data = df_full[c.FIELD_HNF_GF_RATIO]
        return data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[.25, 0.4, .5, .75])
    else:
        # Check different cluster sizes
        df_full[c.FIELD_USAGE_CLUSTER] = df_full[c.FIELD_USAGE_CLUSTER].astype('category')
        pd.options.mode.chained_assignment = 'warn'
        data = df_full[ratio_field]
        return data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[.25, 0.4, .5, .75])
