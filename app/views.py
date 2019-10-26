from django.http import HttpResponse
from django.shortcuts import render
import requests
import couchdb
import json

# Create your views here.

'''
return HttpResponse("OK")
return render(request, "index.html", {"name": "monicx", "hobby": ["reading", "blog"]})
    一是request参数，二是待渲染的html模板文件,三是保存具体数据的字典参数。
return redirect("https://blog.csdn.net/miaoqinian")
    

'''

# Unimelb Publicatino Homepage
def homepage(request):
    return render(request, 'base.html')


def authorcandidate (request, searchstr):
    url = "http://127.0.0.1/staffinfo_scopus/_design/search/_view/searchByName"
    couch = couchdb.Server("http://jingjing:Jing1201@127.0.0.1:5984")
    db = couch['staffinfo_scopus']
    headers = {
        'Connection': 'close',
    }
    dataRaw = requests.get(url, headers=headers)
    data = dataRaw.json()
    dataRow = data["rows"]
    result = {}
    ids = []
    for row in dataRow:
        if searchstr in row["key"]:
            ids.append(row["value"])
    if ids:
        for pid in ids:
            dic = {}
            docDetail = db.get(pid)
            dic["name"] = docDetail["fullName"]
            dic["email"] = docDetail["email"]
            dic["staffType"] = docDetail["staffType"]
            result[pid] = dic
    print(searchstr)

    return render(request, 'authorCandidate.html', {'res':json.dumps(result)})

# title, CIS author, year, all author, cited count, paper type, full abstract
def paperDetails(request):
    # get params from request
    # paperId = request.GET.get('paperid')

    # connect to db
    couch = couchdb.Server("http://admin:password@http://127.0.0.1:5984")
    db = couch['paperinfo_scopus']
    paperdetails = db.get("0000036988")

    # put paper details into dict
    # paperdetailsDict = {}
    # paperdetailsDict['title'] = paperdetails['title']
    # paperdetailsDict['CISAuthors'] = paperdetails['CISAuthors']
    # paperdetailsDict['coverDateYear'] = paperdetails['coverDateYear']
    # paperdetailsDict['co_author'] = paperdetails['co_author']
    # paperdetailsDict['cite_count'] = paperdetails['cite_count']
    # paperdetailsDict['paper_type'] = paperdetails['paper_type']
    # paperdetailsDict['abstract'] = paperdetails['abstract']

    return render(request, 'paperDetails.html', {'paperdetailsDict': "123"})

