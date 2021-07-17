import json
import os
from .models import *
import pandas as pd
import speech_recognition as sr
from django.http import JsonResponse, HttpResponse
from ffmpy3 import FFmpeg
import nltk
import numpy as np
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def recognize(request):
    try:
        audiofile = request.FILES.get('file', '')
        answer=request.POST.get('answer', '')
        change = os.path.join("Audio", audiofile.name)
        if not os.path.exists("Audio"):
            os.mkdir("Audio")
            os.chmod(os.path.join("Audio", audiofile.name), 0o777)
        with open(os.path.join(os.getcwd(), 'Audio', audiofile.name), 'wb') as fw:
            os.chmod(os.path.join(os.getcwd(), "Audio", audiofile.name), 0o777)
            for chunck in audiofile.chunks():
                fw.write(chunck)
        if (audiofile.name.split('.')[-1] != "wav"):
            output = os.path.join("Audio", "".join(audiofile.name.split('.')[:-1]) + ".wav")
            ff = FFmpeg(inputs={change: None}, outputs={output: '-vn -ar 44100 -ac 2 -ab 192k -f wav'})
            ff.cmd
            ff.run()
        else:
            output = os.path.join("Audio", audiofile.name)
        r = sr.Recognizer()
        test = sr.AudioFile(output)
        with test as source:
            audio = r.record(source)
        os.remove(output)
        if (audiofile.name.split('.')[-1] != "wav"):
            os.remove(change)
        # language="cmn-Hans-CN"
        result = r.recognize_google(audio, language="en-US", show_all=True)
        # Can't record
        # if len(result.get("alternative","")):
        #     userAnswer = result['alternative'][0]['transcript']
        #     checkResult = {"result":judge(qnum,userAnswer)}
        # else:
        #     userAnswer = "Nothing"
        #     checkResult = {"result":False}
        # if checkResult.get("Error","")!="":
        #     return JsonResponse({'state': 'fail', "error": checkResult["Error"]})
        # if checkResult["result"]:
        #     return JsonResponse({'state': 'success', "result": True})
        # else:
        #     addUserWrong(userID,qnum)
        #     return JsonResponse({'state': 'success', "result": False})
        judgeResult=judge(result['alternative'][0]['transcript'],answer)
        if judgeResult.get("Error","")!="":
            return JsonResponse({'state': 'fail', 'error': judgeResult.get("Error","")})
        return JsonResponse({'state':'success','result':judgeResult.get("result"),
                             "Your Answer":result['alternative'][0]['transcript'],
                             "True Answer":answer})

    except Exception as e:
        print(e)
        return JsonResponse({'state': 'fail', "error": e.__str__()})

# import logging, os
#
# # make sure there's a directory called "log"
# if not os.path.exists("./log"):
#     os.mkdir("./log")
#
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', \
#                     datefmt='%a, %d %b %Y %H:%M:%S', filename="log/debug.log", filemode='a')  # initialize the format


@csrf_exempt
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

@csrf_exempt
def judge(result,answer):
    try:
        sentences = [result, answer]
        processedSentences = processPunctuation(sentences)
        tokens = getTokens(processedSentences)
        wordVector1, wordVector2 = word2vec(tokens)
        dist = cosDistance(wordVector1, wordVector2)
        if dist > 0.75:
            compareResult=True
        else:
            compareResult=False
        return {"result":compareResult}
    except Exception as e:
        return {"Error":e.__str__()}

def processPunctuation(sentences):
    processedSentences = []
    punctuation = '''!"#$%&()*+,-./:;<=>?@[\\]^_~'{|}'''
    for sent in sentences:
        for ch in punctuation:
            sent = sent.replace(ch,"").lower()
        processedSentences.append(sent)
    return processedSentences

def getTokens(processedSentences):
    tokens1 =nltk.word_tokenize(processedSentences[0])
    tokens2 =nltk.word_tokenize(processedSentences[1])
    tokens = [tokens1,tokens2]
    return tokens


def word2vec(tokens):
    # 列出所有词 取并集
    keyWord = list(set(tokens[0] + tokens[1]))
    print(keyWord)
    wordVector1 = np.zeros(len(keyWord))
    wordVector2 = np.zeros(len(keyWord))

    for i in range(len(keyWord)):
        # 遍历key_word中每个词在句子中的出现次数
        for j in range(len(tokens[0])):
            if tokens[0][j] == keyWord[i]:
                wordVector1[i] += 1
        for k in range(len(tokens[1])):
            if tokens[1][k] == keyWord[i]:
                wordVector2[i] += 1

    return wordVector1, wordVector2

