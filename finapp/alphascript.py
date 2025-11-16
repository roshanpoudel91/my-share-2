import numpy as np
import pandas as pd
import datetime as dt
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import requests
from .newscript import stock_calculation, gain_loss
from .models import BasicData, CompanyBeta, GlobalData
import yfinance as yf
from fmp_python.fmp import FMP
from .graphing import glplot2

from matplotlib.ticker import FuncFormatter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
import seaborn as sns
sns.set_theme(style='darkgrid')


def money(x, pos):
    'The two args are the value and tick position'
    return "${:,.0f}".format(x)
formatter = FuncFormatter(money)

def get_sharpe(ret_data,n):
    cut_off_date=dt.datetime.today() - dt.timedelta(days=365*n+5)
    cut_off_date=pd.Timestamp(cut_off_date.date())
    if ret_data.index.min()<=cut_off_date:

        ret_data['daily_return']=ret_data['Close'].pct_change()
        slice_data=ret_data[ret_data.index >= cut_off_date]
        mean_daily_return=slice_data['daily_return'].mean()
        std_daily_return=slice_data['daily_return'].std()
        mean_annual_return=(1+mean_daily_return)**252-1
        annual_std_dev=std_daily_return*(252**0.5)
        sharpe = mean_annual_return/annual_std_dev
        var = annual_std_dev * 1.28
        return (sharpe, var)
    else:
        return ('n/a','n/a')

