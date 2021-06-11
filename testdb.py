
from django.http import HttpResponse

from TestModel.models import WrongList


# 数据库操作
def testdb(request):
    test1 = WrongList(uid='1',qid='2')
    test1.save()
    test2 = WrongList(uid='2',qid='1')
    test2.save()
    return HttpResponse("<p>数据添加成功！</p>")