def cosDistance(vec1, vec2):
    cosDist = float(np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2)))
    return cosDist

@csrf_exempt
def welcome(request):
    lectureExcel_2 = pd.read_excel('/questionRecord/LecturesLecture  2.xlsx')
    lectureExcel_3 = pd.read_excel('/questionRecord/LecturesLecture 3.xlsx')
    lectureExcel_4 = pd.read_excel('/questionRecord/LecturesLecture 4.xlsx')
    lectureExcel_5 = pd.read_excel('/questionRecord/LecturesLecture 5.xlsx')
    lectureExcel_6 = pd.read_excel('/questionRecord/LecturesLecture 2.xlsx')
    lectureExcel_7 = pd.read_excel('/questionRecord/LecturesLecture 7.xlsx')
    lectureExcel_8 = pd.read_excel('/questionRecord/LecturesLecture 8.xlsx')
    lectureExcel_9 = pd.read_excel('/questionRecord/LecturesLecture 9.xlsx')
    lectureExcel_10 = pd.read_excel('/questionRecord/LecturesLecture 10.xlsx')
    lectureExcel_11 = pd.read_excel('/questionRecord/LecturesLecture 11.xlsx')
    toDataBase(lectureExcel_2,"Lecture  2")
    toDataBase(lectureExcel_3,"Lecture  3")
    toDataBase(lectureExcel_4,"Lecture  4")
    toDataBase(lectureExcel_5,"Lecture  5")
    toDataBase(lectureExcel_6,"Lecture  6")
    toDataBase(lectureExcel_7,"Lecture  7")
    toDataBase(lectureExcel_8,"Lecture  8")
    toDataBase(lectureExcel_9,"Lecture  9")
    toDataBase(lectureExcel_10,"Lecture  10")
    toDataBase(lectureExcel_11,"Lecture  11")

    return HttpResponse("Success")


@csrf_exempt
def toDataBase(dataframe,dataFrameName):
    for index, row in dataframe.iterrows():
        unit=Unit.objects.create(unitName=dataFrameName)
        allConceptID = unit.concept.values_list("conceptID",flat=True)
        allSubConceptName = SubConcept.objects.values_list("subConceptName", flat=True).distinct()
        if pd.isna(row['Example']):
            continue
        if row["ConceptID"] in allConceptID:
            if pd.isna(row["Sub-Concept 1"]):
                subConcept = None
            elif row["Sub-Concept 1"] in allSubConceptName:
                subConcept = SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
            else:
                subConcept = SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
            concept = Concept.objects.get(conceptID=row["ConceptID"])
        else:
            if pd.isna(row["Sub-Concept 1"]):
                subConcept = None
            elif row["Sub-Concept 1"] in allSubConceptName:
                subConcept = SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
            else:
                subConcept = SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
            concept = Concept.objects.create(conceptName=row["Concept"],conceptID=row["ConceptID"])
        if pd.isna(row["Sub-Concept 2"]):
            subConcept2 = None
        elif row["Sub-Concept 2"] in allSubConceptName:
            subConcept2 = SubConcept.objects.get(subConceptName=row["Sub-Concept 2"])
        else:
            subConcept2 = SubConcept.objects.create(subConceptName=row["Sub-Concept 2"])
        example = Example.objects.create(unit=unit,concept=concept,subConcept1=subConcept,subConcept2=subConcept2,
                                         exampleID=row["ExampleID"],example=row["Example"],meaning=row["Meaning"],
                                         translation=row["Meaning（中文）"],
                                         level2Mode=int(row["level_2"]),
                                         level3Mode=int(row["level_3"]),
                                         level4Mode=int(row["level_4"]),
                                         level5Mode=int(row["level_5"]),
                                         level6Mode=int(row["level_6"]),)
        if int(row["level_2"]):
            Level2.objects.create(questionID=row["QueationL2ID"],question=row["Question_L2"],op1=row["wrong concept 1"],
                                  op2=row["wrong concept 2"],op3=row["wrong concept 3"],example=example)
        if int(row["level_3"]):
            Level3.objects.create(questionID=row["QueationL3ID"],question=row["Question_L3"],op1=row["wrong option 1"],
                                  op2=row["wrong option 2"],op3=row["wrong option 3"],example=example)
        if int(row["level_4"]):
            Level3.objects.create(questionID=row["QueationL4ID"],question=row["Question_L4"],example=example)