def alpha_calc(ticker):
    base_url='https://www.alphavantage.co/query?'
    params={'function':'OVERVIEW','symbol':ticker,'apikey':'DFHG4DGYXZA59F12'}

    overview=requests.get(base_url,params=params).json()

    params['function']='INCOME_STATEMENT'
    income_st=requests.get(base_url,params=params).json()

    params['function']='BALANCE_SHEET'
    balance_sh=requests.get(base_url,params=params).json()

    params['function']='EARNINGS'
    eps=requests.get(base_url,params=params).json()

    params['function']='TIME_SERIES_DAILY_ADJUSTED'
    params['outputsize']='full'
    time_series=requests.get(base_url,params=params).json()


    #---- New Code Added to Get Rid of Yahoo Finance Date------#
    price_data=pd.DataFrame.from_dict(time_series['Time Series (Daily)'])
    price_data=price_data.T
    price_data.index=pd.to_datetime(price_data.index)
    #---- End of New Code---------#

    news=requests.get(base_url,params={'function':'NEWS_SENTIMENT','tickers':ticker,'apikey':'DFHG4DGYXZA59F12'}).json()
    try:
        news1=(news['feed'][0]['title'],news['feed'][0]['url'])
    except:
        news1=(None,None)
    try:
        news2=(news['feed'][1]['title'],news['feed'][1]['url'])
    except:
        news2=(None,None)
    try:
        news3=(news['feed'][2]['title'],news['feed'][2]['url'])
    except:
        news3=(None,None)
    try:
        news4=(news['feed'][3]['title'],news['feed'][3]['url'])
    except:
        news4=(None,None)
    try:
        news5=(news['feed'][4]['title'],news['feed'][4]['url'])
    except:
        news5=(None,None)


    # Data pulled from yfinance
    y_tick=yf.Ticker(ticker)

    try:
        y_info=y_tick.info
    except:
        y_info={'earningsGrowth':'n/a'}
    try:
        currentPrice = round(y_tick.history(period='1d')['Close'].iloc[0],2) #used in calculation
    except:
        currentPrice = float(price_data.iloc[0,4])

    try:
        quarterly_growth=round(float(overview['QuarterlyEarningsGrowthYOY'])*100,2)
    except:
        quarterly_growth='n/a'
    try:
        earningsGrowth=round(y_info['earningsGrowth']*100,2)
    except:
        earningsGrowth='n/a'
    try:
        revenueGrowth=round(float(overview['QuarterlyRevenueGrowthYOY'])*100,2)
    except:
        revenueGrowth='n/a'

    # Data pulled from AlphaVantage
    company=overview['Name']
    marketCap=int(overview['MarketCapitalization']) #used in calculation
    try:
        enterpriseValue=round(float(overview['EVToRevenue'])*float(overview['RevenueTTM'])/1E6,3)
    except:
        enterpriseValue='n/a'
    try:
        fiftyTwoWeekLow=overview['52WeekLow']
    except:
        fiftyTwoWeekLow='n/a'
    try:
        fiftyTwoWeekHigh=overview['52WeekHigh']
    except:
        fiftyTwoWeekHigh='n/a'
    try:
        dividendYield=round(float(overview['DividendYield'])*100,2)
    except:
        dividendYield='n/a'
    try:
        ebitdaMargins=round(float(overview['EBITDA'])*100/float(overview['RevenueTTM']),2)
    except:
        ebitdaMargins='n/a'
    try:
        operatingMargins=round(float(overview['OperatingMarginTTM'])*100,2)
    except:
        operatingMargins='n/a'
    try:
        exDividendDate=overview['ExDividendDate']
    except:
        exDividendDate='n/a'
    businessSummary=overview['Description']
    industry=overview['Industry']
    try:
        daily_volume=round(int(time_series['Time Series (Daily)'][next(iter(time_series['Time Series (Daily)']))]['6. volume'])/1E6,2)
    except:
        daily_volume='n/a'
    try:
        beta=float(overview['Beta'])
    except:
        beta='n/a'

    try:
        news=yf.Search(ticker, news_count=5).news
        ynews=[]
        for i in range(min(len(news),5)):
            ynews.append([news[i]['title'],news[i]['link']])
    except:
        ynews=[]

    #--Beta needed from DataBase (for website)
    #-----------------------------------------------------------------------------------
    try:
        beta_past=CompanyBeta.objects.get(symbol=ticker).beta
    except:
        beta_past='n/a'

    if beta == 'n/a': beta = beta_past
    if beta_past == 'n/a': beta_past = beta



    # Data pulled from FMP Python
    # --------------------------------
    try:
        fmp=FMP(api_key='e3a1aa4bd7e2a68ffa55bf8eda886f76')
        earningsDate=fmp.get_quote(ticker)[0]['earningsAnnouncement'][:10]
    except:
        earningsDate='n/a'



    # Getting Various Return from yfinance
    #----------------------------------------------------------------
    current_year=dt.datetime.now().year
    current_month=dt.datetime.now().month
    try:
        #--- New Code to Replace Yahoo Data Download-----#
        #dates=pd.date_range(start_date_0, end_date_0)
        #dfxx=price_data[price_data.index.isin(dates)]
        #print(dfxx)
        #adj_close_0=dfxx.iloc[-1]['5. adjusted close']
        #print(f'Adjusted Close 0 {adj_close_0}')
        # ****** last_10_yr_price=float(price_data[price_data.index >= dt.datetime.now()-relativedelta(years=10)].iloc[-1]['5. adjusted close'])
        #print(last_10_yr_price)
        last_10_yr_price=yf.download(ticker,start=dt.datetime(current_year-10,current_month,1),end=dt.datetime(current_year-10,current_month,28),progress=False).iloc[-1,]['Close'].values[0]
        last_10_return=round(((currentPrice / last_10_yr_price)**(1/10)-1) * 100,2)
    except:
        last_10_return='N/A'
    try:
        # ***** last_5_yr_price=float(price_data[price_data.index >= dt.datetime.now()-relativedelta(years=5)].iloc[-1]['5. adjusted close'])
        last_5_yr_price=yf.download(ticker,start=dt.datetime(current_year-5,current_month,1),end=dt.datetime(current_year-5,current_month,28),progress=False).iloc[-1,]['Close'].values[0]
        last_5_return=round(((currentPrice / last_5_yr_price)**(1/5)-1) * 100,2)
    except:
        last_5_return='N/A'
    try:
        # ***** last_3_yr_price=float(price_data[price_data.index >= dt.datetime.now()-relativedelta(years=3)].iloc[-1]['5. adjusted close'])
        last_3_yr_price=yf.download(ticker,start=dt.datetime(current_year-3,current_month,1),end=dt.datetime(current_year-3,current_month,28),progress=False).iloc[-1,]['Close'].values[0]
        #print(f'Last 3 Year Price {last_3_yr_price}')
        last_3_return=round(((currentPrice / last_3_yr_price)**(1/3)-1) * 100,2)
    except:
        last_3_return='N/A'

    # ----------------------------------------------------------------
    # Extracting data from AlphaVantage
    # 0=2024; 1= 2023; 2=2022; 3=2021; 4=2020
    revenue=[float(income_st['annualReports'][0]['totalRevenue']),
            float(income_st['annualReports'][1]['totalRevenue']),
            float(income_st['annualReports'][2]['totalRevenue']),
            float(income_st['annualReports'][3]['totalRevenue']),
            float(income_st['annualReports'][4]['totalRevenue'])
            ]

    revenue_TTM=float(overview['RevenueTTM'])

    ebitda=[float(income_st['annualReports'][0]['ebit']) if float(income_st['annualReports'][0]['ebitda'])=='None' else float(income_st['annualReports'][0]['ebitda']),
            float(income_st['annualReports'][1]['ebit']) if float(income_st['annualReports'][1]['ebitda'])=='None' else float(income_st['annualReports'][1]['ebitda']),
            float(income_st['annualReports'][2]['ebit']) if float(income_st['annualReports'][2]['ebitda'])=='None' else float(income_st['annualReports'][2]['ebitda']),
            float(income_st['annualReports'][3]['ebit']) if float(income_st['annualReports'][3]['ebitda'])=='None' else float(income_st['annualReports'][3]['ebitda']),
            float(income_st['annualReports'][4]['ebit']) if float(income_st['annualReports'][4]['ebitda'])=='None' else float(income_st['annualReports'][4]['ebitda'])
            ]

    try:
        ebitda_TTM=float(overview['EBITDA'])
    except:
        ebitda_TTM=0

    try:
        ecos_0=float(income_st['annualReports'][0]['netIncomeFromContinuingOperations'])
    except:
        ecos_0=float(income_st['annualReports'][0]['netIncome'])
    try:
        ecos_1=float(income_st['annualReports'][1]['netIncomeFromContinuingOperations'])
    except:
        ecos_1=float(income_st['annualReports'][1]['netIncome'])
    try:
        ecos_2=float(income_st['annualReports'][2]['netIncomeFromContinuingOperations'])
    except:
        ecos_2=float(income_st['annualReports'][2]['netIncome'])
    try:
        ecos_3=float(income_st['annualReports'][3]['netIncomeFromContinuingOperations'])
    except:
        ecos_3=float(income_st['annualReports'][3]['netIncome'])
    try:
        ecos_4=float(income_st['annualReports'][4]['netIncomeFromContinuingOperations'])
    except:
        ecos_4=float(income_st['annualReports'][4]['netIncome'])

    ecos=[ecos_0,ecos_1,ecos_2,ecos_3,ecos_4]

    try:
        ecos_q0=float(income_st['quarterlyReports'][0]['netIncomeFromContinuingOperations'])
    except:
        ecos_q0=float(income_st['quarterlyReports'][0]['netIncome'])
    try:
        ecos_q1=float(income_st['quarterlyReports'][1]['netIncomeFromContinuingOperations'])
    except:
        ecos_q1=float(income_st['quarterlyReports'][1]['netIncome'])
    try:
        ecos_q2=float(income_st['quarterlyReports'][2]['netIncomeFromContinuingOperations'])
    except:
        ecos_q2=float(income_st['quarterlyReports'][2]['netIncome'])
    try:
        ecos_q3=float(income_st['quarterlyReports'][3]['netIncomeFromContinuingOperations'])
    except:
        ecos_q3=float(income_st['quarterlyReports'][3]['netIncome'])


    ecos_calc=ecos_q0+ecos_q1+ecos_q2+ecos_q3
    ecos_TTM=ecos_calc

    long_term_debt=[0 if balance_sh['annualReports'][0]['longTermDebt'] == 'None' else float(balance_sh['annualReports'][0]['longTermDebt']),
            0 if balance_sh['annualReports'][1]['longTermDebt'] == 'None' else float(balance_sh['annualReports'][1]['longTermDebt']),
            0 if balance_sh['annualReports'][2]['longTermDebt'] == 'None' else float(balance_sh['annualReports'][2]['longTermDebt']),
            0 if balance_sh['annualReports'][3]['longTermDebt'] == 'None' else float(balance_sh['annualReports'][3]['longTermDebt']),
            0 if balance_sh['annualReports'][4]['longTermDebt'] == 'None' else float(balance_sh['annualReports'][4]['longTermDebt'])
            ]

    long_term_debt_TTM=0 if balance_sh['quarterlyReports'][0]['longTermDebt']=='None' else float(balance_sh['quarterlyReports'][0]['longTermDebt'])

    cash=[0 if balance_sh['annualReports'][0]['cashAndShortTermInvestments']=='None' else float(balance_sh['annualReports'][0]['cashAndShortTermInvestments']),
        0 if balance_sh['annualReports'][1]['cashAndShortTermInvestments']=='None' else float(balance_sh['annualReports'][1]['cashAndShortTermInvestments']),
        0 if balance_sh['annualReports'][2]['cashAndShortTermInvestments']=='None' else float(balance_sh['annualReports'][2]['cashAndShortTermInvestments']),
        0 if balance_sh['annualReports'][3]['cashAndShortTermInvestments']=='None' else float(balance_sh['annualReports'][3]['cashAndShortTermInvestments']),
        0 if balance_sh['annualReports'][4]['cashAndShortTermInvestments']=='None' else float(balance_sh['annualReports'][4]['cashAndShortTermInvestments'])
        ]

    cash_TTM=0 if balance_sh['quarterlyReports'][0]['cashAndShortTermInvestments']=='None' else float(balance_sh['quarterlyReports'][0]['cashAndShortTermInvestments'])

    fiscal_date=[parse(x) for x in [balance_sh['annualReports'][0]['fiscalDateEnding'],
             balance_sh['annualReports'][1]['fiscalDateEnding'],
             balance_sh['annualReports'][2]['fiscalDateEnding'],
             balance_sh['annualReports'][3]['fiscalDateEnding'],
             balance_sh['annualReports'][4]['fiscalDateEnding'],
            ]
            ]

    fiscal_date_TTM=parse(balance_sh['quarterlyReports'][0]['fiscalDateEnding'])

    # Start of Calculations For Table 1

    # Revenue Growth
    base_rev_growth_TTM=(float(income_st['quarterlyReports'][4]['totalRevenue'])+float(income_st['quarterlyReports'][5]['totalRevenue'])+float(income_st['quarterlyReports'][6]['totalRevenue'])+float(income_st['quarterlyReports'][7]['totalRevenue']))
    #base_rev_growth_ex_TTM=(float(income_st['quarterlyReports'][1]['totalRevenue'])+float(income_st['quarterlyReports'][2]['totalRevenue'])+float(income_st['quarterlyReports'][3]['totalRevenue'])+float(income_st['quarterlyReports'][4]['totalRevenue']))
    #rev_growth_ex_TTM=round((revenue_TTM/base_rev_growth_ex_TTM-1)*100,2)
    rev_growth_TTM=round((revenue_TTM/ base_rev_growth_TTM-1)*100,2)
    rev_growth_py=round((revenue[0]/revenue[1]-1)*100,2)
    rev_growth_3y=round(np.average([
        revenue[0]/revenue[1]-1,
        revenue[1]/revenue[2]-1,
        revenue[2]/revenue[3]-1
        ])*100,2)
    rev_growth_19=round((revenue[3]/revenue[4]-1)*100,2)
    try:
        rev_growth=[rev_growth_TTM,round((revenue[0]/revenue[1]-1)*100,2),round((revenue[1]/revenue[2]-1)*100,2),round((revenue[2]/revenue[3]-1)*100,2),round((revenue[3]/revenue[4]-1)*100,2)]
    except:
        rev_growth=[None*5]


    # ECOS Margin

    ecos_margin_py=round(ecos[0]/revenue[0]*100,2)
    ecos_margin_3y=round(np.average([
        ecos[0]/revenue[0],
        ecos[1]/revenue[1],
        ecos[2]/revenue[2]
        ])*100,2)
    ecos_margin_19=round(ecos[3]*100/revenue[3],2)

    try:
        ecos_mgn_calc1=ecos_calc/revenue_TTM
    except:
        ecos_mgn_calc1=0
    try:
        ecos_mgn_calc2=float((overview['MarketCapitalization'])/float(overview['PERatio']))/revenue_TTM
    except:
        ecos_mgn_calc2=0
    if ecos_mgn_calc1 != 0:
        ecos_mgn_ttm = round(ecos_mgn_calc1*100,2)
    elif ecos_mgn_calc2 != 0 :
        ecos_mgn_ttm = round(ecos_mgn_calc2*100,2)
    else:
        ecos_mgn_ttm=operatingMargins

    ecos_margin_TTM=ecos_mgn_ttm

    try:
        ecos_margin=[ecos_margin_TTM,round(ecos[0]/revenue[0]*100,2),round(ecos[1]/revenue[1]*100,2),round(ecos[2]/revenue[2]*100,2),round(ecos[3]/revenue[3]*100,2)]
    except:
        ecos_margin=[None*5]

    # DEBT

    debt_TTM=int((long_term_debt_TTM - cash_TTM)/1E6)
    debt_py=int((long_term_debt[0] - cash[0])/1E6)
    debt_3y=int(np.average([
        long_term_debt[0]-cash[0],
        long_term_debt[1]-cash[1],
        long_term_debt[2]-cash[2]
        ])/1E6)
    debt_19=int((long_term_debt[3] - cash[3])/1E6)

    # EBITDA Margin

    ebitda_margin_TTM=round(ebitda_TTM*100/revenue_TTM,2)
    ebitda_margin_py=round(ebitda[0]*100/revenue[0],2)
    ebitda_margin_3y=round(np.average([
        ebitda[0]/revenue[0],
        ebitda[1]/revenue[1],
        ebitda[2]/revenue[2]
        ])*100,2)
    ebitda_margin_19=round(ebitda[3]*100/revenue[3],2)

    try:
        ebitda_margin=[ebitda_margin_TTM,round(ebitda[0]*100/revenue[0],2),round(ebitda[1]*100/revenue[1],2),round(ebitda[2]*100/revenue[2],2),round(ebitda[3]*100/revenue[3],2)]
    except:
        ebitda_margin=[None*5]

    # Debt/EBITDA

    try:
        debt_ebitda_TTM=round((long_term_debt_TTM-cash_TTM)/ebitda_TTM,2)
    except:
        debt_ebitda_TTM='n/a'
    debt_ebitda_py=round((long_term_debt[0]-cash[0])/ebitda[0],2)
    debt_ebitda_3y=round(np.average([
        (long_term_debt[0]-cash[0])/ebitda[0],
        (long_term_debt[1]-cash[1])/ebitda[1],
        (long_term_debt[2]-cash[2])/ebitda[2],
        ]),2)
    debt_ebitda_19=round((long_term_debt[3]-cash[3])/ebitda[3],2)

    # Market Cap (From yfinance)

    start_date_3=fiscal_date[3]+dt.timedelta(days=35)
    end_date_3=fiscal_date[3]+dt.timedelta(days=40)

    start_date_2=fiscal_date[2]+dt.timedelta(days=35)
    end_date_2=fiscal_date[2]+dt.timedelta(days=40)

    start_date_1=fiscal_date[1]+dt.timedelta(days=35)
    end_date_1=fiscal_date[1]+dt.timedelta(days=40)

    start_date_0=fiscal_date[0]+dt.timedelta(days=35)
    end_date_0=fiscal_date[0]+dt.timedelta(days=40)

    if end_date_0 > dt.datetime.now():
        end_date_0 = end_date_0 - dt.timedelta(days=5)
        start_date_0 = start_date_0 - dt.timedelta(days=5)

    #--- New Code to Replace Yahoo Data Download-----#
    """
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

    #print(adj_close_0, adj_close_1, adj_close_2, adj_close_3)
    #print(type(adj_close_0), type(adj_close_1), type(adj_close_2), type(adj_close_3))
    market_cap=[float(adj_close_0) * marketCap / currentPrice,
                float(adj_close_1) * marketCap / currentPrice,
                float(adj_close_2) * marketCap / currentPrice,
                float(adj_close_3) * marketCap / currentPrice]

    #print(market_cap)

    """
    market_cap=[yf.download(ticker, progress=False,
                            start=start_date_0,
                            end=end_date_0, auto_adjust=False)['Close'][ticker][-1]*marketCap/currentPrice,
                yf.download(ticker,progress=False,
                            start=start_date_1,
                            end=end_date_1, auto_adjust=False)['Close'][ticker][-1]*marketCap/currentPrice,
                yf.download(ticker,progress=False,
                            start=start_date_2,
                            end=end_date_2, auto_adjust=False)['Close'][ticker][-1]*marketCap/currentPrice,
                yf.download(ticker,progress=False,
                            start=start_date_3,
                            end=end_date_3, auto_adjust=False)['Close'][ticker][-1]*marketCap/currentPrice
                ]

    #--- End New Code -------------#
    market_cap_TTM=marketCap

    # --- SHARPE RATIO
    cut_off_date=dt.datetime.today() - dt.timedelta(days=365*10+5)
    hist=yf.download(ticker,start=cut_off_date, end=dt.datetime.today())
    hist.columns=[col[0] for col in hist.columns.values]

    sharpe10 = get_sharpe(hist,10)
    sharpe5 = get_sharpe(hist,5)
    sharpe3 = get_sharpe(hist,3)
    #print(f'Sharpe 10: {sharpe10}; Sharpe 5: {sharpe5}; Sharpe 3 {sharpe3}')


    # --- END SHARPE RATIO









    ##----Reading from Database
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

    rf_ttm, erp_ttm, gdp_ttm = 4.1, 5.0, 2.453 #4.62, 5.0, 2.453

    """
    try:
        data_2019=GlobalData.objects.get(period='Q42019',tick=ticker)
        try:
            revenue_2019=data_2019.annlrev * 1E6
        except:
            revenue_2019='N/A'
        try:
            ebitda_2019=data_2019.annlebitda *1E6
        except:
            ebitda_2019 = 'N/A'
        try:
            op_income_2019=data_2019.annlecos * 1E6
        except:
            op_income_2019='N/A'

        long_term_debt_2019=np.nan
        cash_2019=np.nan
        market_cap_2019=data_2019.mcap * 1E6


    except GlobalData.DoesNotExist:
        revenue_2019='N/A'
        ebitda_2019='N/A'
        op_income_2019='N/A'
        long_term_debt_2019=np.nan
        cash_2019=np.nan
        market_cap_2019=np.nan"""


    ##----------------------
    # Getting conmgn & indmgn from database (for website)
    #---------------------------------------------------------------
    get_last_data=GlobalData.objects.filter(tick=ticker).last()
    conmgn3m=get_last_data.conmgn3m
    conmgn6m=get_last_data.conmgn6m
    indmgm=get_last_data.indmgm

    if conmgn3m is None: conmgn3m = 0
    if conmgn6m is None: conmgn6m = 0
    if indmgm is None: indmgm = 0
    conmgn=max(max(0,conmgn3m),max(0,conmgn6m),max(0,indmgm))/100

    # for 2019
    #margin_2019=GlobalData.objects.filter(tick=ticker).filter(period='Q42019')[0]
    #margin_2020=GlobalData.objects.filter(tick=ticker).filter(period='Q42020')[0]
    margin_2021=GlobalData.objects.filter(tick=ticker).filter(period='Q42021')[0]
    margin_2022=GlobalData.objects.filter(tick=ticker).filter(period='Q42022')[0]
    margin_2023=GlobalData.objects.filter(tick=ticker).filter(period='Q42023')[0]
    margin_2024=GlobalData.objects.filter(tick=ticker).filter(period='Q42024')[0]
    margin_TTM=GlobalData.objects.filter(tick=ticker).last()

    #conmgn3m_2019=margin_2019.conmgn3m
    #conmgn3m_2020=margin_2020.conmgn3m
    conmgn3m_2021=margin_2021.conmgn3m
    conmgn3m_2022=margin_2022.conmgn3m
    conmgn3m_2023=margin_2023.conmgn3m
    conmgn3m_2024=margin_2024.conmgn3m

    conmgn3m_TTM=margin_TTM.conmgn3m

    #conmgn6m_2019=margin_2019.conmgn6m
    #conmgn6m_2020=margin_2020.conmgn6m
    conmgn6m_2021=margin_2021.conmgn6m
    conmgn6m_2022=margin_2022.conmgn6m
    conmgn6m_2023=margin_2023.conmgn6m
    conmgn6m_2024=margin_2024.conmgn6m

    conmgn6m_TTM=margin_TTM.conmgn6m

    #indmgn_2019=margin_2019.indmgm
    #indmgn_2020=margin_2020.indmgm
    indmgn_2021=margin_2021.indmgm
    indmgn_2022=margin_2022.indmgm
    indmgn_2023=margin_2023.indmgm
    indmgn_2024=margin_2024.indmgm

    indmgn_TTM=margin_TTM.indmgm

    #conmgn_2019 = np.nanmax(np.array([0,conmgn3m_2019,conmgn6m_2019,indmgn_2019],dtype=np.float64))/100
    #conmgn_2020 = np.nanmax(np.array([0,conmgn3m_2020,conmgn6m_2020,indmgn_2020],dtype=np.float64))/100
    conmgn_2021 = np.nanmax(np.array([0,conmgn3m_2021,conmgn6m_2021,indmgn_2021],dtype=np.float64))/100
    conmgn_2022 = np.nanmax(np.array([0,conmgn3m_2022,conmgn6m_2022,indmgn_2022],dtype=np.float64))/100
    conmgn_2023 = np.nanmax(np.array([0,conmgn3m_2023,conmgn6m_2023,indmgn_2023],dtype=np.float64))/100
    conmgn_2024 = np.nanmax(np.array([0,conmgn3m_2024,conmgn6m_2024,indmgn_2024],dtype=np.float64))/100
    conmgn_TTM = np.nanmax(np.array([0,conmgn3m_TTM,conmgn6m_TTM,indmgn_TTM],dtype=np.float64))/100

    #stock_calculation(rf, erp, beta, ecos, mcap, tgrowth, ny, rev, conmgn)
    ny=10
    imp_growth = [stock_calculation(rf[0]/100,erp[0]/100,beta_past,ecos[0],market_cap[0],gdp[0]/100,ny,revenue[0],conmgn_2024),
                stock_calculation(rf[1]/100,erp[1]/100,beta_past,ecos[1],market_cap[1],gdp[1]/100,ny,revenue[1],conmgn_2023),
                stock_calculation(rf[2]/100,erp[2]/100,beta_past,ecos[2],market_cap[2],gdp[2]/100,ny,revenue[2],conmgn_2022),
                stock_calculation(rf[3]/100,erp[3]/100,beta_past,ecos[3],market_cap[3],gdp[3]/100,ny,revenue[3],conmgn_2021)
                ]
    imp_growth_b1 = [stock_calculation(rf[0]/100,erp[0]/100,1.0,ecos[0],market_cap[0],gdp[0]/100,ny,revenue[0],conmgn_2024),
                stock_calculation(rf[1]/100,erp[1]/100,1.0,ecos[1],market_cap[1],gdp[1]/100,ny,revenue[1],conmgn_2023),
                stock_calculation(rf[2]/100,erp[2]/100,1.0,ecos[2],market_cap[2],gdp[2]/100,ny,revenue[2],conmgn_2022),
                stock_calculation(rf[3]/100,erp[3]/100,1.0,ecos[3],market_cap[3],gdp[3]/100,ny,revenue[3],conmgn_2021)
                ]

    imp_growth_TTM=stock_calculation(rf_ttm/100, erp_ttm/100, beta, ecos_TTM, market_cap_TTM, gdp_ttm/100, ny, revenue_TTM,conmgn_TTM)
    imp_growth_TTM_b1=stock_calculation(rf_ttm/100, erp_ttm/100, 1.0, ecos_TTM, market_cap_TTM, gdp_ttm/100, ny, revenue_TTM,conmgn_TTM)
    imp_growth_py=imp_growth[0]
    imp_growth_py_b1=imp_growth_b1[0]
    imp_growth_3y=round(np.average([imp_growth[0],imp_growth[1],imp_growth[2]]),2)
    imp_growth_3y_b1=round(np.average([imp_growth_b1[0],imp_growth_b1[1],imp_growth_b1[2]]),2)
    imp_growth_19=imp_growth[3]
    imp_growth_19_b1=imp_growth_b1[3]



    conmgn=[conmgn_2024,conmgn_2023,conmgn_2022,conmgn_2021]


