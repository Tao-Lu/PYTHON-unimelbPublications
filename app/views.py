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
    #return HttpResponse("OK")
    return render(request, 'base.html')


def authorcandidate (request):
    url = "http://45.113.234.42:5984/staffinfo_scopus/_design/search/_view/searchByName"
    couch = couchdb.Server("http://admin:password@http://45.113.234.42:5984")
    db = couch['staffinfo_scopus']
    dataRaw = requests.get(url)
    data = dataRaw.json()
    dataRow = data["rows"]
    result = {}
    ids = []
    for row in dataRow:
        if request in row["key"]:
            ids.append(row["value"])

    for pid in ids:
        dic = {}
        docDetail = db.get(pid)
        dic["name"] = docDetail["fullName"]
        dic["email"] = docDetail["email"]
        dic["staffType"] = docDetail["staffType"]
        result[pid] = dic

    return render(request, 'authorCandidate.html', {'res':json.dumps(result)})
