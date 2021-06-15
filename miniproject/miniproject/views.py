import json
import os
import time
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import speech_recognition as sr
from questionRecord.models import *
from ffmpy3 import FFmpeg


def upload(request):
    return render(request, "upload.html")


def recognize(request):
    try:
        qnum = int(request.POST.get('qnum', ''))
        audiofile = request.FILES.get('file', '')
        userID=int(request.POST.get('userID', ''))
        change = os.path.join("Audio", audiofile.name)
        if not os.path.exists("Audio"):
            os.mkdir("Audio")
        with open(os.path.join(os.getcwd(), 'Audio', audiofile.name), 'wb') as fw:
            for chunck in audiofile.chunks():
                fw.write(chunck)
        if (audiofile.name.split('.', 1)[1] != "wav"):
            output = os.path.join("Audio", audiofile.name.split('.', 1)[0] + "_.wav")
            ff = FFmpeg(inputs={change: None}, outputs={output: '-vn -ar 44100 -ac 2 -ab 192 -f wav'})
            ff.cmd
            ff.run()
        else:
            output = os.path.join("Audio", audiofile.name)
        r = sr.Recognizer()
        test = sr.AudioFile(output)
        with test as source:
            audio = r.record(source)
        os.remove(output)
        if (audiofile.name.split('.', 1)[1] != "wav"):
            os.remove(change)
        # language="cmn-Hans-CN"
        result = r.recognize_google(audio, language="en-US", show_all=True)
        userAnswer = result['alternative'][0]['transcript']
        checkResult = judge(qnum,userAnswer)
        if checkResult.get("Error","")!="":
            return JsonResponse({'state': 'fail', "error": checkResult["Error"]})
        if checkResult:
            return JsonResponse({'state': 'success', "result": True})
        else:
            addUserWrong(userID,qnum)
            return  JsonResponse({'state': 'success', "result": False})
    except Exception as e:
        print(e)
        return JsonResponse({'state': 'fail',"error":e.__str__()})


# import logging, os
#
# # make sure there's a directory called "log"
# if not os.path.exists("./log"):
#     os.mkdir("./log")
#
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', \
#                     datefmt='%a, %d %b %Y %H:%M:%S', filename="log/debug.log", filemode='a')  # initialize the format


class CheckRight:
    """
        使用说明：
            from check import CheckRight  # 导入类
            cr = CheckRight(<your dictionary here>)  # 使用
            cr.check()

        Inputs:
            d: a dictionary, {
                    "question": <question here>,
                    "answer": <user's answer here>
                }

        Returns:
            bool
    """

    def __init__(self, d):
        try:
            self.q = d["question"]
            self.a = d["answer"]
        except Exception as e:
            pass
        self.result_ls = []
        self.data = {"Lunch is on me": ["I'll pay for lunch.", "I pay for lunch."]}
        self.state = False

    def check(self):
        try:
            for ans in self.data[self.q]:
                if self.a in ans:
                    self.result_ls.append(True)
                else:
                    self.result_ls.append(False)
        except Exception as e:
            # logging.warning(e)
            pass

        if True in self.result_ls:
            self.state = True

        return self.state


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


def judge(questionID,answer):
    try:
        return Question.objects.get(questionID=questionID).meaning==answer
    except Exception as e:
        return {"Error":e}


