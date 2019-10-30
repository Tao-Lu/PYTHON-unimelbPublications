from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
import requests
import couchdb
import json

#const params

BASE_URL = "http://45.113.234.42:5984/"
COUNTRY_NUM = 15


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


def authorOverview(request):
    cisAuthorUrl = "http://45.113.234.42:5984/staffinfo_scopus/_design/search/_view/details"
    headers = {
        'Connection': 'close',
    }
    cisAuthors = requests.get(cisAuthorUrl, headers=headers)
    cisAuthorsList = cisAuthors.json()['rows']

    cisAuthorDictList = []
    for cisauthor in cisAuthorsList:
        cisAuthorDict = {"id": cisauthor['key'], "name": cisauthor['value'][0], "staffType": cisauthor['value'][1],
                         "email": cisauthor['value'][2], "documentCounts": cisauthor['value'][3],
                         "citedCounts": cisauthor['value'][4]}
        cisAuthorDictList.append(cisAuthorDict)

    return render(request, 'authorOverview.html', {"cisAuthorDictList": cisAuthorDictList})


def aboutUs(request):
    return render(request, 'aboutUs.html')

#Utility Function for Overview:




def getTopList(List):
    if(len(List) < COUNTRY_NUM):
        return countryList
    else:
        List.sort(key=lambda x: x["value"], reverse=True)
        rest = List[COUNTRY_NUM:]
        topList = List[0:COUNTRY_NUM]
        otherTotal = 0
        for i in rest:
            otherTotal += i["value"]
        topList.append({"key":"Others","value":otherTotal})
        List = topList
        return List

def yearly_trend(request):
    # TODO: get overview data
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    
    # TODO: papers over countries
    url = BASE_URL + "paperinfo_scopus/_design/match/_view/PaperCountByYear?group=true"
    headers = {
        'Connection': 'close',
    }
    dataRaw = requests.get(url, headers=headers)
    data = dataRaw.json()
    if(data != None):
        countryList = data['rows']
    else:
        countryList = {}
    return JsonResponse(countryList, safe=False)

def research_network(request):
    # TODO: get overview data
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    url_a = BASE_URL + "staffinfo_scopus/_design/search/_view/searchByName"
    url_l = BASE_URL + "allinfo_scopus/_design/relationship/_view/cisAuthorAndCisAuthor?group_level=2"
    headers = {
        'Connection': 'close',
    }
    dataRaw_a = requests.get(url_a, headers=headers)
    dataRaw_l = requests.get(url_l, headers=headers)

    authorList = dataRaw_a.json()["rows"]
    authorlinks = dataRaw_l.json()["rows"]
    graphData = {}
    author_dict = {}
    graphData["nodes"] = list()
    graphData["links"] = list()

    for author in authorList:
        author_dict[author['key']] = author['id']
        graphData["nodes"].append({"id": author['id'],"name":author['key'], "group": 1})
    
    for link in authorlinks:
        link_obj = {"source": link['key'][0], "target": link['key'][1], "value": link['value']}
        graphData["links"].append(link_obj)



    return JsonResponse(graphData, safe=False)

def topic_overview(request):
    # TODO: get overview data
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    url_t = BASE_URL + "paperinfo_scopus/_design/match/_view/matchTopic?group=true"
    url_k = BASE_URL + "paper_topic/_design/topics/_view/all_topic_keywords"
    headers = {
        'Connection': 'close',
    }
    dataRaw_t = requests.get(url_t, headers=headers)
    dataRaw_k = requests.get(url_k, headers=headers)

    topicNumList = dataRaw_t.json()["rows"]
    keywordList = dataRaw_k.json()["rows"]

    graphData = {}
    graphData["name"] = "topics"
    graphData["children"] = list()
    scoreMap = {}
    for num in topicNumList:
        id = num['key']
        scoreMap[id] = num['value']
        topic_obj = {"name": id,"children": []}
        graphData["children"].append(topic_obj)
        
    for topic in keywordList:
        id = int(topic['id'])
        score = scoreMap[id]
        for keyword in topic['key']:
            kw_obj = {"name": keyword, "size": score}
            graphData["children"][id]["children"].append(kw_obj)


    return JsonResponse(graphData, safe=False)

def overview(request):
    # TODO: get overview data
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    
    # TODO: papers over countries
    url = BASE_URL + "coauthorinfo_scopus/_design/countryCount/_view/countTotal?group=true&reduce=true"
    headers = {
        'Connection': 'close',
    }
    dataRaw = requests.get(url, headers=headers)
    data = dataRaw.json()
    if(data != None):
        countryList = data['rows']
        countryList = getTopList(countryList)
    else:
        countryList = {}

    url = BASE_URL + "coauthorinfo_scopus/_design/countryCount/_view/countAusUni?group=true"
    dataRaw = requests.get(url, headers=headers)
    data = dataRaw.json()
    if(data != None):
        uniList = data['rows']
        uniList = getTopList(uniList)
    else:
        uniList = {}

    return render(request, 'overview.html',{'countryList': countryList,'uniList':uniList})

