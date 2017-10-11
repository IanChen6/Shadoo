import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import LagouType
from django.http import HttpResponse
from elasticsearch import Elasticsearch

client = Elasticsearch(hosts=["127.0.0.1"])#初始化一个es连接

# Create your views here.#fuzzy 模糊搜索
class SearchSuggest(View):
    def get(self,request):
        key_words = request.GET.get("s",'')
        re_datas=[]
        if key_words:
            s=LagouType.search()
            s=s.suggest('my_suggest',key_words,completion={
                "field":"suggest","fuzzy":{
                    "fuzziness":2
                 },
                "size":10
            })
            suggestions=s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source['title'])

        return HttpResponse(json.dumps(re_datas),content_type='application/json')


class SearchView(View):
    def get(self,request):
        key_words=request.GET.get("q","")
        response = client.search(
            index="lagoujob",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["title","job_desc"]
                    }

                },
                "from":0,
                "size":10,
                "highlight":{
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields":{
                        "title":{},
                        "job_desc":{}
                    }
                }

            }
        )

        total_nums = response["hits"]["total"]
        hit_list =[]
        for hit in response["hits"]["hits"]:
            hit_dict={}
            if "highlight" in hit:
                if "title" in hit["highlight"]:
                    hit_dict["title"]="".join(hit["highlight"]["title"])
                else:
                    hit_dict["title"] = hit["_source"]["title"]
                if "tags" in ["highlight"]:
                    hit_dict["job_desc"]="".join(hit["highlight"]["job_desc"])
                else:
                    hit_dict["job_desc"] = hit["_source"]["job_desc"]
                if "_source" in hit:
                    hit_dict["publish_time"] = hit["_source"]["publish_time"]
                    hit_dict["url"]=hit["_source"]["url"]
                    hit_dict["score"]=hit["_score"]
            hit_list.append(hit_dict)

        return render(request,"result.html",{"all_hits":hit_list,"key_words":key_words})