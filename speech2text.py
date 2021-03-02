import urllib, sys
import urllib.request
import ssl


host = 'https://audio.market.alicloudapi.com'
path = '/audiolong'
method = 'POST'
appcode = ''
querys = ''
bodys = {}
url_trans = host + path

# 传送片段进行语音识别
def post_speech(pth, filetype, lang='zh'):
    bodys['format'] = filetype  # '''m4a'''
    bodys['src'] = pth  # '''D:\\github\\AI_teaching_project\\test.''' + bodys['format']
    bodys['type'] = lang
    # input(bodys)
    post_data = urllib.parse.urlencode(bodys).encode(encoding='UTF8')
    request = urllib.request.Request(url_trans, post_data)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    # 根据API的要求，定义相对应的Content-Type
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(request, context=ctx)
    content = response.read()
    if (content):
        print(content)
    return content


# 获取识别结果
def get_result(taskId):
    path = '/audioget'
    querys = ''
    bodys = {}
    url_result = host + path

    bodys['src'] = taskId
    post_data = urllib.parse.urlencode(bodys).encode(encoding='UTF8')
    request = urllib.request.Request(url_result, post_data)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(request, context=ctx)
    result = response.read()
    print(bytes(str(result), encoding="utf-8").decode())
    if (result):
        print(result)
    return result


if __name__ == '__main__':
    taskId = post_speech('''D:\\github\\AI_teaching_project\\test.m4a''', "m4a")
    result = get_result(str(taskId).split('"')[-2])
    print(result)