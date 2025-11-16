"""
STILL TO DO:
1. Creating database and pulling RF, ERP, GDP from there. Currently, it's hard-coded.
2. Creating database and pulling Contribution Margin from there. Currently, it's hard-coded as 0.
"""
import numpy as np
import pandas as pd
import datetime as dt
#from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import requests
from .models import xCompany, xAnnualBalanceSh, xAnnualIncomeSt, xQuarterlyBalanceSh, xQuarterlyIncomeSt, xHistory, Beta
import yfinance as yf
#from fmp_python.fmp import FMP

YEAR_LIST=['Q42024','Q42023','Q42022','Q42021']

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

def get_revenue(annual_income_st, quarterly_income_st, overview):
    revenue=annual_income_st['totalrevenue'].tolist()
    qrevenue=quarterly_income_st['totalrevenue'].tolist()
    revenue_TTM=float(overview['RevenueTTM'])
    return(revenue, qrevenue, revenue_TTM)

def get_ecos(annual_income_st, quarterly_income_st):
    x=annual_income_st['netincomefromcontinuingoperations'].fillna(annual_income_st['netincome'])
    ecos=x.to_list()
    x=quarterly_income_st['netincomefromcontinuingoperations'].fillna(annual_income_st['netincome'])[:4]
    ecos_TTM = x.sum()
    return(ecos, ecos_TTM)

def get_ebitda(annual_income_st, overview):
    ebitda=annual_income_st['ebitda'].tolist()
    try:
        ebitda_TTM=float(overview['EBITDA'])
    except:
        ebitda_TTM=0
    return(ebitda, ebitda_TTM)

def get_fiscal_date(annual_balance_sh,quarterly_balance_sh):
    fiscal_date=annual_balance_sh['fiscaldateending'].tolist()
    fiscal_date_TTM=quarterly_balance_sh['fiscaldateending'].iloc[0]
    return(fiscal_date, fiscal_date_TTM)

def get_long_term_debt(annual_balance_sh, quarterly_balance_sh):
    x=annual_balance_sh['longtermdebt'].fillna(0)
    long_term_debt=x.to_list()

    x=quarterly_balance_sh['longtermdebt'].fillna(0)
    long_term_debt_TTM=x[0]
    return(long_term_debt, long_term_debt_TTM)

def get_cash(annual_balance_sh, quarterly_balance_sh):
    x=annual_balance_sh['cashandshortterminvestments'].fillna(0)
    cash=x.to_list()

    x=quarterly_balance_sh['cashandshortterminvestments'].fillna(0)
    cash_TTM=x[0]
    return(cash, cash_TTM)

def get_margin(margin_data):
    margin_dict={}
    margin=[]

    for each in margin_data:
        margin_dict[each[0]]=[each[1],each[2],each[3]]


    for qtr in YEAR_LIST:
        if qtr in margin_dict.keys():
            margin.append(margin_dict[qtr])
        else:
            margin.append([None,None,None])
    return(margin[0],margin[1],margin[2],margin[3])

def get_beta(beta_data, beta_TTM):
    #year_list=['Q42024','Q42023','Q42022','Q42021']
    try:
        beta_mean=beta_data[beta_data.quarter.isin(YEAR_LIST)]['beta'].mean()
    except:
        beta_mean=beta_TTM
    beta=[]
    for each in YEAR_LIST:
        try:
            val=beta_data[beta_data.quarter==each]['beta'].iloc[0]
        except:
            val=beta_mean
        finally:
            beta.append(val)
    return beta

