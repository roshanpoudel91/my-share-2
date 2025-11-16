import pandas as pd
import numpy as np
from .models import HousePrice, BasicData, CompanyBeta, GlobalData
import csv
import yfinance as yf
import yahooquery as yq
import datetime as dt

def gain_loss(rf,erp,beta,ecos,mcap,tgrowth,ny,rev,conmgn,growth):
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



def stock_calculation2(rf,erp,beta,ecos,mcap,tgrowth,ny,rev,conmgn):
    rate=rf+beta*erp
    x=0
    i=0
    ig=0
    while i<300:
        growth=x/100
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

        i+=1
        if gl>0:
            x=x-0.5
        else:
            x=x+0.5
        if (abs(gl) < 0.03):
            ig=round(growth*100,2)
            break
    return ig


def stock_calculation(rf, erp, beta, ebitda, market_cap, tgrowth, ny):
    data=[]

    rate=max(rf+(beta*erp),0.1)

    ebitda1 = ebitda * 0.95
    ebitda2 = ebitda * 0.90
    ebitda3 = ebitda * 0.85
    ebitda4 = ebitda * 1.05

    for x in range(-20,100):
        growth=(x/100)-.005

        cf = pd.DataFrame({"period":np.arange(1,ny+1),'cf':ebitda})
        cf["cf"] = ebitda * (1 + growth) ** (cf["period"] - 1)
        cf["pv"] = cf["cf"] / (1 + rate) ** cf["period"]
        npv = cf["pv"].sum()
        fv = ebitda * (1 + growth) ** (max(cf["period"] ))
        tv = fv/(rate-tgrowth)
        npv_tv = tv/(1+rate) ** (max(cf["period"]) +1)
        iev = npv + npv_tv
        gl = iev/market_cap-1

        cf1 = pd.DataFrame({"period":np.arange(1,ny+1),'cf1':ebitda1})
        cf1["cf1"] = ebitda1 * (1 + growth) ** (cf1["period"] - 1)
        cf1["pv1"] = cf1["cf1"] / (1 + rate) ** cf1["period"]
        npv1 = cf1["pv1"].sum()
        fv1 = ebitda1 * (1 + growth) ** (max(cf1["period"] ))
        tv1 = fv1/(rate-tgrowth)
        npv_tv1 = tv1/(1+rate) ** (max(cf1["period"]) +1)
        iev1 = npv1 + npv_tv1
        gl1 = iev1/market_cap-1

        cf2 = pd.DataFrame({"period":np.arange(1,ny+1),'cf2':ebitda2})
        cf2["cf2"] = ebitda2 * (1 + growth) ** (cf2["period"] - 1)
        cf2["pv2"] = cf2["cf2"] / (1 + rate) ** cf2["period"]
        npv2 = cf2["pv2"].sum()
        fv2 = ebitda2 * (1 + growth) ** (max(cf2["period"] ))
        tv2 = fv2/(rate-tgrowth)
        npv_tv2 = tv2/(1+rate) ** (max(cf2["period"]) +1)
        iev2 = npv2 + npv_tv2
        gl2 = iev2/market_cap-1

        cf3 = pd.DataFrame({"period":np.arange(1,ny+1),'cf3':ebitda3})
        cf3["cf3"] = ebitda3 * (1 + growth) ** (cf3["period"] - 1)
        cf3["pv3"] = cf3["cf3"] / (1 + rate) ** cf3["period"]
        npv3 = cf3["pv3"].sum()
        fv3 = ebitda3 * (1 + growth) ** (max(cf3["period"] ))
        tv3 = fv3/(rate-tgrowth)
        npv_tv3 = tv3/(1+rate) ** (max(cf3["period"]) +1)
        iev3 = npv3 + npv_tv3
        gl3 = iev3/market_cap-1

        cf4 = pd.DataFrame({"period":np.arange(1,ny+1),'cf4':ebitda4})
        cf4["cf4"] = ebitda4 * (1 + growth) ** (cf4["period"] - 1)
        cf4["pv4"] = cf4["cf4"] / (1 + rate) ** cf4["period"]
        npv4 = cf4["pv4"].sum()
        fv4 = ebitda4 * (1 + growth) ** (max(cf4["period"] ))
        tv4 = fv4/(rate-tgrowth)
        npv_tv4 = tv4/(1+rate) ** (max(cf4["period"]) +1)
        iev4 = npv4 + npv_tv4
        gl4 = iev4/market_cap-1




        cols= ["Growth","Gain/Loss","Gain/Loss (95% Margin)","Gain/Loss (90% Margin)","Gain/Loss (85% Margin)","Gain/Loss (105% Margin)"]

        if abs(gl) < .30:
            data.append((round(growth*100,2),round(gl*100,2),round(gl1*100,2),round(gl2*100,2),round(gl3*100,2),round(gl4*100,2)))
            output = pd.DataFrame(data,columns=cols)
            #print('-----OUTPUT-----')
            #print(data)

        #This is the old code that's been commented out. In case of error in result table, need to revert.
        '''if x == 69:
            output1=output.iloc[output.abs()['Gain/Loss'].idxmin()] #output[(output['Gain_Loss']==min(abs(output['Gain_Loss'])))]
            is_data=True #output1.dropna().empty
            out_summary = "Growth to normalize to GDP rate in {} years with expected Perpetual Growth of {}% & Implied Growth of {}% till then. Expected gain or loss under different growth and margin scenarios as below:".format(ny,tgrowth*100, output1["Growth"])
            return (output.to_html(border=0,justify="center",index=False), out_summary, is_data)
            break'''
    try:
        is_data=True
        if data:
            output1=output.iloc[output.abs()['Gain/Loss'].idxmin()] #output[(output['Gain_Loss']==min(abs(output['Gain_Loss'])))]
            imp_growth=output1['Growth']
        else:
            output=pd.DataFrame()
            imp_growth='N/A'

    except:
        is_data=False #output1.dropna().empty
        imp_growth=0
    out_summary = "Growth to normalize to GDP rate in {} years with expected Perpetual Growth of {}% & Implied Growth of {}% till then. Expected gain or loss under different growth and margin scenarios as below:".format(ny,tgrowth*100, imp_growth)
    return (output.to_html(border=0,justify="center",index=False), out_summary, imp_growth)




