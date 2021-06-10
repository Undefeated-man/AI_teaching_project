
from django.http import HttpResponse

from TestModel.models import WrongList


# 数据库操作
def testdb(request):
    test1 = WrongList(name='runoob')
    test1.save()
    return HttpResponse("<p>数据添加成功！</p>")