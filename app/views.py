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

    # couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    # url = "http://45.113.234.42/staffinfo_scopus/_design/search/_view/searchByName"
    # db = couch['staffinfo_scopus']
    # headers = {
    #     'Connection': 'close',
    # }
    # dataRaw = requests.get(url, headers=headers)
    # data = dataRaw.json()
    # dataRow = data["rows"]
    # result = {}
    # ids = []
    # for row in dataRow:
    #     if str(searchstr).lower() in str(row["key"]).lower():
    #         ids.append(row["value"])
    # if ids:
    #     for pid in ids:
    #         dic = {}
    #         docDetail = db.get(pid)
    #         dic["name"] = docDetail["fullName"]
    #         dic["email"] = docDetail["email"]
    #         dic["staffType"] = docDetail["staffType"]
    #         dic["id"] = pid
    #         result[pid] = dic
    # print(searchstr)

    result = {}

    result['001'] = {'name':'richard','email':'email@unimelb.edu.au','staffType':'academic','id':'0001'}
    result['002'] = {'name':'Tim','email':'tim@unimelb.edu.au','staffType':'academic','id':'0002'}
    return render(request, 'authorCandidate.html', {'res':result, 'searchstr':searchstr})



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

def paperCandidate (request, searchstr):
    # paperUrl = "http://45.113.234.42:5984/paperinfo_scopus/_design/match/_view/matchTitle"
    # nameUrl = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/nameMatch"
    # headers = {
    #     'Connection': 'close',
    # }
    # dataRawPaper = requests.get(paperUrl, headers=headers)
    # dataPaper = dataRawPaper.json()
    # dataRow = dataPaper["rows"]
    #
    # dataRawName = requests.get(nameUrl, headers=headers)
    # dataName = dataRawName.json()
    # dataNameRow = dataName["rows"]
    # result = []
    #
    # for row in dataRow:
    #     if str(searchstr).lower() in str(row["key"]).lower():
    #         paperinfo = {}
    #         cisAuthorId = []
    #         paperinfo['id'] = row['value'][0]
    #         paperinfo['title'] = row['value'][1]
    #         cisAuthorId = row['value'][2].split(',')
    #         paperinfo['year'] = row['value'][3]
    #         paperinfo['abstract'] = row['value'][4]
    #         paperinfo['CisAuthor'] = ''
    #         peperinfo['type'] = row['value'][5]
    #         paperinfo['title'].replace('"','')
    #         paperinfo['title'].replace('#','')
    #         paperinfo['title'].replace('\\','')
    #
    #         for scopusId in cisAuthorId:
    #             for name in dataNameRow:
    #                 if scopusId == name['key']:
    #                     paperinfo['CisAuthor']=paperinfo['CisAuthor'] + ', '+name['value']
    #         result.append(paperinfo)
    #  --------------------testing--------------------------------------------------------
    result = []
    paper1 = {'id':'001','title':'title1','year':'2019','abstract':'Queries to text collections are resolved by ranking the documents in the collection and returning the highest-scoring documents to the user.',
              'CisAuthor':'author1, author2, author3','type':'Conference paper'}
    result.append(paper1)
    paper2 = {'id': '002', 'title': 'title2', 'year': '2018',
              'abstract': 'Queries to text collections are resolved by ranking the documents in the collection and returning the highest-scoring documents to the user.',
              'CisAuthor': 'author1, author2','type':'Journal'}
    result.append(paper2)

    return render(request, 'paperCandidate.html', {'res': result, 'searchstr': searchstr,'size':len(result)})