def main_calculation(ticker):
	ticker=ticker
	tick=yq.Ticker(ticker)
	tick2=yf.Ticker(ticker)

	single_data=['summaryDetail','calendarEvents','assetProfile','defaultKeyStatistics','price','financialData']
	data_dict=tick.get_modules(single_data)
	data_dict2=tick2.info

	# Getting Single Data for Display Only. No calculations needed
	#----------------------------------------------------------------
	company=data_dict[ticker]['price'].get('longName','N/A')
	currentPrice=data_dict[ticker]['financialData'].get('currentPrice','N/A')
	try:
	    revenueGrowth=round(data_dict2.get('revenueGrowth','N/A')*100,2)
	except:
	    revenueGrowth='N/A'
	    #data_dict[ticker]['financialData'].get('revenueGrowth','N/A')

	try:
	    ebitdaMargins=round(data_dict2.get('ebitdaMargins','N/A')*100,2)
	except:
	    ebitdaMargins='N/A'
	    #data_dict[ticker]['financialData']['ebitdaMargins']

	try:
	    operatingMargins=round(data_dict2.get('operatingMargins','N/A')*100,2)
	except:
	    operatingMargins='N/A'
	    #data_dict[ticker]['financialData']['operatingMargins']
	enterpriseValue=data_dict2.get('enterpriseValue','N/A') #data_dict[ticker]['defaultKeyStatistics']['enterpriseValue']
	beta=data_dict2.get('beta','N/A') #data_dict[ticker]['defaultKeyStatistics'].get('beta','N/A')
	longBusinessSummary=data_dict2.get('longBusinessSummary','N/A') #data_dict[ticker]['assetProfile']['longBusinessSummary']
	industry=data_dict2.get('industry','N/A') #data_dict[ticker]['assetProfile']['industry']
	try:
	    earningsDate=data_dict[ticker]['calendarEvents']['earnings']['earningsDate'][0].split(' ')[0]
	except:
	    earningsDate='N/A'
	try:
	    exDividendDate=data_dict[ticker]['calendarEvents']['exDividendDate'].split(' ')[0]
	except:
	    exDividendDate='N/A'
	marketCap=data_dict2.get('marketCap','N/A') #data_dict[ticker]['price']['marketCap']
	fiftyTwoWeekLow=data_dict2.get('fiftyTwoWeekLow','N/A') #data_dict[ticker]['summaryDetail']['fiftyTwoWeekLow']
	fiftyTwoWeekHigh=data_dict2.get('fiftyTwoWeekHigh','N/A') #data_dict[ticker]['summaryDetail']['fiftyTwoWeekHigh']
	try:
	    dividendYield=round(data_dict2['dividendYield']*100,2) #round(data_dict[ticker]['summaryDetail']['dividendYield'],2)
	except:
	    dividendYield='N/A'
	try:
	    earningsGrowth=round(data_dict2.get('earningsGrowth','N/A')*100,2)
	except:
	    earningsGrowth='N/A'
	    #data_dict[ticker]['financialData'].get('earningsGrowth','N/A')
	try:
	    quarterly_growth=round(data_dict2.get('earningsQuarterlyGrowth','N/A')*100,2)
	except:
	    quarterly_growth='N/A'
	    #data_dict2.get('earningsQuarterlyGrowth','N/A')

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


	#--RF , ERP, GDP needed from DataBase
	#--------------------------------------------------------
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
		#-- For 2018, getting all data from GlobalData Database Table
	try:
	    data_2018=GlobalData.objects.get(period='Q42018',tick=ticker)
	    try:
	        revenue_2018=data_2018.annlrev * 1E6
	    except:
	        revenue_2018='N/A'
	    #print(revenue_2018)
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

	    #print('Data Not Found')

	#--Beta needed from DataBase
	try:
		beta_past=CompanyBeta.objects.get(symbol=ticker).beta
	except:
		beta_past='N/A'

	if beta == 'N/A': beta = beta_past
	if beta_past == 'N/A': beta_past = beta

	# Getting Data for Last Years
	df=tick.get_financial_data(['TotalRevenue','NetIncomeContinuousOperations','CashAndCashEquivalents',
                        'LongTermDebt','EBITDA','EBIT','DepreciationAndAmortization'])
	data=df[df['periodType']=='12M']
	data_TTM=df[(df['periodType']=='TTM')]

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
	if revenueGrowth == 'N/A':
	    revenue_growth_TTM = round((revenue_TTM/revenue_2022-1)*100,2)
	else:
	    revenue_growth_TTM=revenueGrowth #round((revenue_TTM/revenue_2022-1)*100,2)
	if revenue_2018 == 'N/A':
	    revenue_growth_2019='N/A'
	else:
	    revenue_growth_2019=round((revenue_2019/revenue_2018-1)*100,2)
	#print(f'********* Revenue 2019:{revenue_2019}, Revenue 2018{revenue_2018}')


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
	#print(debt_TTM, long_term_debt_TTM, cash_TTM,enterpriseValue, marketCap)

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


	# Implied Growth
	#imp_growth_2018=stock_calculation(rf[0]/100, erp[0]/100, beta_past, op_income_2018, market_cap_2018, gdp[0]/100, ny=10)
	if op_income_2019 > 0:
	    imp_growth_2019=stock_calculation(rf[1]/100, erp[1]/100, beta_past, op_income_2019, market_cap_2019, gdp[1]/100, ny=10)[2]
	else:
	    imp_growth_2019=np.nan
	if op_income_2020 > 0:
	    imp_growth_2020=stock_calculation(rf[2]/100, erp[2]/100, beta_past, op_income_2020, market_cap_2020, gdp[2]/100, ny=10)[2]
	else:
	    imp_growth_2020=np.nan
	if op_income_2021 > 0:
	    imp_growth_2021=stock_calculation(rf[3]/100, erp[3]/100, beta_past, op_income_2021, market_cap_2021, gdp[3]/100, ny=10)[2]
	else:
	    imp_growth_2021=np.nan
	if op_income_2022 > 0:
	    imp_growth_2022=stock_calculation(rf[4]/100, erp[4]/100, beta_past, op_income_2022, market_cap_2022, gdp[4]/100, ny=10)[2]
	else:
	    imp_growth_2022=np.nan

	imp_growth_TTM=stock_calculation(rf[4]/100, erp[4]/100, beta, op_income_TTM, market_cap_TTM, gdp[4]/100, ny=10)

	# Last & Average Implied Growths
	imp_growth_last=imp_growth_2022
	imp_growth_3_yr=round(np.nanmean([imp_growth_2022,imp_growth_2021,imp_growth_2020]),2)
	final_data={'TTM':[revenue_growth_TTM,ecos_margin_TTM,round(debt_TTM/1E6,2),imp_growth_TTM[2],ebitda_margin_TTM,debt_ebitda_TTM],
	'Previous Year':[revenue_growth_last,ecos_margin_last,round(debt_last/1E6,2),imp_growth_last,ebitda_margin_last,debt_ebitda_last],
	'3 Year Average':[revenue_growth_3_yr,ecos_margin_3_yr,round(debt_3_yr/1E6,2),imp_growth_3_yr,ebitda_margin_3_yr,debt_ebitda_3_yr],
	'2019 (Pre-COVID)':[revenue_growth_2019,ecos_margin_2019,round(debt_2019/1E6,2),imp_growth_2019,ebitda_margin_2019,debt_ebitda_2019]}
	final_table=pd.DataFrame(final_data,columns=['TTM','Previous Year','3 Year Average','2019 (Pre-COVID)'],index=['Revenue Growth (%)','ECOS Margin (%)','Debt (M$)','Implied Growth (%)','EBITDA Margin (%)','Debt/EBITDA (%)'])

	ig_table = imp_growth_TTM[0]
	tick_detail=[company,longBusinessSummary,currentPrice,fiftyTwoWeekHigh,fiftyTwoWeekLow,dividendYield,earningsDate,exDividendDate,last_10_return,last_5_return,last_3_return,int(marketCap/1E6),int(enterpriseValue/1E6),revenueGrowth, earningsGrowth, quarterly_growth, ebitdaMargins, operatingMargins]
	our_result=[]#result1, result2, result3]



	#=========================================================
	# New Calculation for negative ecos case
	#============================================================

	#stock_calculation2(rf,erp,beta,ecos,mcap,tgrowth,ny,rev,conmgn)
	rf=rf[4]/100
	erp=erp[4]/100
	beta=beta
	ecos=op_income_TTM
	mcap=market_cap_TTM
	gdp=gdp[4]/100
	ny=10
	rev=revenue_TTM
	get_last_data=GlobalData.objects.filter(tick=ticker).last()
	conmgn3m=get_last_data.conmgn3m
	conmgn6m=get_last_data.conmgn6m
	indmgm=get_last_data.indmgm

	if conmgn3m is None: conmgn3m = 0
	if conmgn6m is None: conmgn6m = 0
	if indmgm is None: indmgm = 0
	#print(f'Con 3m: {conmgn3m}, Con 6m:{conmgn6m}, Ind Mgn:{indmgm}')
	conmgn=max(max(0,conmgn3m),max(0,conmgn6m),max(0,indmgm))/100
	outer_data=[]
	#inner_data=[]
	#print(f'Con Mgn: {conmgn}')
	#print(f'rf:{rf}, erp:{erp},beta{beta},ecos:{ecos}, rev:{rev},ecos last:{ecos_margin_last},ecos 3 yr:{ecos_margin_3_yr},ecos 19:{ecos_margin_2019}')
	#print(f'mcap: {mcap}, gdp: {gdp}, ny:{ny}')
	print(imp_growth_TTM[2], imp_growth_3_yr, revenue_growth_TTM, revenue_growth_last, revenue_growth_3_yr, revenue_growth_2019)
	for growth in [imp_growth_TTM[2], imp_growth_3_yr, revenue_growth_TTM, revenue_growth_last, revenue_growth_3_yr, revenue_growth_2019]:
	    inner_data=[]
	    for ecos_var in [ecos, rev*ecos_margin_last/100, rev*ecos_margin_3_yr/100, rev*ecos_margin_2019/100]:
	        get_gl=gain_loss(rf,erp,beta,ecos_var,mcap,gdp,ny,rev,conmgn,growth/100)
	        inner_data.append(round(get_gl*100,2))
	    outer_data.append(inner_data)
	    #print(gain_loss(rf,erp,beta,ecos_var,mcap,gdp,ny,rev,conmgn,growth=aa/100))


	new_result=pd.DataFrame(outer_data,columns=['Current ECOS Margin','Prior Year ECOS Margin','3 Year Average ECOS Margin','2019 ECOS Margin'],index=['Implied Growth','3 Year Average Implied Growth','TTM Revenue Growth','Prior Year Revenue Growth','3 Year Average Revenue Growth','2019 Revenue Growth'])
	#print(new_result)









	#==========================================================
	# The End
	#==========================================================



	return(final_table.to_html(border=0,justify="center"), ig_table, tick_detail, our_result, new_result.to_html(border=0,justify="center"))


