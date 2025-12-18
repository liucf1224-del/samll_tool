from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox
import sys
import os
import requests
import time
import hashlib
import hmac
import json
from deep_translator import GoogleTranslator  # 新增依赖

# 腾讯翻译配置
SECRET_ID = os.environ.get('TENCENT_TRANSLATE_SECRET_ID', '')
SECRET_KEY = os.environ.get('TENCENT_TRANSLATE_SECRET_KEY', '')
REGION = 'ap-guangzhou'
ENDPOINT = 'tmt.tencentcloudapi.com'
SERVICE = 'tmt'
VERSION = '2018-03-21'
ACTION = 'TextTranslate'


def sign_request(secret_id, secret_key, method, endpoint, uri, params):
    timestamp = int(time.time())
    date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))

    # 1. Build Canonical Request String
    http_request_method = method
    canonical_uri = uri
    canonical_querystring = ''
    canonical_headers = f'content-type:application/json\nhost:{endpoint}\n'
    signed_headers = 'content-type;host'
    payload_hash = hashlib.sha256(json.dumps(params).encode('utf-8')).hexdigest()
    canonical_request = (http_request_method + '\n' +
                         canonical_uri + '\n' +
                         canonical_querystring + '\n' +
                         canonical_headers + '\n' +
                         signed_headers + '\n' +
                         payload_hash)

    # 2. Build String to Sign
    algorithm = 'TC3-HMAC-SHA256'
    credential_scope = f"{date}/{SERVICE}/tc3_request"
    string_to_sign = (algorithm + '\n' +
                      str(timestamp) + '\n' +
                      credential_scope + '\n' +
                      hashlib.sha256(canonical_request.encode('utf-8')).hexdigest())

    # 3. Sign String
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    secret_date = sign(('TC3' + secret_key).encode('utf-8'), date)
    secret_service = sign(secret_date, SERVICE)
    secret_signing = sign(secret_service, 'tc3_request')
    signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # 4. Build Authorization Header
    authorization = (f"{algorithm} "
                     f"Credential={secret_id}/{credential_scope}, "
                     f"SignedHeaders={signed_headers}, "
                     f"Signature={signature}")

    return authorization, timestamp


def translate_with_tencent(source_text, target_lang="zh"):
    """
    使用腾讯翻译API进行翻译
    """
    params = {
        "SourceText": source_text,
        "Source": "auto",
        "Target": target_lang,
        "ProjectId": 0
    }

    method = 'POST'
    uri = '/'
    authorization, timestamp = sign_request(SECRET_ID, SECRET_KEY, method, ENDPOINT, uri, params)

    headers = {
        'Content-Type': 'application/json',
        'Host': ENDPOINT,
        'X-TC-Action': ACTION,
        'X-TC-Timestamp': str(timestamp),
        'X-TC-Version': VERSION,
        'X-TC-Region': REGION,
        'Authorization': authorization
    }

    try:
        response = requests.post(f'https://{ENDPOINT}{uri}', headers=headers, data=json.dumps(params))
        result = response.json()

        if 'Response' in result and 'TargetText' in result['Response']:
            return result['Response']['TargetText']
        else:
            print(f"腾讯翻译API响应错误: {result}")
            return source_text
    except Exception as e:
        print(f"网络请求异常: {e}")
        return source_text


def translate_with_google(source_text, target_lang="zh"):
    """
    使用 Google 翻译（通过 deep-translator）
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(source_text)
    except Exception as e:
        print(f"Google翻译失败: {e}")
        return source_text


def translate_text(source_text, engine="腾讯", target_lang="zh"):
    """
    通用翻译函数，根据用户选择的引擎调用不同翻译服务
    :param source_text: 原文
    :param engine: 翻译引擎（"腾讯" 或 "Google"）
    :param target_lang: 目标语言代码（"en" 或 "zh"）
    :return: 翻译结果
    """
    if engine == "腾讯":
        return translate_with_tencent(source_text, target_lang)
    elif engine == "Google":
        return translate_with_google(source_text, target_lang)
    else:
        return source_text


class TranslationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("中英翻译器")

        layout = QVBoxLayout()

        # 输入框
        self.input_label = QLabel("请输入文本：")
        layout.addWidget(self.input_label)
        self.input_text = QTextEdit()
        layout.addWidget(self.input_text)

        # 引擎选择
        engine_layout = QHBoxLayout()
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["腾讯", "Google"])
        engine_layout.addWidget(QLabel("翻译引擎："))
        engine_layout.addWidget(self.engine_combo)
        layout.addLayout(engine_layout)

        # 目标语言选择
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "英文"])
        lang_layout.addWidget(QLabel("目标语言："))
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # 翻译按钮
        self.translate_button = QPushButton("翻译")
        self.translate_button.clicked.connect(self.on_translate)
        layout.addWidget(self.translate_button)

        # 输出框
        self.output_label = QLabel("翻译结果：")
        layout.addWidget(self.output_label)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def on_translate(self):
        source_text = self.input_text.toPlainText().strip()
        if not source_text:
            return

        engine = self.engine_combo.currentText()
        target_lang = "zh" if self.lang_combo.currentText() == "中文" else "en"
        translated = translate_text(source_text, engine, target_lang)
        self.output_text.setPlainText(translated)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TranslationApp()
    window.show()
    sys.exit(app.exec_())
