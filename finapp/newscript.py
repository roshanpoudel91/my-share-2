import pandas as pd
import numpy as np
import yfinance as yf
import yahooquery as yq
import datetime as dt
import csv
from .models import BasicData, CompanyBeta, GlobalData
from .graphing import glplot


# Calculating Gain Loss

def gain_loss(rf, erp, beta, ecos, mcap, tgrowth, ny, rev, conmgn, growth):
    rate=rf+beta*erp
    if ecos > 0:
        cf=pd.DataFrame({'period':np.arange(1,ny+1),'cf':ecos})
        cf['cf']=ecos*(1+growth)**(cf['period']-1)
        cf['pv']=cf['cf']/(1+rate)**cf['period']
        npv=cf['pv'].sum()
        fv=ecos*(1+growth)**(max(cf['period']))
    else:
        cf=pd.DataFrame({'period':np.arange(1,ny+1),'cf':rev})
        cf['cf']=(rev*(1+growth)**(cf['period']-1)-rev)*conmgn + ecos
        cf['pv']=cf['cf']/(1+rate)**cf['period']
        npv=cf['pv'].sum()
        fv=(rev*(1+growth)**(max(cf['period']))-rev)*conmgn + ecos
    tv=fv/(rate-tgrowth)
    npv_tv=tv/(1+rate)**(max(cf['period'])+1)
    iev=npv+npv_tv
    gl=iev/mcap-1

    return gl

# Calculating Implied Growth

def stock_calculation(rf, erp, beta, ecos, mcap, tgrowth, ny, rev, conmgn):
    growth=0
    i=0
    ig=0
    rf, erp, beta, ecos, mcap, tgrowth, ny, rev, conmgn = rf, erp, beta, ecos, mcap, tgrowth, ny, rev, conmgn
    while i < 300:
        gl = gain_loss(rf, erp, beta, ecos, mcap, tgrowth, ny, rev, conmgn, growth)
        if gl > 0:
            growth-=0.005
        else:
            growth+=0.005
        if abs(gl) < 0.03:
            ig=round(growth*100,2)
            break
        i+=1
    return ig




# Main Calculation