'''
	#Result Interpretation
	if imp_growth_TTM[2] > 0.9 * revenue_growth_3_yr:
		result1='overvalued'
	    #print('This company seems to be overvalued compared to average 3-year performance.')
	else:
		result1='undervalued'
	    #print('This company seems to be undervalued compared to average 3-year performance.')

	if imp_growth_TTM[2] > 0.8 * revenue_growth_TTM:
		result2='overvalued'
	    #print("This company seems to be overvalued compared to current 12 months' performance.")
	else:
		result2='undervalued'
	    #print("This company seems to be undervalued compared to current 12 months' performance.")

	if imp_growth_TTM[2] < imp_growth_3_yr:
		result3='undervalued'
	    #print("This company seems to be undervalued compared to 3 year average valuation.")
	else:
		result3='overvalued'
	    #print("This company seems to be overvalued compared to 3 year average valuation.") '''




#----------------------------------------------
# Importing HousePrice into our model
#----------------------------------------------

def upload_house():
	fhand = open('input.csv')
	reader = csv.reader(fhand)

	for row in reader:
		#print (row)
		hp, created = HousePrice.objects.get_or_create(ref_date=row[0],symbol=row[1])
		if created:
			hp.vector=row[2]
			hp.coordinate=row[3]
			if row[4]=='':
				hp.value=0
			else:
				hp.value=row[4]
			hp.status=row[5]
			hp.save()

