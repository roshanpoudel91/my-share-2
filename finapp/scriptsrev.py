"""
These are the scripts file to populate (or update) the database tables as per the provided csv files.
Please make sure we have the corresponding model already built-in before running these functions.

Step 1: Populate the Industry table using function 'industry_upload'.
Step 2: Populate the Company table using function 'company_upload'.

"""

def industry_upload():
    """
    Uploading or Updating the Industry Category into the model Industry using industry.csv file
    This model only contains the name column.
    """
    from .models import Industry
    with open('ind.csv','r') as fh:
        for line in fh:
            #print(f'Processing: {line}')
            line=line.strip()
            ind, created=Industry.objects.get_or_create(name=line)
            if created:
                print(f'New industry added: {line}')
                ind.save()


def company_upload():
    """
    Uploading or Updating the list of companies into the model Company.
    Pre-requisite: Industry table should be populated.

    Results: Please note if any "Industry Not Found" message shows up. If yes, then need to add the missing
    industry category and run again.

    """
    from .models import Company, Industry
    import csv
    Company.objects.update(active=False)
    fhand=open('company.csv', 'r')
    reader=csv.reader(fhand)
    for row in reader:
        try:
            ind=Industry.objects.get(name=row[3])
            cm, created=Company.objects.get_or_create(ticker=row[0],defaults={'name':'CompanyRussJul25','industry':ind})
            if created:
                cm.name=row[2]
                cm.longticker=row[1]
                cm.industry=ind
                print(f'New Company Created: {row[0]}')
            cm.active=True
            cm.save()
            #print(f'Processing: {cm.name}')
        except Industry.DoesNotExist:
            print(row[3], 'Industry Not Found')

def beta_upload():
    """
    IN PROGRESS - Not Yet Completed.. Check Code Before Proceeding...
    Uploading or Updating beta into the model Company.
    Pre-requisite: Company table should be populated.

    Results: Please note if any "Company Not Found" message shows up. If yes, then need to add the missing company first and run again.
    """
    from .models import NewBeta, Company
    import csv
    fhand=open('beta.csv','r')
    reader=csv.reader(fhand)
    for row in reader:
        try:
            cm=Company.objects.get(longticker=row[0])
            bt, created = NewBeta.objects.get_or_create(ticker=row[1],beta=row[2],quarter=row[3])
        except:
            print(row[1], 'Error')
    """
    class NewBeta(models.Model):
    ticker=models.ForeignKey('Company',related_name='betacompany',on_delete=models.CASCADE)
    quarter=models.CharField(max_length=6)
    beta=models.FloatField()

    def __str__(self):
        return f'{self.ticker.ticker}:{self.quarter}'


    """