def authorcandidate (request, searchstr):

    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    url = "http://45.113.234.42:5984/staffinfo_scopus/_design/search/_view/searchByName"
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
        if str(searchstr).lower() in str(row["key"]).lower():
            ids.append(row["value"])
    if ids:
        for pid in ids:
            dic = {}
            docDetail = db.get(pid)
            dic["name"] = docDetail["fullName"]
            dic["email"] = docDetail["email"]
            dic["staffType"] = docDetail["staffType"]
            dic["id"] = pid
            result[pid] = dic
    print(searchstr)

    # result = {}
    #
    # result['001'] = {'name':'richard','email':'email@unimelb.edu.au','staffType':'academic','id':'0001'}
    # result['002'] = {'name':'Tim','email':'tim@unimelb.edu.au','staffType':'academic','id':'0002'}
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
    paperdetailsDict['keyword'] = paperdetails['keyword']

    url = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/nameMatch"

    headers = {
        'Connection': 'close',
    }
    authorIdToName = requests.get(url, headers=headers)
    authorIdToNameJson = authorIdToName.json()['rows']

    authorIdName = []
    for authorId in paperdetailsDict['CISAuthors']:
        for author in authorIdToNameJson:
            if authorId == author['key']:
                authorIdName.append({"id": authorId, "name": author['value'][0]})

    coauthorIdName = []
    for coauthorId in paperdetailsDict['co_author']:
        for coauthor in authorIdToNameJson:
            if coauthorId == coauthor['key']:
                coauthorIdName.append({"id": coauthorId, "name": coauthor['value'][0], "authorType": coauthor['value'][1]})

    paperdetailsDict['CISAuthors'] = authorIdName
    paperdetailsDict['co_author'] = coauthorIdName

    return render(request, 'paperDetails.html', {'paperdetailsDict': paperdetailsDict})


# name, orcid, email, staff type, paper count, cited count, paper list (title)
def authorDetails(request, searchStr):
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    db = couch['staffinfo_scopus']
    authordetails = db.get(searchStr)

    # author details
    authordetailsDict = {}
    authordetailsDict['fullName'] = authordetails['fullName']
    authordetailsDict['orcid'] = authordetails['orcid']
    authordetailsDict['email'] = authordetails['email']
    authordetailsDict['staffType'] = authordetails['staffType']
    authordetailsDict['document_count'] = authordetails['document_count']
    authordetailsDict['cited_by_count'] = authordetails['cited_by_count']

    # papers that belong to this author
    paperListUrl = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/cisAuthorPaper?key=%22" + searchStr + "%22"
    headers = {
        'Connection': 'close',
    }
    paperlist = requests.get(paperListUrl, headers=headers)
    paperlistJson = paperlist.json()['rows']

    idTitleList = []
    for paper in paperlistJson:
        idTitleList.append({"id": paper['value'][0], "title": paper['value'][1]})

    authordetailsDict['paperlist'] = idTitleList

    # co-authors that connect to this author
    coAuthorListUrl = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/cisAuthorAndAllAuthor?group_level=2&startkey=[%22" + searchStr + "%22]&endkey=[%22" + searchStr + "%22,{}]"
    headers = {
        'Connection': 'close',
    }
    coAuthorlist = requests.get(coAuthorListUrl, headers=headers)
    coAuthorlistJson = coAuthorlist.json()['rows']

    # author id to name
    url = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/nameMatch"
    headers = {
        'Connection': 'close',
    }
    authorIdToName = requests.get(url, headers=headers)
    authorIdToNameJson = authorIdToName.json()['rows']

    idCoauthoredList = []
    for coauthor in coAuthorlistJson:
        coauthorId = coauthor['key'][1]
        for author in authorIdToNameJson:
            if coauthorId == author['key']:
                idCoauthoredList.append({"id": coauthor['key'][1], "name":  author['value'][0], "papercount": coauthor['value'], "authorType": author['value'][1]})

    authordetailsDict['coauthorlist'] = idCoauthoredList

    ########################################

    nodes = []
    links = []
    totalCountsPaper = 0
    for co_author in idCoauthoredList:
        totalCountsPaper += co_author['papercount']
        nodes.append({"id": co_author["name"], "paperCounts": co_author["papercount"],  "group": 1},)
    nodes.append({"id": authordetails['fullName'], "paperCounts": totalCountsPaper, "group": 1}, )

    for i in range(0, len(nodes)-1):
        links.append({"source": nodes[i]["id"], "target": nodes[-1]["id"], "value": nodes[i]["paperCounts"]})

    jsonData = {"nodes": nodes, "links": links}

    authordetailsDict["jsonData"] = jsonData





    ##########################################

    return render(request, 'authorDetails.html', {'authordetailsDict': authordetailsDict})


