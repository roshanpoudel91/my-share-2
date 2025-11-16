from django.db.models import Q
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.parser import parse
import requests
#import yfinance as yf
from .newscript import stock_calculation#, gain_loss
from .models import BasicData, CompanyBeta, GlobalData, BackTestData2 #, BackTestData2

import seaborn as sns
import matplotlib
matplotlib.use('Agg')
#import matplotlib.dates as mdates
import io, base64
import matplotlib.pyplot as plt
sns.set_theme(style='darkgrid')

def flag_df(df):

    if (df['IGR'] <= df['IGR3YA'] <=df['RevgA3Y']<=df['RevgYoY'] and (df['ECOSMGN']>=df['ECOSMGN3YA'])):
        return 'Diamond'
    elif (df['IGR'] <= df['IGR3YA'] <=df['RevgA3Y']<=df['RevgYoY']):
        return 'Rhodiium'
    elif (df['IGR'] <= df['IGR3YA'] <=df['RevgA3Y'] and (df['IGR']<=df['RevgYoY']) and (df['ECOSMGN']>=df['ECOSMGN3YA'])):
        return 'Platinum'
    elif (df['IGR'] <= df['IGR3YA'] <=df['RevgA3Y'] and (df['IGR']<=df['RevgYoY'])):
        return 'Gold'
    elif (df['IGR'] <= df['IGR3YA'] <=df['RevgA3Y'] and (df['ECOSMGN']>=df['ECOSMGN3YA'])):
        return 'Ruthenium'
    elif (df['IGR'] <= df['IGR3YA']<=df['RevgA3Y']):
        return 'Iridium'
    elif (df['IGR'] <= df['IGR3YA']and (df['IGR']<=df['RevgA3Y']) and (df['ECOSMGN']>=df['ECOSMGN3YA']) ):
        return 'Osmium'
    elif (df['IGR'] <= df['IGR3YA'] and (df['IGR']<=df['RevgA3Y']) ):
        return 'Palladium'
    elif (df['IGR'] <= df['IGR3YA']and (df['ECOSMGN']>=df['ECOSMGN3YA']) ):
        return 'Silver'
    elif (df['IGR'] <= df['IGR3YA']):
        return 'Copper'
    else:
        return 'Lead'

def flag_df1(df1):

    if (df1['RevgYoY'] <= -20):
        return 'DDNegative'
    elif (df1['RevgYoY'] <= -10):
        return 'DNegative'
    elif (df1['RevgYoY'] <= 0):
        return 'Negative'
    elif (df1['RevgYoY'] <= 10):
        return 'Positive'
    elif (df1['RevgYoY'] <= 20):
        return 'HPositive'
    elif (df1['RevgYoY'] <= 40):
        return 'HHPositive'
    elif (df1['RevgYoY'] >= 40):
        return 'SHPositive'

def flag_df2(df2):

    if (df2['RevgA3Y'] <= -20):
        return 'DDNegative'
    elif (df2['RevgA3Y'] <= -10):
        return 'DNegative'
    elif (df2['RevgA3Y'] <= 0):
        return 'Negative'
    elif (df2['RevgA3Y'] <= 10):
        return 'Positive'
    elif (df2['RevgA3Y'] <= 20):
        return 'HPositive'
    elif (df2['RevgA3Y'] <= 40):
        return 'HHPositive'
    elif (df2['RevgA3Y'] >= 40):
        return 'SHPositive'

def flag_df3(df3):

    if (df3['IGR'] <= -20):
        return 'DDNegative'
    elif (df3['IGR'] <= -10):
        return 'DNegative'
    elif (df3['IGR'] <= 0):
        return 'Negative'
    elif (df3['IGR'] <= 10):
        return 'Positive'
    elif (df3['IGR'] <= 20):
        return 'HPositive'
    elif (df3['IGR'] <= 40):
        return 'HHPositive'
    elif (df3['IGR'] >= 40):
        return 'SHPositive'


def flag_df4(df4):

    if (df4['ECOSMGN'] <=0):
        return 'Negative'
    elif (df4['ECOSMGN'] <= 10):
        return 'Positive'
    elif (df4['ECOSMGN'] <= 20):
        return 'HPositive'
    elif (df4['ECOSMGN'] <= 40):
        return 'HHPositive'
    elif (df4['ECOSMGN'] >= 40):
        return 'SHPositive'

def flag_df5(df5):

    if (df5['Dis_Prem3YA'] <= -20):
        return 'SHPremium'
    elif (df5['Dis_Prem3YA'] <= -10):
        return 'HPremium'
    elif (df5['Dis_Prem3YA'] <= 0):
        return 'Premium'
    elif (df5['Dis_Prem3YA'] <= 10):
        return 'Discount'
    elif (df5['Dis_Prem3YA'] <= 20):
        return 'HDiscount'
    elif (df5['Dis_Prem3YA'] <= 40):
        return 'HHDiscount'
    elif (df5['Dis_Prem3YA'] >= 40):
        return 'SHDiscount'

def flag_df6(df6):

    if (df6['Dis_Prem'] <= -20):
        return 'SHPremium'
    elif (df6['Dis_Prem'] <= -10):
        return 'HPremium'
    elif (df6['Dis_Prem'] <= 0):
        return 'Premium'
    elif (df6['Dis_Prem'] <= 10):
        return 'Discount'
    elif (df6['Dis_Prem'] <= 20):
        return 'HDiscount'
    elif (df6['Dis_Prem']<= 40):
        return 'HHDiscount'
    elif (df6['Dis_Prem']>= 40):
        return 'SHDiscount'

def flag_df7(df7):

    if (df7['MCAP'] <=250):
        return 'MicroCap'
    elif (df7['MCAP'] <=2000):
        return 'SmallCap'
    elif (df7['MCAP'] <=5000):
        return 'LowerMidCap'
    elif (df7['MCAP'] <=10000):
        return 'MidCap'
    elif (df7['MCAP'] <=20000):
        return 'LowerLargeCap'
    elif (df7['MCAP'] <=40000):
        return 'MidLargeCap'
    elif (df7['MCAP'] <=80000):
        return 'LargeCap'
    elif (df7['MCAP'] <=150000):
        return 'LowerMegaCap'
    elif (df7['MCAP'] <=200000):
        return 'MidMegaCap'
    elif (df7['MCAP'] >200000):
        return 'MegaCap'

def flag_df8(df8):

    if (df8['Spread_YoY'] <= -20):
        return 'SHASpread'
    elif (df8['Spread_YoY'] <= -10):
        return 'HASpread'
    elif (df8['Spread_YoY'] <= 0):
        return 'ASpread'
    elif (df8['Spread_YoY'] <= 10):
        return 'Spread'
    elif (df8['Spread_YoY'] <= 20):
        return 'HSpread'
    elif (df8['Spread_YoY']<= 40):
        return 'HHSpread'
    elif (df8['Spread_YoY']>= 40):
        return 'SHSpread'

