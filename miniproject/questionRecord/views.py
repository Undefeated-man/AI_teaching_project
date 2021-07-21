import os
import random

import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import *
from django.views.decorators.csrf import csrf_exempt
from . import audioRecognize
from weixin.lib.wxcrypt import WXBizDataCrypt
from weixin import WXAPPAPI
from google.cloud import texttospeech

# Create your views here.


AppID = "wxd27ea3eb3d649f0d"
AppSecret = "da1e11486e57ebb44c7753180e3285a5"


# cd AI_teaching/AI_teaching_project/miniproject


def get_user_info(js_code, userinfo, iv):
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
        userinfo = request.POST.get("userinfo", "")
        name = request.POST.get("name", "")
        iv = request.POST.get("iv", "")
        user_info = get_user_info(code, userinfo, iv)
        photo = request.POST.get("photo", "")  # get the photo
        try:
            commonUser = CommonUser.objects.get(commonUserID=user_info['openId'])
            commonUser.commonUserName = name
            commonUser.imageLocation = photo
            commonUser.save()
        except:
            group = Groups.objects.get(groupID=1)
            commonUser = CommonUser.objects.create(commonUserID=user_info['openId'], commonUserName=name, group=group)
            Progress.objects.create(commonUser=commonUser, qstNum=0, cumScore=0)
            commonUser.session_key = request.session.session_key
            commonUser.imageLocation = photo
            commonUser.save()
        return JsonResponse(
            {"state": "success", "OpenID": user_info['openId'], "Name": name, "Photo": commonUser.imageLocation})
    except Exception as e:
        return JsonResponse({"state": "fail", "error": e.__str__()})


@csrf_exempt
def upload(request):
    return render(request, "userInfor.html")


