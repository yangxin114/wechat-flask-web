from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import json
from flask import Response
import logging
import sys
import requests
from qwen import call_with_messages

# 初始化日志
logger=logging.getLogger('log')
logger.setLevel(logging.DEBUG)  # 设置日志级别，可以根据需要调整
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# stdout_handler = logging.StreamHandler(stream=sys.stdout)  # 使用sys.stdout确保输出到标准输出
stdout_handler = logging.FileHandler("/var/log/log.txt")  # 使用指定的文件路径

stdout_handler.setFormatter(formatter)  # 设置日志格式


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)

#测试接口
@app.route('/api/test', methods=['GET'])
def test():
    return make_succ_response('测试接口')

@app.route('/api/process_wechat_message', methods=['POST'])
def process_wechat_message():
    """
    处理微信消息的函数。
    
    该函数无参数。
    
    返回:
        make_succ_response('success') 的返回值，通常是一个表示处理成功的响应。
    """
    ##接收微信消息
    params = request.get_json()
    to_user_name = params['ToUserName']
    form_user_name = params['FromUserName']
    create_time = params['CreateTime']
    msg_type = params['MsgType']
    content = params['Content']
    msgid = params['MsgId']
    
    print("FromUserName:", form_user_name)
    print("Content:", content)
    logger.info("FromUserName: %s, Content: %s", form_user_name, content)

    res = call_with_messages(content)
    res_content="暂时无法回答您的问题，服务器没有响应。"
    if(res != None):
        res_content = res.output.choices[0].message.content
    
    current_time = datetime.now()
    data = json.dumps({
       'ToUserName': form_user_name,
       'FromUserName': to_user_name,
       "CreateTime": current_time,
       "MsgType": "text",
       "Content": res_content
   },ensure_ascii=False)
    new_data= bytes(data, encoding='utf-8')
    return Response(new_data, mimetype='application/json; charset=utf-8')


def send_wechat_message(form_user_name, content):
    """
    发送微信消息给指定用户。

    参数:
    - form_user_name: 用户的openid，是微信用户的身份标识。
    - content: 要发送的消息内容。

    返回值:
    - 如果请求成功，返回接口返回的JSON对象；如果请求失败，返回None。
    """
    url = "http://api.weixin.qq.com/cgi-bin/message/custom/send"

    # 构建请求体数据
    payload = {
        "touser": form_user_name,  # 用户的openid
        "msgtype": "text",
        "text": {
            "content": content
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # 发送POST请求
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    try:
        response.raise_for_status()  # 检查响应状态码，如果不是2xx则抛出异常
    except requests.HTTPError as e:
        print(f"接口返回错误：{e}")
        return None

    print('接口返回内容:', response.text)

    return json.loads(response.text)