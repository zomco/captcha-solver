# coding: utf-8
import random
import os
import shutil
import urllib.request
import urllib3
import requests
import datetime
import sys
from imutils import paths
from src.predict_model import predict


def download(eopt_dir='tmp/eopt', total=10000, n=0):
    '''
    从网站下载验证码样本，样本用于手工打标签
    '''
    # 检查输出路径
    if os.path.exists(eopt_dir):
        shutil.rmtree(eopt_dir)
        os.makedirs(eopt_dir)
    else:
        os.makedirs(eopt_dir)

    def get_png(start=0):
        try:
            for i in range(start, total):
                urllib.request.urlretrieve('http://www.eoptoken.my/authImage', os.path.join(eopt_dir, '{}.png'.format(i)))
                print('{}.png 保存到 {} {}/{}'.format(i, eopt_dir, i + 1, total))
        except Exception:
            pngs = sorted(os.listdir(eopt_dir), key=lambda x: int(os.path.splitext(x)[0]))
            index = 0 if len(pngs) == 0 else int(os.path.splitext(pngs[-1])[0])
            get_png(start=index)

    get_png(start=n)


def detect(urls=[], eopt_dir='tmp/eopt'):
    '''
    从网站下载验证码，并对其进行识别，返回结果
    '''
    # 检查输出路径
    if os.path.exists(eopt_dir):
        shutil.rmtree(eopt_dir)
        os.makedirs(eopt_dir)
    else:
        os.makedirs(eopt_dir)
    
    for i, url in enumerate(urls):
        urllib.request.urlretrieve(url, os.path.join(eopt_dir, '{}.png'.format(i)))
    images = list(paths.list_images(eopt_dir))
    return predict(images=images)


def receive(username, password, eopt_dir='tmp/eopt'):
    '''
    登录网站领取TOKEN，返回领取TOKEN的数量
    '''
    # 检查用户名密码
    if not username or not password:
        print('[{}] 用户名和密码不能为空'.format(datetime.datetime.now()))
        return None
    # 检查路径
    if os.path.exists(eopt_dir):
        shutil.rmtree(eopt_dir)
        os.makedirs(eopt_dir)
    else:
        os.makedirs(eopt_dir)
    try:
        # 开启会话，以跨请求保持Cookie的JSESSIONID
        s = requests.session()
        # 不验证 ssl
        s.verify = False
        # 连接未验证的 HTTPS 请求时，不提示警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 先下载验证码到本地
        r = s.post('https://www.eoptoken.my/authImage', stream=True)
        auth_image = os.path.join(eopt_dir, 'authImage.png')
        if r.status_code == 200:
            with open(auth_image, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            print('[{}] 获取验证码请求失败'.format(datetime.datetime.now()))
            return None
        
        # 识别验证码
        codes = predict([auth_image])
        if not codes:
            print('[{}] 无法识别验证码'.format(datetime.datetime.now()))
            return None
        # 根据验证码响应Cookies中的JSESSIONID进行登录
        form_data = {
            'act': 'memberLogin',
            'method': 'login',
            'account': username,
            'password': password,
            'validate': codes[0]
        }
        r = s.post('https://www.eoptoken.my/action.do', data=form_data)
        rj = r.json()
        if not rj.get('flag'):
            print('[{}] 登录请求失败 {}'.format(datetime.datetime.now(), rj.get('msg')))
            return None

        # 领取EOPT
        form_data = {
            'act': 'memberEop',
            'method': 'lingQuEop'
        }
        r = s.post('https://www.eoptoken.my/action.do', data=form_data)
        rj = r.json()
        if not rj.get('flag'):
            print('[{}] 领取EOPT请求失败 {}, {}'.format(datetime.datetime.now(), rj.get('msg'), codes[0]))
            return None
  
        # EOPT结果
        form_data = {
            'act': 'memberDetailed',
            'method': 'queryMemberEopLogList',
            'page': 1
        }
        r = s.post('https://www.eoptoken.my/action.do', data=form_data)
        rj = r.json()
        if not rj.get('flag'):
            print('[{}] EOPT结果请求失败 {}'.format(datetime.datetime.now(), rj.get('msg')))
            return None
        rows = rj.get('rows')
        if not rows:
            print('[{}] EOPT结果为空'.format(datetime.datetime.now()))
            return None
        # a_date = datetime.datetime.strptime(rows[0].get('createTime'), '%Y-%m-%d %H:%M:%S').date()
        # b_date = datetime.datetime.now().date()
        # if a_date != b_date:
        #     print('[{}] 当天EOPT领取失败'.format(datetime.datetime.now()))
        #     return None
        eop = rows[0].get('eop')

        # 退出登录
        # form_data = {
        #     'act': 'memberLogin',
        #     'method': 'loginOut'
        # }
        # r = s.post('https://www.eoptoken.my/action.do', data=form_data)
        # rj = r.json()
        # if not rj.get('flag'):
        #     print('[{}] 注销请求失败 {}'.format(datetime.datetime.now(), rj.get('msg')))
        #     return None

        return eop
    except requests.RequestException as error:
        print('[{}] 请求失败 {}'.format(datetime.datetime.now(), error))


if __name__ == '__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    is_success = False
    print('[{}] [{}] 领取EOPT'.format(datetime.datetime.now(), username))
    for i in range(10):
        eop = receive(username=username, password=password)
        if eop is not None:
            is_success = True
            print('[{}] [{}] 领取成功 {}'.format(datetime.datetime.now(), username, eop))
            break
        else:
            print('[{}] [{}] 领取失败，重试 {}'.format(datetime.datetime.now(), username, i + 1))
    if not is_success:
        print('[{}] [{}] 领取失败，退出'.format(datetime.datetime.now(), username))
        sys.exit(1)
    else:
        sys.exit(0)