def coAuthorDetails(request, searchStr):
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    db = couch['coauthorinfo_scopus']
    coauthordetails = db.get(searchStr)

    # author details
    coauthordetailsDict = {}
    coauthordetailsDict['name'] = coauthordetails['name']
    coauthordetailsDict['affiliation'] = coauthordetails['affiliation']
    coauthordetailsDict['affiliation_city'] = coauthordetails['affiliation_city']
    coauthordetailsDict['affiliation_country'] = coauthordetails['affiliation_country']

    return render(request, "coAuthorDetails.html", {'coauthordetailsDict': coauthordetailsDict})


def coAuthoredPapers(request, cisAuthorId, coAuthorId):

    coauthoredpaperUrl = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/cisAuthorAndAllAuthor?group_level=3&startkey=[%22" + cisAuthorId + "%22,%22" + coAuthorId + "%22,null]&endkey=[%22" + cisAuthorId + "%22,%22" + coAuthorId + "%22,{}]"
    headers = {
        'Connection': 'close',
    }
    coauthoredpaperList = requests.get(coauthoredpaperUrl, headers=headers)
    coauthoredpaperListJson = coauthoredpaperList.json()['rows']
    coauthoredpaperIdList = []
    for paper in coauthoredpaperListJson:
        coauthoredpaperIdList.append(paper['key'][2])

    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    db = couch['staffinfo_scopus']
    coauthoredpaperinfoList = []
    for paperid in coauthoredpaperIdList:
        idToPaperUrl = "http://45.113.234.42:5984/paperinfo_scopus/_design/match/_view/matchIdtoDetail?key=%22" + paperid + "%22"
        paperinfo = requests.get(idToPaperUrl, headers=headers)
        paperinfoJson = paperinfo.json()['rows'][0]

        paperinfoDict = {}
        paperinfoDict['id'] = paperinfoJson['key']
        paperinfoDict['title'] = paperinfoJson['value'][0]
        paperinfoDict['cisAuthors'] = paperinfoJson['value'][1]
        paperinfoDict['year'] = paperinfoJson['value'][2]
        paperinfoDict['abstract'] = paperinfoJson['value'][3]
        paperinfoDict['paperType'] = paperinfoJson['value'][4]
        paperinfoDict['keyword'] = paperinfoJson['value'][5]


        cisAuthorList = paperinfoDict['cisAuthors'].split(',')
        cisAuthorsDetails = []
        for cisauthor in cisAuthorList:
            authordetails = db.get(cisauthor)
            cisAuthorsDetails.append({'id': authordetails['_id'], 'name': authordetails['fullName']})

        paperinfoDict['cisAuthors'] = cisAuthorsDetails
        coauthoredpaperinfoList.append(paperinfoDict)

    return render(request, 'coAuthoredPapers.html', {'coauthoredpaperinfoList': coauthoredpaperinfoList})


def paperCandidate (request, searchstr):
    paperUrl = "http://45.113.234.42:5984/paperinfo_scopus/_design/match/_view/matchTitle"
    nameUrl = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/nameMatch"
    headers = {
        'Connection': 'close',
    }
    dataRawPaper = requests.get(paperUrl, headers=headers)
    dataPaper = dataRawPaper.json()
    dataRow = dataPaper["rows"]

    dataRawName = requests.get(nameUrl, headers=headers)
    dataName = dataRawName.json()
    dataNameRow = dataName["rows"]
    result = []

    for row in dataRow:
        if str(searchstr).lower() in str(row["key"]).lower():
            paperinfo = {}
            cisAuthorId = []
            paperinfo['id'] = row['value'][0]
            paperinfo['title'] = row['key']
            cisAuthorId = row['value'][1].split(',')
            paperinfo['year'] = row['value'][2]
            paperinfo['abstract'] = row['value'][3]
            paperinfo['CisAuthor'] = []
            paperinfo['type'] = row['value'][4]
            paperinfo['title'].replace('"','')
            paperinfo['title'].replace('#','')
            paperinfo['title'].replace('\\','')

            coauthorIdName = []
            for scopusId in cisAuthorId:
                for name in dataNameRow:
                    if scopusId == name['key']:
                        coauthorIdName.append({"id": scopusId, "name": name['value'][0]})
            paperinfo['CisAuthor'] = coauthorIdName
            result.append(paperinfo)

    return render(request, 'paperCandidate.html', {'res': result, 'searchstr': searchstr,'size':len(result)})


