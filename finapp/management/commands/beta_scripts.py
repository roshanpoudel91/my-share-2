from finapp.models import xCompany, xIndustry, xAnnualBalanceSh, xQuarterlyBalanceSh, xAnnualIncomeSt, xQuarterlyIncomeSt, xHistory, Beta
import csv
import pandas as pd

def industry_upload():
    """
    Uploading or Updating the Industry Category into the model Industry using industry.csv file
    This model only contains the name column.
    """
    with open('industry_master.csv','r') as fh:
        for line in fh:
            print(f'Processing: {line}')
            line=line.strip()
            ind,created = xIndustry.objects.get_or_create(name=line)
            if created:
                ind.save()


def company_upload():
    """
    Uploading or Updating the list of companies into the model Company.
    Pre-requisite: Industry table should be populated.

    Results: Please note if any "Industry Not Found" message shows up. If yes, then need to add the missing
    industry category and run again.

    """
    xCompany.objects.update(active=False)
    fhand=open('company_master.csv', 'r')
    reader=csv.reader(fhand)
    for row in reader:
        try:
            ind=xIndustry.objects.get(name=row[3])
            cm, created=xCompany.objects.get_or_create(ticker=row[2],defaults={'name':'Company','industry':ind})
            if created:
                cm.name=row[0]
                cm.longticker=row[1]
                cm.industry=ind
            cm.active=True
            cm.save()
            print(f'Processing: {cm.name}')
        except xIndustry.DoesNotExist:
            print(row[3], 'Industry Not Found')

def annual_balance_sh_upload(fobj):
    #i=0
    if fobj=='ab':
        ftype='annual_balance_sh.csv'
        obj=xAnnualBalanceSh
    elif fobj=='qb':
        ftype='quarterly_balance_sh.csv'
        obj=xQuarterlyBalanceSh
    elif fobj=='ai':
        ftype='annual_income_st.csv'
        obj=xAnnualIncomeSt
    elif fobj=='qi':
        ftype='quarterly_income_st.csv'
        obj=xQuarterlyIncomeSt
    else:
        ftype='xx'
        print('Wrong file type chosen.')
        return None

    fhand=open(ftype,'r')
    reader=csv.reader(fhand)
    for row in reader:
        try:
            if fobj=='ab' or fobj=='qb':
                #i+=1
                cm=xCompany.objects.get(ticker=row[3])
                print(cm)
                a_b_sh,created=obj.objects.get_or_create(fiscaldateending=row[0], ticker=cm)
                a_b_sh.cashandshortterminvestments=row[1] if row[1] else None
                a_b_sh.longtermdebt=row[2] if row[2] else None
                a_b_sh.save()
                #print(a_b_sh.cashandshortterminvestments)
                print(f'Processing: {cm.ticker}::{a_b_sh.fiscaldateending}')
            elif fobj=='ai' or fobj=='qi':
                cm=xCompany.objects.get(ticker=row[6])
                a_b_sh,created=obj.objects.get_or_create(fiscaldateending=row[0], ticker=cm)
                a_b_sh.reportedcurrency=row[1] if row[1] else None
                a_b_sh.totalrevenue=row[2] if row[2] else None
                a_b_sh.ebitda=row[3] if row[3] else None
                a_b_sh.netincomefromcontinuingoperations=row[4] if row[4] else None
                a_b_sh.netincome=row[5] if row[5] else None
                a_b_sh.save()
                print(f'Processing: {cm.ticker}::{a_b_sh.fiscaldateending}')
            else:
                print("Wrong file type chosen.")
        except:
            print(f'Error Occurred')
        #if i>2: break


def history_upload():
    fhand=open('history1.csv', 'r')
    reader=csv.reader(fhand)
    i=1
    for row in reader:
        try:
            cm=xCompany.objects.get(ticker=row[1])
            his, created=xHistory.objects.get_or_create(t_date=row[0],ticker=cm, defaults={'adj_close':0.0})
            if created:
                his.adj_close=row[2]
                his.save()
            print(f'Processing: {i}')
        except:
            print(f'Error in row{i}')
        i+=1

def beta_upload():
    fhand=open('beta_file.csv','r')
    reader=csv.reader(fhand)
    i=1
    for row in reader:
        try:
            cm=xCompany.objects.get(ticker=row[0])
            bt, created = Beta.objects.get_or_create(ticker=cm, quarter=row[1], defaults={'beta':-100})
            if created:
                bt.beta=row[2]
                bt.save()
            print(f'Processing {i}')
        except:
            print(f'Error {i}')
        i+=1