def flag_df9(df9):

    if (df9['Spread_3YA'] <= -20):
        return 'SHA3YSpread'
    elif (df9['Spread_3YA'] <= -10):
        return 'HA3YSpread'
    elif (df9['Spread_3YA'] <= 0):
        return 'A3YSpread'
    elif (df9['Spread_3YA'] <= 10):
        return '3YSpread'
    elif (df9['Spread_3YA'] <= 20):
        return 'H3YSpread'
    elif (df9['Spread_3YA']<= 40):
        return 'HH3YSpread'
    elif (df9['Spread_3YA']>= 40):
        return 'SH3YSpread'

def flag_df10(df10):
    if (df10['Yield'] <= 0):
        return 'NoDiv'
    elif (df10['Yield'] <= 1.5):
        return 'LYield'
    elif (df10['Yield'] <= 3):
        return 'MYield'
    elif (df10['Yield'] <= 4.5):
        return 'HYield'
    elif (df10['Yield'] <= 6):
        return 'HHYield'
    elif (df10['Yield']>= 6):
        return 'SHYield'

def flag_df11(df11):
    if (df11['YieldA3Y'] <= 0):
        return 'NoDiv'
    elif (df11['YieldA3Y'] <= 1.5):
        return 'LYieldA3Y'
    elif (df11['YieldA3Y'] <= 3):
        return 'MYieldA3Y'
    elif (df11['YieldA3Y'] <= 4.5):
        return 'HYieldA3Y'
    elif (df11['YieldA3Y'] <= 6):
        return 'HHYieldA3Y'
    elif (df11['YieldA3Y']>= 6):
        return 'SHYieldA3Y'

def flag_df12(df12):
    if (df12['Yield'] <= 0):
        return 'NoDiv'
    elif (df12['PayOutRatio'] <= 15):
        return 'VLPR'
    elif (df12['PayOutRatio'] <= 30):
        return 'LPR'
    elif (df12['PayOutRatio'] <= 45):
        return 'MPR'
    elif (df12['PayOutRatio'] <= 60):
        return 'HPR'
    elif (df12['PayOutRatio']<= 75):
        return 'HHPR'
    elif (df12['PayOutRatio']>= 75):
        return 'SHPR'

def flag_df13(df13):
    if (df13['Yield'] <= 0):
        return 'NoDiv'
    elif (df13['PayOutRatioA3Y'] <= 15):
        return 'VLPRA3Y'
    elif (df13['PayOutRatioA3Y'] <= 30):
        return 'LPRA3Y'
    elif (df13['PayOutRatio'] <= 45):
        return 'MPRA3Y'
    elif (df13['PayOutRatioA3Y'] <= 60):
        return 'HPRA3Y'
    elif (df13['PayOutRatioA3Y']<= 75):
        return 'HHPRA3Y'
    elif (df13['PayOutRatioA3Y']>= 75):
        return 'SHPRA3Y'

def flag_df14(df14):
    if (df14['AnnlRev'] == 'NaN'):
        return 'NoRev'
    elif (df14['CFOToRev'] <= 0):
        return 'NegCFOR'
    elif (df14['CFOToRev'] <= 15):
        return 'LCFOR'
    elif (df14['CFOToRev'] <= 30):
        return 'MCFOR'
    elif (df14['CFOToRev'] <= 45):
        return 'HCFOR'
    elif (df14['CFOToRev']<= 60):
        return 'HHCFOR'
    elif (df14['CFOToRev']>= 60):
        return 'SHPCFOR'

def flag_df15(df15):
    if (df15['AnnlRev'] == 'NaN'):
        return 'NoRev'
    elif (df15['CFOToRevA3Y'] <= 0):
        return 'NegCFORA3Y'
    elif (df15['CFOToRevA3Y'] <= 15):
        return 'LCFORA3Y'
    elif (df15['CFOToRevA3Y'] <= 30):
        return 'MCFORA3Y'
    elif (df15['CFOToRevA3Y'] <= 45):
        return 'HCFORA3Y'
    elif (df15['CFOToRevA3Y']<= 60):
        return 'HHCFORA3Y'
    elif (df15['CFOToRevA3Y']>= 60):
        return 'SHPCFORA3Y'




