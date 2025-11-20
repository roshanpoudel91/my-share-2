from django.shortcuts import render, redirect
from django.views import View
from .forms import CompanyForm, PostCompanyForm, LocationForm, TickerInput, ContactForm
from .newscript import main_calculation
from django.contrib.auth.mixins import LoginRequiredMixin
from .backscript import backtest
from .models import HousePrice, BasicData, CompanyBeta, Company

from .alphascript import alpha_calc

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64
from matplotlib.ticker import LinearLocator
import seaborn as sns
import datetime as dt
sns.set_theme(style='darkgrid')
import yfinance as yf

from dal import autocomplete

import traceback, sys
from finapp.scripts import company_upload, industry_upload, upload_global, upload_basic_data, data_upload2, update_beta
from django.http import HttpResponse
#import yahooquery as yq

#===========================================================
# Landing Page View
#===========================================================
def mainview(request):
    try:
        tickers=yf.download(tickers=['^IXIC','^GSPTSE','CADUSD=X','^DJI','^GSPC'], period='1d')['Close'].values.flatten().tolist()
    except:
        tickers=['Data Unavailable'] * 4

    context = {'tickers':tickers, 'is_auth':'user.is_authenticated'}
    return render(request, 'finapp/main.html', context)

#===========================================================
# Privacy Policy Page View
#===========================================================
def privacy(request):
    context = {}
    return render(request, 'finapp/privacy.html', context)

#===========================================================
# Terms of Use Page View
#===========================================================
def termsofuse(request):
    context = {}
    return render(request, 'finapp/termsofuse.html', context)

#============================================================
# Plans and Pricing View
#============================================================
def plans(request):
    context={}
    return render(request, 'finapp/plans.html',context)

#============================================================
# Help View
#============================================================
def helps(request):
    context={}
    return render(request, 'finapp/help.html',context)

#============================================================
# Coming Soon View
#============================================================
def coming(request):
    context={}
    return render(request, 'finapp/comingsoon.html',context)


#==================================================================
# Stock Selection View with company selection.
#==================================================================
class StockSelectionView(LoginRequiredMixin, View):
    """
    Creating a new version of Stock Input View which has only company selection button and will show the calculation by
    downloading data from yahoo finance without showing any data.
    """
    def get(self, request):
        # tick_form=Company.objects.all() #New Code
        # context={'tick_form':tick_form}
        if request.user.is_staff:
            datas=Company.objects.all()
        else:
            datas = Company.objects.filter(tier=1)
        form = CompanyForm()
        return render(request, 'finapp/stockselection.html', {'form':form,'datas':datas})

    def post(self,request):
        # tick_form=TickerInput(request.POST)
            tick_form=PostCompanyForm(request.POST)
            if tick_form.is_valid() is not True:
                context={'tick_form':tick_form}
                return render(request, 'finapp/stockselection.html', context)
            ticker=tick_form.cleaned_data['ticker']
            print(ticker)
            # This is backtest data

            #-----THIS IS FOR DEVELOPMENT ONLY CODE--------

            #buckets, matches, summary_details, chart1, qtr_details = backtest(ticker)

            #------END OF DEVELOPMENT ONLY CODE-------------

            #-----THIS IS FOR PRODUCTION ONLY CODE--------
            """
            try:
                buckets, matches, summary_details, chart1, qtr_details = backtest(ticker)
            except Exception as ex:
                errormsg = traceback.format_exc()
                print(ex)
                context={'traceback':errormsg, 'source':'Back Testing'}
                return render(request, 'finapp/errortemp.html',context)
            """
            #------END OF PRODUCTION ONLY CODE-------------


            #Getting Alpha Calculations---------
            comparative_table,tick_detail, ynews, new_result,plot1, plot2, waterfallchart,eer_table=alpha_calc(ticker)
            '''
            try:
                comparative_table,tick_detail, new_result,plot1, plot2, waterfallchart=alpha_calc(ticker)
            except Exception as ex:
                errormsg = traceback.format_exc()
                context={'traceback':errormsg, 'source':'Main Calculation'}
                return render(request, 'finapp/errortemp.html',context)
            '''
            #context={'comparative':comparative_table, 'is_data':True, 'tick_detail':tick_detail, 'new_result':new_result,'plot1':plot1,'plot2':plot2,'waterfallchart':waterfallchart, 'backout':buckets,
            #        'matches':matches, 'summary_details':summary_details, 'chart1':chart1, 'qtr_details':qtr_details}
            #print("tick_detail",tick_detail)
            request.session['comparative_table']=comparative_table
            request.session['new_result']=new_result
            request.session['eer_table']=eer_table
            request.session['plot1']=plot1
            request.session['waterfallchart']=waterfallchart


            context = {'tick_detail':tick_detail,'ticker':ticker, 'ynews':ynews}
            return render(request, 'finapp/stockresult2.html',context)


