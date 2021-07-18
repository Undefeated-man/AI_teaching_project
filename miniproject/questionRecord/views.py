import random

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
    try:
        commonUser=CommonUser.objects.get(commonUserID=user_info.openid)
    except:
        commonUser=CommonUser.objects.create(commonUserID=user_info.openid,commonUserName=user_info.nickname)
    commonUser.session_key = request.session.session_key
    return JsonResponse({"OpenID":user_info.openid})


@csrf_exempt
def upload(request):
    return render(request, "upload.html")


@csrf_exempt
def getUserInformation(request):
    try:
        commonUserID=request.POST.get("openID")
        commonUser=CommonUser.objects.get(commonUserID=commonUserID)
        score=Progress.objects.get(commonUser=commonUser).cumScore
        level=commonUser.level
        doneQuestion=[]
        wrongQuestion=[]
        for i in History.objects.filter(commonUser=commonUser):
            level=i.level
            example=eval(level).objects.get(questionID=i.questionID).example
            doneQuestion.append(serializationQuestion(example,i.level))
        for i in Wrong.objects.filter(commonUser=commonUser):
            example = i.example
            wrongQuestion.append(serializationQuestion(example,i.level))
        return JsonResponse({"state":"success","commonUserID":commonUserID,"score":score,"level":level,"doneQuestion":doneQuestion,
                             "wrongQuestion":wrongQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getRankWithLevel(request):
    try:
        level=request.POST.get("level")
        allCommonUser=CommonUser.objects.filter(level=level,).order_by("Progress__cumScore")
        result=[]
        for i in allCommonUser:
            result.append({"commonUserID":i.commonUserID,"commonUserName":i.commonUserName,
                           "score":i.Progress.cumScore})
        return JsonResponse({"state":"success","result":result})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getRankWithoutLevel(request):
    try:
        allCommonUser=CommonUser.objects.order_by("Progress__cumScore")
        result=[]
        for i in allCommonUser:
            result.append({"commonUserID":i.commonUserID,"commonUserName":i.commonUserName,
                           "score":i.Progress.cumScore,"level":i.level})
        return JsonResponse({"state":"success","result":result})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getNewQuestion(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        if level=="Level1":
            alreadyDoneID=History.objects.get(commonUser=commonUser).questionID
            allLevelQuestion=Level2.objects.exclude(question__in=alreadyDoneID).example
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level2")}
        if level=="Level2":
            alreadyDoneID=History.objects.get(commonUser=commonUser).questionID
            allLevelQuestion=Level3.objects.exclude(question__in=alreadyDoneID).example
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level3")}
        if level=="Level3":
            alreadyDoneID=History.objects.get(commonUser=commonUser).questionID
            allLevelQuestion=Level4.objects.exclude(question__in=alreadyDoneID).example
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level4")}
        if level=="Level4":
            alreadyDoneID=History.objects.get(commonUser=commonUser).questionID
            allLevelQuestion=Level4.objects.exclude(question__in=alreadyDoneID).example
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level4")}
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getOneQuesiton(request):
    try:
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        example=eval(level).objects.get(questionID=questionID).example
        if level == "Level3":
            if example.level3Mode:
                exampleDict = serializationQuestion(example,level)
        elif level == "Level4":
            if example.level4Mode:
                exampleDict = serializationQuestion(example,level)
        else:
            exampleDict = serializationQuestion(example,level)
        return JsonResponse({"state":"success","question":exampleDict})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getWrongQuestion(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        wrongQuestion = []
        for i in Wrong.objects.filter(commonUser=commonUser,level=level):
            example = i.example
            wrongQuestion.append(serializationQuestion(example,level))
        return JsonResponse({"state":"success","wrongQuestion":wrongQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getNotesCollection(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        collectedQuestion = []
        for i in NotesCollection.objects.filter(commonUser=commonUser):
            example = i.example
            collectedQuestion.append(serializationQuestion(example,i.level))
        return JsonResponse({"state":"success","collectedQuestion":collectedQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getHistory(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        historyQuestion = []
        for i in History.objects.filter(commonUser=commonUser):
            example = i.example
            historyQuestion.append(serializationQuestion(example, i.level))
        return JsonResponse({"state": "success", "historyQuestion": historyQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})

def serializationQuestion(example,level):
    exampleDict = {}
    exampleDict["unit"] = example.unit.unitName
    exampleDict["example"] = example.example
    exampleDict["meaning"] = example.meaning
    exampleDict["translation"] = example.translation
    if level=="Level3":
        if example.level3Mode:
            level3Question = example.Level3
            exampleDict["question"] = {"level":level,"questionID":level3Question.questionID,"question": level3Question.question, "op1": level3Question.op1,
                                            "op2": level3Question.op2, "op3": level3Question.op3}
    elif level=="Level4":
        if example.level4Mode:
            level4Question = example.Level4
            exampleDict["question"] = {"level": level, "questionID": level4Question.questionID,"question": level4Question.question}
    else:
        level2Question = example.Level2
        exampleDict["question"] = {"level": level, "questionID": level2Question.questionID,"question": level2Question.question, "op1": level2Question.op1,
                                         "op2": level2Question.op2, "op3": level2Question.op3}

    return exampleDict


