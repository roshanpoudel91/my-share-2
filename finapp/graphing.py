import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import io, base64
from matplotlib.ticker import LinearLocator, FuncFormatter
import seaborn as sns
import datetime as dt
sns.set_theme(style='darkgrid')

def glplot(df):
    #fig, ax = plt.subplots(figsize=(12,5))
    #ax.set_xlabel('Growth Scenario',labelpad=8.0,color='Blue',size=14,alpha=0.65)
    #ax.set_ylabel('Gain (Loss) %',labelpad=8.0,color='Blue',size=14,alpha=0.65)
    #ax.set_title('Gain/Loss under Different Margin & Revenue Scenario',size=18,alpha=0.8,color='blue',pad=10)
    #ax.tick_params(colors='b',labelsize=11)
    df1=pd.melt(df.reset_index(),id_vars=['index'],value_vars=['Current ECOS Margin (%)','Prior Year ECOS Margin (%)','3 Year Average ECOS Margin (%)','2019 ECOS Margin (%)'])
    #print(df)
    sns.set(font_scale=0.8)
    grid=sns.catplot(data=df1,kind="bar",x="index",y='value',hue='variable',palette='dark',alpha=0.6,height=5,aspect=2,legend_out=False)

    #axs=sns.lineplot(ax=ax,data=df,x='Ref_Date',y='Value',label=symbol)
    grid.despine(left=True)
    grid.set_axis_labels("Growth Scenarios",'Gain (Loss) %')
    plt.legend(loc='upper left')

    #grid.legend.set_title("Margin Scenarios")
    for axes in grid.axes.flat:
        _=axes.set_xticklabels(axes.get_xticklabels(),rotation=30)




    flike = io.BytesIO()
    grid.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    chart = b64

    return chart

def glplot2(df, df2):
    #fig, ax = plt.subplots(figsize=(8,5))
    ax=df.plot(kind='barh',stacked=True, width=0.4,title='-Gain/(loss)$ Changes from Past Year',figsize=(12,5))
    for c1 in ax.containers:
        ax.bar_label(c1,label_type='center',fontsize=12,color='white')

    flike = io.BytesIO()
    plt.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    chart1 = b64

    ax2=df2.plot(kind='barh',stacked=True, width=0.4,title='Gain/(loss)% in different Scenarios in multiples of 5',figsize=(12,5))
    for c in ax.containers:
        ax2.bar_label(c,label_type='center',fontsize=12,color='white')

    flike = io.BytesIO()
    plt.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    chart2 = b64


    return (chart1, chart2)



