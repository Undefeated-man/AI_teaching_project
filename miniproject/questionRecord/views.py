from wechatpy.oauth import WeChatOAuth
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import *
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

AppID = "wxd27ea3eb3d649f0d"
AppSecret = "da1e11486e57ebb44c7753180e3285a5"



# 定义授权装饰器
def getWeChatOAuth(redirect_url):
    return WeChatOAuth(AppID, AppSecret, redirect_url, 'snsapi_userinfo')


def oauth(method):
    def warpper(request):
        if request.session.get('user_info', None) is None:
            code = request.POST.get('code', None)
            wechat_oauth = getWeChatOAuth(request.get_raw_uri())
            url = wechat_oauth.authorize_url
            if code:
                try:
                    wechat_oauth.fetch_access_token(code)
                    user_info = wechat_oauth.get_user_info()
                except Exception as e:
                    print(str(e))
                    # 这里需要处理请求里包含的 code 无效的情况
                    # abort(403)
                else:
                    # 建议存储在用户表
                    request.session['user_info'] = user_info
                    request.session.set_expiry(None)
            else:
                return redirect(url)

        return method(request)

    return warpper


# 获取用户信息UserInfo

@oauth
def userinfo(request):
    user_info = request.session.get('user_info')
    return JsonResponse({"OpenID":user_info.openid})


@csrf_exempt
def upload(request):
    return render(request, "upload.html")


@csrf_exempt
def getUserWrong(request):
    try:
        userID = request.POST.get("userID")
        wrongRecords = []
        for i in Wrong.objects.filter(userID=userID):
            self_dict = {"count": i.count, "question": {"example": i.question.example, "meaning": i.question.meaning}}
            wrongRecords.append(self_dict)
        return JsonResponse(wrongRecords, safe=False)
    except Exception as e:
        return JsonResponse({"state": "Fail", "Error": e.__str__()})


@csrf_exempt
def addUserWrong(userID,questionID):
    try:
        result = Wrong.objects.filter(userID=userID, questionID=questionID)
        if len(result) == 0:
            Wrong.objects.create(userID=userID, question_id=questionID, count=1)
        else:
            result[0].count += 1
            result[0].save()
        return JsonResponse({"state": "Success"})
    except Exception as e:
        return JsonResponse({"state": "fail", "Error": e.__str__()})


