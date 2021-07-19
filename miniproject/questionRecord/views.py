import random

import requests
from wechatpy.oauth import WeChatOAuth
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import *
from django.views.decorators.csrf import csrf_exempt
from . import audioRecognize
from weixin.lib.wxcrypt import WXBizDataCrypt
from weixin import WXAPPAPI

# Create your views here.


AppID = "wxd27ea3eb3d649f0d"
AppSecret = "da1e11486e57ebb44c7753180e3285a5"


#cd AI_teaching/AI_teaching_project/miniproject


def get_user_info(js_code,userinfo,iv):
    api = WXAPPAPI(AppID, AppSecret)
    session_info = api.exchange_code_for_session_key(js_code)
    # print(api);

    # 获取session_info 后

    session_key = session_info.get('session_key')
    print("session_key", session_key)
    # print()
    crypt = WXBizDataCrypt(AppID, session_key)
    user_info = crypt.decrypt(userinfo, iv)
    return user_info


# 获取用户信息UserInfo
def userinfo(request):
    try:
        code = request.POST.get('code', None)
        userinfo=request.POST.get("userinfo","")
        name=request.POST.get("name","")
        iv=request.POST.get("iv","")
        user_info = get_user_info(code,userinfo,iv)
        try:
            commonUser=CommonUser.objects.get(commonUserID=user_info['openId'])
            commonUser.commonUserName=name
            commonUser.save()
        except:
            group=Groups.objects.get(groupID=1)
            commonUser=CommonUser.objects.create(commonUserID=user_info['openId'],commonUserName=name,group=group)
            Progress.objects.create(commonUser=commonUser,qstNum=0,cumScore=0)
            commonUser.session_key = request.session.session_key
        return JsonResponse({"state":"success","OpenID":user_info['openId'],"Name":name})
    except Exception as e:
        return JsonResponse({"state":"fail","error":e.__str__()})


@csrf_exempt
def upload(request):
    return render(request, "userInfor.html")


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
            doneQuestion.append(serializationQuestion(example,i.level,commonUser))
        for i in Wrong.objects.filter(commonUser=commonUser):
            example = i.example
            wrongQuestion.append(serializationQuestion(example,i.level,commonUser))
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
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level3",commonUser)}
        if level=="Level3":
            alreadyDoneID=History.objects.get(commonUser=commonUser).questionID
            allLevelQuestion=Level4.objects.exclude(question__in=alreadyDoneID).example
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level4",commonUser)}
        if level=="Level4":
            alreadyDoneID=History.objects.get(commonUser=commonUser).questionID
            allLevelQuestion=Level4.objects.exclude(question__in=alreadyDoneID).example
            return {"state":"success","question":serializationQuestion(random.choice(allLevelQuestion),"Level4",commonUser)}
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getOneQuesiton(request):
    try:
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        example=eval(level).objects.get(questionID=questionID).example
        if level == "Level3":
            if example.level3Mode:
                exampleDict = serializationQuestion(example,level,commonUser)
        elif level == "Level4":
            if example.level4Mode:
                exampleDict = serializationQuestion(example,level,commonUser)
        else:
            exampleDict = serializationQuestion(example,level,commonUser)
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


def serializationQuestion(example,level,commonUser):
    exampleDict = {}
    exampleDict["unit"] = example.unit.unitName
    exampleDict["example"] = example.example
    exampleDict["meaning"] = example.meaning
    exampleDict["translation"] = example.translation
    if level=="Level3":
        if example.level3Mode:
            level3Question = example.Level3
            exampleDict["question"] = {"level":level,"questionID":level3Question.questionID,"question": level3Question.question, "op1": level3Question.op1,
                                            "op2": level3Question.op2, "op3": level3Question.op3,
                                       "whetherCollect":judgeCollect(commonUser,level,level3Question.questionID)}
    elif level=="Level4":
        if example.level4Mode:
            level4Question = example.Level4
            exampleDict["question"] = {"level": level, "questionID": level4Question.questionID,"question": level4Question.question,
                                       "whetherCollect":judgeCollect(commonUser,level,level4Question.questionID)}
    else:
        level2Question = example.Level2
        exampleDict["question"] = {"level": level, "questionID": level2Question.questionID,"question": level2Question.question, "op1": level2Question.op1,
                                         "op2": level2Question.op2, "op3": level2Question.op3,
                                   "whetherCollect":judgeCollect(commonUser,level,level2Question.questionID)}

    return exampleDict


def toCollect(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        questionID=request.POST.get("questionID")
        NotesCollection.objects.create(commonUser=commonUser,level=level,questionID=questionID)
        return JsonResponse({"state": "success"})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def toCancelCollect(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        questionID=request.POST.get("questionID")
        NotesCollection.objects.get(commonUser=commonUser,level=level,questionID=questionID).delete()
        return JsonResponse({"state": "success"})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def judgeAnswer(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        example=eval(level).objects.get(questionID=questionID).example
        if level=="Level4":
            audiofile = request.FILES.get('file', '')
            trueAnswer=example.meaning
            result=audioRecognize.recognizeAudio(audiofile,trueAnswer)
            yourAnswer=result["yourAnswer"]
            result=result["result"]
        else:
            trueAnswer=example.meaning
            yourAnswer=request.POST.get("answer")
            result =(yourAnswer==trueAnswer)
        if result:
            commonUser.Progress.qstNum+=1
        else:
            if(commonUser.Progress.qstNum>1):
                commonUser.Progress.qstNum -= 1
            try:
                Wrong.objects.get(commonUser=commonUser, level=level, questionID=questionID).count+=1
            except:
                Wrong.objects.create(commonUser=commonUser,level=level,questionID=questionID,count=1)
        History.objects.create(commonUser=commonUser,questionID=questionID,level=level)
        commonUser.Progress.cumScore += 1
        return JsonResponse({'state': 'success', "result": result,"trueAnswer":trueAnswer,"yourAnswer":yourAnswer})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def judgeCollect(commonUser,level,questionID):
    result=False
    try:
        NotesCollection.objects.get(commonUser=commonUser,level=level,questionID=questionID)
        result=True
    except Exception as e:
        result=False
    return result