def main_calculation(ticker):
    ticker=ticker
    tick=yq.Ticker(ticker) #Yahoo Query
    tick2=yf.Ticker(ticker) #Yahoo Finance

    #print(tick2)

    single_data=['summaryDetail','calendarEvents','assetProfile','defaultKeyStatistics','price','financialData']
    data_dict=tick.get_modules(single_data)
    data_dict2=tick2.info

    #print("---------Getting Data-------------")
    #print(data_dict2)

    # Getting Singular Data for Display Only. No calculations needed
    #----------------------------------------------------------------
    print(data_dict[ticker])
    company=data_dict[ticker]['price'].get('longName','N/A')
    marketCap=data_dict2.get('marketCap','N/A') #used in calculation
    enterpriseValue=data_dict2.get('enterpriseValue','N/A')
    currentPrice=data_dict[ticker]['financialData'].get('currentPrice','N/A') #Used in calculation
    fiftyTwoWeekLow=data_dict2.get('fiftyTwoWeekLow','N/A')
    fiftyTwoWeekHigh=data_dict2.get('fiftyTwoWeekHigh','N/A')
    try:
        dividendYield=round(data_dict2['dividendYield']*100,2) #round(data_dict[ticker]['summaryDetail']['dividendYield'],2)
    except:
        dividendYield='N/A'
    try:
        ebitdaMargins=round(data_dict2.get('ebitdaMargins','N/A')*100,2)
    except:
        ebitdaMargins='N/A'
    try:
        operatingMargins=round(data_dict2.get('operatingMargins','N/A')*100,2)
    except:
        operatingMargins='N/A'

    try:
        earningsDate=data_dict[ticker]['calendarEvents']['earnings']['earningsDate'][0].split(' ')[0]
    except:
        earningsDate='N/A'
    try:
        exDividendDate=data_dict[ticker]['calendarEvents']['exDividendDate'].split(' ')[0]
    except:
        exDividendDate='N/A'
    try:
        revenueGrowth=round(data_dict2.get('revenueGrowth','N/A')*100,2)
    except:
        revenueGrowth='N/A'
    try:
        earningsGrowth=round(data_dict2.get('earningsGrowth','N/A')*100,2)
    except:
        earningsGrowth='N/A'
    try:
        quarterly_growth=round(data_dict2.get('earningsQuarterlyGrowth','N/A')*100,2)
    except:
        quarterly_growth='N/A'

    longBusinessSummary=data_dict2.get('longBusinessSummary','N/A')
    industry=data_dict2.get('industry','N/A')

    # Getting Various Return from Stock Prices
    #----------------------------------------------------------------
    current_year=dt.datetime.now().year
    current_month=dt.datetime.now().month
    try:
        last_10_yr_price=yf.download(ticker,start=dt.datetime(current_year-10,current_month,1),end=dt.datetime(current_year-10,current_month,28)).iloc[-1,]['Adj Close']
        last_10_return=round(((currentPrice / last_10_yr_price)**(1/10)-1) * 100,2)
    except:
        last_10_return='N/A'
    try:
        last_5_yr_price=yf.download(ticker,start=dt.datetime(current_year-5,current_month,1),end=dt.datetime(current_year-5,current_month,28)).iloc[-1,]['Adj Close']
        last_5_return=round(((currentPrice / last_5_yr_price)**(1/5)-1) * 100,2)
    except:
        last_5_return='N/A'
    try:
        last_3_yr_price=yf.download(ticker,start=dt.datetime(current_year-3,current_month,1),end=dt.datetime(current_year-3,current_month,28)).iloc[-1,]['Adj Close']
        last_3_return=round(((currentPrice / last_3_yr_price)**(1/3)-1) * 100,2)
    except:
        last_3_return='N/A'


    # Getting Data used for calculations
    #----------------------------------------------------------------

    beta=data_dict2.get('beta','N/A')




    #--RF , ERP, GDP pulling from DataBase (for using on Website)
    #------------------------------------------------------------
    rf=[BasicData.objects.get(date=dt.date(2018,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2019,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2020,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2021,12,31)).rf_rate,
        BasicData.objects.get(date=dt.date(2022,12,31)).rf_rate]

    erp=[BasicData.objects.get(date=dt.date(2018,12,31)).erp,
        BasicData.objects.get(date=dt.date(2019,12,31)).erp,
        BasicData.objects.get(date=dt.date(2020,12,31)).erp,
        BasicData.objects.get(date=dt.date(2021,12,31)).erp,
        BasicData.objects.get(date=dt.date(2022,12,31)).erp]

    gdp=[BasicData.objects.get(date=dt.date(2018,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2019,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2020,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2021,12,31)).gdp,
        BasicData.objects.get(date=dt.date(2022,12,31)).gdp]

    #--RF , ERP, GDP pulling from CSV File (for using with Jupyter Notebook)
    #----------------------------------------------------------------------
    '''basicdata=pd.read_csv(r'basicdata.csv',names=['date','rf','erp','gdp'],parse_dates=['date'])
    data_2018=basicdata[basicdata['date']=='2018-12-31'].iloc[0]
    data_2019=basicdata[basicdata['date']=='2019-12-31'].iloc[0]
    data_2020=basicdata[basicdata['date']=='2020-12-31'].iloc[0]
    data_2021=basicdata[basicdata['date']=='2021-12-31'].iloc[0]
    data_2022=basicdata[basicdata['date']=='2022-12-31'].iloc[0]

    rf=[data_2018.rf, data_2019.rf, data_2020.rf, data_2021.rf, data_2022.rf]
    erp=[data_2018.erp, data_2019.erp, data_2020.erp, data_2021.erp, data_2022.erp]
    gdp=[data_2018.gdp, data_2019.gdp, data_2020.gdp, data_2021.gdp, data_2022.gdp] '''

    #-------------------------------------------------------------------------------

    #-- For 2018, getting all data from GlobalData Database Table (for website)
    #------------------------------------------------------------------------------
    try:
        data_2018=GlobalData.objects.get(period='Q42018',tick=ticker)
        try:
            revenue_2018=data_2018.annlrev * 1E6
        except:
            revenue_2018='N/A'
        try:
            ebitda_2018=data_2018.annlebitda *1E6
        except:
            ebitda_2018 = 'N/A'
        try:
            op_income_2018=data_2018.annlecos * 1E6
        except:
            op_income_2018='N/A'

        long_term_debt_2018=np.nan
        cash_2018=np.nan
        market_cap_2018=data_2018.mcap * 1E6


    except GlobalData.DoesNotExist:
        revenue_2018='N/A'
        ebitda_2018='N/A'
        op_income_2018='N/A'
        long_term_debt_2018=np.nan
        cash_2018=np.nan
        market_cap_2018=np.nan

    #-- For 2018, getting all data from global csv file (for Jupyter Notebook)
    #------------------------------------------------------------------------------
    '''globaldata=pd.read_csv(r'global.csv',names=['qend','longticker','mcap','period','tick','quarter',
                                                'year','annlrev','annlebitda','annlecos','revg6m','revg3m',
                                                'ecosmgn','conmgn3m','conmgn6m','beta','industry','indmgn'],
                           parse_dates=['qend'])
    global_data_2018=globaldata[(globaldata['period']=='Q42018') & (globaldata['tick']==ticker)].iloc[0]

    revenue_2018=global_data_2018.annlrev*1E6
    ebitda_2018=global_data_2018.annlebitda*1E6
    op_income_2018=global_data_2018.annlecos*1E6
    long_term_debt_2018=np.nan
    cash_2018=np.nan
    market_cap_2018=global_data_2018.mcap*1E6 '''

    #----------------------------------------------------------------------------------


    #--Beta needed from DataBase (for website)
    #-----------------------------------------------------------------------------------
    try:
        beta_past=CompanyBeta.objects.get(symbol=ticker).beta
    except:
        beta_past='N/A'

    #--Beta needed from csv file (for Jupyter Notebook)
    #-----------------------------------------------------------------------------------
    '''betas=pd.read_csv(r'beta.csv',names=['ticker','beta','industry'])
    beta_past=betas[betas['ticker']=='AAPL'].iloc[0].beta '''
    #-------------------------------------------------------------------------------------

    if beta == 'N/A': beta = beta_past
    if beta_past == 'N/A': beta_past = beta

    # Getting Data for Past Years
    df=tick.get_financial_data(['TotalRevenue','NetIncomeContinuousOperations','CashAndCashEquivalents',
                        'LongTermDebt','EBITDA','EBIT','DepreciationAndAmortization'])
    data=df[df['periodType']=='12M']
    data_TTM=df[(df['periodType']=='TTM')]

    #print(data_TTM['asOfDate'])

    # Revenue
    revenue_2019=data['TotalRevenue'][0]
    revenue_2020=data['TotalRevenue'][1]
    revenue_2021=data['TotalRevenue'][2]
    revenue_2022=data['TotalRevenue'][3]
    try:
        revenue_TTM=data_dict2['totalRevenue']
    except:
        revenue_TTM=data_TTM['TotalRevenue'][0]

    # EBITDA
    try:
        if np.isnan(data['EBITDA'][0]):
            ebitda_2019=data['EBIT'][0] + data['DepreciationAndAmortization'][0]
        else:
            ebitda_2019=data['EBITDA'][0]
    except KeyError:
        ebitda_2019=0

    try:
        if np.isnan(data['EBITDA'][1]):
            ebitda_2020=data['EBIT'][1] + data['DepreciationAndAmortization'][1]
        else:
            ebitda_2020=data['EBITDA'][1]
    except KeyError:
        ebitda_2020=0

    try:
        if np.isnan(data['EBITDA'][2]):
            ebitda_2021=data['EBIT'][2] + data['DepreciationAndAmortization'][2]
        else:
            ebitda_2021=data['EBITDA'][2]
    except KeyError:
        ebitda_2021=0

    try:
        if np.isnan(data['EBITDA'][3]):
            ebitda_2022=data['EBIT'][3] + data['DepreciationAndAmortization'][3]
        else:
            ebitda_2022=data['EBITDA'][3]
    except KeyError:
        ebitda_2022=0

    try:
        ebitda_TTM=data_dict2['ebitda']
    except:
        try:
            if np.isnan(data_TTM['EBITDA'][0]):
                ebitda_TTM=data_TTM['EBIT'][0] + data_TTM['DepreciationAndAmortization'][0]
            else:
                ebitda_TTM=data_TTM['EBITDA'][0]
        except KeyError:
            ebitda_TTM=0


    # Operating Income
    op_income_2019=data['NetIncomeContinuousOperations'][0]
    op_income_2020=data['NetIncomeContinuousOperations'][1]
    op_income_2021=data['NetIncomeContinuousOperations'][2]
    op_income_2022=data['NetIncomeContinuousOperations'][3]

    #print(ebitda_TTM)

    try:
        op_income_TTM=data_dict2['netIncomeToCommon']
    except:
        op_income_TTM=data_TTM['NetIncomeContinuousOperations'][0]

    # Long Term Debt
    try:
        long_term_debt_2019=data['LongTermDebt'][0]
    except:
        long_term_debt_2019=np.nan
    try:
        long_term_debt_2020=data['LongTermDebt'][1]
    except:
        long_term_debt_2020=np.nan
    try:
        long_term_debt_2021=data['LongTermDebt'][2]
    except:
        long_term_debt_2021=np.nan
    try:
        long_term_debt_2022=data['LongTermDebt'][3]
    except:
        long_term_debt_2022=np.nan
    try:
        long_term_debt_TTM=data_TTM['LongTermDebt'][0]
    except:
        long_term_debt_TTM=np.nan

    # Cash
    cash_2019=data['CashAndCashEquivalents'][0]
    cash_2020=data['CashAndCashEquivalents'][1]
    cash_2021=data['CashAndCashEquivalents'][2]
    cash_2022=data['CashAndCashEquivalents'][3]
    cash_TTM=data_TTM['CashAndCashEquivalents'][0]

    #print(cash_TTM)

    # Market Cap

    start_date_2019=data['asOfDate'][0]+dt.timedelta(days=35)
    end_date_2019=data['asOfDate'][0]+dt.timedelta(days=40)

    start_date_2020=data['asOfDate'][1]+dt.timedelta(days=35)
    end_date_2020=data['asOfDate'][1]+dt.timedelta(days=40)

    start_date_2021=data['asOfDate'][2]+dt.timedelta(days=35)
    end_date_2021=data['asOfDate'][2]+dt.timedelta(days=40)

    start_date_2022=data['asOfDate'][3]+dt.timedelta(days=35)
    end_date_2022=data['asOfDate'][3]+dt.timedelta(days=40)

    market_cap_2019=yf.download(ticker,
                            start=start_date_2019,
                            end=end_date_2019).iloc[-1]['Adj Close']*marketCap/currentPrice
    market_cap_2020=yf.download(ticker,
                            start=start_date_2020,
                            end=end_date_2020).iloc[-1]['Adj Close']*marketCap/currentPrice
    market_cap_2021=yf.download(ticker,
                            start=start_date_2021,
                            end=end_date_2021).iloc[-1]['Adj Close']*marketCap/currentPrice
    market_cap_2022=yf.download(ticker,
                            start=start_date_2022,
                            end=end_date_2022).iloc[-1]['Adj Close']*marketCap/currentPrice
    market_cap_TTM=marketCap


    # Start of Calculations
    revenue_growth_last=round((revenue_2022/revenue_2021-1)*100,2)
    revenue_growth_3_yr=round(np.average([(revenue_2022/revenue_2021-1.),(revenue_2021/revenue_2020-1.),(revenue_2020/revenue_2019-1.)])*100.0,2)
    try:
        revenue_growth_TTM = round((revenue_TTM/revenue_2022-1)*100,2)
    except:
        revenue_growth_TTM=revenueGrowth
    if revenue_2018 == 'N/A':
        revenue_growth_2019='N/A'
    else:
        revenue_growth_2019=round((revenue_2019/revenue_2018-1)*100,2)



    # ECOS Margin
    ecos_margin_2019=round(op_income_2019/revenue_2019*100,2)
    ecos_margin_2020=op_income_2020/revenue_2020
    ecos_margin_2021=op_income_2021/revenue_2021
    ecos_margin_2022=op_income_2022/revenue_2022
    ecos_margin_TTM=op_income_TTM/revenue_TTM

    ecos_margin_last=round(ecos_margin_2022*100,2)
    ecos_margin_3_yr=round(np.average([ecos_margin_2022,ecos_margin_2021,ecos_margin_2020])*100,2)
    ecos_margin_TTM=round(ecos_margin_TTM*100,2)

    # Debt
    debt_last=(long_term_debt_2022-cash_2022)
    debt_3_yr= np.average([long_term_debt_2022-cash_2022,
                       long_term_debt_2021-cash_2021,
                       long_term_debt_2020-cash_2020])
    debt_TTM = long_term_debt_TTM-cash_TTM
    if debt_TTM is np.nan:
        debt_TTM=enterpriseValue - marketCap
    debt_2019=long_term_debt_2019-cash_2019


    # EBITDA Margin
    ebitda_margin_last=round(ebitda_2022/revenue_2022*100,2)
    ebitda_margin_3_yr=round(np.average([ebitda_2022/revenue_2022,ebitda_2021/revenue_2021,ebitda_2020/revenue_2020])*100,2)
    ebitda_margin_TTM=round(ebitda_TTM/revenue_TTM*100,2)
    ebitda_margin_2019=round(ebitda_2019/revenue_2019*100,2)

    # Debt / EBITDA
    debt_ebitda_last=round(((long_term_debt_2022-cash_2022)/ebitda_2022),2)
    debt_ebitda_3_yr=round(np.average([(long_term_debt_2022-cash_2022)/ebitda_2022,
                             (long_term_debt_2021-cash_2021)/ebitda_2021,
                             (long_term_debt_2020-cash_2020)/ebitda_2020]),2)
    debt_ebitda_TTM=round((long_term_debt_TTM-cash_TTM)/ebitda_TTM,2)
    debt_ebitda_2019=round(((long_term_debt_2019-cash_2019)/ebitda_2019),2)



    # Getting conmgn & indmgn from database (for website)
    #---------------------------------------------------------------
    get_last_data=GlobalData.objects.filter(tick=ticker).last()
    conmgn3m=get_last_data.conmgn3m
    conmgn6m=get_last_data.conmgn6m
    indmgm=get_last_data.indmgm

    if conmgn3m is None: conmgn3m = 0
    if conmgn6m is None: conmgn6m = 0
    if indmgm is None: indmgm = 0
    #print(f'Con 3m: {conmgn3m}, Con 6m:{conmgn6m}, Ind Mgn:{indmgm}')
    conmgn=max(max(0,conmgn3m),max(0,conmgn6m),max(0,indmgm))/100

    # for 2019
    margin_2019=GlobalData.objects.filter(tick=ticker).filter(period='Q42019')[0]
    margin_2020=GlobalData.objects.filter(tick=ticker).filter(period='Q42020')[0]
    margin_2021=GlobalData.objects.filter(tick=ticker).filter(period='Q42021')[0]
    margin_2022=GlobalData.objects.filter(tick=ticker).filter(period='Q42022')[0]
    margin_TTM=GlobalData.objects.filter(tick=ticker).last()

    conmgn3m_2019=margin_2019.conmgn3m
    conmgn3m_2020=margin_2020.conmgn3m
    conmgn3m_2021=margin_2021.conmgn3m
    conmgn3m_2022=margin_2022.conmgn3m

    conmgn3m_TTM=margin_TTM.conmgn3m

    conmgn6m_2019=margin_2019.conmgn6m
    conmgn6m_2020=margin_2020.conmgn6m
    conmgn6m_2021=margin_2021.conmgn6m
    conmgn6m_2022=margin_2022.conmgn6m

    conmgn6m_TTM=margin_TTM.conmgn6m

    indmgn_2019=margin_2019.indmgm
    indmgn_2020=margin_2020.indmgm
    indmgn_2021=margin_2021.indmgm
    indmgn_2022=margin_2022.indmgm

    indmgn_TTM=margin_TTM.indmgm

    # Getting conmgn & indmgn from csv file (for Jypyter Notebook)
    #---------------------------------------------------------------
    '''global_19_22 = globaldata[(globaldata['tick']==ticker) & (globaldata['period'].isin(['Q42019','Q42020','Q42021','Q42022']))]

    conmgn3m_2019=global_19_22[global_19_22.period=='Q42019'].iloc[0].conmgn3m
    conmgn3m_2020=global_19_22[global_19_22.period=='Q42020'].iloc[0].conmgn3m
    conmgn3m_2021=global_19_22[global_19_22.period=='Q42021'].iloc[0].conmgn3m
    conmgn3m_2022=global_19_22[global_19_22.period=='Q42022'].iloc[0].conmgn3m

    conmgn3m_TTM=global_19_22.tail(1).iloc[0].conmgn3m

    conmgn6m_2019=global_19_22[global_19_22.period=='Q42019'].iloc[0].conmgn6m
    conmgn6m_2020=global_19_22[global_19_22.period=='Q42020'].iloc[0].conmgn6m
    conmgn6m_2021=global_19_22[global_19_22.period=='Q42021'].iloc[0].conmgn6m
    conmgn6m_2022=global_19_22[global_19_22.period=='Q42022'].iloc[0].conmgn6m

    conmgn6m_TTM=global_19_22.tail(1).iloc[0].conmgn6m

    indmgn_2019=global_19_22[global_19_22.period=='Q42019'].iloc[0].indmgn
    indmgn_2020=global_19_22[global_19_22.period=='Q42020'].iloc[0].indmgn
    indmgn_2021=global_19_22[global_19_22.period=='Q42021'].iloc[0].indmgn
    indmgn_2022=global_19_22[global_19_22.period=='Q42022'].iloc[0].indmgn

    indmgn_TTM=global_19_22.tail(1).iloc[0].indmgn '''

    #------------------------------------------------------------------------------

    '''conmgn_2019 = max(max(0,conmgn3m_2019),max(0,conmgn6m_2019),max(0,indmgn_2019))/100
    conmgn_2020 = max(max(0,conmgn3m_2020),max(0,conmgn6m_2020),max(0,indmgn_2020))/100
    conmgn_2021 = max(max(0,conmgn3m_2021),max(0,conmgn6m_2021),max(0,indmgn_2021))/100
    conmgn_2022 = max(max(0,conmgn3m_2022),max(0,conmgn6m_2022),max(0,indmgn_2022))/100
    conmgn_TTM = max(max(0,conmgn3m_TTM),max(0,conmgn6m_TTM),max(0,indmgn_TTM))/100'''

    conmgn_2019 = np.nanmax(np.array([0,conmgn3m_2019,conmgn6m_2019,indmgn_2019],dtype=np.float64))/100
    conmgn_2020 = np.nanmax(np.array([0,conmgn3m_2020,conmgn6m_2020,indmgn_2020],dtype=np.float64))/100
    conmgn_2021 = np.nanmax(np.array([0,conmgn3m_2021,conmgn6m_2021,indmgn_2021],dtype=np.float64))/100
    conmgn_2022 = np.nanmax(np.array([0,conmgn3m_2022,conmgn6m_2022,indmgn_2022],dtype=np.float64))/100
    conmgn_TTM = np.nanmax(np.array([0,conmgn3m_TTM,conmgn6m_TTM,indmgn_TTM],dtype=np.float64))/100


    # Now calculating Implied Growth
    ny=10
    imp_growth_2019=stock_calculation(rf[1]/100, erp[1]/100, beta_past, op_income_2019, market_cap_2019, gdp[1]/100, ny, revenue_2019, conmgn_2019)
    imp_growth_2020=stock_calculation(rf[2]/100, erp[2]/100, beta_past, op_income_2020, market_cap_2020, gdp[2]/100, ny, revenue_2020, conmgn_2020)
    imp_growth_2021=stock_calculation(rf[3]/100, erp[3]/100, beta_past, op_income_2021, market_cap_2021, gdp[3]/100, ny, revenue_2021, conmgn_2021)
    imp_growth_2022=stock_calculation(rf[4]/100, erp[4]/100, beta_past, op_income_2022, market_cap_2022, gdp[4]/100, ny, revenue_2022, conmgn_2022)
    imp_growth_TTM=stock_calculation(rf[4]/100, erp[4]/100, beta, op_income_TTM, market_cap_TTM, gdp[4]/100, ny, revenue_TTM, conmgn_TTM)

    # Last & Average Implied Growths
    imp_growth_last=imp_growth_2022
    imp_growth_3_yr=round(np.nanmean([imp_growth_2022,imp_growth_2021,imp_growth_2020]),2)

    ttm_date=data_TTM.iloc[-1]['asOfDate']
    ttm_str='TTM (Ending '+ ttm_date.strftime("%Y-%m-%d") +')'

    prev_yr_date=data.iloc[-1]['asOfDate']
    prev_yr_str='Previous Year (Ending ' + prev_yr_date.strftime("%Y-%m-%d") + ')'

    final_data={ttm_str:[revenue_growth_TTM,ecos_margin_TTM,round(debt_TTM/1E6,2),imp_growth_TTM,ebitda_margin_TTM,debt_ebitda_TTM],
    prev_yr_str:[revenue_growth_last,ecos_margin_last,round(debt_last/1E6,2),imp_growth_last,ebitda_margin_last,debt_ebitda_last],
    '3 Year Average':[revenue_growth_3_yr,ecos_margin_3_yr,round(debt_3_yr/1E6,2),imp_growth_3_yr,ebitda_margin_3_yr,debt_ebitda_3_yr],
    '2019 (Pre-COVID)':[revenue_growth_2019,ecos_margin_2019,round(debt_2019/1E6,2),imp_growth_2019,ebitda_margin_2019,debt_ebitda_2019]}

    final_table=pd.DataFrame(final_data,columns=[ttm_str,prev_yr_str,'3 Year Average','2019 (Pre-COVID)'],index=['Revenue Growth (%)','ECOS Margin (%)','Debt (M$)','Implied Growth (%)','EBITDA Margin (%)','Debt/EBITDA (%)'])


    #Extrapolated Revenue Growth
    quarters=round((ttm_date-prev_yr_date).days / 30)
    inter_rev_growth=round(((1+revenue_growth_TTM/100)**(12/quarters)-1)*100,2)

    tick_detail=[company,longBusinessSummary,currentPrice,fiftyTwoWeekHigh,fiftyTwoWeekLow,dividendYield,earningsDate,exDividendDate,last_10_return,last_5_return,last_3_return,int(marketCap/1E6),int(enterpriseValue/1E6),inter_rev_growth, earningsGrowth, quarterly_growth, ebitdaMargins, operatingMargins]


    # second_table
    rf=rf[4]/100
    erp=erp[4]/100
    beta=beta
    ecos=op_income_TTM
    mcap=market_cap_TTM
    gdp=gdp[4]/100
    ny=10
    rev=revenue_TTM
    conmgn=conmgn_TTM

    outer_list=[]
    for growth in [imp_growth_TTM, imp_growth_last, imp_growth_3_yr, imp_growth_2019, inter_rev_growth, revenue_growth_last, revenue_growth_3_yr, revenue_growth_2019]:
        inner_list=[]
        #print(imp_growth_TTM, imp_growth_3_yr, revenue_growth_TTM, revenue_growth_last, revenue_growth_3_yr, revenue_growth_2019)
        for ecos_var in [rev*ecos_margin_TTM/100, rev*ecos_margin_last/100, rev*ecos_margin_3_yr/100, rev*ecos_margin_2019/100]:
            get_gl=gain_loss(rf,erp,beta,ecos_var,mcap,gdp,ny,rev,conmgn,growth/100)
            inner_list.append(round(get_gl*100,2))
        outer_list.append(inner_list)

    gain_loss_table=pd.DataFrame(outer_list,columns=['Current ECOS Margin (%)','Prior Year ECOS Margin (%)','3 Year Average ECOS Margin (%)','2019 ECOS Margin (%)'],index=['Implied Growth','Previous Year Implied Growth','3 Year Average Implied Growth','2019 Implied Growth','Extrapolated Revenue Growth','Prior Year Revenue Growth','3 Year Average Revenue Growth','2019 Revenue Growth'])
    print(gain_loss_table.loc[['Implied Growth','Previous Year Implied Growth','3 Year Average Implied Growth','2019 Implied Growth']])


    # Getting Plots
    plot1=glplot(gain_loss_table.loc[['Implied Growth','Previous Year Implied Growth','3 Year Average Implied Growth','2019 Implied Growth']])
    plot2=glplot(gain_loss_table.loc[['Extrapolated Revenue Growth','Prior Year Revenue Growth','3 Year Average Revenue Growth','2019 Revenue Growth']])

    return(final_table.to_html(border=0,justify="center"), tick_detail, gain_loss_table.to_html(border=0,justify="center"),plot1,plot2)