import csv

dictionary = dict()
with open('companies.csv', 'r') as companies:
    content = companies.readlines()

for line in content:
    columns = line.split(",")
    email_column = columns[2]
    name_column = columns[4]
    dictionary[name_column] = email_column

with open('results.csv', 'r') as result_file:
    results_emails = result_file.readlines()

emails_to_match = []
for line in results_emails:
    columns = line.split(",")
    match_email = columns[0]
    emails_to_match.append(match_email)

for k, v in dictionary.items():
    if v in emails_to_match:
        print("Company: {}, Email: {},".format(k, v))
        print("\n")