def backtest(ticker):
    base_url='https://www.alphavantage.co/query?'
    params={'function':'OVERVIEW','symbol':ticker,'apikey':'DFHG4DGYXZA59F12'}

    overview=requests.get(base_url,params=params).json()

    params['function']='INCOME_STATEMENT'
    income_st=requests.get(base_url,params=params).json()

    params['function']='BALANCE_SHEET'
    balance_sh=requests.get(base_url,params=params).json()

    params['function']='CASH_FLOW'
    cashflow_st=requests.get(base_url,params=params).json()

    params['function']='TIME_SERIES_DAILY_ADJUSTED'
    params['outputsize']='full'
    time_series=requests.get(base_url,params=params).json()
    price_data=pd.DataFrame.from_dict(time_series['Time Series (Daily)'])
    price_data=price_data.T
    price_data.index=pd.to_datetime(price_data.index)

    # Getting Beta (This one is similar to the older script)
    try:
        beta=float(overview['Beta'])
    except:
        beta='n/a'

    try:
        beta_past=CompanyBeta.objects.get(symbol=ticker).beta
    except:
        beta_past='n/a'

    if beta == 'n/a': beta = beta_past
    if beta_past == 'n/a': beta_past = beta

    # Getting RF, ERP, GDP (This one is similar to the older script)
    rf=[BasicData.objects.get(date=dt.date(2024,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2023,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2022,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2021,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2020,12,31)).rf_rate]

    erp=[BasicData.objects.get(date=dt.date(2024,12,31)).erp,
        BasicData.objects.get(date=dt.date(2023,12,31)).erp,
        BasicData.objects.get(date=dt.date(2022,12,31)).erp,
        BasicData.objects.get(date=dt.date(2021,12,31)).erp,
        BasicData.objects.get(date=dt.date(2020,12,31)).erp]

    gdp=[BasicData.objects.get(date=dt.date(2024,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2023,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2022,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2021,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2020,12,31)).gdp]


    # Getting conmgn & indmgn from database (for website) (This one is similar to the older script)
    get_last_data=GlobalData.objects.filter(tick=ticker).last()
    conmgn3m=get_last_data.conmgn3m
    conmgn6m=get_last_data.conmgn6m
    indmgm=get_last_data.indmgm

    if conmgn3m is None: conmgn3m = 0
    if conmgn6m is None: conmgn6m = 0
    if indmgm is None: indmgm = 0
    conmgn=max(max(0,conmgn3m),max(0,conmgn6m),max(0,indmgm))/100

    margin_2019=GlobalData.objects.filter(tick=ticker).filter(period='Q42019')[0]
    margin_2020=GlobalData.objects.filter(tick=ticker).filter(period='Q42020')[0]
    margin_2021=GlobalData.objects.filter(tick=ticker).filter(period='Q42021')[0]
    margin_2022=GlobalData.objects.filter(tick=ticker).filter(period='Q42022')[0]
    margin_2023=GlobalData.objects.filter(tick=ticker).filter(period='Q42023')[0]
    margin_2024=GlobalData.objects.filter(tick=ticker).filter(period='Q42024')[0]
    margin_TTM=GlobalData.objects.filter(tick=ticker).last()

    conmgn3m_2019=margin_2019.conmgn3m
    conmgn3m_2020=margin_2020.conmgn3m
    conmgn3m_2021=margin_2021.conmgn3m
    conmgn3m_2022=margin_2022.conmgn3m
    conmgn3m_2023=margin_2023.conmgn3m
    conmgn3m_2024=margin_2024.conmgn3m

    conmgn3m_TTM=margin_TTM.conmgn3m

    conmgn6m_2019=margin_2019.conmgn6m
    conmgn6m_2020=margin_2020.conmgn6m
    conmgn6m_2021=margin_2021.conmgn6m
    conmgn6m_2022=margin_2022.conmgn6m
    conmgn6m_2023=margin_2023.conmgn6m
    conmgn6m_2024=margin_2024.conmgn6m

    conmgn6m_TTM=margin_TTM.conmgn6m

    indmgn_2019=margin_2019.indmgm
    indmgn_2020=margin_2020.indmgm
    indmgn_2021=margin_2021.indmgm
    indmgn_2022=margin_2022.indmgm
    indmgn_2023=margin_2023.indmgm
    indmgn_2024=margin_2024.indmgm

    indmgn_TTM=margin_TTM.indmgm

    conmgn_y4 = np.nanmax(np.array([0,conmgn3m_2021,conmgn6m_2021,indmgn_2021],dtype=np.float64))/100
    conmgn_y3 = np.nanmax(np.array([0,conmgn3m_2022,conmgn6m_2022,indmgn_2022],dtype=np.float64))/100
    conmgn_y2 = np.nanmax(np.array([0,conmgn3m_2023,conmgn6m_2023,indmgn_2023],dtype=np.float64))/100
    conmgn_y1 = np.nanmax(np.array([0,conmgn3m_2024,conmgn6m_2024,indmgn_2024],dtype=np.float64))/100
    conmgn_y0 = np.nanmax(np.array([0,conmgn3m_TTM,conmgn6m_TTM,indmgn_TTM],dtype=np.float64))/100


    # Annual Revenue
    rev_y0 = float(income_st['quarterlyReports'][0]['totalRevenue']) + float(income_st['quarterlyReports'][1]['totalRevenue']) + float(income_st['quarterlyReports'][2]['totalRevenue']) + float(income_st['quarterlyReports'][3]['totalRevenue'])
    rev_y1 = float(income_st['quarterlyReports'][4]['totalRevenue']) + float(income_st['quarterlyReports'][5]['totalRevenue']) + float(income_st['quarterlyReports'][6]['totalRevenue']) + float(income_st['quarterlyReports'][7]['totalRevenue'])
    rev_y2 = float(income_st['quarterlyReports'][8]['totalRevenue']) + float(income_st['quarterlyReports'][9]['totalRevenue']) + float(income_st['quarterlyReports'][10]['totalRevenue']) + float(income_st['quarterlyReports'][11]['totalRevenue'])
    rev_y3 = float(income_st['quarterlyReports'][12]['totalRevenue']) + float(income_st['quarterlyReports'][13]['totalRevenue']) + float(income_st['quarterlyReports'][14]['totalRevenue']) + float(income_st['quarterlyReports'][15]['totalRevenue'])
    rev_y4 = float(income_st['quarterlyReports'][16]['totalRevenue']) + float(income_st['quarterlyReports'][17]['totalRevenue']) + float(income_st['quarterlyReports'][18]['totalRevenue']) + float(income_st['quarterlyReports'][19]['totalRevenue'])

    # Market Cap
    fiscal_date_0 = parse(income_st['quarterlyReports'][0]['fiscalDateEnding'])
    fiscal_date_1 = parse(income_st['quarterlyReports'][4]['fiscalDateEnding'])
    fiscal_date_2 = parse(income_st['quarterlyReports'][8]['fiscalDateEnding'])
    fiscal_date_3 = parse(income_st['quarterlyReports'][12]['fiscalDateEnding'])
    fiscal_date_4 = parse(income_st['quarterlyReports'][16]['fiscalDateEnding'])

    start_date_0, end_date_0 = fiscal_date_0 + dt.timedelta(days=35), fiscal_date_0 + dt.timedelta(days=40)
    start_date_1, end_date_1 = fiscal_date_1 + dt.timedelta(days=35), fiscal_date_1 + dt.timedelta(days=40)
    start_date_2, end_date_2 = fiscal_date_2 + dt.timedelta(days=35), fiscal_date_2 + dt.timedelta(days=40)
    start_date_3, end_date_3 = fiscal_date_3 + dt.timedelta(days=35), fiscal_date_3 + dt.timedelta(days=40)
    start_date_4, end_date_4 = fiscal_date_4 + dt.timedelta(days=35), fiscal_date_4 + dt.timedelta(days=40)

    currentPrice = float(price_data.iloc[0,4])
    #currentPrice = round(yf.Ticker(ticker).history(period='1d')['Close'][0],2)
    if end_date_0 > dt.datetime.now():
        end_date_0 = end_date_0 - dt.timedelta(days=5)
        start_date_0 = start_date_0 - dt.timedelta(days=5)

    dates=pd.date_range(start_date_0, end_date_0)
    dfxx=price_data[price_data.index.isin(dates)]
    #print(dfxx)
    adj_close_0=dfxx.iloc[-1]['5. adjusted close']
    #print(f'Adjusted Close 0 {adj_close_0}')

    dates=pd.date_range(start_date_1, end_date_1)
    dfxx=price_data[price_data.index.isin(dates)]
    #print(dfxx)
    adj_close_1=dfxx.iloc[-1]['5. adjusted close']

    dates=pd.date_range(start_date_2, end_date_2)
    dfxx=price_data[price_data.index.isin(dates)]
    adj_close_2=dfxx.iloc[-1]['5. adjusted close']

    dates=pd.date_range(start_date_3, end_date_3)
    dfxx=price_data[price_data.index.isin(dates)]
    adj_close_3=dfxx.iloc[-1]['5. adjusted close']

    dates=pd.date_range(start_date_4, end_date_4)
    dfxx=price_data[price_data.index.isin(dates)]
    adj_close_4=dfxx.iloc[-1]['5. adjusted close']

    market_cap_y0 = int(overview['MarketCapitalization'])
    market_cap_y1 = float(adj_close_1) * market_cap_y0 / currentPrice #yf.download(ticker, start=start_date_1, end=end_date_1).iloc[-1]['Adj Close'] * market_cap_y0 / currentPrice
    market_cap_y2 = float(adj_close_2) * market_cap_y0 / currentPrice #yf.download(ticker, start=start_date_2, end=end_date_2).iloc[-1]['Adj Close'] * market_cap_y0 / currentPrice
    market_cap_y3 = float(adj_close_3) * market_cap_y0 / currentPrice #yf.download(ticker, start=start_date_3, end=end_date_3).iloc[-1]['Adj Close'] * market_cap_y0 / currentPrice
    market_cap_y4 = float(adj_close_4) * market_cap_y0 / currentPrice #yf.download(ticker, start=start_date_4, end=end_date_4).iloc[-1]['Adj Close'] * market_cap_y0 / currentPrice

    # Cashflow from Operation
    cfo_y0 = np.sum(float(cashflow_st['quarterlyReports'][0]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][1]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][2]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][3]['operatingCashflow']))
    cfo_y1 = np.sum(float(cashflow_st['quarterlyReports'][4]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][5]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][6]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][7]['operatingCashflow']))
    cfo_y2 = np.sum(float(cashflow_st['quarterlyReports'][8]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][9]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][10]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][11]['operatingCashflow']))
    cfo_y3 = np.sum(float(cashflow_st['quarterlyReports'][12]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][13]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][14]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][15]['operatingCashflow']))
    cfo_y4 = np.sum(float(cashflow_st['quarterlyReports'][16]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][17]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][18]['operatingCashflow'])+float(cashflow_st['quarterlyReports'][19]['operatingCashflow']))

    #Common Dividend Paid
    try:
        div_q0=float(cashflow_st['quarterlyReports'][0]['dividendPayoutCommonStock'])
    except:
        div_q0=0
    try:
        div_q1=float(cashflow_st['quarterlyReports'][1]['dividendPayoutCommonStock'])
    except:
        div_q1=0
    try:
        div_q2=float(cashflow_st['quarterlyReports'][2]['dividendPayoutCommonStock'])
    except:
        div_q2=0
    try:
        div_q3=float(cashflow_st['quarterlyReports'][3]['dividendPayoutCommonStock'])
    except:
        div_q3=0
    try:
        div_q4=float(cashflow_st['quarterlyReports'][4]['dividendPayoutCommonStock'])
    except:
        div_q4=0
    try:
        div_q5=float(cashflow_st['quarterlyReports'][5]['dividendPayoutCommonStock'])
    except:
        div_q5=0
    try:
        div_q6=float(cashflow_st['quarterlyReports'][6]['dividendPayoutCommonStock'])
    except:
        div_q6=0
    try:
        div_q7=float(cashflow_st['quarterlyReports'][7]['dividendPayoutCommonStock'])
    except:
        div_q7=0
    try:
        div_q8=float(cashflow_st['quarterlyReports'][8]['dividendPayoutCommonStock'])
    except:
        div_q8=0
    try:
        div_q9=float(cashflow_st['quarterlyReports'][9]['dividendPayoutCommonStock'])
    except:
        div_q9=0
    try:
        div_q10=float(cashflow_st['quarterlyReports'][10]['dividendPayoutCommonStock'])
    except:
        div_q10=0
    try:
        div_q11=float(cashflow_st['quarterlyReports'][11]['dividendPayoutCommonStock'])
    except:
        div_q11=0
    try:
        div_q12=float(cashflow_st['quarterlyReports'][12]['dividendPayoutCommonStock'])
    except:
        div_q12=0
    try:
        div_q13=float(cashflow_st['quarterlyReports'][13]['dividendPayoutCommonStock'])
    except:
        div_q13=0
    try:
        div_q14=float(cashflow_st['quarterlyReports'][14]['dividendPayoutCommonStock'])
    except:
        div_q14=0
    try:
        div_q15=float(cashflow_st['quarterlyReports'][15]['dividendPayoutCommonStock'])
    except:
        div_q15=0
    try:
        div_q16=float(cashflow_st['quarterlyReports'][16]['dividendPayoutCommonStock'])
    except:
        div_q16=0
    try:
        div_q17=float(cashflow_st['quarterlyReports'][17]['dividendPayoutCommonStock'])
    except:
        div_q17=0
    try:
        div_q18=float(cashflow_st['quarterlyReports'][18]['dividendPayoutCommonStock'])
    except:
        div_q18=0
    try:
        div_q19=float(cashflow_st['quarterlyReports'][19]['dividendPayoutCommonStock'])
    except:
        div_q19=0
    div_y0 = np.sum(div_q0+div_q1+div_q2+div_q3)
    div_y1 = np.sum(div_q4+div_q5+div_q6+div_q7)
    div_y2 = np.sum(div_q8+div_q9+div_q10+div_q11)
    div_y3 = np.sum(div_q12+div_q13+div_q14+div_q15)
    div_y4 = np.sum(div_q16+div_q17+div_q18+div_q19)

    #Yield Related Calculations:
    yield_y0=round(div_y0/market_cap_y0,4)*100
    yield_y1=round(div_y1/market_cap_y1,4)*100
    yield_y2=round(div_y2/market_cap_y2,4)*100
    yield_y3=round(div_y3/market_cap_y3,4)*100
    yield_y4=round(div_y4/market_cap_y4,4)*100
    yield_3ya = np.average([yield_y0,yield_y1,yield_y2,yield_y3])

    # ECOS
    try:
        ecos0=float(income_st['quarterlyReports'][0]['netIncomeFromContinuingOperations'])
    except:
        ecos0=float(income_st['quarterlyReports'][0]['netIncome'])
    try:
        ecos1=float(income_st['quarterlyReports'][1]['netIncomeFromContinuingOperations'])
    except:
        ecos1=float(income_st['quarterlyReports'][1]['netIncome'])
    try:
        ecos2=float(income_st['quarterlyReports'][2]['netIncomeFromContinuingOperations'])
    except:
        ecos2=float(income_st['quarterlyReports'][2]['netIncome'])
    try:
        ecos3=float(income_st['quarterlyReports'][3]['netIncomeFromContinuingOperations'])
    except:
        ecos3=float(income_st['quarterlyReports'][3]['netIncome'])
    try:
        ecos4=float(income_st['quarterlyReports'][4]['netIncomeFromContinuingOperations'])
    except:
        ecos4=float(income_st['quarterlyReports'][4]['netIncome'])
    try:
        ecos5=float(income_st['quarterlyReports'][5]['netIncomeFromContinuingOperations'])
    except:
        ecos5=float(income_st['quarterlyReports'][5]['netIncome'])
    try:
        ecos6=float(income_st['quarterlyReports'][6]['netIncomeFromContinuingOperations'])
    except:
        ecos6=float(income_st['quarterlyReports'][6]['netIncome'])
    try:
        ecos7=float(income_st['quarterlyReports'][7]['netIncomeFromContinuingOperations'])
    except:
        ecos7=float(income_st['quarterlyReports'][7]['netIncome'])
    try:
        ecos8=float(income_st['quarterlyReports'][8]['netIncomeFromContinuingOperations'])
    except:
        ecos8=float(income_st['quarterlyReports'][8]['netIncome'])
    try:
        ecos9=float(income_st['quarterlyReports'][9]['netIncomeFromContinuingOperations'])
    except:
        ecos9=float(income_st['quarterlyReports'][9]['netIncome'])
    try:
        ecos10=float(income_st['quarterlyReports'][10]['netIncomeFromContinuingOperations'])
    except:
        ecos10=float(income_st['quarterlyReports'][10]['netIncome'])
    try:
        ecos11=float(income_st['quarterlyReports'][11]['netIncomeFromContinuingOperations'])
    except:
        ecos11=float(income_st['quarterlyReports'][11]['netIncome'])
    try:
        ecos12=float(income_st['quarterlyReports'][12]['netIncomeFromContinuingOperations'])
    except:
        ecos12=float(income_st['quarterlyReports'][12]['netIncome'])
    try:
        ecos13=float(income_st['quarterlyReports'][13]['netIncomeFromContinuingOperations'])
    except:
        ecos13=float(income_st['quarterlyReports'][13]['netIncome'])
    try:
        ecos14=float(income_st['quarterlyReports'][14]['netIncomeFromContinuingOperations'])
    except:
        ecos14=float(income_st['quarterlyReports'][14]['netIncome'])
    try:
        ecos15=float(income_st['quarterlyReports'][15]['netIncomeFromContinuingOperations'])
    except:
        ecos15=float(income_st['quarterlyReports'][15]['netIncome'])
    try:
        ecos16=float(income_st['quarterlyReports'][16]['netIncomeFromContinuingOperations'])
    except:
        ecos16=float(income_st['quarterlyReports'][16]['netIncome'])
    try:
        ecos17=float(income_st['quarterlyReports'][17]['netIncomeFromContinuingOperations'])
    except:
        ecos17=float(income_st['quarterlyReports'][17]['netIncome'])
    try:
        ecos18=float(income_st['quarterlyReports'][18]['netIncomeFromContinuingOperations'])
    except:
        ecos18=float(income_st['quarterlyReports'][18]['netIncome'])
    try:
        ecos19=float(income_st['quarterlyReports'][19]['netIncomeFromContinuingOperations'])
    except:
        ecos19=float(income_st['quarterlyReports'][19]['netIncome'])



    #ecos_y0 = float(income_st['quarterlyReports'][0]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][1]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][2]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][3]['netIncomeFromContinuingOperations'])
    #ecos_y1 = float(income_st['quarterlyReports'][4]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][5]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][6]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][7]['netIncomeFromContinuingOperations'])
    #ecos_y2 = float(income_st['quarterlyReports'][8]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][9]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][10]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][11]['netIncomeFromContinuingOperations'])
    #ecos_y3 = float(income_st['quarterlyReports'][12]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][13]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][14]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][15]['netIncomeFromContinuingOperations'])
    #ecos_y4 = float(income_st['quarterlyReports'][16]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][17]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][18]['netIncomeFromContinuingOperations']) + float(income_st['quarterlyReports'][19]['netIncomeFromContinuingOperations'])

    ecos_y0=ecos0+ecos1+ecos2+ecos3
    ecos_y1=ecos4+ecos5+ecos6+ecos7
    ecos_y2=ecos8+ecos9+ecos10+ecos11
    ecos_y3=ecos12+ecos13+ecos14+ecos15
    ecos_y4=ecos16+ecos17+ecos18+ecos19


    # ECOS Margin
    ecos_mgn_y0 = ecos_y0/rev_y0
    ecos_mgn_y1 = ecos_y1/rev_y1
    ecos_mgn_y2 = ecos_y2/rev_y2
    ecos_mgn_y3 = ecos_y3/rev_y3
    ecos_mgn_y4 = ecos_y4/rev_y4

    #PayoutRatio:
    payout_ratio_y0=div_y0/ecos_y0
    payout_ratio_y1=div_y1/ecos_y1
    payout_ratio_y2=div_y2/ecos_y2
    payout_ratio_y3=div_y3/ecos_y3
    payout_ratio_y4=div_y4/ecos_y4

    #PayoutRatio3ya:
    payout_ratio_3ya= np.average([payout_ratio_y0,payout_ratio_y1,payout_ratio_y2,payout_ratio_y3])

    # IGR (Left to do)
    igr_y0 = stock_calculation(rf[0]/100, erp[0]/100, beta, ecos_y0, market_cap_y0, gdp[0]/100, 10, rev_y0, conmgn_y0)
    igr_y1 = stock_calculation(rf[0]/100, erp[0]/100, beta_past, ecos_y1, market_cap_y1, gdp[0]/100, 10, rev_y1, conmgn_y1)
    igr_y2 = stock_calculation(rf[1]/100, erp[1]/100, beta_past, ecos_y2, market_cap_y2, gdp[1]/100, 10, rev_y2, conmgn_y2)
    igr_y3 = stock_calculation(rf[2]/100, erp[2]/100, beta_past, ecos_y3, market_cap_y3, gdp[2]/100, 10, rev_y3, conmgn_y3)


    # Rate (rf + erp * beta)
    rate_y0 = (rf[0] + erp[0] * beta)/100
    rate_y1 = (rf[0] + erp[0] * beta_past)/100
    rate_y2 = (rf[1] + erp[1] * beta_past)/100
    rate_y3 = (rf[2] + erp[2] * beta_past)/100

    # 3 Year Average Annual Revenue
    p3y_annl_rev = np.average([rev_y1, rev_y2, rev_y3])

    # Revenue Growth YoY
    rev_g_y0 = rev_y0 / rev_y1 -1
    rev_g_y1 = rev_y1 / rev_y2 -1
    rev_g_y2 = rev_y2 / rev_y3 -1
    rev_g_y3 = rev_y3 / rev_y4 -1

    #CFO to Revenue Ratio
    cfo_rev_ratio_y0=cfo_y0/rev_y0
    cfo_rev_ratio_y1=cfo_y1/rev_y1
    cfo_rev_ratio_y2=cfo_y2/rev_y2
    cfo_rev_ratio_y3=cfo_y3/rev_y3

    #CFO to Revenue Ratio 3YA
    cfo_rev_ratio_3ya=np.average([cfo_rev_ratio_y0 , cfo_rev_ratio_y1 , cfo_rev_ratio_y2,cfo_rev_ratio_y3])

    # Discount Premium
    disc_prem_y0 = (rev_g_y0 - rate_y0 + 1) * ecos_mgn_y0 / ecos_mgn_y1 * (market_cap_y1 / market_cap_y0 - 1)
    disc_prem_y1 = (rev_g_y1 - rate_y1 + 1) * ecos_mgn_y1 / ecos_mgn_y2 * (market_cap_y2 / market_cap_y1 - 1)
    disc_prem_y2 = (rev_g_y2 - rate_y2 + 1) * ecos_mgn_y2 / ecos_mgn_y3 * (market_cap_y3 / market_cap_y2 - 1)
    disc_prem_y3 = (rev_g_y3 - rate_y3 + 1) * ecos_mgn_y3 / ecos_mgn_y4 * (market_cap_y4 / market_cap_y3 - 1)

    # Revenue Growth 3 Year Average
    rev_g_3ya = np.average([rev_g_y0 , rev_g_y1 , rev_g_y2, rev_g_y3])

    # ECOS Margin 3 Year Average
    ecos_mgn_3ya = np.average([ecos_mgn_y0,ecos_mgn_y1,ecos_mgn_y2,ecos_mgn_y3])

    # IGR 3 Year Average
    igr_3ya = np.average([igr_y0, igr_y1, igr_y2, igr_y3])

    # Discount Premium 3 Year Average
    disc_prem_3ya = np.average([disc_prem_y0, disc_prem_y1, disc_prem_y2, disc_prem_y3])

    # Spread
    spread_y0 = (rev_g_y0 + 1) / (igr_y0/100 + 1) - 1

    # Spread 3 Year Average
    spread_3ya = (rev_g_3ya + 1) / (igr_y0/100 + 1) - 1

    output = {'PYAnnlRev':rev_y1,
        'PY_MCAP':market_cap_y1,
        'PY_IGR':igr_y1,
        'PY_MGN':ecos_mgn_y1,
        'PY_Rate':rate_y1,
        'P3YAnnlRev':p3y_annl_rev,
        'IGR':igr_y0,
        'MCAP':market_cap_y0,
        'AnnlRev':rev_y0,
        'ECOSMGN':ecos_mgn_y0,
        'Rate':rate_y0,

        'RevgYoY':rev_g_y0,
        'Dis_Prem':disc_prem_y0,
        'RevgA3Y':rev_g_3ya,
        'ECOSMGN3YA':ecos_mgn_3ya,
        'IGR3YA':igr_3ya,
        'Dis_Prem3YA':disc_prem_3ya,
        'Spread_YoY':spread_y0,
        'Spread_3YA':spread_3ya,

        'Yield':yield_y0,
        'YieldA3Y':yield_3ya,
        'PayOutRatio':payout_ratio_y0,
        'PayOutRatioA3Y':payout_ratio_3ya,
        'CFOToRev':cfo_rev_ratio_y0,
        'CFOToRevA3Y':cfo_rev_ratio_3ya}

    buckets = {'Flag_Val':flag_df(output),
        'Flag_Revg':flag_df1(output),
        'Flag_RevgA3Y':flag_df2(output),
        'Flag_IGR':flag_df3(output),
        'Flag_MGN':flag_df4(output),
        'Flag_Disc_Prem':flag_df5(output),
        'Flag_Disc_PremCY':flag_df6(output),
        'Flag_MCAP':flag_df7(output),
        'Flag_Spread_YoY':flag_df8(output),
        'Flag_Spread_3YA':flag_df9(output),

        'Flag_Yield':flag_df10(output),
        'Flag_Yield3YA':flag_df11(output),
        'Flag_PayOutRatio':flag_df12(output),
        'Flag_PayOutRatioA3Y':flag_df13(output),
        'Flag_CFOToRev':flag_df14(output),
        'Flag_CFOToRevA3Y':flag_df15(output) }

    #print(buckets)

    #print(BackTestData2.objects.filter(Q(flag_val=buckets['Flag_Val'])).count())
    #print(BackTestData2.objects.filter(Q(flag_val=flag_df(output))).count())

    matches1 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &  #The Source of the Problem
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        Q(flag_spread_yoy = flag_df8(output)) &
        Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches2 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        Q(flag_spread_yoy = flag_df8(output)) &
        Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches3 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches4 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches5 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches6 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        #Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches7 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        #Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches8 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches9 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        #Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches10 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        #Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches11 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        #Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        #Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches12 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        #Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches13 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        #Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )

    matches14 = BackTestData2.objects.filter(
        Q(flag_val = buckets['Flag_Val']) &
        #Q(flag_revg = buckets['Flag_Revg']) &
        Q(flag_revg_3ya = buckets['Flag_RevgA3Y']) &
        #Q(flag_igr = buckets['Flag_IGR']) &
        Q(flag_mgn = buckets['Flag_MGN']) &
        Q(flag_disc_prem = buckets['Flag_Disc_Prem']) &
        #Q(flag_disc_prem_cy = buckets['Flag_Disc_PremCY']) &
        #Q(flag_spread_yoy = flag_df8(output)) &
        #Q(flag_spread_3ya = flag_df9(output)) &
        Q(mcap__gte = 1000) &

        #Q(flag_yield = buckets['Flag_Yield']) &
        Q(flag_yield_3ya = buckets['Flag_Yield3YA']) &
        #Q(flag_payout_ratio = buckets['Flag_PayOutRatio']) &
        #Q(flag_payout_ratio_3ya = buckets['Flag_PayOutRatioA3Y']) &
        #Q(flag_cfo_to_rev = buckets['Flag_CFOToRev']) &
        Q(flag_cfo_to_rev_3ya = buckets['Flag_CFOToRevA3Y'])
        )


    count1=matches1.count()-matches1.filter(mcapg6m=None).count()
    count2=matches2.count()-matches2.filter(mcapg6m=None).count()
    count3=matches3.count()-matches3.filter(mcapg6m=None).count()
    count4=matches4.count()-matches4.filter(mcapg6m=None).count()
    count5=matches5.count()-matches5.filter(mcapg6m=None).count()
    count6=matches6.count()-matches6.filter(mcapg6m=None).count()
    count7=matches7.count()-matches7.filter(mcapg6m=None).count()
    count8=matches8.count()-matches8.filter(mcapg6m=None).count()
    count9=matches9.count()-matches9.filter(mcapg6m=None).count()
    count10=matches10.count()-matches10.filter(mcapg6m=None).count()
    count11=matches11.count()-matches11.filter(mcapg6m=None).count()
    count12=matches12.count()-matches12.filter(mcapg6m=None).count()
    count13=matches13.count()-matches13.filter(mcapg6m=None).count()
    count14=matches14.count()-matches14.filter(mcapg6m=None).count()

    #print(matches1.count(), matches2.count(), matches3.count(), matches4.count(), matches5.count(), matches6.count(), matches7.count())
    #matches= matches1

    n=15
    if count1 >= n:
        matches=matches1
    elif count2 >= n:
        matches=matches2
    elif count3 >= n:
        matches=matches3
    elif count4 >= n:
        matches=matches4
    elif count5 >= n:
        matches=matches5
    elif count6 >= n:
        matches=matches6
    elif count7 >= n:
        matches=matches7
    elif count8 >= n:
        matches=matches8
    elif count9 >= n:
        matches=matches9
    elif count10 >= n:
        matches=matches10
    elif count11 >= n:
        matches=matches11
    elif count12 >= n:
        matches=matches12
    elif count13 >= n:
        matches=matches13
    else:
        matches=matches14

    if matches.count()-matches.filter(mcapg6m=None).count() <= 100:
        fmatches=matches
    else:
        fmatches=matches.filter(mcap__gte=3000)

    # Here need to deduct null values for matches for mcapg6m


    df=pd.DataFrame(list(fmatches.values()))

    summary=df.describe()
    count_3m_ret = summary['mcapg3m']['count']
    count_6m_ret = summary['mcapg6m']['count']
    count_9m_ret = summary['mcapg9m']['count']
    count_1y_ret = summary['mcapg1y']['count']
    mean_3m_ret = summary['mcapg3m']['mean']
    mean_6m_ret = summary['mcapg6m']['mean']
    mean_9m_ret = summary['mcapg9m']['mean']
    mean_1y_ret = summary['mcapg1y']['mean']
    ret_3m_25 = summary['mcapg3m']['25%']
    ret_6m_25 = summary['mcapg6m']['25%']
    ret_9m_25 = summary['mcapg9m']['25%']
    ret_1y_25 = summary['mcapg1y']['25%']
    ret_3m_50 = summary['mcapg3m']['50%']
    ret_6m_50 = summary['mcapg6m']['50%']
    ret_9m_50 = summary['mcapg9m']['50%']
    ret_1y_50 = summary['mcapg1y']['50%']
    max_3m_ret = summary['mcapg3m']['max']
    max_6m_ret = summary['mcapg6m']['max']
    max_9m_ret = summary['mcapg9m']['max']
    max_1y_ret = summary['mcapg1y']['max']

    ret_3m_10=df['mcapg3m'].quantile(0.10)
    ret_6m_10=df['mcapg6m'].quantile(0.10)
    ret_9m_10=df['mcapg9m'].quantile(0.10)
    ret_1y_10=df['mcapg1y'].quantile(0.10)

    #print(df['mcapg3m'].isnull().sum(), df['mcapg6m'].isnull().sum())

    p_gainers_3m=len(df[df['mcapg3m']>0])/len(df['mcapg3m'])
    p_gainers_6m=len(df[df['mcapg6m']>0])/len(df['mcapg6m'])
    p_gainers_9m=len(df[df['mcapg9m']>0])/len(df['mcapg9m'])
    p_gainers_1y=len(df[df['mcapg1y']>0])/len(df['mcapg1y'])

    summary_details = [round(count_3m_ret), round(count_6m_ret), round(count_9m_ret), round(count_1y_ret),
                        round(p_gainers_3m*100,2),round(p_gainers_6m*100,2),round(p_gainers_9m*100,2),round(p_gainers_1y*100,2),
                        round(mean_3m_ret,2), round(mean_6m_ret,2),round(mean_9m_ret,2),round(mean_1y_ret,2),
                        round(ret_3m_10,2),round(ret_6m_10,2),round(ret_9m_10,2),round(ret_1y_10,2),
                        round(ret_3m_25,2), round(ret_6m_25,2),round(ret_9m_25,2),round(ret_1y_25,2),
                        round(ret_3m_50,2), round(ret_6m_50,2),round(ret_9m_50,2),round(ret_1y_50,2),
                        round(max_3m_ret,2), round(max_6m_ret,2),round(max_9m_ret,2),round(max_1y_ret,2)]

    # summary_details = [round(count_3m_ret), round(count_6m_ret),round(count_9m_ret), round(count_1y_ret),
    #                     round(p_gainers_3m*100,2),round(p_gainers_6m*100,2),round(p_gainers_9m*100,2),round(p_gainers_1y*100,2),
    #                     round(mean_3m_ret,2), round(mean_6m_ret,2),round(mean_9m_ret,2), round(mean_1y_ret,2),
    #                     round(ret_3m_10,2),round(ret_6m_10,2),round(ret_9m_10,2),round(ret_1y_10,2),
    #                     round(ret_3m_25,2), round(ret_6m_25,2),round(ret_9m_25,2), round(ret_1y_25,2),
    #                     round(ret_3m_50,2), round(ret_6m_50,2), round(ret_9m_50,2), round(ret_1y_50,2),
    #                     round(max_3m_ret,2), round(max_6m_ret,2),round(max_9m_ret,2), round(max_1y_ret,2)]
    #print (df.columns)


    # Make A Plot
    df['date']=df['period'].apply(get_date)
    df['date']=pd.to_datetime(df['date'])
    x=df.groupby(['date','period']).agg(
        mcapg3m_count=pd.NamedAgg(column='mcapg3m',aggfunc='count'),
        mcapg3m_mean=pd.NamedAgg(column='mcapg3m',aggfunc='mean'),
        mcapg6m_count=pd.NamedAgg(column='mcapg6m',aggfunc='count'),
        mcapg6m_mean=pd.NamedAgg(column='mcapg6m',aggfunc='mean'),
        mcapg9m_count=pd.NamedAgg(column='mcapg9m',aggfunc='count'),
        mcapg9m_mean=pd.NamedAgg(column='mcapg9m',aggfunc='mean'),
        mcapg1y_count=pd.NamedAgg(column='mcapg1y',aggfunc='count'),
        mcapg1y_mean=pd.NamedAgg(column='mcapg1y',aggfunc='mean'),
    )
    x.reset_index(inplace=True)
    x['return3']=(1+x['mcapg3m_mean']/100).cumprod()*100
    x['return6']=(1+x['mcapg6m_mean']/100).cumprod()*100
    x['return9']=(1+x['mcapg9m_mean']/100).cumprod()*100
    x['return1y']=(1+x['mcapg1y_mean']/100).cumprod()*100

    # x['return12']=(1+x['mcapg1y_mean']/100).cumprod()*100

    fig, ax1 = plt.subplots(figsize=(12,8))
    #sns.lineplot(data=x['mcapg3m_mean'], marker='o', ax=ax1, legend='full', label='3-Month Return')
    # sns.barplot(data=x, x='period',y='mcapg3m_count',alpha=0.5,ax=ax1)
    sns.barplot(data=x, x='period',y='mcapg6m_count',alpha=0.5,ax=ax1)
    ax1.set_xlabel('Time Period')
    ax1.set_ylabel('Number of Observations')
    plt.xticks(rotation=30)
    ax_new=ax1.twinx()
    # sns.lineplot(data=x['return3'], marker='+',ax=ax_new, color='r', legend='full', label='Cumulative 3-Month Return')
    sns.lineplot(data=x['return3'],marker='+',ax=ax_new, color='r', legend='full', label='Cumulative 3-Month Return')
    sns.lineplot(data=x['return6'],marker='o',ax=ax_new, color='b', legend='full', label='Cumulative 6-Month Return')
    sns.lineplot(data=x['return9'],marker='x',ax=ax_new, color='g',legend='full',label='Cumulative 9-Month Return')
    sns.lineplot(data=x['return1y'],marker='+',ax=ax_new,color='k',legend='full',label='Cumulative 1-Year Return')
    ax_new.grid(None)
    ax_new.set_ylabel('Cumulative Return (%)')
    plt.title('Average Cumulative Return')
    ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
    #plt.legend()

    flike = io.BytesIO()
    plt.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    chart1 = b64

    #-------------------QUARTERLY SUMMARY DETAILS-----------
    aaa=df.groupby(['date','period']).agg({'mcapg1y':'mean','mcapg9m':'mean','mcapg6m':'mean','mcapg3m':'mean'}).droplevel('date')
    # aaa=df.groupby(['date','period']).agg({'mcapg1y':'mean','mcapg9m':'mean','mcapg6m':'mean','mcapg3m':'mean'}).droplevel('date')
    aaa.index.name=None
    count_3m_qtr = aaa.describe()['mcapg3m']['count']
    count_6m_qtr = aaa.describe()['mcapg6m']['count']
    count_9m_qtr = aaa.describe()['mcapg9m']['count']
    count_1y_qtr = aaa.describe()['mcapg1y']['count']

    mean_3m_qtr = aaa.describe()['mcapg3m']['mean']
    mean_6m_qtr = aaa.describe()['mcapg6m']['mean']
    mean_9m_qtr = aaa.describe()['mcapg9m']['mean']
    mean_1y_qtr = aaa.describe()['mcapg1y']['mean']

    max_3m_qtr = aaa.describe()['mcapg3m']['max']
    max_6m_qtr = aaa.describe()['mcapg6m']['max']
    max_9m_qtr = aaa.describe()['mcapg9m']['max']
    max_1y_qtr = aaa.describe()['mcapg1y']['max']

    pct_3m_pstv = len(aaa[aaa['mcapg3m']>0])/len(aaa)
    pct_6m_pstv = len(aaa[aaa['mcapg6m']>0])/len(aaa)
    pct_9m_pstv = len(aaa[aaa['mcapg9m']>0])/len(aaa)
    pct_1y_pstv = len(aaa[aaa['mcapg1y']>0])/len(aaa)

    ret_3m_qtr_10=aaa['mcapg3m'].quantile(0.10)
    ret_6m_qtr_10=aaa['mcapg6m'].quantile(0.10)
    ret_9m_qtr_10=aaa['mcapg9m'].quantile(0.10)
    ret_1y_qtr_10=aaa['mcapg1y'].quantile(0.10)

    ret_3m_qtr_25 = aaa.describe()['mcapg3m']['25%']
    ret_6m_qtr_25 = aaa.describe()['mcapg6m']['25%']
    ret_9m_qtr_25 = aaa.describe()['mcapg9m']['25%']
    ret_1y_qtr_25 = aaa.describe()['mcapg1y']['25%']

    qtr_details=[round(count_3m_qtr),round(count_6m_qtr),round(count_9m_qtr),round(count_1y_qtr),
                    round(mean_3m_qtr,2),round(mean_6m_qtr,2),round(mean_9m_qtr,2),round(mean_1y_qtr,2),
                    round(max_3m_qtr,2),round(max_6m_qtr,2),round(max_9m_qtr,2),round(max_1y_qtr,2),
                    round(pct_3m_pstv*100,2),round(pct_6m_pstv*100,2),round(pct_9m_pstv*100,2),round(pct_1y_pstv*100,2),
                    round(ret_3m_qtr_10,2),round(ret_6m_qtr_10,2),round(ret_9m_qtr_10,2),round(ret_1y_qtr_10,2),
                    round(ret_3m_qtr_25,2),round(ret_6m_qtr_25,2),round(ret_9m_qtr_25,2),round(ret_1y_qtr_25,2)
                    ]
    # qtr_details=[round(count_3m_qtr),round(count_6m_qtr),round(count_9m_qtr),round(count_1y_qtr),
    #                 round(mean_3m_qtr,2),round(mean_6m_qtr,2),round(mean_9m_qtr,2),round(mean_1y_qtr,2),
    #                 round(max_3m_qtr,2),round(max_6m_qtr,2),round(max_9m_qtr,2),round(max_1y_qtr,2),
    #                 round(pct_3m_pstv*100,2),round(pct_6m_pstv*100,2), round(pct_9m_pstv*100,2),round(pct_1y_pstv*100,2),
    #                 round(ret_3m_qtr_10,2),round(ret_6m_qtr_10,2),round(ret_9m_qtr_10,2),round(ret_1y_qtr_10,2),
    #                 round(ret_3m_qtr_25,2),round(ret_6m_qtr_25,2),round(ret_9m_qtr_25,2),round(ret_1y_qtr_25,2)
    #                 ]
    #--------------------------------------------------------

    #----------------------------------------------------------------------
    # Now we are not using the following graph. Both are merged into above
    #----------------------------------------------------------------------
    '''
    fig, ax2 = plt.subplots(figsize=(12,8))
    sns.lineplot(data=x['mcapg6m_mean'], marker='o', ax=ax2, legend='full', label='6-Month Return')
    sns.barplot(data=x, x='period',y='mcapg6m_count',alpha=0.5,ax=ax2)
    ax2.set_xlabel('Time Period')
    ax2.set_ylabel('Return (%)')
    plt.xticks(rotation=30)
    ax_new2=ax2.twinx()
    sns.lineplot(data=x['return6'],marker='+',ax=ax_new2, color='r', legend='full', label='Cumulative 6-Month Return')
    ax_new2.grid(None)
    ax_new2.set_ylabel('Cumulative Return (%)')
    plt.title('6 Month Average Return')
    ax2.xaxis.set_major_locator(plt.MaxNLocator(10))


    flike = io.BytesIO()
    plt.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    chart2 = b64
    '''
    #-------------------------------------------------------------------------
    # End
    #------------------------------------------------------------------------

    return buckets, matches, summary_details, chart1, qtr_details

def get_date(val):
    q=val[0:2]
    y=val[2:]
    if q=='Q1':
        return '{}-03-31'.format(y)
    elif q=='Q2':
        return '{}-06-30'.format(y)
    elif q=='Q3':
        return '{}-09-30'.format(y)
    else:
        return '{}-12-31'.format(y)

