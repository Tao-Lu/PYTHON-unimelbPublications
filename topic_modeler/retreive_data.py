import couchdb
import csv

couch=couchdb.Server("http://admin:password@localhost:5984")
try:
    database=couch["paperinfo_scopus"]
except:
    print("wrong db name")

with open('title_abstract.csv', 'w') as csvfile:
    fieldnames = ['paperId', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for id in database:
        idstr = str(id)+"a"
        jsonData = database[id]
        text = jsonData["title"]+' : '+ jsonData["abstract"]
        writer.writerow({'paperId':idstr, 'text':text})