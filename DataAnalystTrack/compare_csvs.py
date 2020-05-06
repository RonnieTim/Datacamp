import csv

email_column_companies = []
email_column_companies_created = []
with open('companies.csv', 'r') as t1, open('CompaniesCreated.csv', 'r') as t2:
    companies = t1.readlines()
    companies_created = t2.readlines()


for line in companies:
    columns = line.split(",")
    email_column = columns[2]
    email_column_companies.append(email_column)

for line in companies_created:
    columns = line.split(",")
    email_column = columns[2]
    email_column_companies_created.append(email_column)

diff_column = [item for item in email_column_companies if not item in email_column_companies_created]

with open('results.csv', 'w') as result_file:
    wr = csv.writer(result_file)
    wr.writerow(diff_column)
