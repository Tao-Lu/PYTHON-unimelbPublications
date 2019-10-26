from django.http import HttpResponse
from django.shortcuts import render

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
    return render(request, 'homePage.html')


