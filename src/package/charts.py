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
    """ Plot GF in relation to other field with Seaborn Implot """

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

    # save figure
    if percentile is not None:
        gf.savefig(f'../exports/{ratio_label}/lmplot_{ratio_label}_{percentile}.png', bbox_inches="tight", dpi=200)

    return gf


def lmplot_clustered(df: DataFrame, y: str = None, y_label: str = None, ratio_label: str = None,
                     save_label: str = None):
    """ Plot GF clustered in relation to other field with Seaborn Implot """

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

    # save figure
    if save_label is not None:
        gf.savefig(f'../exports/{ratio_label}/lmplot_{save_label}_clustered.png', bbox_inches="tight", dpi=200)


def regplot_gf_field(df: DataFrame, field: str = None, field_label: str = None, logscale=False) -> FacetGrid:
    """ Plot GF clustered in relation to other field with Regression Plot """

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


def plot_feature_importance(importance, names, model_type, save_label: str = None):
    """ Plot importance of features for a model """

    # create arrays from feature importance and feature names
    feature_importance = np.array(importance)
    feature_names = np.array(names)

    # create DataFrame using a Dictionary
    data = {'feature_names': feature_names, 'feature_importance': feature_importance}
    fi_df = pd.DataFrame(data)

    # sort the DataFrame in order decreasing feature importance
    fi_df.sort_values(by=['feature_importance'], ascending=False, inplace=True)
    fi_df = fi_df.nlargest(n=10, columns='feature_importance')

    # define size of bar plot
    plt.figure(figsize=(10, 8))

    # plot seaborn bar chart
    sns.barplot(x=fi_df['feature_importance'], y=fi_df['feature_names'])

    # add chart labels
    plt.title(model_type + ' Feature Importance')
    plt.xlabel('Feature Importance')
    plt.ylabel('Feature Namen')

    # save plot
    if save_label is not None:
        plt.savefig(f"../analysis/exports/feature_importance/barplot_fe_importance_{save_label}.png",
                    bbox_inches="tight", dpi=200)


def scatter_highlight(df, df_highlight, x, y, show_id=True, x_label: str = None, y_label: str = None,
                      save_label: str = None):
    """ Highlight outliers with scatter plot """

    fig, ax = plt.subplots()

    ax.scatter(x=df[x], y=df[y])
    ax.scatter(x=df_highlight[x], y=df_highlight[y], c='red')

    # show id on highlighted data points
    if show_id:
        for i, row in df_highlight.iterrows():
            ax.annotate(row[c.FIELD_ID], (row[x], row[y]))

    # set labels
    x_label = x_label if x_label is not None else x
    y_label = y_label if y_label is not None else y
    ax.set(xlabel=x_label, ylabel=y_label)

    # plot and save
    plt.gcf()
    plt.plot()
    if save_label is not None:
        plt.savefig(f"exports/outliers/scatter_outliers_{save_label}.png", bbox_inches="tight", dpi=200)


def barplot_reversed_percentiles(ratio_data: DataFrame, df_full: DataFrame, percentile: int, ratio_label: str,
                                 ratio_field: str = None,
                                 upper_limit=None, lower_limit=None):
    """ Use barplot to display ratio bigger than certain threshold """

    # preprocess data
    percentiles = ratio_data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[percentile / 100])
    percentiles = percentiles[[f'{percentile}%']]
    percentiles.columns = [f'{100 - percentile}%']  # reversed percentiles

    # reshape and sort data
    percentiles = percentiles.stack()
    percentiles = percentiles.reset_index(level=[0, 1])
    percentiles.columns = [c.FIELD_USAGE_CLUSTER, 'percentile', 'ratio']

    # setup preferences and colors
    set_preferences(sns, rc=[15, 8], font_scale=2)
    sns.set_style("whitegrid")
    palette = __cluster_colors(df_full)  # guarantees color continuity

    # set plot limits
    if upper_limit is not None and lower_limit is not None:
        plt.xlim(lower_limit, upper_limit)

    # plot data
    ax = sns.barplot(y=c.FIELD_USAGE_CLUSTER, x='ratio', data=percentiles,
                     order=percentiles.sort_values('ratio')[c.FIELD_USAGE_CLUSTER],
                     palette=palette)

    # set labels and ticks
    for p in ax.patches:
        width = p.get_width()
        width = width + 0.05
        ax.text(width,
                p.get_y() + p.get_height() / 2,
                '{:1.2f}'.format(width),
                ha='left',
                va='center')
    ax.set(xlabel=f'{100 - percentile}% mit {ratio_label} grösser als', ylabel='Nutzungstyp')

    # save figure
    if ratio_field is not None:
        plt.savefig(f'../exports/{ratio_field}/barplot_{ratio_field}_{percentile}percentile_reversed.png',
                    bbox_inches="tight",
                    dpi=200)