def get_price_data(ticker, historical_data, fiscal_date, fiscal_date_TTM):
    price_dict={}
    y_tick=yf.Ticker(ticker)
    price_dict['current']=round(y_tick.history(period='1d')['Close'].iloc[0],2)

    try:
        price_dict['3yr']=historical_data[historical_data.t_date <= dt.date.today()+relativedelta(years=-3)].iloc[0]['adj_close']
    except:
        price_dict['3yr']=None

    try:
        price_dict['5yr']=historical_data[historical_data.t_date <= dt.date.today()+relativedelta(years=-5)].iloc[0]['adj_close']
    except:
        price_dict['5yr']=None

    try:
        price_dict['10yr']=historical_data[historical_data.t_date <= dt.date.today()+relativedelta(years=-10)].iloc[0]['adj_close']
    except:
        price_dict['10yr']=None

    try:
        end_date_0=fiscal_date[0]+dt.timedelta(days=40)
        if end_date_0 > dt.date.today():
            end_date_0 = end_date_0 - dt.timedelta(days=5)
        price_dict['1fyb']=historical_data[historical_data.t_date <= end_date_0].iloc[0]['adj_close']
    except:
        price_dict['1fyb']=None
    try:
        end_date_1=fiscal_date[1]+dt.timedelta(days=40)
        price_dict['2fyb']=historical_data[historical_data.t_date <= end_date_1].iloc[0]['adj_close']
    except:
        price_dict['2fyb']=None
    try:
        end_date_2=fiscal_date[2]+dt.timedelta(days=40)
        price_dict['3fyb']=historical_data[historical_data.t_date <= end_date_2].iloc[0]['adj_close']
    except:
        price_dict['3fyb']=None
    try:
        end_date_3=fiscal_date[3]+dt.timedelta(days=40)
        price_dict['4fyb']=historical_data[historical_data.t_date <= end_date_3].iloc[0]['adj_close']
    except:
        price_dict['4fyb']=None

    return (price_dict)

def get_sharpe(ret_data,n):

    # 10-year sharpe ratio
    cutoff_date=pd.Timestamp(dt.datetime.now().year-n, dt.datetime.now().month,dt.datetime.now().day)
    if ret_data['t_date'].min()<=cutoff_date.date():
        ret_data['daily_return']=ret_data['adj_close'].pct_change()

        # slicing n year data
        slice_data=ret_data[ret_data['t_date'] >= cutoff_date.date()]
        mean_daily_return=slice_data['daily_return'].mean()
        std_daily_return=slice_data['daily_return'].std()
        mean_annual_return=(1+mean_daily_return)**252-1
        annual_std_dev=std_daily_return*(252**0.5)
        sharpe = mean_annual_return/annual_std_dev
        var = annual_std_dev * 1.28
        return (sharpe, var)
    else:
        return ('n/a','n/a')

# Main Calculation

