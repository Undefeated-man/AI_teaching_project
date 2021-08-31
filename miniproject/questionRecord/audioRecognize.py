import json
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db import models as model, IntegrityError
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
        answer = request.POST.get('answer', '')
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
        judgeResult = judge(result['alternative'][0]['transcript'], answer)
        return JsonResponse(
            {'state': 'success', "result": judgeResult, "yourAnswer": result['alternative'][0]['transcript'],
             "trueAnswer": answer})

    except Exception as e:
        print(e)
        return JsonResponse({'state': 'fail', "error": e.__str__()})


@csrf_exempt
def recognizeAudio(audiofile, answer):
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
    judgeResult = judge(result['alternative'][0]['transcript'], answer)
    return {"result":judgeResult,"yourAnswer":result['alternative'][0]['transcript']}


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
def judge(result, answer):
    sentences = [result, answer]
    processedSentences = processPunctuation(sentences)
    tokens = getTokens(processedSentences)
    wordVector1, wordVector2 = word2vec(tokens)
    dist = cosDistance(wordVector1, wordVector2)
    if dist > 0.75:
        compareResult = True
    else:
        compareResult = False
    return compareResult


def processPunctuation(sentences):
    processedSentences = []
    punctuation = '''!"#$%&()*+,-./:;<=>?@[\\]^_~'{|}'''
    for sent in sentences:
        for ch in punctuation:
            sent = sent.replace(ch, "").lower()
        processedSentences.append(sent)
    return processedSentences


def getTokens(processedSentences):
    tokens1 = nltk.word_tokenize(processedSentences[0])
    tokens2 = nltk.word_tokenize(processedSentences[1])
    tokens = [tokens1, tokens2]
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
    cosDist = float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    return cosDist


@csrf_exempt
def refreshDatabase(request):
    Groups.objects.create(groupName="Default")
    lectureExcel_1 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 1.xlsx"))
    lectureExcel_2 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 2.xlsx"))
    lectureExcel_3 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 3.xlsx"))
    lectureExcel_4 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 4.xlsx"))
    lectureExcel_5 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 5.xlsx"))
    lectureExcel_6 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 6.xlsx"))
    lectureExcel_7 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 7.xlsx"))
    lectureExcel_8 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 8.xlsx"))
    lectureExcel_9 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 9.xlsx"))
    lectureExcel_10 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 10.xlsx"))
    lectureExcel_11 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 11.xlsx"))
    toDataBase(lectureExcel_1, "Lecture  1")
    toDataBase(lectureExcel_2, "Lecture  2")
    toDataBase(lectureExcel_3, "Lecture  3")
    toDataBase(lectureExcel_4, "Lecture  4")
    toDataBase(lectureExcel_5, "Lecture  5")
    toDataBase(lectureExcel_6, "Lecture  6")
    toDataBase(lectureExcel_7, "Lecture  7")
    toDataBase(lectureExcel_8, "Lecture  8")
    toDataBase(lectureExcel_9, "Lecture  9")
    toDataBase(lectureExcel_10, "Lecture  10")
    toDataBase(lectureExcel_11, "Lecture  11")

    return HttpResponse("Success")


@csrf_exempt
def toDataBase(dataframe, dataFrameName):
    if len(Unit.objects.filter(unitName=dataFrameName)) == 0:
        unit = Unit.objects.create(unitName=dataFrameName)
    else:
        unit = Unit.objects.get(unitName=dataFrameName)

    for index, row in dataframe.iterrows():
        # try:
            isHave = Concept.objects.filter(conceptName=row["Concept"])
            allSubConceptName = SubConcept.objects.values_list("subConceptName", flat=True).distinct()
            if pd.isna(row['Example']):
                continue
            if len(isHave) != 0:
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
                concept = Concept.objects.create(conceptName=row["Concept"], conceptID=row["ConceptID"], unit=unit)
            if pd.isna(row["Sub-Concept 2"]):
                subConcept2 = None
            elif row["Sub-Concept 2"] in allSubConceptName:
                subConcept2 = SubConcept.objects.get(subConceptName=row["Sub-Concept 2"])
            else:
                subConcept2 = SubConcept.objects.create(subConceptName=row["Sub-Concept 2"])
            example = Example.objects.create(unit=unit, concept=concept, subConcept1=subConcept,
                                             subConcept2=subConcept2,
                                             exampleID=row["ExampleID"], example=row["Example"], meaning=row["Meaning"],
                                             translation=row["Translation"],
                                             level2Mode=int(row["Level_2"]),
                                             level3Mode=int(row["Level_3"]),
                                             level4Mode=int(row["Level_4"]),
                                             level5Mode=int(row["Level_5"]),
                                             level6Mode=int(row["Level_6"]), )
            if int(row["Level_2"]):
                Level2.objects.create(questionID=row["QueationL2ID"], question=row["Question_L2"], example=example)
            if int(row["Level_3"]):
                Level3.objects.create(questionID=row["QueationL3ID"], question=row["Question_L3"],
                                      op1=row["Wrong option 1"],
                                      op2=row["Wrong option 2"], op3=row["Wrong option 3"], example=example)
            if int(row["Level_4"]):
                Level4.objects.create(questionID=row["QueationL4ID"], question=row["Queation_L4"], example=example)
        # except:
        #     continue


