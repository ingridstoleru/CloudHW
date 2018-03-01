from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from . import myfuncs

# Create your views here.


def index(request):
    template = loader.get_template('tema1app\\index.html')
    return HttpResponse(template.render({}, request))

def getdata(request):
    start = int(request.POST["start"])
    stop = int(request.POST["stop"])

    data = myfuncs.getAttachments(start, stop)

    return HttpResponse(str(data))