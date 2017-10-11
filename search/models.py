from django.db import models

# Create your models here.
from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])#连接服务器

#避免analyzer报错
class CustonAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer=CustonAnalyzer("ik_max_word",filter=["lowercase"])

class LagouType(DocType):
    #拉钩职位类型
    suggest=Completion(analyzer=ik_analyzer)#添加suggester
    url = Keyword()
    url_object_id = Keyword()
    title = Text(analyzer="ik_max_word")
    salary = Text(analyzer="ik_max_word")
    job_city = Text(analyzer="ik_max_word")
    work_years = Text(analyzer="ik_max_word")
    degree_needed = Text(analyzer="ik_max_word")
    job_type = Text(analyzer="ik_max_word")
    publish_time = Text(analyzer="ik_max_word")
    job_advantage = Text(analyzer="ik_max_word")
    job_desc = Text(analyzer="ik_max_word")
    job_addr = Text(analyzer="ik_max_word")
    company_name = Text(analyzer="ik_max_word")
    company_url = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")
    crawl_time = Date()

    class Meta:
        index = "lagoujob"
        doc_type = "job"

if __name__ == "__main__":
    LagouType.init()#会根据生成的类生成mapping