#performance_tab
    ttm_str='TTM (Ending '+ fiscal_date_TTM.strftime("%Y-%m-%d") +')'
    prev_yr_str='Previous Year (Ending ' + fiscal_date[0].strftime("%Y-%m-%d") + ')'
    if fiscal_date_TTM == fiscal_date[0]:
        rev_growth_py=round((revenue[1]/revenue[2]-1)*100,2)
        ecos_margin_py=round(ecos[1]/revenue[1]*100,2)
        debt_py=int((long_term_debt[1] - cash[1])/1E6)
        debt_ebitda_py=round((long_term_debt[1]-cash[1])/ebitda[1],2)
        ebitda_margin_py=round(ebitda[1]*100/revenue[1],2)
        imp_growth_py=imp_growth[1]
        prev_yr_str='Previous Year (Ending ' + fiscal_date[1].strftime("%Y-%m-%d") + ')'

    final_data={ttm_str:[rev_growth_TTM,ecos_margin_TTM,debt_TTM,imp_growth_TTM,imp_growth_TTM_b1,ebitda_margin_TTM,debt_ebitda_TTM],
        prev_yr_str:[rev_growth_py,ecos_margin_py,debt_py,imp_growth_py,imp_growth_py_b1,ebitda_margin_py,debt_ebitda_py],
        '3 Yr Average':[rev_growth_3y,ecos_margin_3y,debt_3y,imp_growth_3y,imp_growth_3y_b1,ebitda_margin_3y,debt_ebitda_3y],
        '4 Year Before':[rev_growth_19,ecos_margin_19,debt_19,imp_growth_19,imp_growth_19_b1,ebitda_margin_19,debt_ebitda_19]}

    final_table=pd.DataFrame(final_data,columns=[ttm_str,prev_yr_str,'3 Yr Average','4 Year Before'],index=['Revenue Growth (%)','ECOS Margin (%)','Debt (M$)','Implied Growth (%)','Implied Growth (\u03B2=1) (%)','EBITDA Margin (%)','Debt/EBITDA'])

    # ecos, ebitda, rev growth table
    print(f'Revenue G {rev_growth} \n ECOS M {ecos_margin} \n EBITDA M {ebitda_margin}')
    eer_df = pd.DataFrame({"Fiscal Date": [fiscal_date_TTM]+fiscal_date[:4], "Revenue Growth": rev_growth, "ECOS Margin": ecos_margin, "EBITDA Margin":ebitda_margin})
    eer_html = eer_df.to_html(index=False, border=0,justify="center")

    # second_table
    rf=rf_ttm/100 #rf_ttm, erp_ttm, gdp_ttm
    erp=erp_ttm/100
    beta=beta
    ecos=ecos_TTM
    mcap=market_cap_TTM
    gdp=gdp_ttm/100
    ny=10
    rev=revenue_TTM
    conmgn=conmgn_TTM

    # Calculating extrapolated_rev_growth
    months=round((fiscal_date_TTM-fiscal_date[0]).days/30)
    if months==0: months=12
    extra_rev_growth = round(((1+rev_growth_TTM/100)**(12/months)-1)*100,2)
    #extra_rev_growth = round(((1+rev_growth_ex_TTM/100)**(12/4)-1)*100,2)
    outer_list=[]
    for growth in [imp_growth_TTM, imp_growth_py, imp_growth_3y, imp_growth_19, extra_rev_growth, rev_growth_py, rev_growth_3y, rev_growth_19]:
        inner_list=[]
        #print(imp_growth_TTM, imp_growth_3_yr, revenue_growth_TTM, revenue_growth_last, revenue_growth_3_yr, revenue_growth_2019)
        for ecos_var in [rev*ecos_margin_TTM/100, rev*ecos_margin_py/100, rev*ecos_margin_3y/100, rev*ecos_margin_19/100]:
            get_gl=gain_loss(rf,erp,beta,ecos_var,mcap,gdp,ny,rev,conmgn,growth/100)
            inner_list.append(round(get_gl*100,2))
        outer_list.append(inner_list)

    gain_loss_table=pd.DataFrame(outer_list,columns=['Current ECOS Margin (%)','Prior Year ECOS Margin (%)','3 Year Average ECOS Margin (%)','2019 ECOS Margin (%)'],index=['Implied Growth','Previous Year Implied Growth','3 Year Average Implied Growth','2019 Implied Growth','Extrapolated Revenue Growth','Prior Year Revenue Growth','3 Year Average Revenue Growth','2019 Revenue Growth'])
    gain_loss_table_for_display=gain_loss_table.copy(deep=True)