class PreScreenListView(View):
    def get(self, request):
       
     tickers = ['AMZN', 'WMT', 'COST']
     data_list = []

     for ticker in tickers:
       result = alpha_calc(ticker, 1)
       data_list.append({'ticker': ticker, 'data': result})

     context = {'data_list': data_list, 'tickers': tickers}
     return render(request, 'finapp/prescreenlist.html', context)
         

def stockPerformaceTab(request):
     comparative = request.session.get('comparative_table')
     new_result = request.session.get('new_result')
     ainc_data = request.session.get('ainc_data')
     abal_data = request.session.get('abal_data')
     qinc_data = request.session.get('qinc_data')
     qbal_data = request.session.get('qbal_data')
     eer = request.session.get('eer_table')
     html_content = render(request, 'finapp/tabs/performance.html',{'comparative':comparative,'new_result':new_result,'ainc_data':ainc_data,'abal_data':abal_data,'qinc_data':qinc_data,'qbal_data':qbal_data,'is_data':True,'eer':eer})

     return HttpResponse(html_content, content_type='text/html')

def stockVisualTab(request):
     plot1 = request.session.get('plot1')
     waterfallchart = request.session.get('waterfallchart')
     html_content = render(request, 'finapp/tabs/visualization.html',{'plot1':plot1,'waterfallchart':waterfallchart})
     return HttpResponse(html_content, content_type='text/html')

def stockBackTestTab(request):
     ticker = request.GET.get('ticker')
     print(ticker)
     buckets, matches, summary_details, chart1, qtr_details = backtest(ticker)
     html_content = render(request, 'finapp/tabs/back-testing.html',{'summary_details':summary_details,'chart1':chart1,'qtr_details':qtr_details})
     return HttpResponse(html_content, content_type='text/html')


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  New Stock Selection AutoComplete View
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class StockSelection2View(autocomplete.Select2ListView, View):
    def get_queryset(self):
        #if not self.request.user.is_authenticated:
        qs=Company.objects.all()

        if self.q:
            qs=qs.filter(name__istartswith=self.q)
        return qs