def welcome(request):
    lectureExcel_2 = pd.read_excel('./questionRecord/Lectures/lecture2.xlsx')
    lectureExcel_3 = pd.read_excel('./questionRecord/Lectures/lecture3.xlsx')
    lectureExcel_4 = pd.read_excel('./questionRecord/Lectures/lecture4.xlsx')
    lectureExcel_5 = pd.read_excel('./questionRecord/Lectures/lecture5.xlsx')
    lectureExcel_6 = pd.read_excel('./questionRecord/Lectures/lecture2.xlsx')
    lectureExcel_7 = pd.read_excel('./questionRecord/Lectures/lecture7.xlsx')
    lectureExcel_8 = pd.read_excel('./questionRecord/Lectures/lecture8.xlsx')
    lectureExcel_9 = pd.read_excel('./questionRecord/Lectures/lecture9.xlsx')
    lectureExcel_10 = pd.read_excel('./questionRecord/Lectures/lecture10.xlsx')
    lectureExcel_11 = pd.read_excel('./questionRecord/Lectures/lecture11.xlsx')

    # to generate a list with all the concept in all excels
    # conceptList = lectureExcel_2['Concept'].tolist() + lectureExcel_3['Concept'].tolist() + \
    #               lectureExcel_4['Concept'].tolist() + lectureExcel_5['Concept'].tolist() + \
    #               lectureExcel_6['Concept'].tolist() + lectureExcel_7['Concept'].tolist() + \
    #               lectureExcel_8['Concept'].tolist() + lectureExcel_9['Concept'].tolist() + \
    #               lectureExcel_10['Concept'].tolist() + lectureExcel_11['Concept'].tolist()

    # to generate a list with all the sub-concept 1 in all excels
    # subConceptList_1 = lectureExcel_2['Sub-Concept 1'].tolist() + lectureExcel_3['Sub-Concept 1'].tolist() + \
    #                    lectureExcel_4['Sub-Concept 1'].tolist() + lectureExcel_5['Sub-Concept 1'].tolist() + \
    #                    lectureExcel_6['Sub-Concept 1'].tolist() + lectureExcel_7['Sub-Concept 1'].tolist() + \
    #                    lectureExcel_8['Sub-Concept 1'].tolist() + lectureExcel_9['Sub-Concept 1'].tolist() + \
    #                    lectureExcel_10['Sub-Concept 1'].tolist() + lectureExcel_11['Sub-Concept 1'].tolist()

    # to generate a list with all the sub-concept 2 in all excels (llectureExcel_4 does not have sub-concept 2 column1!)
    # subConceptList_2 = lectureExcel_2['Sub-Concept 2'].tolist() + lectureExcel_3['Sub-Concept 2'].tolist() + \
    #                    lectureExcel_10['Sub-Concept 2'].tolist() + lectureExcel_5['Sub-Concept 2'].tolist() + \
    #                    lectureExcel_6['Sub-Concept 2'].tolist() + lectureExcel_7['Sub-Concept 2'].tolist() + \
    #                    lectureExcel_8['Sub-Concept 2'].tolist() + lectureExcel_9['Sub-Concept 2'].tolist() + \
    #                    lectureExcel_11['Sub-Concept 2'].tolist()

    # to generate a dataframe with unique concept in all excels
    # conceptListDataFrame = pd.Series(conceptList).dropna().drop_duplicates().reset_index().drop(labels="index", axis=1)

    # to generate a dataframe with unique sub-concept 1 & 2 in all excels
    # subConceptListDataFrame1 = pd.Series(subConceptList_1).dropna().drop_duplicates().reset_index().drop(
    #    labels="index", axis=1)
    # subConceptListDataFrame2 = pd.Series(subConceptList_2).dropna().drop_duplicates().reset_index().drop(
    #    labels="index", axis=1)
    # subConceptListDataFrame = pd.concat([subConceptListDataFrame1, subConceptListDataFrame2], axis=0,
    #                                    ignore_index=True)
    toDataBase(lectureExcel_2)
    toDataBase(lectureExcel_3)
    toDataBase(lectureExcel_4)
    toDataBase(lectureExcel_5)
    toDataBase(lectureExcel_6)
    toDataBase(lectureExcel_7)
    toDataBase(lectureExcel_8)
    toDataBase(lectureExcel_9)
    toDataBase(lectureExcel_10)
    toDataBase(lectureExcel_11)

    return HttpResponse("Success")


def toDataBase(dataframe):
    for index, row in dataframe.iterrows():
        allConceptName = Concept.objects.values_list("conceptName", flat=True).distinct()
        allSubConceptName = SubConcept.objects.values_list("subConceptName", flat=True).distinct()
        if pd.isna(row['Example']):
            continue
        if pd.isna(row['Concept']):
            question = Question.objects.create(example=row["Example"],
                                           meaning=row["Meaning （English）"], translation=row["Meaning"])
            continue
        if row["Concept"] in allConceptName:
            if pd.isna(row["Sub-Concept 1"]):
                subConcept = None
            elif row["Sub-Concept 1"] in allSubConceptName:
                subConcept = SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
            else:
                subConcept = SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
            concept = Concept.objects.get(conceptName=row["Concept"])
        else:
            if pd.isna(row["Sub-Concept 1"]):
                subConcept = None
            elif row["Sub-Concept 1"] in allSubConceptName:
                subConcept = SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
            else:
                subConcept = SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
            concept = Concept.objects.create(conceptName=row["Concept"])
        if pd.isna(row["Sub-Concept 2"]):
            subConcept2 = None
        elif row["Sub-Concept 2"] in allSubConceptName:
            subConcept2 = SubConcept.objects.get(subConceptName=row["Sub-Concept 2"])
        else:
            subConcept2 = SubConcept.objects.create(subConceptName=row["Sub-Concept 2"])
        question = Question.objects.create(concept=concept, subConcept1=subConcept, subConcept2=subConcept2,
                                           example=row["Example"],
                                           meaning=row["Meaning （English）"], translation=row["Meaning"])
