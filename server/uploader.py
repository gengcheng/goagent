#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re
import getpass
import socket

def println(s, file=sys.stderr):
    assert type(s) is type(u'')
    file.write(s.encode(sys.getfilesystemencoding(), 'replace') + os.linesep)

try:
    socket.create_connection(('127.0.0.1', 8087), timeout=1).close()
    os.environ['HTTPS_PROXY'] = '127.0.0.1:8087'
except socket.error:
    println(u'警告：建议先启动 goagent 客户端或者 VPN 然后再上传，如果您的 VPN 已经打开的话，请按回车键继续。')
    raw_input()

sys.path += ['google_appengine.zip', 'google_appengine.zip/lib']

import mimetypes
mimetypes._winreg = None

import urllib2
import fancy_urllib
fancy_urllib.FancyHTTPSHandler = urllib2.HTTPSHandler

_realgetpass = getpass.getpass
def getpass_getpass(prompt='Password:', stream=None):
    try:
        import msvcrt
        password = ''
        sys.stdout.write(prompt)
        while 1:
            ch = msvcrt.getch()
            if ch == '\b':
                if password:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                else:
                    continue
            elif ch == '\r':
                sys.stdout.write(os.linesep)
                return password
            else:
                password += ch
                sys.stdout.write('*')
    except Exception:
        return _realgetpass(prompt, stream)
getpass.getpass = getpass_getpass


from google.appengine.tools import appengine_rpc, appcfg
appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH = './.appcfg_cookies'

def upload(dirname, appid):
    assert isinstance(dirname, basestring) and isinstance(appid, basestring)
    filename = os.path.join(dirname, 'app.yaml')
    assert os.path.isfile(filename), u'%s not exists!' % filename
    with open(filename, 'rb') as fp:
        yaml = fp.read()
    yaml = re.sub(r'application:\s*\S+', 'application: '+appid, yaml)
    with open(filename, 'wb') as fp:
        fp.write(yaml)
    appcfg.main(['appcfg', 'rollback', dirname])
    appcfg.main(['appcfg', 'update', dirname])


def main():
    appids = raw_input('APPID:')
    if not re.match(r'[0-9a-zA-Z\-|]+', appids):
        println(u'错误的 appid 格式，请登录 http://appengine.google.com 查看您的 appid!')
        sys.exit(-1)
    if any(x in appids.lower() for x in ('ios', 'android', 'mobile')):
        println(u'appid 不能包含 ios/android/mobile 等字样。')
        sys.exit(-1)
    try:
        os.remove('.appcfg_cookies')
    except OSError:
        pass
    for appid in appids.split('|'):
        upload('gae', appid)


if __name__ == '__main__':
    println(u'''\
===============================================================
 GoAgent服务端部署程序, 开始上传 gae 应用文件夹
 Linux/Mac 用户, 请使用 python uploader.py 来上传应用
===============================================================

请输入您的appid, 多个appid请用|号隔开
注意：appid 请勿包含 android/ios 字样，否则可能被某些网站识别成移动设备。
        '''.strip())
    main()
    println(os.linesep + u'上传成功，请不要忘记编辑proxy.ini把你的appid填进去，谢谢。按回车键退出程序。')
    raw_input()