#===============================================================
# Real Estate View
#===============================================================
class RealEstateView(View):
    def get(self,request):
        form=LocationForm()
        context={'form':form,'msg':'get'}
        return render(request,'finapp/realestate.html',context)

    def post(self,request):
        form=LocationForm(request.POST)

        if form.is_valid():
            percentile=[]
            symbol=form.cleaned_data['location']

            #Getting data into table
            #--------------------------
            a = HousePrice.objects.only('value').filter(symbol=symbol).values()
            data=pd.DataFrame(a)
            data.columns=['Prg_Index','Ref_Date','Symbol','Vector','Coordinate','Value','Status']
            data['MA5Y']=data['Value'].rolling(20).mean()
            data['MA3Y']=data['Value'].rolling(12).mean()
            data['QReturn']=round(((data.Value/data.Value.shift(1))-1)*100,4)
            data['5YPrice']=data['Value'].shift(20).ffill()
            data['Five_YRet']=round(((data['Value']/data['5YPrice'])**(1/5)-1)*100,4)
            data=data.dropna()
            for Perc in (5,10,15,20,25,30,35,50,60,75,80,85):
                w =round(np.percentile(data.QReturn, Perc),3)
                y =round(np.percentile(data.Five_YRet, Perc),3)
                percentile.append((Perc,w,y))
                cols4=["Percentile","Quarterly Return (%)","5 Year Return (%)"]
                stat=pd.DataFrame(percentile,columns=cols4)
                #stat=stat.to_html()

            msg_1='There is more than {}% probability of getting an annual positive return.'.format(100-stat.iloc[stat.abs()['5 Year Return (%)'].idxmin()]['Percentile'])
            msg_2='You are likely to get an annual return of greater than {}% in 5 years.'.format(stat[stat['Percentile']==50].iloc[0]['5 Year Return (%)'])
            msg_3='There is 90% probability of getting an annual return greater than {}%.'.format(stat[stat['Percentile']==10].iloc[0]['5 Year Return (%)'])
            result_msg=[msg_1, msg_2, msg_3]
            #Making Chart
            #-------------
            b=HousePrice.objects.filter(symbol=symbol).values()
            df=pd.DataFrame(b)
            df.columns=['Prg_Index','Ref_Date','Symbol','Vector','Coordinate','Value','Status']
            df['Ref_Date']=pd.to_datetime(df['Ref_Date'])



            fig, ax = plt.subplots(figsize=(12,5))
            fig.autofmt_xdate()

            ax.xaxis.set_major_locator(mdates.YearLocator(base=2,month=12,day=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.set_xlabel('Year',labelpad=8.0,color='Blue',size=14,alpha=0.65)
            ax.set_ylabel('Value (%)',labelpad=8.0,color='Blue',size=14,alpha=0.65)
            ax.set_title('Real Estate Trend from 1980-2022\n(Indexed 2016 = 100%)',size=18,alpha=0.8,color='blue',pad=10)
            ax.tick_params(colors='b',labelsize=11)


            sns.lineplot(ax=ax,data=df,x='Ref_Date',y='Value',label=symbol)
            ax.legend()


            flike = io.BytesIO()
            fig.savefig(flike)
            b64 = base64.b64encode(flike.getvalue()).decode()
            chart = b64


            return render(request, 'finapp/realestate.html',{'stat':stat.to_html(border=0,justify="center",index=False), 'form':form, 'chart':chart,'msg':'post','result_msg':result_msg})
        context={'form':form,'msg':'get'}
        return render(request, 'finapp/realestate.html',context)



#===============================================================
# Contact Form View
#===============================================================
class ContactView(LoginRequiredMixin, View):
    def get(self, request):
        form = ContactForm()
        context={'form':form}
        return render(request, 'finapp/contact.html',context)

    def post(self,request):
        form=ContactForm(request.POST)
        if form.is_valid():
            contact=form.save(commit=False)
            contact.owner=request.user
            contact.save()
            #print(form.cleaned_data['comment'])
            msg='Thank You'
            context={'msg':msg}
            return render(request,'finapp/main.html',context)
        context={'form':form}
        return render(request, 'finapp/contact.html',context)


#===============================================================
# Extra View - For Trial And Error Codes
#===============================================================
class ExtraView(LoginRequiredMixin, View):
    """
    Creating a new version of Stock Selection View for internal trial and error code.
    """
    def get(self, request):
        tick_form=TickerInput()
        context={'tick_form':tick_form}
        return render(request, 'finapp/stockselection2.html', context)

    def post(self,request):
        tick_form=TickerInput(request.POST)
        if tick_form.is_valid():
            ticker=tick_form.cleaned_data['ticker']

            comparative_table, stock_result, tick_detail, our_result=main_calculation(ticker)
            stock_summary="The Summary"
            is_data=True

            context={'stock_result':stock_result, 'comparative':comparative_table, 'tick_detail':tick_detail, 'stock_summary':stock_summary, 'is_data':is_data, 'our_result':our_result }
            return render(request, 'finapp/stockresult2.html',context)
        context={'tick_form':tick_form}
        return render(request, 'finapp/stockselection2.html', context)

# For uploading the csv files
def temp(request):
    # industry_upload()
    # company_upload()
    # upload_global()
    # data_upload2()
    #update_beta()
    upload_basic_data()



    return HttpResponse("Hello, world!")


#============================================================================
# BETA test View
#============================================================================
from .forms import BetaPostCompanyForm
from .alpha2script import fin_calc
from .models import xCompany
class BetaStockSelectionView(LoginRequiredMixin, View):


    """
    BETA Version
    """
    def get(self, request):
        form=CompanyForm()
        if request.user.is_staff:
            datas=xCompany.objects.all()
            return render(request, 'finapp/betastockselection.html', {'form':form,'datas':datas})
        datas = xCompany.objects.filter(tier=1)
        return render(request, 'finapp/betastockselection.html', {'form':form,'datas':datas})

    def post(self,request):
        tick_form=BetaPostCompanyForm(request.POST)
        if tick_form.is_valid() is not True:
            context={'tick_form':tick_form}
            return render(request, 'finapp/betastockselection.html', context)
        ticker=tick_form.cleaned_data['ticker']
        #comparative_table,tick_detail, ynews, new_result,plot1, plot2, waterfallchart=alpha_calc(ticker)
        comparative_table,tick_detail,new_result,annual_income_data,quarterly_income_data,annual_balance_data,quarterly_balance_data=fin_calc(ticker)
        request.session['comparative_table']=comparative_table
        request.session['new_result']=new_result
        request.session['ainc_data']=annual_income_data
        request.session['abal_data']=annual_balance_data
        request.session['qinc_data']=quarterly_income_data
        request.session['qbal_data']=quarterly_balance_data
        context = {'tick_detail':tick_detail,'ticker':ticker}
        return render(request, 'finapp/betastockresult2.html',context)
#============================================================================
# End BETA test View
#============================================================================