def upload_basic_data():
    fhand=open('finapp/static/finapp/assets/basicdata.csv')
    reader=csv.reader(fhand)

    for row in reader:
        print(row)
        bd, created = BasicData.objects.get_or_create(date=row[0])
        if created:
            bd.rf_rate=row[1]
            bd.erp=row[2]
            bd.gdp=row[3]
            bd.save()

def update_beta():
    fhand=open('finapp/static/finapp/assets/beta24.csv')
    reader=csv.reader(fhand)
    for row in reader:
        print(row)
        bt, created = CompanyBeta.objects.get_or_create(symbol=row[0])
        if created:
            if row[1]!='': bt.beta=row[1]
            bt.save()

def update_betass():
    fhand=open('finapp/static/finapp/assets/beta24.csv')
    reader=csv.reader(fhand)
    count=0
    for row in reader:
        #print(row)
        try:
            bt=CompanyBeta.objects.get(symbol=row[0])
            if bt.beta is None:
                print(bt.beta)
                bt.beta=row[1]
                bt.save()
        except:
            print('company {} doesn\'t exist.'.format(row[0]))

def upload_global():
    fhand=open('finapp/static/finapp/assets/global24q2.csv')
    reader=csv.reader(fhand)
    for row in reader:
        print('{}::{}'.format(row[1],row[7]))
        gd, created=GlobalData.objects.get_or_create(longticker=row[1],period=row[7])
        if created:
            gd.qend=row[0]
            gd.revenue=row[2] if row[2] != '' else None
            gd.ebitda=row[3] if row[3] != '' else None
            gd.ecos=row[4] if row[4] != '' else None
            gd.ev=row[5] if row[5] != '' else None
            gd.mcap=row[6] if row[6] != '' else None
            gd.annlrev=row[8] if row[8] != '' else None
            gd.annlebitda=row[9] if row[9]!= '' else None
            gd.annlecos=row[10] if row[10] != '' else None
            gd.pp1mcap=row[11] if row[11] != '' else None
            gd.pp2mcap=row[12] if row[12] != '' else None
            gd.pp1annlrev=row[13] if row[13] != '' else None
            gd.pp2annlrev=row[14] if row[14] != '' else None
            gd.revg6m=row[15] if row[15] != '' else None
            gd.revg3m=row[16] if row[16] != '' else None
            gd.ecosmgn=row[17] if row[17] != '' else None
            gd.pp1annlecos=row[18] if row[18] != '' else None
            gd.pp2annlecos=row[19] if row[19] != '' else None
            gd.conmgn3m=row[20] if row[20] != '' else None
            gd.conmgn6m=row[21] if row[21] != '' else None
            gd.mcapg3m=row[22] if row[22] != '' else None
            gd.mcapg6m=row[23] if row[23] != '' else None
            gd.exch=row[24]
            gd.tick=row[25]
            gd.beta=row[26] if row[26] != '' else None
            gd.industry=row[27]
            gd.indrev=row[28] if row[28] != '' else None
            gd.indecos=row[29] if row[29] != '' else None
            gd.indmgm=row[30] if row[30] != '' else None

            gd.save()



