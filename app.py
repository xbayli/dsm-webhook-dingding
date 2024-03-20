import requests
from flask import Flask, request, jsonify, json
import time
import hmac
import hashlib
import base64
import urllib.parse

app = Flask(__name__)


# 处理GET请求和POST请求,群晖的包应该就是从请求头发出的，多余的也可以删掉。
@app.route('/recevice_data', methods=['GET', 'POST'])
def recevice_data():
    access_token = None
    text = None
    secret = None

    # 尝试从GET请求中获取参数
    if request.args:
        access_token = request.args.get('access_token')
        text = request.args.get('text')
        secret = request.args.get('secret')

    # 如果仍未找到参数，尝试从POST请求中获取参数
    if not access_token and request.method == 'POST':
        data = request.get_json()
        if data:
            access_token = data.get('access_token')
            text = data.get('text')
            secret = data.get('secret')

    # 如果仍未找到参数，尝试从请求头中获取参数
    if not access_token:
        access_token = request.headers.get('access_token')
    if not text:
        text = request.headers.get('text')
    if not secret:
        secret = request.headers.get('secret')

    text: str = text.replace(r"\n", "\n")
    if not secret or not access_token:
        print("钉钉机器人 服务的 SECRET 或者 TOKEN 未设置!!\n取消推送")
        return
    print("钉钉机器人 服务启动")
    # sign生成算法
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    title = "[ 群晖通知 ]"

    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n{text}"}}
    dd_response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=30
    ).json()

    if not dd_response["errcode"]:
        print("钉钉机器人 推送成功！")
    else:
        print("钉钉机器人 推送失败！")

    response = {
        "errcode": "0",
        "errmsg": "ok"
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
