from django.shortcuts import render
from django.views.generic.base import View


# Create your views here.
class SearchSuggest(View):
    def get(self,request):
        key_words = request.GET.get("s",'')
        re_datas=[]
        if key_words:

