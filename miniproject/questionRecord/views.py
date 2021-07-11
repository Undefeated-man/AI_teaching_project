from wechatpy.oauth import WeChatOAuth
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

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
            print(url)
            if code:
                try:
                    wechat_oauth.fetch_access_token(code)
                    user_info = wechat_oauth.get_user_info()
                    print(user_info)
                except Exception as e:
                    print(str(e))
                    # 这里需要处理请求里包含的 code 无效的情况
                    # abort(403)
                else:
                    # 建议存储在用户表
                    request.session['user_info'] = user_info
            else:
                return redirect(url)

        return method(request)

    return warpper


# 获取用户信息UserInfo

@oauth
def userinfo(request):
    user_info = request.session.get('user_info')
    return render(request, {"openid":user_info.openid,"user_info_nickname": user_info.nickname})