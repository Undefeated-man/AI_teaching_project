import json
import math
import random

from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import base64
from .models import *
from django.views.decorators.csrf import csrf_exempt
from . import audioRecognize
from weixin.lib.wxcrypt import WXBizDataCrypt
from weixin import WXAPPAPI
from google.cloud import texttospeech
from datetime import datetime, timedelta
from random import shuffle

# Create your views here.


AppID = "wxd27ea3eb3d649f0d"
AppSecret = "da1e11486e57ebb44c7753180e3285a5"


# cd AI_teaching/AI_teaching_project/miniproject


def get_user_info(js_code, userinfo, iv):
    api = WXAPPAPI(AppID, AppSecret)
    session_info = api.exchange_code_for_session_key(js_code)
    session_key = session_info.get('session_key')
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
            commonUser.imageLocation = photo
            commonUser.lastCheckDate = datetime.strptime('1980-01-01', "%Y-%m-%d")
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
        return JsonResponse({"state": "success", "commonUserID": commonUserID, "score": score, "level": level,
                             "imageURL": commonUser.imageLocation,
                             })
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
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        lecture = request.POST.get("lecture")
        alreadyDone = History.objects.filter(commonUser=commonUser, level=level).values_list("questionID", flat=True)
        if level != "Level1":
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
        else:
            allExample = Example.objects.exclude(exampleID__in=alreadyDone)
            question = []
            number = 0
            for i in allExample:
                if i.unit.unitName == lecture:
                    question.append(serializationQuestion(i, level, commonUser))
                    number += 1
                if number == 10:
                    break
            return JsonResponse({"state": "success", "question": question})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getOneQuesiton(request):
    try:
        level = request.POST.get("level")
        questionID = request.POST.get("questionID")
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        if level != "Level1":
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
        else:
            example = Example.objects.get(exampleID=questionID)
            return JsonResponse({"state": "success", "question": serializationQuestion(example, level, commonUser)})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getWrongQuestion(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        # lecture = request.POST.get("lecture")
        wrongQuestion = []
        for i in Wrong.objects.filter(commonUser=commonUser, level=level)[0:10]:
            example = eval(i.level).objects.get(questionID=i.questionID).example
            # if example.unit.unitName == lecture:
            wrongQuestion.append(serializationQuestion(example, level, commonUser))
        return JsonResponse({"state": "success", "wrongQuestion": wrongQuestion})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getNotesCollection(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        collectedDict = {}
        for i in NotesCollection.objects.filter(commonUser=commonUser):
            if i.level != "Level1":
                example = eval(i.level).objects.get(questionID=i.questionID).example
                lect = example.unit.unitName.replace('Lecture  ', 'LECT')
                if collectedDict.get(lect, None) is None:
                    collectedDict[lect] = {}
                if collectedDict[lect].get(i.level, None) is None:
                    collectedDict[lect][i.level] = []
                if i.level == "Level2":
                    answer = example.concept.conceptName
                else:
                    answer = example.meaning
                collectedDict[lect][i.level].append(
                    {"Question": eval(i.level).objects.get(questionID=i.questionID).question,
                     "Answer": answer, "ID": i.questionID})
            else:
                example = Example.objects.get(exampleID=i.questionID)
                collectedDict[i.level].append(
                    {"Example": example.example, "Meaning": example.meaning, "translation": example.translation,
                     "Concept": example.concept.conceptName, "Decription": example.concept.conceptDescription})
        collectedDict = sorted(collectedDict.items(), key=lambda i: int(i[0][i[0].rfind("T") + 1:]))
        return JsonResponse({"state": "success", "collectedQuestion": collectedDict})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def random_options(dicts):
    dict_value_ls = list(dicts.values())
    shuffle(dict_value_ls)
    new_dic = {}
    new_dic["A"] = dict_value_ls[0]
    new_dic["B"] = dict_value_ls[1]
    new_dic["C"] = dict_value_ls[2]
    new_dic["D"] = dict_value_ls[3]
    return new_dic


def judgeCollect(commonUser, level, questionID):
    result = False
    try:
        NotesCollection.objects.get(commonUser=commonUser, level=level, questionID=questionID)
        result = True
    except Exception as e:
        result = False
    return result


def getHistoryNum(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        lecture = request.POST.get("lecture")
        historyQuestion = {"Level1": {}, "Level2": {}, "Level3": {}, "Level4": {}}
        for i in History.objects.filter(commonUser=commonUser):
            if i.level != "Level1":
                example = eval(i.level).objects.get(questionID=i.questionID).example
            else:
                example = Example.objects.get(exampleID=i.questionID)
                print(example.unit.unitName)
            if example.unit.unitName == lecture:
                if historyQuestion[i.level].get("doneNum", None) is None:
                    historyQuestion[i.level]["doneNum"] = 1
                else:
                    historyQuestion[i.level]["doneNum"] += 1

        historyQuestion["Level1"]["doneNum"] = historyQuestion["Level1"].get("doneNum", 0)
        historyQuestion["Level1"]["allLevelNum"] = \
            Example.objects.filter(unit__unitName=lecture).aggregate(latest=Count('*'))["latest"]

        for i in ["Level2", "Level3", "Level4"]:
            historyQuestion[i]["doneNum"] = historyQuestion[i].get("doneNum", 0)
            historyQuestion[i]["allLevelNum"] = \
                eval(i).objects.filter(example__unit__unitName=lecture).aggregate(latest=Count('*'))["latest"]
            if i == "Level2":
                if historyQuestion["Level1"]["doneNum"] < historyQuestion["Level1"]["allLevelNum"]:
                    historyQuestion[i]["whetherLock"] = True
                else:
                    historyQuestion[i]["whetherLock"] = False
            elif i == "Level3":
                if historyQuestion["Level2"]["doneNum"] < historyQuestion["Level2"]["allLevelNum"] * 0.85:
                    historyQuestion[i]["whetherLock"] = True
                else:
                    historyQuestion[i]["whetherLock"] = False
            elif i == "Level4":
                if historyQuestion["Level3"]["doneNum"] < historyQuestion["Level3"]["allLevelNum"] * 0.85:
                    historyQuestion[i]["whetherLock"] = True
                else:
                    historyQuestion[i]["whetherLock"] = False

        allNum = 0
        for i in ["Level1", "Level2", "Level3", "Level4"]:
            if historyQuestion[i]["doneNum"] == historyQuestion[i]["allLevelNum"]:
                historyQuestion[i]["whetherDone"] = True
            else:
                historyQuestion[i]["whetherDone"] = False
            allNum += historyQuestion[i]["allLevelNum"]

        return JsonResponse({"state": "success", "allDone": historyQuestion, "allNum": allNum})
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
            options = {
                "A": level3Question.op1,
                "B": level3Question.op2,
                "C": level3Question.op3,
                "D": example.meaning
            }
            optionsDict = random_options(options)
            exampleDict["question"] = {"level": level, "questionID": level3Question.questionID,
                                       "question": level3Question.question, "options": optionsDict,
                                       "true": list(optionsDict.keys())[
                                           list(optionsDict.values()).index(example.meaning)],
                                       "whetherCollect": judgeCollect(commonUser, level, level3Question.questionID)}
    elif level == "Level4":
        if example.level4Mode:
            level4Question = example.Level4
            exampleDict["question"] = {"level": level, "questionID": level4Question.questionID,
                                       "question": level4Question.question,
                                       "whetherCollect": judgeCollect(commonUser, level, level4Question.questionID)}
    elif level == "Level2":
        level2Question = example.Level2
        concepts = []
        for i in Concept.objects.all():
            if i.conceptName != example.concept.conceptName:
                concepts.append(i.conceptName)
        options = {
            "A": concepts.pop(random.randint(0, len(concepts)-1)),
            "B": concepts.pop(random.randint(0, len(concepts)-1)),
            "C": concepts.pop(random.randint(0, len(concepts)-1)),
            "D": example.concept.conceptName,
        }
        optionsDict = random_options(options)
        exampleDict["question"] = {"level": level, "questionID": level2Question.questionID,
                                   "question": level2Question.question, "options": optionsDict,
                                   "true": list(optionsDict.keys())[
                                       list(optionsDict.values()).index(example.concept.conceptName)],
                                   "whetherCollect": judgeCollect(commonUser, level, level2Question.questionID)}

    else:
        level1Question = example
        subConcepts = {}
        try:
            subConcepts["subConcept1"] = example.subConcept1.subConceptName
        except:
            pass
        try:
            subConcepts["subConcept2"] = example.subConcept2.subConceptName
        except:
            pass
        exampleDict["question"] = {"level": level, "questionID": level1Question.exampleID,
                                   "translation": level1Question.translation,
                                   "meaning": level1Question.meaning,
                                   "question": level1Question.example, "concept": level1Question.concept.conceptName,
                                   "conceptDescription": level1Question.concept.conceptDescription,
                                   "subConcept": subConcepts,
                                   "whetherCollect": judgeCollect(commonUser, level, level1Question.exampleID)}

    return exampleDict


def toCollect(request):
    try:
        commonUserID = request.POST["commonUserID"]
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
    # try:
    commonUserID = request.POST["commonUserID"]
    commonUser = CommonUser.objects.get(commonUserID=commonUserID)
    level = request.POST["level"]
    questionID = request.POST.get("questionID")
    if level == "Level1":
        level = "Level2"
    example = eval(level).objects.get(questionID=questionID).example
    if level == "Level4":
        audiofile = request.FILES.get('file', '')
        trueAnswer = example.example
        result = audioRecognize.recognizeAudio(audiofile, trueAnswer)
        yourAnswer = result["yourAnswer"]
        result = result["result"]
    else:
        trueAnswer = example.meaning
        yourAnswer = request.POST.get("answer")
        result = (yourAnswer == trueAnswer)
    History.objects.create(commonUser=commonUser, questionID=questionID, level=level)
    commonUser.save()
    return JsonResponse({'state': 'success', "result": result, "trueAnswer": trueAnswer, "yourAnswer": yourAnswer})


# except Exception as e:
#     return JsonResponse({'state': 'fail', "error": e.__str__()})

def getUserRank(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        score = commonUser.Progress.cumScore
        allCommonUser = CommonUser.objects.order_by("-Progress__cumScore")
        check = False
        rank = 1
        for i in allCommonUser:
            if i == commonUser:
                break
            rank += 1
        if commonUser.level == "Level1":
            toNext = 500 - score
        elif commonUser.level == "Level2":
            toNext = 1000 - score
        elif commonUser.level == "Level3":
            toNext = 2000 - score
        else:
            toNext = 0
        userPercent = format(((len(allCommonUser) - rank) / len(allCommonUser)) * 100, '.2f')
        if userPercent == int(userPercent):
            userPercent = int(userPercent)

        if commonUser.lastCheckDate.strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d"):
            check = True
        return JsonResponse({"state": "success", "score": score, "rank": rank, "percent": userPercent, "toNext": toNext,
                             "commonUserName": commonUser.commonUserName, "level": commonUser.level,
                             "imageURL": commonUser.imageLocation, 'checked': check,
                             'days': commonUser.continueCheckDays})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def textToSpeechEN_CN(request):
    try:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()
        print(request.GET.get('text'))
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(ssml=request.GET.get('text'))

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Wavenet-F", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
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
        # audio = base64.b64decode(response.audio_content)
        audio = base64.b64decode(response.audio_content)
        print(audio)
        return HttpResponse(response.audio_content, content_type='audio/mp3')
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def textToSpeechEN(request):
    try:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()
        print(request.GET.get('text'))
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=request.GET.get('text'))

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        name = request.GET.get('name')
        if name == '1':
            name = "en-US-Wavenet-J"
        elif name == '2':
            name = "en-US-Wavenet-A"
        elif name == '3':
            name = 'en-US-Wavenet-H'
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name=name, ssml_gender=texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
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
        # audio = base64.b64decode(response.audio_content)
        audio = base64.b64decode(response.audio_content)
        print(audio)
        return HttpResponse(response.audio_content, content_type='audio/mp3')
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def recordAnswer(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        right = json.loads(request.POST.get("right"))
        wrong = json.loads(request.POST.get("wrong"))
        score = request.POST.get("score")
        commonUser.Progress.qstNum += len(right) + len(wrong)
        commonUser.Progress.cumScore += int(score, base=10)
        for i in right:
            History.objects.create(commonUser=commonUser, questionID=i, level=level)
        for i in wrong:
            try:
                wrongObject = Wrong.objects.get(commonUser=commonUser, level=level, questionID=i)
                wrongObject.count += 1
                wrongObject.save()
            except:
                Wrong.objects.create(commonUser=commonUser, level=level, questionID=i)
            History.objects.create(commonUser=commonUser, questionID=i, level=level)
        commonUser.Progress.save()
        if commonUser.Progress.cumScore >= 500:
            commonUser.level = "Level2"
        if commonUser.Progress.cumScore >= 1000:
            commonUser.level = "Level3"
        if commonUser.Progress.cumScore >= 2000:
            commonUser.level = "Level4"
        commonUser.save()
        return JsonResponse({'state': 'success', "score": commonUser.Progress.cumScore, "level": commonUser.level})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def getWrongNum(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        wrongQuestionNum = {}
        for level in ["Level2", "Level3", "Level4"]:
            wrongQuestionNum[level] = {}
            wrongQuestionNum[level]["wrongNum"] = \
                Wrong.objects.filter(commonUser=commonUser, level=level).aggregate(latest=Count('*'))["latest"]

        wrongQuestionNum["total"] = Wrong.objects.filter(commonUser=commonUser).aggregate(latest=Count('*'))["latest"]
        return JsonResponse({"state": "success", "wrongQuestionNum": wrongQuestionNum, "level": commonUser.level})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


def correctAnswer(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        level = request.POST.get("level")
        right = json.loads(request.POST.get("right"))
        wrong = json.loads(request.POST.get("wrong"))
        score = request.POST.get("score")
        commonUser.Progress.qstNum += len(right) + len(wrong)
        commonUser.Progress.cumScore += int(score, base=10)
        commonUser.Progress.save()
        for i in right:
            rightObject = Wrong.objects.get(commonUser=commonUser, level=level, questionID=i)
            rightObject.delete()
        for i in wrong:
            try:
                wrongObject = Wrong.objects.get(commonUser=commonUser, level=level, questionID=i)
                wrongObject.count += 1
                wrongObject.save()
            except:
                Wrong.objects.create(commonUser=commonUser, level=level, questionID=i)
        if commonUser.Progress.cumScore >= 500:
            commonUser.level = "Level2"
        if commonUser.Progress.cumScore >= 1000:
            commonUser.level = "Level3"
        if commonUser.Progress.cumScore >= 2000:
            commonUser.level = "Level4"
        commonUser.save()
        return JsonResponse({'state': 'success', "score": commonUser.Progress.cumScore, "level": commonUser.level})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})


# sudo chmod 777 /media

def signAddScore(request):
    try:
        commonUserID = request.POST.get("commonUserID")
        commonUser = CommonUser.objects.get(commonUserID=commonUserID)
        # whetherAdd = int(request.POST.get("whetherAdd"))
        now = datetime.now().strftime("%Y-%m-%d")
        if commonUser.lastCheckDate.strftime("%Y-%m-%d") != now:
            if commonUser.lastCheckDate is None or \
                    now != (commonUser.lastCheckDate + timedelta(days=1)).strftime("%Y-%m-%d"):
                # 未连续签到
                commonUser.continueCheckDays = 0
            else:
                print("已连续", (commonUser.lastCheckDate + timedelta(days=1)))
                commonUser.continueCheckDays += 1
            commonUser.lastCheckDate = datetime.now()
            commonUser.save()

            days = commonUser.continueCheckDays
            bonus = 0
            print(math.modf(days / 7.0)[0])
            if math.modf(days / 7.0)[0] == 0:
                if days >= 91:
                    bonus = 70
                else:
                    bonus = 5 * days / 7
                    print(bonus)
            commonUser.Progress.cumScore += 5 + bonus
            commonUser.Progress.save()
            print(bonus)
            if commonUser.Progress.cumScore >= 500:
                commonUser.level = "Level2"
            if commonUser.Progress.cumScore >= 1000:
                commonUser.level = "Level3"
            if commonUser.Progress.cumScore >= 2000:
                commonUser.level = "Level4"
            commonUser.save()
            print(bonus)
            return JsonResponse(
                {"state": "success", "score": commonUser.Progress.cumScore, "level": commonUser.level, "days": days,
                 "bonus": bonus})
        else:
            return JsonResponse(
                {"state": "success", "score": commonUser.Progress.cumScore, "level": commonUser.level, "checked": True})
    except Exception as e:
        return JsonResponse({'state': 'fail', "error": e.__str__()})