#end-performance-tab

    # Getting Plots
    '''plot1=glplot(gain_loss_table.loc[['Implied Growth','Previous Year Implied Growth','3 Year Average Implied Growth','2019 Implied Growth']])
    plot2=glplot(gain_loss_table.loc[['Extrapolated Revenue Growth','Prior Year Revenue Growth','3 Year Average Revenue Growth','2019 Revenue Growth']])'''


    # --------------------------------------------------------------
    # ---------------------------------------------------------------
    gain_loss_table['CY_MGN%']=round(gain_loss_table['Current ECOS Margin (%)']/5,0)
    gain_loss_table['PY_MGN%']=round(gain_loss_table['Prior Year ECOS Margin (%)']/5,0)
    gain_loss_table['3YA_MGN%']=round(gain_loss_table['3 Year Average ECOS Margin (%)']/5,0)
    gain_loss_table['2019_MGN%']=round(gain_loss_table['2019 ECOS Margin (%)']/5,0)
    # gain_loss_table.loc[df['CY_MGN%'] <= -20, "gender"] = 1
    gain_loss_table.mask(gain_loss_table <=-20,-20,inplace=True)
    gain_loss_table.mask(gain_loss_table >=20,20,inplace=True)
    GL_2019MGN=round(min(max(gain_loss_table.at['Implied Growth', '2019_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_3YAMGN=round(min(max(gain_loss_table.at['Implied Growth', '3YA_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_PYMGN=round(min(max(gain_loss_table.at['Implied Growth', 'PY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_2019Revg=round(min(max(gain_loss_table.at['2019 Revenue Growth', 'CY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_3YARevg=round(min(max(gain_loss_table.at['3 Year Average Revenue Growth', 'CY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_PYRevg=round(min(max(gain_loss_table.at['Prior Year Revenue Growth', 'CY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_2019Sentiment=round(min(max(gain_loss_table.at['2019 Implied Growth', 'CY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_3YASentiment=round(min(max(gain_loss_table.at['3 Year Average Implied Growth', 'CY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_PYSentiment=round(min(max(gain_loss_table.at['Previous Year Implied Growth', 'CY_MGN%'],-20),20)*5/100*currentPrice,0)
    GL_Overall2019=round(max(GL_2019Sentiment+GL_2019Revg+GL_2019MGN,-currentPrice),0)
    GL_Overall3YA=round(max(GL_3YASentiment+GL_3YARevg+GL_3YAMGN,-currentPrice),0)
    GL_OverallPY=round(max(GL_PYSentiment+GL_PYRevg+GL_PYMGN,-currentPrice),0)
    df1 = pd.DataFrame(index = ['Like_PY','Like_3YA','Like_4YB'],
        data = {
        'ImpactFromEfficiencyChange': [GL_PYMGN,GL_3YAMGN,GL_2019MGN],
        'ImpactOfSpread-DemandtoImplied': [GL_PYRevg,GL_3YARevg,GL_2019Revg],
        'ImpactFromSentimentChange': [GL_PYSentiment,GL_3YASentiment,GL_2019Sentiment],
        'Overall': [GL_OverallPY,GL_Overall3YA,GL_Overall2019]
    })


    df = pd.DataFrame(index = ['IG', 'IG_PY',
                  'IG_3YA', 'IG_4YB','Extra REVG','REVG_PY','REVG_3YA','REVG_4YB'],
        data = {
            'ECOSMGN_CY': gain_loss_table["CY_MGN%"].values.tolist(),
            'ECOSMGN_PY': gain_loss_table["PY_MGN%"].values.tolist(),
            'ECOSMGN_3YA': gain_loss_table["3YA_MGN%"].values.tolist(),
            'ECOSMGN_4YB': gain_loss_table["2019_MGN%"].values.tolist()
        })

    plot1, plot2=glplot2(df1,df)

    #Data to plot. Do not include a total, it will be calculated
    index = ['Price','MGN_2019','MGN3YA_19','MGNPY_3YA','Demand_2019','Dem3YA_19','DemandPY_3YA','Sentiment_2019','Sentiment3YA_19','SentimentPY_3YA']
    #['Price','MGN_2019','Demand_2019','Sentiment_2019','MGN_3YA','Demand_3YA','Sentiment_3YA','MGN_PY','Demand_PY','Sentiment_PY']

    data2 = {'amount': [currentPrice,GL_2019MGN,GL_3YAMGN-GL_2019MGN,GL_PYMGN-GL_3YAMGN,GL_2019Revg,GL_3YARevg-GL_2019Revg,GL_PYRevg-GL_3YARevg,GL_2019Sentiment,GL_3YASentiment-GL_2019Sentiment,GL_PYSentiment-GL_3YASentiment]}
    #[currentPrice,GL_2019MGN,GL_2019Revg,GL_2019Sentiment,GL_3YAMGN,GL_3YARevg,GL_3YASentiment,GL_PYMGN,GL_PYRevg,GL_PYSentiment]}

    #Store data and create a blank series to use for the waterfall
    trans = pd.DataFrame(data=data2,index=index)
    blank = trans.amount.cumsum().shift(1).fillna(0)

    #Get the net total number for the final element in the waterfall
    total = trans.sum().amount
    trans.loc["Exp_Price"]= total
    blank.loc["Exp_Price"] = total

    #The steps graphically show the levels as well as used for label placement
    step = blank.reset_index(drop=True).repeat(3).shift(-1)
    step[1::3] = np.nan

    #When plotting the last element, we want to show the full bar,
    #Set the blank to 0
    blank.loc["Exp_Price"] = 0

    #Plot and label
    my_plot = trans.plot(kind='bar', stacked=True, bottom=blank,legend=None, figsize=(10,6), title="Price Waterfall")
    my_plot.plot(step.index, step.values,'k')
    my_plot.set_xlabel("Transaction Types")

    #Format the axis for dollars
    my_plot.yaxis.set_major_formatter(formatter)

    #Get the y-axis position for the labels
    y_height = trans.amount.cumsum().shift(1).fillna(0)

    #Get an offset so labels don't sit right on top of the bar
    maxi = trans.max()
    neg_offset = maxi / 25
    pos_offset = maxi / 50
    plot_offset = int(maxi.iloc[0] / 15)

    #Start label loop
    loop = 0
    for index, row in trans.iterrows():
        # For the last item in the list, we don't want to double count
        if row['amount'] == total:
            y = y_height[loop]
        else:
            y = y_height[loop] + row['amount']
        # Determine if we want a neg or pos offset
        if row['amount'] > 0:
            y += pos_offset
        else:
            y -= neg_offset
        my_plot.annotate("{:,.0f}".format(row['amount']),(loop,y),ha="center")
        loop+=1

    #Scale up the y axis so there is room for the labels
    my_plot.set_ylim(-currentPrice/2,blank.max()+int(plot_offset))
    #Rotate the labels
    my_plot.set_xticklabels(trans.index,rotation=15)
    #my_plot.get_figure().savefig("waterfall.png",dpi=200,bbox_inches='tight')

    flike = io.BytesIO()
    plt.savefig(flike)
    b64 = base64.b64encode(flike.getvalue()).decode()
    waterfallchart = b64



    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------

    tick_detail=[company,
                businessSummary,
                currentPrice,
                fiftyTwoWeekHigh,
                fiftyTwoWeekLow,
                dividendYield,
                earningsDate,
                exDividendDate,
                last_10_return,last_5_return,last_3_return,
                int(marketCap/1E6),
                enterpriseValue,extra_rev_growth, quarterly_growth, earningsGrowth,revenueGrowth,
                ebitdaMargins,
                operatingMargins,
                ticker,
                industry, daily_volume,
                news1[0],news2[0],news3[0],news4[0],news5[0],
                news1[1],news2[1],news3[1],news4[1],news5[1],
                sharpe10, sharpe5, sharpe3]


    return (final_table.to_html(border=0,justify="center"),tick_detail, ynews, gain_loss_table_for_display.to_html(border=0,justify="center"),plot1, plot2, waterfallchart, eer_html)