def industry_upload():
    from .models import Industry
    with open('finapp/static/finapp/assets/industry.csv','r') as fh:
        for line in fh:
            print(line)
            line=line.strip()
            ind, created=Industry.objects.get_or_create(name=line)
            if created:
                ind.save()

def company_upload():
    from .models import Company, Industry
    fhand=open(f'finapp/static/finapp/assets/mycompany.csv')
    reader=csv.reader(fhand)
    for row in reader:
        #print(row)
        try:
            ind=Industry.objects.get(name=row[3])
            cm, created=Company.objects.get_or_create(ticker=row[0],defaults={'name':'Company'})
            if created:
                cm.name=row[2]
                cm.longticker=row[1]
                #cm.industry=ind
                cm.save()
                print('****')
        except Industry.DoesNotExist:
            print(row[3], 'Industry Not Found')

#-------------------------------------------------------------
#------------------------------------------------------------
#    New Bucket Building
#------------------------------------------------------------
def data_upload():
    from .models import BackTestData
    fhand=open('newbackdata.csv')
    reader=csv.reader(fhand)
    i=0
    for row in reader:
        #print(row)
        bd, created=BackTestData.objects.get_or_create(period=row[0],ticker=row[1])
        if created:
            bd.mcap=row[2] if row[2] else None
            bd.mcapg3m=row[3] if row[3] else None
            bd.mcapg6m=row[4] if row[4] else None
            bd.flag_val=row[5] if row[5] else None
            bd.flag_revg=row[6] if row[6] else None
            bd.flag_revga3y=row[7] if row[7] else None
            bd.flag_igr=row[8] if row[8] else None
            bd.flag_mgn=row[9] if row[9] else None
            bd.flag_disc_prem=row[10] if row[10] else None
            bd.flag_disc_prem_cy=row[11] if row[11] else None
            bd.flag_mcap=row[12] if row[12] else None
            bd.flag_spread_yoy=row[13] if row[13] else None
            bd.flag_spread_3ya=row[14] if row[14] else None
            bd.save()
            print(i)
            i+=1

