from .models import BackTestData2, GlobalData
import csv

def data_upload2():
    fhand=open('finapp/static/finapp/assets/out.csv')
    reader=csv.reader(fhand)
    i=0
    for row in reader:
        #print(row)
        bd, created=BackTestData2.objects.get_or_create(period=row[0],ticker=row[1])
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
        bd.save()
        print(i)
        i+=1

def upload_global():
    #fhand=open('finapp/static/finapp/assets/gout.csv')
    fhand=open('global2.csv')
    reader=csv.reader(fhand)
    i=0
    for row in reader:
        #print('{}::{}'.format(row[1],row[7]))
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
            print(i)
            i+=1
