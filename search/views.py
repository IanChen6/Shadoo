import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import LagouType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis
client = Elasticsearch(hosts=["127.0.0.1"])#初始化一个es连接
redis_cli = redis.StrictRedis()


class IndexView(View):
    def get(self, request):

        #首页
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request,"index.html",{"topn_search":topn_search})

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
        s_type=request.GET.get("s_type","article")
        redis_cli.zincrby("search_keywords_set",key_words)#将搜索的词放入Redis中，并自动加1
        topn_search=redis_cli.zrevrangebyscore("search_keywords_set","+inf","-inf",start=0,num=5)
        page = request.GET.get("p","1")
        try:
            page = int(page)
        except:
            page = 1

        lagoujob_count = redis_cli.get("lagoujob_count")
        start_time=datetime.now()
        response = client.search(
            index="lagoujob",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["title","job_desc"]
                    }

                },
                "from":(page-1)*10,
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
        end_time=datetime.now()
        last_seconds = (end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page%10)>0:
            page_nums= int(total_nums/10)+1
        else:
            page_nums = int(total_nums/10)

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

        return render(request,"result.html",{"topn_search":topn_search,"lagoujob_count":lagoujob_count,"last_seconds":last_seconds,"page_nums":page_nums,"page":page,"all_hits":hit_list,"key_words":key_words,"total_nums":total_nums})