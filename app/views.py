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
    return render(request, 'homePage.html')

def overview(request):
    return render(request, 'overview.html')

def authorcandidate (request, searchstr):
    url = "http://45.113.234.42:5984/staffinfo_scopus/_design/search/_view/searchByName"
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
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
def paperDetails(request, searchStr):
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    # couch = couchdb.Server("http://admin:password@127.0.0.1:5984")
    db = couch['paperinfo_scopus']
    paperdetails = db.get(searchStr)

    # put paper details into dict
    paperdetailsDict = {}
    paperdetailsDict['title'] = paperdetails['title']
    paperdetailsDict['CISAuthors'] = paperdetails['CISAuthors'].split(',')
    paperdetailsDict['coverDateYear'] = paperdetails['coverDateYear']
    paperdetailsDict['co_author'] = paperdetails['co_author']
    paperdetailsDict['cite_count'] = paperdetails['cite_count']
    paperdetailsDict['paper_type'] = paperdetails['paper_type']
    paperdetailsDict['abstract'] = paperdetails['abstract']

    url = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/nameMatch"
    headers = {
        'Connection': 'close',
    }
    authorIdToName = requests.get(url, headers=headers)
    authorIdToNameJson = authorIdToName.json()['rows']
    # print(authorIdToName)
    # print(authorIdToNameJson)

    authorIdName = []
    for authorId in paperdetailsDict['CISAuthors']:
        for author in authorIdToNameJson:
            if authorId == author['key']:
                authorIdName.append({"id": authorId, "name": author['value']})

    coauthorIdName = []
    for coauthorId in paperdetailsDict['co_author']:
        for coauthor in authorIdToNameJson:
            if coauthorId == coauthor['key']:
                coauthorIdName.append({"id": coauthorId, "name": coauthor['value']})

    paperdetailsDict['CISAuthors'] = authorIdName
    paperdetailsDict['co_author'] = coauthorIdName

    return render(request, 'paperDetails.html', {'paperdetailsDict': paperdetailsDict})


# name, orcid, email, staff type, paper count, cited count, paper list (title)
def authorDetails(request, searchStr):
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    db = couch['staffinfo_scopus']
    authordetails = db.get(searchStr)

    # put paper details into dict
    authordetailsDict = {}
    authordetailsDict['fullName'] = authordetails['fullName']
    authordetailsDict['orcid'] = authordetails['orcid']
    authordetailsDict['email'] = authordetails['email']
    authordetailsDict['staffType'] = authordetails['staffType']
    authordetailsDict['document_count'] = authordetails['document_count']
    authordetailsDict['cited_by_count'] = authordetails['cited_by_count']

    url = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/cisAuthorPaper?key=%22" + searchStr + "%22"
    headers = {
        'Connection': 'close',
    }
    paperlist = requests.get(url, headers=headers)
    paperlistJson = paperlist.json()['rows']

    idTitleList = []
    for paper in paperlistJson:
        idTitleList.append({"id": paper['value'][0], "title": paper['value'][1]})

    authordetailsDict['paperlist'] = idTitleList

    return render(request, 'authorDetails.html', {'authordetailsDict': authordetailsDict})