def searchKeywords(request,str):
    result = []
    keywords = str.split(',')
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    db = couch['paperinfo_scopus']
    nameUrl = "http://45.113.234.42:5984/allinfo_scopus/_design/relationship/_view/nameMatch"
    headers = {
        'Connection': 'close',
    }
    dataRawName = requests.get(nameUrl, headers=headers)
    dataName = dataRawName.json()
    dataNameRow = dataName["rows"]
    for word in keywords:
        searchWord = word.lower()
        url = "http://45.113.234.42:5984/paperinfo_scopus/_design/match/_view/matchKeyWords?reduce=false&key=%22"+searchWord+"%22"

        dataRawPaper = requests.get(url, headers=headers)
        dataPaper = dataRawPaper.json()
        dataRow = dataPaper["rows"]
        for paper in dataRow:
            paperinfo = {}
            docDetail = db.get(paper['value'])
            cisAuthorId = []
            paperinfo['id'] = docDetail['_id']
            paperinfo['title'] = docDetail['title']
            cisAuthorId = docDetail['CISAuthors'].split(',')
            paperinfo['year'] = docDetail['coverDateYear']
            paperinfo['abstract'] = docDetail['abstract'].split('.')[0]+'. ' + docDetail['abstract'].split('.')[1]+'.'
            paperinfo['CisAuthor'] = []
            paperinfo['type'] = docDetail['paper_type']
            paperinfo['keyword'] = docDetail['keyword']
            # paperinfo['title'].replace('"', '')
            # paperinfo['title'].replace('#', '')
            # paperinfo['title'].replace('\\', '')

            coauthorIdName = []
            for scopusId in cisAuthorId:
                for name in dataNameRow:
                    if scopusId == name['key']:
                        coauthorIdName.append({"id": scopusId, "name": name['value'][0]})
            paperinfo['CisAuthor'] = coauthorIdName
            result.append(paperinfo)

    return render(request, 'paperCandidate.html', {'res': result, 'searchstr': str, 'size': len(result)})


def recommmendedPapers(request, originalpaperId):
    couch = couchdb.Server("http://admin:password@45.113.234.42:5984")
    db = couch['paperinfo_scopus']
    paperdetails = db.get(originalpaperId)
    topicId = paperdetails['topic_ids'][0]
    keywords = paperdetails['keyword']

    headers = {
        'Connection': 'close',
    }
    recommendedpaperidList = []
    for keyword in keywords:
        recommendedPapersUrl = "http://45.113.234.42:5984/paperinfo_scopus/_design/match/_view/topicMatchKeyword?key=[" + str(
            topicId) + ",%22" + keyword + "%22]"
        topickeywordPapers = requests.get(recommendedPapersUrl, headers=headers)
        topickeywordPapersList = topickeywordPapers.json()['rows']
        for topickeywordPaper in topickeywordPapersList:
            if topickeywordPaper['value'] != originalpaperId:
                recommendedpaperidList.append(topickeywordPaper['value'])

    recommendedpapersList = []
    for paperid in recommendedpaperidList:
        idToPaperUrl = "http://45.113.234.42:5984/paperinfo_scopus/_design/match/_view/matchIdtoDetail?key=%22" + paperid + "%22"
        paperinfo = requests.get(idToPaperUrl, headers=headers)
        paperinfoJson = paperinfo.json()['rows'][0]

        paperinfoDict = {}
        paperinfoDict['id'] = paperinfoJson['key']
        paperinfoDict['title'] = paperinfoJson['value'][0]
        paperinfoDict['cisAuthors'] = paperinfoJson['value'][1]
        paperinfoDict['year'] = paperinfoJson['value'][2]
        paperinfoDict['abstract'] = paperinfoJson['value'][3]
        paperinfoDict['type'] = paperinfoJson['value'][4]
        paperinfoDict['keyword'] = paperinfoJson['value'][5]

        cisAuthorList = paperinfoDict['cisAuthors'].split(',')
        db = couch['staffinfo_scopus']
        cisAuthorsDetails = []
        for cisauthor in cisAuthorList:
            authordetails = db.get(cisauthor)
            cisAuthorsDetails.append({'id': authordetails['_id'], 'name': authordetails['fullName']})

        paperinfoDict['CisAuthor'] = cisAuthorsDetails
        recommendedpapersList.append(paperinfoDict)

    return render(request, 'paperCandidate.html', {'res': recommendedpapersList, 'searchstr': "relevant topic", "size": len(recommendedpapersList)})