def addNewQuestion(request):
    lectureExcel_1 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 1.xlsx"))
    lectureExcel_2 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 2.xlsx"))
    lectureExcel_3 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 3.xlsx"))
    lectureExcel_4 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 4.xlsx"))
    lectureExcel_5 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 5.xlsx"))
    lectureExcel_6 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 6.xlsx"))
    lectureExcel_7 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 7.xlsx"))
    lectureExcel_8 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 8.xlsx"))
    lectureExcel_9 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 9.xlsx"))
    lectureExcel_10 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 10.xlsx"))
    lectureExcel_11 = pd.read_excel(os.path.join(".", ".", os.getcwd(), "template", "Lectures", "Lecture 11.xlsx"))
    addDataBase(lectureExcel_1, "Lecture  1")
    addDataBase(lectureExcel_2, "Lecture  2")
    addDataBase(lectureExcel_3, "Lecture  3")
    addDataBase(lectureExcel_4, "Lecture  4")
    addDataBase(lectureExcel_5, "Lecture  5")
    addDataBase(lectureExcel_6, "Lecture  6")
    addDataBase(lectureExcel_7, "Lecture  7")
    addDataBase(lectureExcel_8, "Lecture  8")
    addDataBase(lectureExcel_9, "Lecture  9")
    addDataBase(lectureExcel_10, "Lecture  10")
    addDataBase(lectureExcel_11, "Lecture  11")

    return HttpResponse("Success")


@csrf_exempt
def addDataBase(dataframe, dataFrameName):
    try:
        unit = Unit.objects.get(unitName=dataFrameName)
    except:
        unit = Unit.objects.create(unitName=dataFrameName)

    for index, row in dataframe.iterrows():
        # try:
            if pd.isna(row["ExampleID"]):
                continue
            isHave = Concept.objects.filter(conceptID=row["ConceptID"])
            allSubConceptName = SubConcept.objects.values_list("subConceptName", flat=True).distinct()
            if pd.isna(row['Example']):
                continue
            if len(isHave) != 0:
                if pd.isna(row["Sub-Concept 1"]):
                    subConcept = None
                elif row["Sub-Concept 1"] in allSubConceptName:
                    subConcept = SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
                else:
                    subConcept = SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
                concept = isHave[0]
            else:
                if pd.isna(row["Sub-Concept 1"]):
                    subConcept = None
                elif row["Sub-Concept 1"] in allSubConceptName:
                    subConcept = SubConcept.objects.get(subConceptName=row["Sub-Concept 1"])
                else:
                    subConcept = SubConcept.objects.create(subConceptName=row["Sub-Concept 1"])
                concept = Concept.objects.create(conceptName=row["Concept"], conceptID=row["ConceptID"], unit=unit)
            if pd.isna(row["Sub-Concept 2"]):
                subConcept2 = None
            elif row["Sub-Concept 2"] in allSubConceptName:
                subConcept2 = SubConcept.objects.get(subConceptName=row["Sub-Concept 2"])
            else:
                subConcept2 = SubConcept.objects.create(subConceptName=row["Sub-Concept 2"])

            try:
                example = Example.objects.get( exampleID=row["ExampleID"])
            except ObjectDoesNotExist:
                example = Example.objects.create(exampleID=row["ExampleID"])
            example.unit=unit
            example.concept = concept
            example.subConcept1 = subConcept
            example.subConcept2 = subConcept2
            example.example = row["Example"]
            example.meaning = row["Meaning"]
            example.translation = row["Translation"]
            example.level2Mode = int(row["Level_2"])
            example.level3Mode = int(row["Level_3"])
            example.level4Mode = int(row["Level_4"])
            example.level5Mode = int(row["Level_5"])
            example.level6Mode = int(row["Level_6"])
            example.save()
            if int(row["Level_2"]):
                try:
                    question = Level2.objects.get(questionID=row["QueationL2ID"])
                    question.question = row["Question_L2"]
                    question.example = example
                    question.save()
                except ObjectDoesNotExist:
                    Level2.objects.create(questionID=row["QueationL2ID"], question=row["Question_L2"], example=example)
            if int(row["Level_3"]):
                try:
                    try:
                        question = Level3.objects.get(questionID=row["QueationL3ID"])
                        question.question = row["Question_L3"]
                        question.op1 = row["Wrong option 1"]
                        question.op2 = row["Wrong option 2"]
                        question.op3 = row["Wrong option 3"]
                        question.example = example
                        question.save()
                    except ObjectDoesNotExist:
                        Level3.objects.create(questionID=row["QueationL3ID"], question=row["Question_L3"],
                                          op1=row["Wrong option 1"],
                                          op2=row["Wrong option 2"], op3=row["Wrong option 3"], example=example)
                except IntegrityError:
                    pass
            if int(row["Level_4"]):
                try:
                    question = Level4.objects.get(questionID=row["QueationL4ID"])
                    question.question=row["Queation_L4"]
                    question.example = example
                    question.save()
                except ObjectDoesNotExist:
                    Level4.objects.create(questionID=row["QueationL4ID"], question=row["Queation_L4"], example=example)
        # except:
        #     continue