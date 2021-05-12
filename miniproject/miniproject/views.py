import json
import threading
import time

from django.http import JsonResponse
from django.shortcuts import render, redirect
import speech_recognition as sr
import os
from ffmpy3 import FFmpeg
def upload(request):
    return render(request, "upload.html")

def recognize(request):
    try:
        qnum=request.POST.get('qnum','')
        audiofile=request.FILES.get('file','')
        change = os.path.join("Audio", audiofile.name)
        with open(os.path.join(os.getcwd(), 'Audio', audiofile.name), 'wb') as fw:
            for chunck in audiofile.chunks():
                fw.write(chunck)
        if(audiofile.name.split('.', 1)[1]!="wav"):
            output = os.path.join("Audio", audiofile.name.split('.', 1)[0] + "_.wav")
            ff = FFmpeg(inputs={change: None}, outputs={output: '-vn -ar 44100 -ac 2 -ab 192 -f wav'})
            ff.cmd
            ff.run()
        else:
            output=os.path.join("Audio", audiofile.name)
        r = sr.Recognizer()
        test = sr.AudioFile(output)
        with test as source:
            audio = r.record(source)
        os.remove(output)
        if (audiofile.name.split('.', 1)[1] != "wav"):
            os.remove(change)
        #language="cmn-Hans-CN"
        result = r.recognize_google(audio, language="en-US", show_all=True)
        question=result['alternative'][0]['transcript']
        answer="The Answer"
        checkResult=CheckRight({"question":question,"answer":answer})
        if checkResult.check():
            return JsonResponse({"state":"succeed","question":question,"answer":answer})
        else:
            return JsonResponse({"state":"fail","question":question,"answer":answer})
    except Exception as e:
        print(e)
        return JsonResponse({'state':'fail'})
import logging, os

# make sure there's a directory called "log"
if not os.path.exists("./log"):
    os.mkdir("./log")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', \
                    datefmt='%a, %d %b %Y %H:%M:%S', filename="log/debug.log", filemode='a')  # initialize the format


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
            logging.warning(e)
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
            logging.warning(e)

        if True in self.result_ls:
            self.state = True

        return self.state