@csrf_exempt
def getUserInformation(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        score = Progress.objects.get(commonUser=commonUser).cumScore
        level = commonUser.level
        doneQuestion = []
        wrongQuestion = []
        for i in History.objects.filter(commonUser=commonUser):
            levelToDeal = i.level
            example = eval(levelToDeal).objects.get(questionID=i.questionID).example
            doneQuestion.append(serializationQuestion(example, i.level, commonUser))
        for i in Wrong.objects.filter(commonUser=commonUser):
            example = i.example
            wrongQuestion.append(serializationQuestion(example, i.level, commonUser))
        return JsonResponse({"state": "success", "commonUserID": commonUserID, "score": score, "level": level,
                             "imageURL": commonUser.imageLocation,
                             "doneQuestion": doneQuestion,
                             "wrongQuestion": wrongQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getRankWithLevel(request):
    try:
        level = request.POST.get("level")
        allCommonUser = CommonUser.objects.filter(level=level, ).order_by("-Progress__cumScore")
        result = []
        for i in allCommonUser:
            result.append({"commonUserID": i.commonUserID, "commonUserName": i.commonUserName,
                           "score": i.Progress.cumScore, "imageURL": i.imageLocation})
        return JsonResponse({"state": "success", "result": result})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getRankWithoutLevel(request):
    try:
        allCommonUser = CommonUser.objects.order_by("-Progress__cumScore")
        result = []
        for i in allCommonUser:
            result.append({"commonUserID": i.commonUserID, "commonUserName": i.commonUserName,
                           "score": i.Progress.cumScore, "level": i.level, "imageURL": i.imageLocation})
        return JsonResponse({"state": "success", "result": result})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getNewQuestion(request):
    # try:
    commonUserID = request.POST.get("commonUserID")
    commonUser = CommonUser.objects.get(commonUserID=commonUserID)
    level = request.POST.get("level")
    lecture = request.POST.get("lecture")
    if level == "Level1":
        level = "Level2"
    alreadyDone = History.objects.filter(commonUser=commonUser, level=level).values_list("questionID", flat=True)
    allLevelQuestion = eval(level).objects.exclude(questionID__in=alreadyDone)
    question = []
    number = 0
    for i in allLevelQuestion:
        if i.example.unit.unitName == lecture:
            question.append(serializationQuestion(i.example, level, commonUser))
            number += 1
        if number == 10:
            break
    return JsonResponse({"state": "success", "question": question})


# except Exception as e:
#     return JsonResponse({'state': 'fail', "error": e.__str__()})


def getOneQuesiton(request):
    try:
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        if level == "Level1":
            level = "Level2"
        example = eval(level).objects.get(questionID=questionID).example
        if level == "Level3":
            if example.level3Mode:
                exampleDict = serializationQuestion(example, level, commonUser)
        elif level == "Level4":
            if example.level4Mode:
                exampleDict = serializationQuestion(example, level, commonUser)
        else:
            exampleDict = serializationQuestion(example, level, commonUser)
        return JsonResponse({"state": "success", "question": exampleDict})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getWrongQuestion(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        lecture = request.POST.get("lecture")
        wrongQuestion = []
        for i in Wrong.objects.filter(commonUser=commonUser, level=level):
            example = eval(i.level).objects.get(questionID=i.questionID).example
            if example.unit.unitName == lecture:
                wrongQuestion.append(serializationQuestion(example, level, commonUser))
            if len(wrongQuestion) == 10:
                break
        return JsonResponse({"state": "success", "wrongQuestion": wrongQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getNotesCollection(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        collectedQuestion = []
        for i in NotesCollection.objects.filter(commonUser=commonUser):
            example = eval(i.level).objects.get(questionID=i.questionID).example
            collectedQuestion.append(serializationQuestion(example, i.level, commonUser))
        return JsonResponse({"state": "success", "collectedQuestion": collectedQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getHistory(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        lecture = request.POST.get("lecture")
        historyQuestion = []
        for i in History.objects.filter(commonUser=commonUser, level=level):
            example = eval(i.level).objects.get(questionID=i.questionID).example
            if example.unit.unitName == lecture:
                historyQuestion.append(serializationQuestion(example, i.level, commonUser))
        return JsonResponse({"state": "success", "historyQuestion": historyQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def serializationQuestion(example, level, commonUser):
    exampleDict = {}
    exampleDict["unit"] = example.unit.unitName
    exampleDict["example"] = example.example
    exampleDict["meaning"] = example.meaning
    exampleDict["translation"] = example.translation
    if level == "Level3":
        if example.level3Mode:
            level3Question = example.Level3
            exampleDict["question"] = {"level": level, "questionID": level3Question.questionID,
                                       "question": level3Question.question, "op1": level3Question.op1,
                                       "op2": level3Question.op2, "op3": level3Question.op3,
                                       "whetherCollect": judgeCollect(commonUser, level, level3Question.questionID)}
    elif level == "Level4":
        if example.level4Mode:
            level4Question = example.Level4
            exampleDict["question"] = {"level": level, "questionID": level4Question.questionID,
                                       "question": level4Question.question,
                                       "whetherCollect": judgeCollect(commonUser, level, level4Question.questionID)}
    else:
        level2Question = example.Level2
        exampleDict["question"] = {"level": level, "questionID": level2Question.questionID,
                                   "question": level2Question.question, "op1": level2Question.op1,
                                   "op2": level2Question.op2, "op3": level2Question.op3,
                                   "whetherCollect": judgeCollect(commonUser, level, level2Question.questionID)}

    return exampleDict


def toCollect(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        NotesCollection.objects.create(commonUser=commonUser, level=level, questionID=questionID)
        return JsonResponse({"state": "success"})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def toCancelCollect(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        NotesCollection.objects.get(commonUser=commonUser, level=level, questionID=questionID).delete()
        return JsonResponse({"state": "success"})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def judgeAnswer(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        if level == "Level1":
            level = "Level2"
        example = eval(level).objects.get(questionID=questionID).example
        if level == "Level4":
            audiofile = request.FILES.get('file', '')
            trueAnswer = example.meaning
            result = audioRecognize.recognizeAudio(audiofile, trueAnswer)
            yourAnswer = result["yourAnswer"]
            result = result["result"]
        else:
            trueAnswer = example.meaning
            yourAnswer = request.POST.get("answer")
            result = (yourAnswer == trueAnswer)
        if result:
            commonUser.Progress.cumScore += 1
        else:
            if (commonUser.Progress.cumScore > 1):
                commonUser.Progress.cumScore -= 1
            try:
                Wrong.objects.get(commonUser=commonUser, level=level, questionID=questionID).count += 1
            except:
                Wrong.objects.create(commonUser=commonUser, level=level, questionID=questionID, count=1)
        History.objects.create(commonUser=commonUser, questionID=questionID, level=level)
        commonUser.Progress.qstNum += 1
        commonUser.Progress.save()
        commonUser.save()
        return JsonResponse({'state': 'success', "result": result, "trueAnswer": trueAnswer, "yourAnswer": yourAnswer})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def judgeCollect(commonUser, level, questionID):
    result = False
    try:
        NotesCollection.objects.get(commonUser=commonUser, level=level, questionID=questionID)
        result = True
    except Exception as e:
        result = False
    return result


def getUserRank(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        score = commonUser.Progress.cumScore
        allCommonUser = CommonUser.objects.order_by("-Progress__cumScore")
        rank = 1
        for i in allCommonUser:
            if i == commonUser:
                break
            rank += 1
        return JsonResponse({"state": "success", "score": score, "rank": rank * 100 / len(allCommonUser)})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def textToSpeechCN(request):
    try:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()
        print(request.POST['text'])
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=request.POST['text'])

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        # The response's audio_content is binary.
        # with open("output.mp3", "wb") as out:
        #     # Write the response to the output file.
        #     out.write(response.audio_content)
        #     print('Audio content written to file "output.mp3"')
        return JsonResponse({"state": "success", "audio": response})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})