def violinplot_ratios(data: DataFrame, ratio_field: str, ratio_label: str,
                      cut: float = 2, bw='scott', garage_hue: bool = True):
    """ Use violin plot to display clustered ratios """

    # add garage present
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

    # save figure
    additional_label = '_garages' if garage_hue else ''
    plt.savefig(f'../exports/{ratio_field}/violin_{ratio_field}{additional_label}_clustered.png', bbox_inches="tight",
                dpi=200)


def describe_ratios(df_full: DataFrame, ratio_field: str = None):
    """ Describe ratio with count, mean, sdt, min and different percentiles for cluster """

    pd.options.mode.chained_assignment = None
    if ratio_field is None:
        # check different cluster sizes
        df_full[c.FIELD_USAGE_CLUSTER] = df_full[c.FIELD_USAGE_CLUSTER].astype('category')
        pd.options.mode.chained_assignment = 'warn'
        data = df_full[c.FIELD_HNF_GF_RATIO]
        return data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[.25, 0.4, .5, .75])
    else:
        # check different cluster sizes
        df_full[c.FIELD_USAGE_CLUSTER] = df_full[c.FIELD_USAGE_CLUSTER].astype('category')
        pd.options.mode.chained_assignment = 'warn'
        data = df_full[ratio_field]
        return data.groupby(df_full[c.FIELD_USAGE_CLUSTER]).describe(percentiles=[.25, 0.4, .5, .75])


def correlation_hmp(df: DataFrame):
    """ Show correlation heatmap for dataset """

    # select relevant features and preprocces plot
    mask = np.triu(np.ones_like(df.corr(), dtype=np.bool))

    # prepare and plot heatmap
    heatmap = sns.heatmap(df.corr(), mask=mask, vmin=-1, vmax=1, annot=True, cmap='BrBG')
    heatmap.set_title('Correlation Heatmap', fontdict={'fontsize': 12}, pad=16)

    # set rotation of ticks
    plt.xticks(
        rotation=45,
        horizontalalignment='right'
    )

    # save figure
    plt.savefig('exports/correlation/correlation_heatmap_general.png', bbox_inches="tight", dpi=200)


def correlation_ratio(df: DataFrame, ratio_field: str = None, ratio_label: str = "Verhältnis HNF – GF"):
    """ Show correlation heatmap for a ratio """

    if ratio_field is None:
        ratio_field = c.FIELD_HNF_GF_RATIO

    # preprocess dataset
    cor_data = df.copy()
    # cor_data = filtered_df[filtered_df[imp_usg.NOM_PRIMARY_USAGE].str.contains("WOHNBAUTEN", na=False)]
    if ratio_field is None:
        cor_data = cor_data.corr()[[c.FIELD_HNF_GF_RATIO]].sort_values(by=c.FIELD_HNF_GF_RATIO, ascending=False)
    else:
        cor_data = cor_data.corr()[[ratio_field]].sort_values(by=ratio_field, ascending=False)

    # plot heatmap
    heatmap = sns.heatmap(cor_data, vmin=-1, vmax=1, annot=True, cmap='BrBG')
    heatmap.set_title(f'Korrelation mit {ratio_label}', fontdict={'fontsize': 18}, pad=16)

    plt.savefig(f'exports/correlation/correlation_heatmap_{ratio_field}.png', bbox_inches="tight", dpi=200)


def __cluster_colors(df: DataFrame):
    # get color palette
    colors = sns.color_palette(n_colors=len(df[c.FIELD_USAGE_CLUSTER].unique()), palette="Set2")
    palette = dict()

    # assign colors to categories
    for cluster in df[c.FIELD_USAGE_CLUSTER].unique():
        palette[cluster] = colors.pop(0)

    return palette