#------------------------------------------------------------
#----- New BackTestData Upload
#------------------------------------------------------------
def data_upload2():
    from .models import BackTestData2
    fhand=open('finapp/static/finapp/assets/back2024.csv')
    reader=csv.reader(fhand)
    i=0
    for row in reader:
        #print(row)
        bd, created=BackTestData2.objects.get_or_create(period=row[0],ticker=row[1])
        if created:
            bd.mcap=row[2] if row[2] else None
            bd.mcapg3m=row[3] if row[3] else None
            bd.mcapg6m=row[4] if row[4] else None
            bd.mcapg9m=row[5] if row[5] else None
            bd.mcapg1y=row[6] if row[6] else None

            bd.amcapg3m=row[7] if row[7] else None
            bd.amcapg6m=row[8] if row[8] else None
            bd.amcapg9m=row[9] if row[9] else None
            bd.amcapg1y=row[10] if row[10] else None

            bd.flag_val=row[11] if row[11] else None
            bd.flag_revg=row[12] if row[12] else None
            bd.flag_revg_3ya=row[13] if row[13] else None
            bd.flag_igr=row[14] if row[14] else None
            bd.flag_mgn=row[15] if row[15] else None
            bd.flag_disc_prem=row[16] if row[16] else None
            bd.flag_disc_prem_cy=row[17] if row[17] else None
            bd.flag_mcap=row[18] if row[18] else None
            bd.flag_spread_yoy=row[19] if row[19] else None
            bd.flag_spread_3ya=row[20] if row[20] else None

            bd.flag_yield=row[21] if row[21] else None
            bd.flag_yield_3ya=row[22] if row[22] else None
            bd.flag_payout_ratio=row[23] if row[23] else None
            bd.flag_payout_ratio_3ya=row[24] if row[24] else None
            bd.flag_cfo_to_rev=row[25] if row[25] else None
            bd.flag_cfo_to_rev_3ya=row[26] if row[26] else None
            bd.pcount=row[27] if row[27] else None
            bd.save()
            print(i)
            i+=1

def data_upload3():
    """
    Adding Only revg3ya as it was missing in previous version
    """
    from .models import BackTestData2
    fhand=open('back22.csv')
    reader=csv.reader(fhand)
    i=0
    for row in reader:
        #print(row)
        bd, created=BackTestData2.objects.get_or_create(period=row[0],ticker=row[1])
        bd.flag_revg_3ya=row[2] if row[2] else None
        bd.save()
        print(i)
        i+=1