def fin_calc(ticker, mass=False):
    apikey='DFHG4DGYXZA59F12'
    ny=10

    base_url='https://www.alphavantage.co/query?'
    params={'function':'OVERVIEW','symbol':ticker,'apikey':apikey}
    overview=requests.get(base_url,params=params).json()

    #data=[2024, 2023, 2022, 2021]
    rf=[4.86, 4.37, 4.14, 1.94]
    erp=[5.0, 5.5, 6, 5.5]
    gdp=[2.499, 2.335, 2.138, 2.159]

    rf_0=4.1
    erp_0=5.0
    gdp_0=2.453

    company=xCompany.objects.get(ticker=ticker)

    query_data = xAnnualIncomeSt.objects.filter(ticker=company).order_by('-fiscaldateending')[:5]
    annual_income_st_data=pd.DataFrame.from_records(query_data.values())

    query_data = xQuarterlyIncomeSt.objects.filter(ticker=company).order_by('-fiscaldateending')[:8]
    quarterly_income_st_data=pd.DataFrame.from_records(query_data.values())

    query_data = xAnnualBalanceSh.objects.filter(ticker=company).order_by('-fiscaldateending')[:5]
    annual_balance_sh_data=pd.DataFrame.from_records(query_data.values())

    query_data = xQuarterlyBalanceSh.objects.filter(ticker=company).order_by('-fiscaldateending')[:1]
    quarterly_balance_sh_data=pd.DataFrame.from_records(query_data.values())

    fiscal_date, fiscal_date_TTM = get_fiscal_date(annual_balance_sh_data,quarterly_balance_sh_data)

    # ============= STILL NEED TO WORK ON MARGIN ==========================
    margin_data = [0.0, 0.0, 0.0, 0.0] #GET FROM DATABASE TABLE margin_data
    conmgn=[0.,0.,0.,0.]
    conmgn_TTM=0.0
    # ============== END MARGIN CALCULATION ===============================

    query_data=Beta.objects.filter(ticker=company)
    beta_data=pd.DataFrame.from_records(query_data.values())

    query_data = xHistory.objects.filter(ticker=company).order_by('-t_date')
    historical_data = pd.DataFrame.from_records(query_data.values())

    # -- New sharpe calc
    ret_data = historical_data.sort_values('t_date', ascending=True)

    # 10-yr sharpe ratio
    ret_10, dev_10 = get_sharpe(ret_data,10)
    #print(f'Ret 10: {ret_10}; Var 10: {dev_10}')

    # 5-yr sharpe ratio
    ret_5, dev_5 = get_sharpe(ret_data,5)
    #print(f'Ret 5: {ret_5}; Var 5: {dev_5}')
    # 3-yr sharpe ratio
    ret_3, dev_3 = get_sharpe(ret_data,3)
    #print(f'Ret 3: {ret_3}; Var 3: {dev_3}')
    # -- end sharpe calc

    price_data = get_price_data(company.ticker, historical_data, fiscal_date, fiscal_date_TTM)

    # +++++++++++++++ Historical Graph (ECOS, Rev & Year End Closing Price) ++++++++++++++++++++++++++++
    query_data = xAnnualIncomeSt.objects.filter(ticker=company).order_by('fiscaldateending')
    graph_data=pd.DataFrame.from_records(query_data.values())

    # +++++++++++++++ END +++++++++++++++++++++++++++++++++++++++++

    # Getting 5 Annual Revenue & 8 Quarterly Revenue & Revenue TTM
    revenue, qrevenue, revenue_TTM=get_revenue(annual_income_st_data, quarterly_income_st_data, overview)

    # 4 Annual ECOS & ECOS TTM
    ecos, ecos_TTM=get_ecos(annual_income_st_data, quarterly_income_st_data)

    # 4 Annual EBITDA & EBITDA TTM
    ebitda, ebitda_TTM=get_ebitda(annual_income_st_data, overview)


    # 4 Long Term Debt & Long Term Debt TTM
    long_term_debt, long_term_debt_TTM=get_long_term_debt(annual_balance_sh_data, quarterly_balance_sh_data)

    # 4 Cash & Cash TTM
    cash, cash_TTM=get_cash(annual_balance_sh_data, quarterly_balance_sh_data)

    currentPrice=price_data['current']

    # Getting 4 Beta
    beta_TTM=float(overview['Beta'])
    beta=get_beta(beta_data,beta_TTM)

    """
    ============================================
    Downloading Data
    ============================================
    """
    quarterly_growth=round(float(overview['QuarterlyEarningsGrowthYOY'])*100,2)
    revenueGrowth=round(float(overview['QuarterlyRevenueGrowthYOY'])*100,2)
    marketCap=int(overview['MarketCapitalization'])

    try:
        operatingMargins=round(float(overview['OperatingMarginTTM'])*100,2)
    except:
        operatingMargins='n/a'
    companyname=overview['Name']
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

    # Last 3-yr, 5-yr, 10-yr return
    try:
        last_10_yr_price=price_data['10yr']
        last_10_return=round(((currentPrice / last_10_yr_price)**(1/10)-1) * 100,2)
    except:
        last_10_return='N/A'
    try:
        last_5_yr_price=price_data['5yr']
        last_5_return=round(((currentPrice / last_5_yr_price)**(1/5)-1) * 100,2)
    except:
        last_5_return='N/A'
    try:
        last_3_yr_price=price_data['3yr']
        last_3_return=round(((currentPrice / last_3_yr_price)**(1/3)-1) * 100,2)
    except:
        last_3_return='N/A'

    # Start of Calculations For Table 1

    # Revenue Growth
    base_rev_growth_TTM= sum(qrevenue[4:]) #(float(income_st['quarterlyReports'][4]['totalRevenue'])+float(income_st['quarterlyReports'][5]['totalRevenue'])+float(income_st['quarterlyReports'][6]['totalRevenue'])+float(income_st['quarterlyReports'][7]['totalRevenue']))
    rev_growth_TTM=round((revenue_TTM/base_rev_growth_TTM-1)*100,2)
    try:
        rev_growth_py=round((revenue[0]/revenue[1]-1)*100,2)
    except:
        rev_growth_py=None
    try:
        rev_growth_3y=round(np.average([
        revenue[0]/revenue[1]-1,
        revenue[1]/revenue[2]-1,
        revenue[2]/revenue[3]-1
        ])*100,2)
    except:
        rev_growth_3y=None
    try:
        rev_growth_4yb=round((revenue[3]/revenue[4]-1)*100,2)
    except:
        rev_growth_4yb=None


    # ECOS Margin

    try:
        ecos_margin_py=round(ecos[0]/revenue[0]*100,2)
    except:
        ecos_margin_py=None
    try:
        ecos_margin_3y=round(np.average([
        ecos[0]/revenue[0],
        ecos[1]/revenue[1],
        ecos[2]/revenue[2]
        ])*100,2)
    except:
        ecos_margin_3y=None
    try:
        ecos_margin_4yb=round(ecos[3]*100/revenue[3],2)
    except:
        ecos_margin_4yb=None

    try:
        ecos_mgn_calc1=ecos_TTM/revenue_TTM
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


    # DEBT

    debt_TTM=int((long_term_debt_TTM - cash_TTM)/1E6)
    try:
        debt_py=int((long_term_debt[0] - cash[0])/1E6)
    except:
        debt_py=None
    try:
        debt_3y=int(np.average([
        long_term_debt[0]-cash[0],
        long_term_debt[1]-cash[1],
        long_term_debt[2]-cash[2]
        ])/1E6)
    except:
        debt_3y=None
    try:
        debt_4yb=int((long_term_debt[3] - cash[3])/1E6)
    except:
        debt_4yb=None

    # EBITDA Margin

    ebitda_margin_TTM=round(ebitda_TTM*100/revenue_TTM,2)
    try:
        ebitda_margin_py=round(ebitda[0]*100/revenue[0],2)
    except:
        ebitda_margin_py=None
    try:
        ebitda_margin_3y=round(np.average([
        ebitda[0]/revenue[0],
        ebitda[1]/revenue[1],
        ebitda[2]/revenue[2]
        ])*100,2)
    except:
        ebitda_margin_3y=None
    try:
        ebitda_margin_4yb=round(ebitda[3]*100/revenue[3],2)
    except:
        ebitda_margin_4yb=None

    # Debt/EBITDA

    try:
        debt_ebitda_TTM=round((long_term_debt_TTM-cash_TTM)/ebitda_TTM,2)
    except:
        debt_ebitda_TTM=None
    try:
        debt_ebitda_py=round((long_term_debt[0]-cash[0])/ebitda[0],2)
    except:
        debt_ebitda_py=None
    try:
        debt_ebitda_3y=round(np.average([
        (long_term_debt[0]-cash[0])/ebitda[0],
        (long_term_debt[1]-cash[1])/ebitda[1],
        (long_term_debt[2]-cash[2])/ebitda[2],
        ]),2)
    except:
        debt_ebitda_3y=None
    try:
        debt_ebitda_4yb=round((long_term_debt[3]-cash[3])/ebitda[3],2)
    except:
        debt_ebitda_4yb=None

    # Market Cap
    try:
        mcap_1yb=price_data['1fyb']*marketCap/currentPrice
    except:
        mcap_1yb=None
    try:
        mcap_2yb=price_data['2fyb']*marketCap/currentPrice
    except:
        mcap_2yb=None
    try:
        mcap_3yb=price_data['3fyb']*marketCap/currentPrice
    except:
        mcap_3yb=None
    try:
        mcap_4yb=price_data['4fyb']*marketCap/currentPrice
    except:
        mcap_4yb=None

    market_cap=[mcap_1yb,mcap_2yb,mcap_3yb,mcap_4yb]
    market_cap_TTM=marketCap

    # Implied Growth Calculation
    try:
        ig0=stock_calculation(rf[0]/100,erp[0]/100,beta[0],ecos[0],market_cap[0],gdp[0]/100,ny,revenue[0],conmgn[0])
        ig0_b1=stock_calculation(rf[0]/100,erp[0]/100,1.0,ecos[0],market_cap[0],gdp[0]/100,ny,revenue[0],conmgn[0])
    except:
        ig0=None
        ig0_b1=None
    try:
        ig1=stock_calculation(rf[1]/100,erp[1]/100,beta[1],ecos[1],market_cap[1],gdp[1]/100,ny,revenue[1],conmgn[1])
        ig1_b1=stock_calculation(rf[1]/100,erp[1]/100,1.0,ecos[1],market_cap[1],gdp[1]/100,ny,revenue[1],conmgn[1])
    except:
        ig1=None
        ig1_b1=None
    try:
        ig2=stock_calculation(rf[2]/100,erp[2]/100,beta[2],ecos[2],market_cap[2],gdp[2]/100,ny,revenue[2],conmgn[2])
        ig2_b1=stock_calculation(rf[2]/100,erp[2]/100,1.0,ecos[2],market_cap[2],gdp[2]/100,ny,revenue[2],conmgn[2])
    except:
        ig2=None
        ig2_b1=None
    try:
        ig3=stock_calculation(rf[3]/100,erp[3]/100,beta[3],ecos[3],market_cap[3],gdp[3]/100,ny,revenue[3],conmgn[3])
        ig3_b1=stock_calculation(rf[3]/100,erp[3]/100,1.0,ecos[3],market_cap[3],gdp[3]/100,ny,revenue[3],conmgn[3])
    except:
        ig3=None
        ig3_b1=None
    imp_growth = [ig0,ig1,ig2,ig3]
    imp_growth_b1=[ig0_b1, ig1_b1, ig2_b1, ig3_b1]

    imp_growth_TTM=stock_calculation(rf_0/100, erp_0/100, beta_TTM, ecos_TTM, market_cap_TTM, gdp_0/100, ny, revenue_TTM,conmgn_TTM)
    imp_growth_TTM_b1=stock_calculation(rf_0/100, erp_0/100, 1.0, ecos_TTM, market_cap_TTM, gdp_0/100, ny, revenue_TTM,conmgn_TTM)
    try:
        imp_growth_py=imp_growth[0]
        imp_growth_py_b1=imp_growth_b1[0]
    except:
        imp_growth_py=None
        imp_growth_py_b1=None
    try:
        imp_growth_3y=round(np.average([imp_growth[0],imp_growth[1],imp_growth[2]]),2)
        imp_growth_3y_b1=round(np.average([imp_growth_b1[0],imp_growth_b1[1],imp_growth_b1[2]]),2)
    except:
        imp_growth_3y=None
        imp_growth_3y_b1=None
    try:
        imp_growth_4yb=imp_growth[3]
        imp_growth_4yb_b1=imp_growth[3]
    except:
        imp_growth_4yb=None
        imp_growth_4yb_b1=None

    # PERFORMANCE TAB


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
        '4 Year Before':[rev_growth_4yb,ecos_margin_4yb,debt_4yb,imp_growth_4yb,imp_growth_4yb_b1,ebitda_margin_4yb,debt_ebitda_4yb]}

    final_table=pd.DataFrame(final_data,columns=[ttm_str,prev_yr_str,'3 Yr Average','4 Year Before'],index=['Revenue Growth (%)','ECOS Margin (%)','Debt (M$)','Implied Growth (%)','Implied Growth (\u03B2=1) (%)','EBITDA Margin (%)','Debt/EBITDA'])

    # second_table
    # Calculating extrapolated_rev_growth
    months=round((fiscal_date_TTM-fiscal_date[0]).days/30)
    if months==0: months=12
    extra_rev_growth = round(((1+rev_growth_TTM/100)**(12/months)-1)*100,2)

    outer_list=[]
    for growth in [imp_growth_TTM, imp_growth_py, imp_growth_3y, imp_growth_4yb, extra_rev_growth, rev_growth_py, rev_growth_3y, rev_growth_4yb]:
        inner_list=[]
        for ecos_var in [ecos_margin_TTM, ecos_margin_py, ecos_margin_3y, ecos_margin_4yb]:
            try:
                get_gl=round(gain_loss(rf_0/100,erp_0/100,beta_TTM,revenue_TTM*ecos_var/100,market_cap_TTM,gdp_0/100,ny,revenue_TTM,conmgn_TTM,growth/100)*100,2)
            except:
                get_gl=None
            inner_list.append(get_gl)
        outer_list.append(inner_list)

    gain_loss_table=pd.DataFrame(outer_list,columns=['Current ECOS Margin (%)','Prior Year ECOS Margin (%)','3 Year Average ECOS Margin (%)','4 Year Before ECOS Margin (%)'],index=['Implied Growth','Previous Year Implied Growth','3 Year Average Implied Growth','4 Year Before Implied Growth','Extrapolated Revenue Growth','Prior Year Revenue Growth','3 Year Average Revenue Growth','4 Year Before Revenue Growth'])
    gain_loss_table_for_display=gain_loss_table.copy(deep=True)

    # Revenue Growth, ecos margin, ebitda margin table
    print(f'Revenue {revenue} \n ECOS {ecos} \n EBITDA {ebitda}')

    #end-performance-tab


    # Sending data to template
    tick_detail=[companyname,
                businessSummary,
                currentPrice,
                fiftyTwoWeekHigh,
                fiftyTwoWeekLow,
                dividendYield,
                'earningsDate',
                exDividendDate,
                last_10_return,last_5_return,last_3_return,
                int(marketCap/1E6),
                enterpriseValue,extra_rev_growth, quarterly_growth, 'earningsGrowth',revenueGrowth,
                ebitdaMargins,
                operatingMargins,
                ticker,
                industry, 'daily_volume',
                'news1[0]','news2[0]','news3[0]','news4[0]','news5[0]',
                'news1[1]','news2[1]','news3[1]','news4[1]','news5[1]']

    if mass:
        if fiscal_date_TTM == fiscal_date[0]:
            last_year=fiscal_date[1]
        else:
            last_year=fiscal_date[0]
        ret_dict={'Ticker':ticker,
              'Industry':industry,
              'Market Cap':round(marketCap/1E6),
              'EV':enterpriseValue,
              'Current Price':currentPrice,
              #'Daily Volume':daily_volume,

              'Debt-EBITDA TTM':debt_ebitda_TTM,


              'Quarterly Earnings Growth YoY':quarterly_growth,
              'Quarterly Revenue Growth YoY':revenueGrowth,
              'Extrapolated Revenue Growth':extra_rev_growth,


              'Last 10 Y Return':last_10_return,
              'Last 5 Y Return':last_5_return,
              'Last 3 Y Return':last_3_return,

              'Revenue Growth TTM':rev_growth_TTM,
              'Previous Year Revenue Growth':rev_growth_py,
              '3 Year Average Revenue Growth':rev_growth_3y,
              'Revenue Growth - 4 YB':rev_growth_4yb,

              'Implied Growth TTM':imp_growth_TTM,
              'Previous Year Implied Growth':imp_growth_py,
              '3 Year Average Implied Growth':imp_growth_3y,
              'Implied Growth - 4 YB': imp_growth_4yb,

              'ECOS Margin TTM':ecos_margin_TTM,
              'Previous Year ECOS Margin':ecos_margin_py,
              '3 Year Average ECOS Margin':ecos_margin_3y,
              'ECOS Margin - 4 YB': ecos_margin_4yb,

              'EBITDA Margin TTM':ebitda_margin_TTM,
              'Previous Year EBITDA Margin':ebitda_margin_py,
              '3 Year Average EBITDA Margin':ebitda_margin_3y,
              'EBITDA Margin - 4 YB': ebitda_margin_4yb,

              'Previous Year Ending': last_year,
              'TTM Ending': fiscal_date_TTM,
        }
        return (ret_dict)
    else:
        return(final_table.to_html(border=0,justify="center"),
            tick_detail,
            gain_loss_table_for_display.to_html(border=0,justify="center"),
            annual_income_st_data.to_html(border=0,justify="center"),
            quarterly_income_st_data.to_html(border=0,justify="center"),
            annual_balance_sh_data.to_html(border=0,justify="center"),
            quarterly_balance_sh_data.to_html(border=0,justify="center")
            )


"""
============================================
    MASS DOWNLOAD
============================================
"""

def mass_download():
    import time
    # Provide a list of tickers to download
    lst=xCompany.objects.all().values_list('ticker',flat=True)
    import warnings
    warnings.filterwarnings('ignore')

    out_dict={}
    error_files=[]

    i=0
    for ticker in lst:
        time1=time.time()
        try:
            print(f'{i}:{ticker}')
            output=fin_calc(ticker,mass=True)
            #print(output)
            out_dict[ticker]=output
        except:
            error_files.append(ticker)
            #print(f'Error encountered in ticker: {ticker}')
        finally:
            i+=1
            time2=time.time()
            elapsed_time=time2-time1
            if elapsed_time < 2:
                time.sleep(2-elapsed_time)

    # Need to create a csv file for error list
    print(f'Error List: {error_files}')
    odf=pd.DataFrame.from_dict(out_dict)
    odf.to_csv('all_data.csv')
