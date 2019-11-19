import re
import os
import json

import requests

"""
获取详细教程、获取代码帮助、提出意见建议
关注微信公众号「裸睡的猪」与猪哥联系

@Author  :   猪哥,
@Version :   2.0"
"""

s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'


class TaoBaoLogin:

    def __init__(self, session):
        """
        账号登录对象
        :param username: 用户名
        :param ua: 淘宝的ua参数
        :param TPL_password2: 加密后的密码
        """
        # 检测是否需要验证码的URL
        self.user_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        # 验证淘宝用户名密码URL
        self.verify_password_url = "https://login.taobao.com/member/login.jhtml"
        # 访问st码URL
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        # 淘宝个人 主页
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        # 淘宝用户名
        self.username = '你的用户名'
        # 淘宝重要参数，从浏览器或抓包工具中复制，可重复使用
        self.ua = '121#G4olktdt0uwlVl28xV27l94UMahfKrMV9lbvxD1IoFZ/KmVr3bx5lwLYAcFfKujVllgm+aAN0/vQA3rnqdjIlwXYLaMvN4o9lGuYZ7pIKM9STQrJEmD5lwLYAcfdK5jVVmgY+zP5KMlVA3rnEkDIbwLYOcMYPCPPOMQVBIbvsbc9MtFPD0rOaFFbbZ3glWfopCibkZ0T83Smbgi0CeIAFtZFHOpznjxSRjLbCZeTM3tA3pFDkeHXmo60bZienqC9pCibCZ0T83BhbZs0keHaF9FbbZsbnjxSpXb0MqLNK81abgj5YvIPB9JNMSEIUqypRmdCC6748u/m3MtLlHGmt5c7QZYCDra3yr5+47VL8ibH7PsqmpWX0EZZITT4WYm4oiA4iL+yFubmk2c93MGBVMTh7XFh6KInVFFaeOfsV/s7Oj8oSVm6uimGX1avuCg5mtt2HbCJx5n2S3pr1OR18KydHNG1IW/V6aDwEaPu2lZwPdEAzl9v6ECSnIAg0eln+Scre2n90lmoO4nHb12dSsn4Km5hWHW2rWufJ+mgWuXSPffPYgLIS+aoKud/2coK3glZ8JLbyKjbQpT+wuUp2bQYkF4jkTWOx2ZsW7PIFm1PJogrKvYPoxiDsjE2ZewTswdAvtQWUNjeE7Bgp2AtqK5fwH/9u4epTNPaKTRZYZvQHkRm2/hPwWmOmzH0VEqWCbQz4zJfdDlc4edt9dlVq9t3H8sxaTC0023Us1IdkdGJ8jg/gpp2aMs57vTlRYrd1wjYCi9MLuU55DkMr8Fu+BvipB3M+Fx4eaJYy6BFgfF6wwqvv3EMFZsEln0P3Bj/0YePJTOFdbAeSFXim+QW0S1YL0bI1gIMBYJuEihxNjSeIYkvX25ypIAQtQDAoEwsCB09KFr9xPUGgnR7Y+6dlPWWqmHO4IeK8TOzUQypuCK52hwVtrdHUxh52Vj5rfdyriJKHieZrFk7PAcjZC1m0CIUYy7eOZXB3PeAbo6u7rvUDGzIfaH2NElQRVjdLCK0R3/4c89la7P5BqTctSwVQjmipAB8EM/RsLFY3osKfrA1B1KkFFrXOLsrKEXLWP2yOg4NDXadpxF/zpZMeEU2+MptPqDWmrr+svV9qcNW1DRZZnOCJrSpC22xdYizzIr62Enn/GZLWf1SO19v1y9/3JHTAdF9ITz54Qui4lGVaocghf8a4zSe7KcCSnfBzuAATUFhol49JZLwZxmoFs8XPOdEBmmpVsklR+3BEMWUfO+uUZ6OVkkj3j7YHwLHsQKH08FP/GANgYZGN5/NszMNygonCf62lTxLGQCjSAKc6nzwC3cy0qtzLKe3HngS'
        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        self.TPL_password2 = '3d5c99efe5e421f26b07b66a4a0f764b307062d4deebaf085ed7bf6ad72e6a02d0c3f7c1e848e7f35c929a3decdc21d42a8e6e2a8f07272b1b1b0f9d503db7aee3fea03fc7e788c7841e0a5e99e125e0a138525b7e00ffa9b1772e1cef47bb872d7a2d742fa96a522ccc926032bcebc1adc4eb9f9951d0ca4fbc638e70340f7e'

        # 请求超时时间
        self.timeout = 3
        # session对象，用于共享cookies
        self.session = session

        if not self.username:
            raise RuntimeError('请填写你的淘宝用户名')

    def _user_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'username': self.username,
            'ua': self.ua
        }
        try:
            response = self.session.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因：')
            raise e
        needcode = response.json()['needcode']
        print('是否需要滑块验证：{}'.format(needcode))
        return needcode

    def _verify_password(self):
        """
        验证用户名密码，并获取st码申请URL
        :return: 验证成功返回st码申请地址
        """
        verify_password_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://login.taobao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?from=taobaoindex&f=top&style=&sub=true&redirect_url=https%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm',
        }
        # 登录toabao.com提交的数据，如果登录失败，可以从浏览器复制你的form data
        verify_password_data = {
            'TPL_username': self.username,
            'ncoToken': '78401cd0eb1602fc1bbf9b423a57e91953e735a5',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': 0,
            'newlogin': 0,
            'TPL_redirect_url': 'https://s.taobao.com/search?q=%E9%80%9F%E5%BA%A6%E9%80%9F%E5%BA%A6&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            # 'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61323330722E312E3735343839343433372E372E33353836363032633279704A767526663D746F70266F75743D7472756526726564697265637455524C3D6874747073253341253246253246732E74616F62616F2E636F6D25324673656172636825334671253344253235453925323538302532353946253235453525323542412532354136253235453925323538302532353946253235453525323542412532354136253236696D6766696C65253344253236636F6D6D656E64253344616C6C2532367373696425334473352D652532367365617263685F747970652533446974656D253236736F75726365496425334474622E696E64657825323673706D253344613231626F2E323031372E3230313835362D74616F62616F2D6974656D2E31253236696525334475746638253236696E69746961746976655F69642533447462696E6465787A5F3230313730333036',
            'TPL_password_2': self.TPL_password2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1440*900',
            'osVer': 'macos|10.145',
            'naviVer': 'chrome|76.038091',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'osPF': 'MacIntel',
            'appkey': '00000000',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://s.taobao.com/search?q=%E9%80%9F%E5%BA%A6%E9%80%9F%E5%BA%A6&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'TD0789BC99BFBBF893B3C8C0E1729CCA3CB0469EA11FF6D196BA826C8EB',
            'ua': self.ua
        }
        try:
            response = self.session.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data,
                              timeout=self.timeout)
            response.raise_for_status()
            # 从返回的页面中提取申请st码地址
        except Exception as e:
            print('验证用户名和密码请求失败，原因：')
            raise e
        # 提取申请st码url
        apply_st_url_match = re.search(r'<script src="(.*?)"></script>', response.text)
        # 存在则返回
        if apply_st_url_match:
            print('验证用户名密码成功，st码申请地址：{}'.format(apply_st_url_match.group(1)))
            return apply_st_url_match.group(1)
        else:
            raise RuntimeError('用户名密码验证失败！response：{}'.format(response.text))

    def _apply_st(self):
        """
        申请st码
        :return: st码
        """
        apply_st_url = self._verify_password()
        try:
            response = self.session.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败！response：{}'.format(response.text))

    def login(self):
        """
        使用st码登录
        :return:
        """
        # 加载cookies文件
        if self._load_cookies():
            return True
        # 判断是否需要滑块验证
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = self.session.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求，原因：')
            raise e
        # 登录成功，提取跳转淘宝用户主页url
        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        self.session.cookies = self._deserialization_cookies()
        # 3、判断cookies是否过期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝登录cookies成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        """
        获取淘宝昵称
        :return: 淘宝昵称
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = self.session.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))


if __name__ == '__main__':
    ul = TaoBaoLogin(s)
    ul.login()
    ul.get_taobao_nick_name()
